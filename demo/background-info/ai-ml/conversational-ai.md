# Conversational Evolution Guide

> **From Simple RAG to Advanced Conversational AI**
> **Focus**: Conversation Memory + Voice Integration + Real-time Considerations

## 🧠 **Phase 1: Conversational Memory Implementation**

### **Current State Analysis**

Your current implementation is **stateless** - each query is independent:

```python
# Current: No conversation context
def query_documents(self, request: QueryRequest) -> QueryResponse:
    query_vector = self.embed.embed_query(request.query)  # Only current query
    hits = self.store.search(tenant_id, query_vector, k)
    answer = self.llm.answer(hits, request.query)  # No conversation history
```

### **Conversation Memory Architecture**

#### **1. Domain Models Extension**

```python
# apps/api/app/domain/models.py

@dataclass
class ConversationMessage:
    id: str
    conversation_id: str
    role: str  # "user" | "assistant"
    content: str
    timestamp: datetime
    metadata: Dict[str, Any]  # sources, confidence, etc.

@dataclass
class Conversation:
    id: str
    tenant_id: str
    user_id: str
    title: str  # Auto-generated from first message
    created_at: datetime
    updated_at: datetime
    messages: List[ConversationMessage]
    metadata: Dict[str, Any]  # conversation settings, context

@dataclass
class ConversationalQueryRequest:
    conversation_id: Optional[str]  # None for new conversation
    query: str
    tenant_id: str
    user_id: str
    context_limit: int = 5
    memory_window: int = 10  # How many previous messages to consider
```

#### **2. Conversation Storage Port**

```python
# apps/api/app/ports/conversation_store.py

from typing import Protocol, Optional, List
from ..domain.models import Conversation, ConversationMessage

class IConversationStore(Protocol):
    def create_conversation(self, tenant_id: str, user_id: str, title: str) -> str: ...
    def get_conversation(self, conversation_id: str, tenant_id: str) -> Optional[Conversation]: ...
    def list_conversations(self, tenant_id: str, user_id: str, limit: int = 20) -> List[Conversation]: ...
    def add_message(self, conversation_id: str, message: ConversationMessage) -> None: ...
    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[ConversationMessage]: ...
    def update_conversation_title(self, conversation_id: str, title: str) -> None: ...
    def delete_conversation(self, conversation_id: str, tenant_id: str) -> bool: ...
```

#### **3. Neo4j Conversation Adapter**

```python
# apps/api/app/adapters/neo4j_conversation_store.py

class Neo4jConversationStore(IConversationStore):
    def __init__(self, cfg):
        self.driver = GraphDatabase.driver(cfg.uri, auth=(cfg.user, cfg.password))
        self.db = cfg.database

    def create_conversation(self, tenant_id: str, user_id: str, title: str) -> str:
        conversation_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"

        with self.driver.session(database=self.db) as session:
            session.run("""
                CREATE (c:Conversation {
                    id: $id,
                    tenantId: $tenantId,
                    userId: $userId,
                    title: $title,
                    createdAt: $now,
                    updatedAt: $now
                })
            """, id=conversation_id, tenantId=tenant_id, userId=user_id, title=title, now=now)

        return conversation_id

    def add_message(self, conversation_id: str, message: ConversationMessage) -> None:
        with self.driver.session(database=self.db) as session:
            session.run("""
                MATCH (c:Conversation {id: $convId})
                CREATE (m:Message {
                    id: $msgId,
                    role: $role,
                    content: $content,
                    timestamp: $timestamp,
                    metadata: $metadata
                })
                CREATE (c)-[:HAS_MESSAGE]->(m)
                SET c.updatedAt = $timestamp
            """,
            convId=conversation_id,
            msgId=message.id,
            role=message.role,
            content=message.content,
            timestamp=message.timestamp.isoformat() + "Z",
            metadata=json.dumps(message.metadata)
            )

    def get_conversation_history(self, conversation_id: str, limit: int = 50) -> List[ConversationMessage]:
        with self.driver.session(database=self.db) as session:
            result = session.run("""
                MATCH (c:Conversation {id: $convId})-[:HAS_MESSAGE]->(m:Message)
                RETURN m
                ORDER BY m.timestamp ASC
                LIMIT $limit
            """, convId=conversation_id, limit=limit)

            messages = []
            for record in result:
                m = record["m"]
                messages.append(ConversationMessage(
                    id=m["id"],
                    conversation_id=conversation_id,
                    role=m["role"],
                    content=m["content"],
                    timestamp=datetime.fromisoformat(m["timestamp"].replace("Z", "+00:00")),
                    metadata=json.loads(m.get("metadata", "{}"))
                ))
            return messages
```

#### **4. Enhanced RAG Service with Memory**

```python
# apps/api/app/domain/services.py - Enhanced RagService

class ConversationalRagService:
    def __init__(self, store: IVectorStore, llm: IChatLLM, embed: IEmbedder,
                 conversation_store: IConversationStore, rag_only: bool = False):
        self.store = store
        self.llm = llm
        self.embed = embed
        self.conversation_store = conversation_store
        self.rag_only = rag_only

    def conversational_query(self, request: ConversationalQueryRequest) -> QueryResponse:
        """Execute a conversational RAG query with memory."""

        # Get or create conversation
        if request.conversation_id:
            conversation_history = self.conversation_store.get_conversation_history(
                request.conversation_id,
                limit=request.memory_window
            )
        else:
            # Create new conversation
            title = self._generate_conversation_title(request.query)
            conversation_id = self.conversation_store.create_conversation(
                request.tenant_id,
                request.user_id,
                title
            )
            conversation_history = []
            request.conversation_id = conversation_id

        # Build contextual query considering conversation history
        contextual_query = self._build_contextual_query(request.query, conversation_history)

        # Generate query embedding (could be enhanced with conversation context)
        query_vector = self.embed.embed_query(contextual_query)

        # Search with tenant isolation
        hits = self.store.search(
            tenant_id=request.tenant_id,
            query_vector=query_vector,
            k=request.context_limit or 5
        )

        # Generate conversational answer
        answer = self._generate_conversational_answer(
            hits,
            request.query,
            conversation_history,
            rag_only=self.rag_only
        )

        # Save user message
        user_message = ConversationMessage(
            id=str(uuid.uuid4()),
            conversation_id=request.conversation_id,
            role="user",
            content=request.query,
            timestamp=datetime.utcnow(),
            metadata={}
        )
        self.conversation_store.add_message(request.conversation_id, user_message)

        # Save assistant response
        assistant_message = ConversationMessage(
            id=str(uuid.uuid4()),
            conversation_id=request.conversation_id,
            role="assistant",
            content=answer,
            timestamp=datetime.utcnow(),
            metadata={
                "sources": [hit.get("source", "") for hit in hits],
                "confidence": self._calculate_confidence(hits),
                "context_used": len(hits)
            }
        )
        self.conversation_store.add_message(request.conversation_id, assistant_message)

        # Convert hits to domain documents
        source_documents = [
            Document(
                id=hit.get("id", ""),
                title=hit.get("source", "Unknown"),
                content=hit.get("text", ""),
                source=hit.get("source", ""),
                metadata={"score": hit.get("score", 0.0)},
                tenant_id=request.tenant_id,
                created_at=datetime.utcnow()
            )
            for hit in hits
        ]

        return QueryResponse(
            answer=answer,
            sources=source_documents,
            confidence=self._calculate_confidence(hits),
            query_id=str(uuid.uuid4()),
            tenant_id=request.tenant_id,
            conversation_id=request.conversation_id
        )

    def _build_contextual_query(self, current_query: str, history: List[ConversationMessage]) -> str:
        """Enhance current query with conversation context."""
        if not history:
            return current_query

        # Take last few exchanges for context
        recent_context = []
        for msg in history[-6:]:  # Last 3 exchanges (user + assistant)
            role_prefix = "User" if msg.role == "user" else "Assistant"
            recent_context.append(f"{role_prefix}: {msg.content}")

        if recent_context:
            context_str = "\n".join(recent_context)
            return f"Previous conversation:\n{context_str}\n\nCurrent question: {current_query}"

        return current_query

    def _generate_conversational_answer(self, hits: List[Dict[str, Any]],
                                      current_query: str,
                                      history: List[ConversationMessage],
                                      rag_only: bool = False) -> str:
        """Generate answer considering conversation context."""

        # Format retrieved context
        ctx = [f"[{i+1}] {h['text']} (src: {h.get('source','')})" for i, h in enumerate(hits)]

        if rag_only:
            return "RAG_ONLY mode: returning top snippets only.\n" + "\n".join(ctx[:3])

        # Build conversation-aware system prompt
        sys_prompt = """You are the Organizational Twin, an AI assistant that helps users understand their organization through documents and data.

Key behaviors:
- Always cite sources using [1], [2], [3] format
- Maintain conversation context and refer to previous exchanges when relevant
- If the user asks follow-up questions, connect them to the previous discussion
- Be conversational but professional
- If you don't have enough information, say so clearly"""

        # Build conversation context for the LLM
        conversation_context = ""
        if history:
            recent_exchanges = []
            for msg in history[-4:]:  # Last 2 exchanges
                role = "Human" if msg.role == "user" else "Assistant"
                recent_exchanges.append(f"{role}: {msg.content}")

            if recent_exchanges:
                conversation_context = f"\nRecent conversation:\n" + "\n".join(recent_exchanges) + "\n"

        # Build user message with context and retrieved documents
        user_message = f"""{conversation_context}
Retrieved documents:
{chr(10).join(ctx)}

Current question: {current_query}

Please provide a helpful answer using the retrieved documents and conversation context."""

        # Use LangChain for response generation
        messages = [
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.llm.llm.invoke(messages)
        return response.content

    def _generate_conversation_title(self, first_query: str) -> str:
        """Generate a title for the conversation based on the first query."""
        # Simple approach - use first few words
        words = first_query.split()[:6]
        title = " ".join(words)
        if len(first_query.split()) > 6:
            title += "..."
        return title or "New Conversation"
```

#### **5. Updated Router with Conversation Support**

```python
# apps/api/app/routers/rag.py - Add conversation endpoints

@router.post("/conversation/query")
def conversational_query(payload: ConversationalQuery, request: Request):
    """Conversational query endpoint with memory."""
    user = getattr(request.state, "user", {"tenantId": "demo", "role": "owner", "uid": "dev"})
    tenant = payload.tenantId or user["tenantId"]

    # Authorization check
    if not container.tenant_service.validate_cross_tenant_access(
        user_role=user["role"],
        user_tenant=user["tenantId"],
        target_tenant=tenant
    ):
        raise HTTPException(403, "Cross-tenant access denied")

    # Create domain request
    domain_request = ConversationalQueryRequest(
        conversation_id=payload.conversationId,
        query=payload.question,
        tenant_id=tenant,
        user_id=user["uid"],
        context_limit=payload.k,
        memory_window=payload.memoryWindow or 10
    )

    # Delegate to conversational service
    response = container.conversational_rag.conversational_query(domain_request)

    return {
        "answer": response.answer,
        "sources": [
            {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "score": doc.metadata.get("score", 0.0)
            }
            for doc in response.sources
        ],
        "confidence": response.confidence,
        "conversationId": response.conversation_id,
        "queryId": response.query_id
    }

@router.get("/conversations")
def list_conversations(request: Request, limit: int = 20):
    """List user's conversations."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})

    conversations = container.conversation_store.list_conversations(
        tenant_id=user["tenantId"],
        user_id=user["uid"],
        limit=limit
    )

    return {
        "conversations": [
            {
                "id": conv.id,
                "title": conv.title,
                "createdAt": conv.created_at.isoformat(),
                "updatedAt": conv.updated_at.isoformat(),
                "messageCount": len(conv.messages)
            }
            for conv in conversations
        ]
    }

@router.get("/conversations/{conversation_id}")
def get_conversation(conversation_id: str, request: Request):
    """Get conversation with full message history."""
    user = getattr(request.state, "user", {"tenantId": "demo", "uid": "dev"})

    conversation = container.conversation_store.get_conversation(
        conversation_id,
        user["tenantId"]
    )

    if not conversation:
        raise HTTPException(404, "Conversation not found")

    return {
        "id": conversation.id,
        "title": conversation.title,
        "createdAt": conversation.created_at.isoformat(),
        "updatedAt": conversation.updated_at.isoformat(),
        "messages": [
            {
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "metadata": msg.metadata
            }
            for msg in conversation.messages
        ]
    }

class ConversationalQuery(BaseModel):
    conversationId: Optional[str] = None
    question: str
    k: int = 5
    tenantId: Optional[str] = None
    memoryWindow: Optional[int] = 10
```

---

## 🎙️ **Phase 2: Voice Integration Deep Dive**

### **Real-time vs Async Voice - The Trade-offs**

#### **Real-time Voice (Streaming)**

**What it means**: Continuous audio processing with immediate response

- User speaks → Audio streamed to server → Processed in chunks → Response streamed back
- **Latency**: 200-500ms end-to-end
- **Experience**: Natural conversation flow, interruptions possible

#### **Async Voice (Record → Process → Respond)**

**What it means**: Complete audio recording before processing

- User speaks → Complete recording → Send to server → Full processing → Response
- **Latency**: 2-5 seconds depending on recording length
- **Experience**: Walkie-talkie style, no interruptions

#### **Why You Shouldn't Settle for Async**

**For "5-minute conversation with organizational twin":**

1. **Natural Flow**: Real conversations have interruptions, clarifications, "um, actually..."
2. **User Experience**: Async feels robotic and frustrating for complex discussions
3. **Engagement**: Real-time keeps users engaged, async breaks flow
4. **Professional Feel**: Your enterprise customers expect smooth, natural interactions

### **Real-time Voice Architecture**

#### **Technical Requirements**

```python
# Real-time voice processing pipeline
class RealTimeVoiceProcessor:
    def __init__(self):
        self.audio_buffer = AudioBuffer()
        self.speech_detector = VoiceActivityDetector()
        self.transcriber = StreamingTranscriber()
        self.response_synthesizer = StreamingTTS()

    async def process_audio_stream(self, audio_stream):
        async for audio_chunk in audio_stream:
            # 1. Voice Activity Detection
            if self.speech_detector.is_speech(audio_chunk):
                self.audio_buffer.add(audio_chunk)

            # 2. Streaming transcription
            if self.speech_detector.is_pause():
                partial_text = await self.transcriber.transcribe_partial(
                    self.audio_buffer.get_audio()
                )

                # 3. Early processing for quick responses
                if self.is_complete_thought(partial_text):
                    response = await self.generate_response(partial_text)
                    yield self.response_synthesizer.synthesize_stream(response)
```

#### **Cost Considerations**

**OpenAI Whisper API (Recommended for Production)**:

- **Cost**: $0.006 per minute of audio
- **Quality**: Excellent, multilingual
- **Latency**: ~500ms for real-time
- **5-minute conversation**: ~$0.03 per conversation

**Local Whisper Models**:

- **Cost**: Hardware/compute only
- **Quality**: Good (depends on model size)
- **Latency**: Varies by hardware (200ms-2s)
- **Models**: whisper-tiny (39MB) to whisper-large (1.5GB)

**Google Speech-to-Text**:

- **Cost**: $0.024 per minute (4x more expensive)
- **Quality**: Excellent
- **Latency**: Very low (~200ms)

### **Local Whisper in Flutter/Dart**

#### **Current State (2024)**

**Direct Dart/Flutter**: No native Whisper implementation
**Available Options**:

1. **Flutter + Native Plugins**:

```dart
// Using flutter_whisper plugin (community)
import 'package:flutter_whisper/flutter_whisper.dart';

class LocalWhisperService {
  late Whisper _whisper;

  Future<void> initialize() async {
    _whisper = await Whisper.fromAsset('assets/models/whisper-tiny.bin');
  }

  Future<String> transcribe(String audioPath) async {
    return await _whisper.transcribe(audioPath);
  }
}
```

2. **WebAssembly Whisper** (Web only):

```dart
// Using whisper.wasm in Flutter web
import 'dart:js' as js;

class WebWhisperService {
  Future<String> transcribe(Uint8List audioData) async {
    return js.context.callMethod('whisperTranscribe', [audioData]);
  }
}
```

3. **Server-side Processing** (Recommended):

```dart
// Send audio to your API for processing
class ServerWhisperService {
  Future<String> transcribe(File audioFile) async {
    var request = http.MultipartRequest('POST', Uri.parse('$baseUrl/transcribe'));
    request.files.add(await http.MultipartFile.fromPath('audio', audioFile.path));

    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    return json.decode(responseData)['text'];
  }
}
```

#### **Recommended Approach for Flutter**

**Hybrid Architecture**:

1. **Mobile**: Use device speech recognition for real-time feedback
2. **Server**: Use Whisper API for accurate final transcription
3. **Fallback**: Local processing when offline

```dart
class HybridVoiceService {
  final SpeechToText _localSTT = SpeechToText();
  final ServerWhisperService _serverSTT = ServerWhisperService();

  Stream<String> transcribeRealTime(Stream<List<int>> audioStream) async* {
    // Local real-time transcription for immediate feedback
    await _localSTT.listen(
      onResult: (result) => streamController.add(result.recognizedWords),
      listenMode: ListenMode.dictation,
    );

    // Server-side accurate transcription for final processing
    final audioFile = await _saveAudioStream(audioStream);
    final accurateTranscription = await _serverSTT.transcribe(audioFile);

    yield accurateTranscription;
  }
}
```

### **Voice Implementation Roadmap**

#### **Phase 1: Basic Voice (2-3 weeks)**

```dart
// Flutter implementation
class BasicVoiceChat extends StatefulWidget {
  @override
  _BasicVoiceChatState createState() => _BasicVoiceChatState();
}

class _BasicVoiceChatState extends State<BasicVoiceChat> {
  final SpeechToText _speech = SpeechToText();
  final FlutterTts _tts = FlutterTts();
  bool _isListening = false;
  String _transcription = '';

  Future<void> _startListening() async {
    bool available = await _speech.initialize();
    if (available) {
      setState(() => _isListening = true);
      _speech.listen(
        onResult: (result) {
          setState(() => _transcription = result.recognizedWords);
          if (result.finalResult) {
            _processTranscription(_transcription);
          }
        },
      );
    }
  }

  Future<void> _processTranscription(String text) async {
    // Send to your conversational API
    final response = await _apiClient.conversationalQuery(
      question: text,
      conversationId: _currentConversationId,
    );

    // Speak the response
    await _tts.speak(response['answer']);
  }
}
```

#### **Phase 2: Real-time Voice (4-6 weeks)**

```python
# Backend real-time voice processing
from fastapi import WebSocket
import asyncio
import whisper
import openai

@app.websocket("/voice/stream")
async def voice_stream(websocket: WebSocket):
    await websocket.accept()

    # Initialize real-time components
    audio_buffer = AudioBuffer()
    vad = VoiceActivityDetector()

    try:
        while True:
            # Receive audio chunk
            audio_data = await websocket.receive_bytes()
            audio_buffer.add(audio_data)

            # Check for speech completion
            if vad.is_speech_complete(audio_buffer):
                # Transcribe
                text = await transcribe_audio(audio_buffer.get_audio())

                # Process with conversational RAG
                response = await process_conversational_query(text, user_context)

                # Generate speech
                audio_response = await text_to_speech(response['answer'])

                # Send back to client
                await websocket.send_bytes(audio_response)

                audio_buffer.clear()

    except WebSocketDisconnect:
        pass
```

#### **Phase 3: Advanced Voice Features (6-8 weeks)**

- **Interrupt handling**: Stop speaking when user starts talking
- **Emotion detection**: Analyze tone and adjust responses
- **Multi-language support**: Detect language and respond accordingly
- **Voice authentication**: Identify users by voice patterns

### **Cost Analysis for Voice**

#### **5-minute Conversation Costs**

- **Whisper API**: $0.03 per conversation
- **OpenAI TTS**: $0.015 per 1000 characters (~$0.05 per response)
- **Total per conversation**: ~$0.08-0.15
- **1000 conversations/month**: $80-150

#### **Local Processing Costs**

- **Initial setup**: Higher (model downloads, optimization)
- **Per conversation**: Only compute/electricity
- **Privacy**: Complete data control
- **Offline capability**: Works without internet

### **Recommendation: Hybrid Approach**

1. **Start with OpenAI APIs** for quick implementation and excellent quality
2. **Add local Whisper** for privacy-sensitive customers
3. **Implement real-time streaming** for natural conversation flow
4. **Use device STT** for immediate feedback, server processing for accuracy

This gives you the best of all worlds: quick time-to-market, excellent quality, privacy options, and natural conversation flow that matches your "5-minute conversation" vision.

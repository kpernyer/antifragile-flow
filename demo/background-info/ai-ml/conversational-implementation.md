# Conversational Memory Implementation Guide

> **Quick Start Guide for Adding Conversation Memory to Your Living Twin**

## 🎯 **What We've Built**

I've implemented a complete conversational memory system that extends your existing RAG architecture:

### **New Components Added:**

1. **Domain Models** (`apps/api/app/domain/models.py`)
   - `ConversationMessage`: Individual messages in a conversation
   - `Conversation`: Full conversation with metadata
   - `ConversationalQueryRequest`: Request model for conversational queries

2. **Conversation Storage Port** (`apps/api/app/ports/conversation_store.py`)
   - Abstract interface for conversation persistence
   - Follows your hexagonal architecture pattern

3. **Neo4j Conversation Adapter** (`apps/api/app/adapters/neo4j_conversation_store.py`)
   - Stores conversations and messages in Neo4j
   - Maintains tenant isolation
   - Efficient queries for conversation history

4. **Conversational RAG Service** (`apps/api/app/domain/conversational_service.py`)
   - Extends your existing RAG with conversation memory
   - Builds contextual queries using conversation history
   - Maintains conversation state automatically

5. **Updated API Endpoints** (`apps/api/app/routers/rag.py`)
   - `POST /conversation/query` - Query with conversation memory
   - `GET /conversations` - List user's conversations
   - `GET /conversations/{id}` - Get full conversation history
   - `DELETE /conversations/{id}` - Delete conversation

6. **Dependency Injection** (`apps/api/app/di.py`)
   - Wired up all new components
   - Ready to use in your existing container

## 🚀 **How to Test It**

### **1. Start Your API**

```bash
cd apps/api
uvicorn app.main:app --reload
```

### **2. Test Conversational Query**

```bash
# First message (creates new conversation)
curl -X POST "http://localhost:8000/query/conversation/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is our company policy on remote work?",
    "k": 5
  }'

# Response includes conversationId
# {
#   "answer": "Based on the documents...",
#   "conversationId": "uuid-here",
#   "sources": [...],
#   "confidence": 0.85
# }

# Follow-up message (uses conversation memory)
curl -X POST "http://localhost:8000/query/conversation/query" \
  -H "Content-Type: application/json" \
  -d '{
    "conversationId": "uuid-from-previous-response",
    "question": "What about hybrid work arrangements?",
    "k": 5
  }'
```

### **3. List Conversations**

```bash
curl -X GET "http://localhost:8000/query/conversations"
```

### **4. Get Full Conversation**

```bash
curl -X GET "http://localhost:8000/query/conversations/{conversation-id}"
```

## 🔧 **Integration with Your Mobile App**

### **Update Flutter API Client**

Your existing `ApiClientEnhanced` can be extended:

```dart
// Add to apps/mobile/lib/services/api_client.dart

class ApiClientEnhanced {
  // ... existing code ...

  Future<Map<String, dynamic>> conversationalQuery({
    required String question,
    String? conversationId,
    int k = 5,
    int memoryWindow = 10,
  }) async {
    try {
      final response = await _makeRequest(
        'POST',
        '/query/conversation/query',
        body: {
          'question': question,
          'conversationId': conversationId,
          'k': k,
          'memoryWindow': memoryWindow,
        },
      );

      if (response['success']) {
        // Save conversation locally for offline support
        await _storage.saveChatMessage({
          'conversation_id': response['conversationId'],
          'question': question,
          'answer': response['answer'],
          'sources': response['sources'],
          'confidence': response['confidence'],
          'timestamp': DateTime.now().millisecondsSinceEpoch,
          'is_synced': true,
        });
      }

      return response;
    } catch (e) {
      // Handle offline mode
      return await _handleOfflineConversationalQuery(question, conversationId);
    }
  }

  Future<List<Map<String, dynamic>>> getConversations() async {
    final response = await _makeRequest('GET', '/query/conversations');
    return List<Map<String, dynamic>>.from(response['conversations'] ?? []);
  }

  Future<Map<String, dynamic>> getConversation(String conversationId) async {
    final response = await _makeRequest('GET', '/query/conversations/$conversationId');
    return response;
  }
}
```

### **Update Chat Screen**

Your existing `ChatScreen` needs minimal changes:

```dart
// In apps/mobile/lib/features/chat/chat_screen.dart

class _ChatScreenState extends State<ChatScreen> {
  String? _currentConversationId;

  // ... existing code ...

  Future<void> _sendMessage() async {
    final question = _controller.text.trim();
    if (question.isEmpty) return;

    _controller.clear();
    setState(() => _isLoading = true);

    try {
      // Use conversational query instead of regular query
      final response = await _apiClient.conversationalQuery(
        question: question,
        conversationId: _currentConversationId,
      );

      if (response['success']) {
        // Update conversation ID for follow-up messages
        _currentConversationId = response['conversationId'];
        await _loadMessages();
      }

      // ... rest of existing error handling ...
    } finally {
      setState(() => _isLoading = false);
    }
  }
}
```

## 🎨 **Frontend Integration (React Admin)**

### **Add Conversation Support**

```typescript
// apps/admin_web/src/shared/api.ts

export interface ConversationalQuery {
  conversationId?: string;
  question: string;
  k?: number;
  memoryWindow?: number;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

export class ApiClient {
  // ... existing methods ...

  async conversationalQuery(query: ConversationalQuery): Promise<QueryResponse & { conversationId: string }> {
    return this.post('/query/conversation/query', query);
  }

  async getConversations(): Promise<{ conversations: Conversation[] }> {
    return this.get('/query/conversations');
  }

  async getConversation(id: string): Promise<ConversationDetail> {
    return this.get(`/query/conversations/${id}`);
  }
}
```

### **Conversation UI Component**

```jsx
// apps/admin_web/src/features/chat/ConversationList.jsx

import React, { useState, useEffect } from 'react';
import { apiClient } from '../../shared/api';

export function ConversationList({ onSelectConversation }) {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    try {
      const response = await apiClient.getConversations();
      setConversations(response.conversations);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading conversations...</div>;

  return (
    <div className="conversation-list">
      <h3>Recent Conversations</h3>
      {conversations.map(conv => (
        <div
          key={conv.id}
          className="conversation-item"
          onClick={() => onSelectConversation(conv.id)}
        >
          <h4>{conv.title}</h4>
          <p>{conv.messageCount} messages</p>
          <small>{new Date(conv.updatedAt).toLocaleDateString()}</small>
        </div>
      ))}
    </div>
  );
}
```

## 🗄️ **Database Schema**

The Neo4j conversation schema is automatically created when you use the service:

```cypher
// Conversation nodes
(:Conversation {
  id: "uuid",
  tenantId: "tenant-id",
  userId: "user-id",
  title: "Conversation title",
  createdAt: "2024-01-01T00:00:00Z",
  updatedAt: "2024-01-01T00:00:00Z"
})

// Message nodes
(:Message {
  id: "uuid",
  role: "user" | "assistant",
  content: "message content",
  timestamp: "2024-01-01T00:00:00Z",
  metadata: "{\"sources\": [...], \"confidence\": 0.85}"
})

// Relationships
(:Conversation)-[:HAS_MESSAGE]->(:Message)
```

## 🔄 **Migration from Existing Chat**

If you have existing chat data, you can migrate it:

```python
# tools/scripts/migrate_chat_to_conversations.py

def migrate_existing_chats():
    """Migrate existing chat messages to conversation format."""

    # Get existing messages from your current storage
    existing_messages = get_existing_chat_messages()

    # Group by user and session
    conversations = group_messages_by_conversation(existing_messages)

    # Create conversations in new format
    for user_id, message_groups in conversations.items():
        for messages in message_groups:
            conversation_id = container.conversation_store.create_conversation(
                tenant_id=messages[0]['tenant_id'],
                user_id=user_id,
                title=generate_title_from_first_message(messages[0])
            )

            for msg in messages:
                container.conversation_store.add_message(
                    conversation_id,
                    ConversationMessage(
                        id=str(uuid.uuid4()),
                        conversation_id=conversation_id,
                        role=msg['role'],
                        content=msg['content'],
                        timestamp=msg['timestamp'],
                        metadata=msg.get('metadata', {})
                    )
                )
```

## 🎯 **Next Steps**

1. **Test the API endpoints** with your existing data
2. **Update your mobile app** to use conversational queries
3. **Add conversation UI** to your admin interface
4. **Consider voice integration** using the patterns in `CONVERSATIONAL_EVOLUTION_GUIDE.md`

## 🐛 **Troubleshooting**

### **Common Issues:**

1. **Import Errors**: Make sure all new files are properly imported
2. **Neo4j Connection**: Verify your Neo4j configuration in `config.py`
3. **Missing Dependencies**: The implementation uses existing dependencies

### **Debug Endpoints:**

```bash
# Test conversation creation
curl -X POST "http://localhost:8000/query/conversation/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "test message"}'

# Check Neo4j directly
MATCH (c:Conversation)-[:HAS_MESSAGE]->(m:Message)
RETURN c, m
ORDER BY m.timestamp DESC
LIMIT 10
```

The conversational memory system is now ready to use and will provide a much more natural interaction experience for your "5-minute conversation with the organizational twin" vision! 🚀

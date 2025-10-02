# Human-in-the-Loop Architecture

## The Human-in-the-Loop Problem

### What is Human-in-the-Loop?
Human-in-the-Loop (HITL) refers to workflows where automated processes require human intervention for:
- **Approval/Rejection** - Humans approve or reject automated decisions
- **Clarification** - Humans provide missing information
- **Judgment Calls** - Humans make decisions AI cannot make
- **Quality Control** - Humans verify automated outputs

### The Core Challenges

#### 1. **Timing Uncertainty**
- Humans respond on unpredictable timescales (minutes to days)
- Systems must wait indefinitely without consuming resources
- Workflows can't block other operations

#### 2. **Scalability Issues**
- Traditional systems struggle with thousands of pending human decisions
- Memory consumption grows with waiting workflows
- Connections timeout during long waits

#### 3. **Robustness Requirements**
- System crashes must not lose pending approvals
- State must persist across restarts
- Human decisions must reach the correct workflow instance

#### 4. **Timeout Management**
- When do you give up waiting for human response?
- Should AI take over if humans don't respond?
- How to escalate stale approvals?

## How Temporal Solves HITL

### 1. Durable Execution
```python
@workflow.defn
class ApprovalWorkflow:
    def __init__(self):
        self._approved = False

    @workflow.run
    async def run(self, request):
        # Start automated process
        result = await workflow.execute_activity(
            process_document,
            request,
            task_queue=DEFAULT_QUEUE
        )

        # Wait for human approval (can wait days/weeks!)
        await workflow.wait_condition(lambda: self._approved)

        # Continue after approval
        return await workflow.execute_activity(
            finalize_document,
            result,
            task_queue=DEFAULT_QUEUE
        )

    @workflow.signal
    def approve(self):
        self._approved = True
```

**Key Benefits:**
- Workflow sleeps without consuming resources
- State persists in Temporal server
- Can wait indefinitely (days, weeks, months)
- System restarts don't affect pending approvals

### 2. Timeouts with AI Fallback

```python
@workflow.defn
class SmartApprovalWorkflow:
    def __init__(self):
        self._approved = False
        self._ai_approved = False

    @workflow.run
    async def run(self, request):
        # Process document
        result = await workflow.execute_activity(
            analyze_document,
            request,
            task_queue=OPENAI_QUEUE  # AI analysis
        )

        # Wait for human approval with timeout
        try:
            # Wait up to 24 hours for human
            await asyncio.wait_for(
                workflow.wait_condition(lambda: self._approved),
                timeout=timedelta(hours=24)
            )
            workflow.logger.info("Human approved")

        except asyncio.TimeoutError:
            # Human didn't respond - use AI decision
            workflow.logger.info("Human timeout - requesting AI decision")

            ai_decision = await workflow.execute_activity(
                ai_approval_decision,
                result,
                task_queue=OPENAI_QUEUE,
                start_to_close_timeout=timedelta(minutes=5)
            )

            if ai_decision.approved:
                self._ai_approved = True
                workflow.logger.info("AI approved instead")
            else:
                raise Exception("Both human and AI rejected")

        # Continue with approved result
        return await finalize_process(result)

    @workflow.signal
    def approve(self):
        self._approved = True
```

### 3. Escalation Patterns

```python
@workflow.defn
class EscalatingApprovalWorkflow:
    def __init__(self):
        self._approved_by = None

    @workflow.run
    async def run(self, request):
        result = await process_request(request)

        # Level 1: Wait for team member (2 hours)
        try:
            await asyncio.wait_for(
                workflow.wait_condition(lambda: self._approved_by),
                timeout=timedelta(hours=2)
            )
            workflow.logger.info(f"Approved by: {self._approved_by}")

        except asyncio.TimeoutError:
            # Level 2: Escalate to manager (4 hours)
            await workflow.execute_activity(
                notify_manager,
                request,
                task_queue=DEFAULT_QUEUE
            )

            try:
                await asyncio.wait_for(
                    workflow.wait_condition(lambda: self._approved_by),
                    timeout=timedelta(hours=4)
                )
                workflow.logger.info(f"Manager approved: {self._approved_by}")

            except asyncio.TimeoutError:
                # Level 3: Use AI decision as final fallback
                ai_decision = await workflow.execute_activity(
                    ai_approval_decision,
                    result,
                    task_queue=OPENAI_QUEUE
                )

                if not ai_decision.approved:
                    raise Exception("Approval failed at all levels")

                self._approved_by = "AI-Fallback"

        return await finalize_with_approval(result, self._approved_by)

    @workflow.signal
    def approve(self, user_id: str):
        self._approved_by = user_id
```

## Three-Worker Architecture Benefits for HITL

### Separation of Concerns

```
┌─────────────────────────────────────────────────────────┐
│                  Temporal Workflows                      │
│              (Orchestration + HITL Logic)                │
└─────────────────────────────────────────────────────────┘
         │              │                    │
         v              v                    v
┌──────────────┐ ┌──────────────┐  ┌──────────────────┐
│ Default      │ │ ML Worker    │  │ OpenAI Worker    │
│ Worker       │ │              │  │                  │
│              │ │ Handles:     │  │ Handles:         │
│ Handles:     │ │ - Training   │  │ - AI Analysis    │
│ - Basic ops  │ │ - Models     │  │ - AI Decisions   │
│ - Storage    │ │              │  │ - Fallback logic │
│ - Notify     │ │ 4-hour jobs  │  │                  │
│              │ │              │  │ Fast: seconds    │
│ Fast: ms     │ └──────────────┘  └──────────────────┘
└──────────────┘
```

### Advantages

#### 1. **Non-Blocking Human Waits**
- Workflows sleep in Temporal (no worker resources used)
- Workers remain available for other tasks
- Can handle thousands of concurrent pending approvals

#### 2. **Fast AI Fallback**
- OpenAI worker responds in seconds
- No queue contention with long-running ML jobs
- Dedicated capacity for time-sensitive decisions

#### 3. **Independent Scaling**
```yaml
# Scale for HITL workload
services:
  worker-default:
    replicas: 5  # Handle notifications, basic ops

  worker-ml:
    replicas: 1  # Rare, long-running training

  worker-openai:
    replicas: 3  # Frequent AI decisions + fallbacks
```

#### 4. **Resource Isolation**
- ML training doesn't block AI decisions
- AI fallback logic has guaranteed capacity
- Human notification system scales independently

## Real-World Example: Document Approval

### Workflow with Multiple Fallback Levels

```python
@dataclass
class DocumentApprovalRequest:
    document_id: str
    content: str
    priority: Priority
    required_approver: str
    manager_approver: str

@dataclass
class ApprovalDecision:
    approved: bool
    approver: str
    decision_type: str  # "human", "manager", "ai_fallback"
    reasoning: str
    timestamp: str

@workflow.defn
class DocumentApprovalWorkflow:
    def __init__(self):
        self._decision: ApprovalDecision | None = None

    @workflow.run
    async def run(self, request: DocumentApprovalRequest) -> ApprovalDecision:
        """
        Multi-tier approval with AI fallback
        """
        workflow.logger.info(
            f"Starting approval for document: {request.document_id}"
        )

        # Step 1: AI Pre-Analysis (immediate)
        ai_analysis = await workflow.execute_activity(
            analyze_document_risk,
            request.content,
            start_to_close_timeout=timedelta(minutes=2),
            task_queue=OPENAI_QUEUE  # Fast AI analysis
        )

        workflow.logger.info(f"AI Risk Score: {ai_analysis.risk_score}")

        # Auto-approve low-risk documents
        if ai_analysis.risk_score < 0.3:
            return ApprovalDecision(
                approved=True,
                approver="AI-Auto-Approved",
                decision_type="automatic",
                reasoning="Low risk document",
                timestamp=workflow.now().isoformat()
            )

        # Step 2: Request human approval
        await workflow.execute_activity(
            send_approval_request,
            request.required_approver,
            request.document_id,
            start_to_close_timeout=timedelta(minutes=1),
            task_queue=DEFAULT_QUEUE  # Notification
        )

        # Step 3: Wait for human (Priority-based timeout)
        if request.priority == Priority.HIGH:
            timeout = timedelta(hours=2)
        elif request.priority == Priority.NORMAL:
            timeout = timedelta(hours=8)
        else:
            timeout = timedelta(hours=24)

        try:
            await asyncio.wait_for(
                workflow.wait_condition(lambda: self._decision is not None),
                timeout=timeout
            )

            workflow.logger.info(
                f"Human decision received from: {self._decision.approver}"
            )
            return self._decision

        except asyncio.TimeoutError:
            workflow.logger.warning(
                f"Timeout waiting for {request.required_approver}"
            )

        # Step 4: Escalate to manager
        await workflow.execute_activity(
            send_escalation_notification,
            request.manager_approver,
            request.document_id,
            f"Original approver {request.required_approver} did not respond",
            start_to_close_timeout=timedelta(minutes=1),
            task_queue=DEFAULT_QUEUE
        )

        try:
            await asyncio.wait_for(
                workflow.wait_condition(lambda: self._decision is not None),
                timeout=timedelta(hours=4)
            )

            workflow.logger.info(
                f"Manager decision received from: {self._decision.approver}"
            )
            return self._decision

        except asyncio.TimeoutError:
            workflow.logger.warning(
                f"Timeout waiting for manager {request.manager_approver}"
            )

        # Step 5: AI Fallback Decision
        workflow.logger.info("Using AI fallback decision")

        ai_decision = await workflow.execute_activity(
            make_ai_approval_decision,
            request.content,
            ai_analysis,
            request.priority,
            start_to_close_timeout=timedelta(minutes=5),
            task_queue=OPENAI_QUEUE  # AI decision maker
        )

        # Log that AI made decision
        await workflow.execute_activity(
            log_ai_fallback_decision,
            request.document_id,
            ai_decision,
            f"Neither {request.required_approver} nor {request.manager_approver} responded",
            start_to_close_timeout=timedelta(minutes=1),
            task_queue=DEFAULT_QUEUE
        )

        return ApprovalDecision(
            approved=ai_decision.approved,
            approver="AI-Fallback",
            decision_type="ai_fallback",
            reasoning=ai_decision.reasoning,
            timestamp=workflow.now().isoformat()
        )

    @workflow.signal
    def human_decision(self, decision: ApprovalDecision):
        """Called by UI when human makes decision"""
        self._decision = decision

    @workflow.query
    def get_status(self) -> dict:
        """Query current approval status"""
        return {
            "has_decision": self._decision is not None,
            "workflow_id": workflow.info().workflow_id,
            "waiting_for_approval": True
        }
```

### Activity Implementations

```python
# OpenAI Worker Activities
@activity.defn
async def analyze_document_risk(content: str) -> dict:
    """Fast AI risk analysis"""
    # Uses GPT-4 to analyze document
    risk_score = await openai_risk_analysis(content)
    return {"risk_score": risk_score, "confidence": 0.85}

@activity.defn
async def make_ai_approval_decision(
    content: str,
    risk_analysis: dict,
    priority: Priority
) -> dict:
    """AI makes approval decision"""
    # More thorough AI analysis
    decision = await openai_decision_maker(content, risk_analysis, priority)
    return {
        "approved": decision.approved,
        "reasoning": decision.reasoning,
        "confidence": decision.confidence
    }

# Default Worker Activities
@activity.defn
async def send_approval_request(user_id: str, doc_id: str):
    """Send notification to user"""
    await notification_service.send(
        user_id,
        f"Please approve document {doc_id}",
        link=f"/approve/{doc_id}"
    )

@activity.defn
async def log_ai_fallback_decision(doc_id: str, decision: dict, reason: str):
    """Log when AI makes decision"""
    await audit_log.record({
        "document_id": doc_id,
        "decision_type": "ai_fallback",
        "reason": reason,
        "decision": decision
    })
```

## Scaling Properties

### Handles Massive HITL Workload

```python
# Can support thousands of concurrent approvals
# Each workflow sleeps until signaled - minimal resources

workflows_pending = 10000  # 10K documents waiting approval
worker_count = 3           # Only 3 default workers needed
memory_per_workflow = 0    # Workflows sleep in Temporal
```

### Fast AI Response Under Load

```python
# OpenAI workers dedicated to AI decisions
# Never blocked by long-running tasks

worker_openai_count = 5    # Scale for AI throughput
avg_ai_decision_time = 3   # 3 seconds per decision
throughput = 5 * 20        # ~100 decisions/minute
```

### Independent Component Scaling

```yaml
# Kubernetes scaling configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: worker-openai-hpa
spec:
  scaleTargetRef:
    name: worker-openai
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100  # Double capacity quickly
        periodSeconds: 60
```

## Robustness Guarantees

### 1. **State Persistence**
- All approval state stored in Temporal
- Survives worker crashes, restarts, deployments
- Exactly-once signal delivery

### 2. **No Lost Approvals**
- Human decisions reach correct workflow instance
- Replay-safe signal handlers
- Idempotent decision recording

### 3. **Graceful Degradation**
```
Human Available    → Best outcome (human judgment)
Human Delayed      → AI fallback (automated decision)
All Systems Down   → Workflow paused (resumes when back)
```

### 4. **Audit Trail**
```python
# Every decision logged
{
    "workflow_id": "approval-doc-123",
    "decision_path": [
        {"step": "ai_prescreen", "result": "high_risk"},
        {"step": "human_request", "user": "alice@company.com"},
        {"step": "human_timeout", "waited": "8 hours"},
        {"step": "escalation", "manager": "bob@company.com"},
        {"step": "manager_timeout", "waited": "4 hours"},
        {"step": "ai_fallback", "decision": "approved", "confidence": 0.92}
    ]
}
```

## Best Practices

### 1. **Set Appropriate Timeouts**
```python
# Base timeouts on business requirements
URGENT_APPROVAL_TIMEOUT = timedelta(hours=1)
NORMAL_APPROVAL_TIMEOUT = timedelta(hours=8)
LOW_PRIORITY_TIMEOUT = timedelta(days=2)
```

### 2. **Always Provide Fallback**
```python
# Never let workflow hang indefinitely
try:
    await wait_for_human(timeout=TIMEOUT)
except TimeoutError:
    await use_ai_decision()  # Always have plan B
```

### 3. **Monitor Fallback Rate**
```python
# Alert if AI fallback rate too high
ai_fallback_rate = ai_decisions / total_decisions
if ai_fallback_rate > 0.3:
    alert("30% of decisions using AI fallback - humans not responding")
```

### 4. **Optimize for Common Case**
```python
# Fast path for obvious decisions
if obviously_safe(document):
    return auto_approve()  # Skip human entirely

# Human only for edge cases
await request_human_review()
```

## Summary

The three-worker architecture + Temporal provides:

✅ **Scalability** - Handle unlimited concurrent human waits
✅ **Robustness** - State persists across failures
✅ **Fast Fallback** - AI decisions in seconds via dedicated worker
✅ **Resource Efficiency** - Sleeping workflows use no resources
✅ **Clear Escalation** - Multi-tier approval with timeouts
✅ **Audit Trail** - Complete decision history
✅ **Independent Scaling** - Scale each component separately

This enables sophisticated human-in-the-loop systems that scale to enterprise workloads while maintaining fast response times and robust failure handling.

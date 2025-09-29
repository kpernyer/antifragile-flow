# Implementation Plan: Strategic Alignment MVP

[Overview]
This document outlines the three-month implementation plan for a Minimum Viable Product (MVP) of the Living Twin platform. The focus is to deliver a **Strategic Alignment Platform** for mid-size organizations. The MVP will enable leadership to create and disseminate strategic goals, which the system will translate into **Priority Communications**. These communications are enriched with context from the internal **Living Knowledge Base** and external **Market Intelligence** (from simplified agents) to ensure strategic goals are understood and actionable at every level of the organization. The system will track engagement and use an intelligent escalation model to maintain strategic focus.

[Types]
This section defines the data structures required for the MVP, using business-friendly terms for user-facing concepts and technical names for internal models.

**New Data Models (Python - `apps/api/app/domain/strategic_intelligence_models.py`)**

```python
# Renaming existing models for clarity might be needed, but for now, new models:
import uuid
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class StrategicGoal(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    author_id: str
    title: str
    description: str
    target_audience: str  # e.g., 'all_managers', 'product_team'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"

class PriorityCommunication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    recipient_id: str
    source_goal_id: str
    content: str  # Personalized content for the recipient
    type: str = "nudge"  # 'nudge', 'recommendation', 'order'
    status: str = "delivered"  # 'delivered', 'seen', 'acknowledged', 'escalated'
    created_at: datetime = Field(default_factory=datetime.utcnow)
    related_internal_docs: List[str] = []
    related_market_intelligence: List[str] = []

class MarketIntelligence(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    source: str # e.g., 'RSS Feed Agent'
    source_url: str
    title: str
    summary: str
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)

class UserInteraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    user_id: str
    communication_id: str
    action: str # 'seen', 'acknowledged'
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

[Files]
This section details file modifications, adhering to the new naming conventions.

**New Files:**
-   `apps/api/app/domain/strategic_intelligence_service.py`: Core logic for processing goals, enriching context, and generating Priority Communications.
-   `apps/api/app/routers/strategic_intelligence.py`: New FastAPI router for strategic intelligence endpoints.
-   `apps/api/app/domain/market_intelligence_service.py`: Service to manage simplified external agents (e.g., RSS monitoring).
-   `apps/api/app/workers/market_intelligence_worker.py`: Background worker to periodically fetch external data.
-   `apps/admin_web/src/features/strategy/GoalComposer.jsx`: New React component for leadership to define strategic goals.
-   `apps/admin_web/src/features/user/PriorityInbox.jsx`: New React component for users to view and interact with Priority Communications.

**Modified Files:**
-   `apps/api/app/main.py`: Include the new `strategic_intelligence` router.
-   `apps/api/app/di.py`: Initialize and provide the new services.
-   `apps/api/app/domain/models.py`: Add the new Pydantic models (or place them in a new `strategic_intelligence_models.py`).
-   `apps/simulation/simulation/escalation_manager.py`: Adapt to operate on `PriorityCommunication` and `UserInteraction` data from the database.
-   `apps/admin_web/src/ui/Dashboard.jsx`: Add navigation to the "Strategic Intelligence Center", which will house the new features.
-   `apps/admin_web/src/types/schema.ts`: Update with TypeScript interfaces corresponding to the new Python models.

[Functions]
This section describes key functions, using the updated terminology.

**New Functions:**
-   `process_strategic_goal(goal: StrategicGoal)` in `StrategicIntelligenceService`: Orchestrates the dissemination of a strategic goal.
-   `generate_priority_communication(goal: StrategicGoal, user: UserData, ...)` in `StrategicIntelligenceService`: Personalizes the communication for a specific user.
-   `run_rss_monitoring_agent(...)` in `MarketIntelligenceService`: Fetches and stores new Market Intelligence data points.
-   `check_communication_status_and_escalate(user_id: str)` in `EscalationManager`: Periodically checks for unacknowledged communications and escalates them.
-   `POST /api/strategic-intelligence/goals` in `strategic_intelligence.py`: API endpoint to create a new `StrategicGoal`.
-   `GET /api/strategic-intelligence/communications` in `strategic_intelligence.py`: API endpoint for a user to fetch their `PriorityCommunication` items.
-   `POST /api/strategic-intelligence/communications/{comm_id}/acknowledge` in `strategic_intelligence.py`: Endpoint to acknowledge a communication.

[Classes]
This section outlines the classes that will encapsulate the MVP's logic.

**New Classes:**
-   `StrategicIntelligenceService` (`apps/api/app/domain/strategic_intelligence_service.py`): Orchestrates the strategic communication flow.
-   `MarketIntelligenceService` (`apps/api/app/domain/market_intelligence_service.py`): Manages external data gathering agents.

**Modified Classes:**
-   `EscalationManager` (`apps/simulation/simulation/escalation_manager.py`): Repurposed to handle the escalation logic for live `PriorityCommunication` data.

[Dependencies]
This section lists new third-party packages.

-   **`feedparser`** (Python): To be added to `apps/api/requirements.txt` for parsing RSS feeds.

[Testing]
This section defines the testing strategy.

-   **Unit Tests**: For `StrategicIntelligenceService` (user targeting, communication generation), `EscalationManager` (escalation logic), and `MarketIntelligenceService` (RSS parsing).
-   **Integration Tests**: An end-to-end test for the entire flow from goal creation to communication retrieval.
-   **Manual E2E Testing**: A test plan covering the user journey from a CEO defining a goal to a manager receiving and acknowledging a Priority Communication.

[Implementation Order]
This provides a logical sequence for implementation.

1.  **Backend Foundation (Data Models):** Implement the new Pydantic models.
2.  **Backend Core Logic (Services):** Implement the `StrategicIntelligenceService` for the internal flow.
3.  **Backend API Layer:** Create the `strategic_intelligence.py` router and endpoints.
4.  **Frontend UI Development:** Build the `GoalComposer` and `PriorityInbox` React components.
5.  **Milestone 1: Internal E2E Validation:** The primary workflow should be functional.
6.  **Backend Market Intelligence:** Implement the `MarketIntelligenceService` and worker.
7.  **Backend Context Integration:** Enhance `StrategicIntelligenceService` to include Market Intelligence.
8.  **Backend Escalation Logic:** Refactor and schedule the `EscalationManager`.
9.  **Frontend Polish:** Update the UI to display enriched context and escalation status.
10. **Final Testing and Deployment:** Execute all tests before deployment.

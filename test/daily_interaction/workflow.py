from dataclasses import dataclass
from datetime import datetime, timedelta

from activities import Activities
from temporalio import workflow


@dataclass
class Decision:
    user_id: str
    decision: str
    reason: str
    timestamp: str


@dataclass
class CompetitorThreat:
    competitor_name: str
    threat_description: str
    market_segment: str
    urgency: str  # "low", "medium", "high"


@workflow.defn
class HelloWorldWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            Activities.sayName,
            name,
            schedule_to_close_timeout=timedelta(seconds=10),
        )


@workflow.defn
class StrategicDecisionWorkflow:
    """
    CEO proposes a strategic decision, VPs provide input, CEO makes final decision
    Perfect for demonstrating human-in-the-loop with multiple stakeholders
    """

    def __init__(self) -> None:
        self._proposal: str = ""
        self._vp_responses: dict[str, Decision] = {}
        self._final_decision: str | None = None
        self._required_vps = ["john", "isac", "priya"]  # Sales, Engineering, Legal

    @workflow.run
    async def run(self, proposal: str, initiator_id: str = "mary") -> dict[str, any]:
        self._proposal = proposal

        # Create inbox messages for VPs via OrganizationalTwin activity
        activity_result = await workflow.execute_activity(
            Activities.create_strategic_decision_messages,
            args=[workflow.info().workflow_id, initiator_id, self._proposal],
            schedule_to_close_timeout=timedelta(seconds=30),
        )

        if not activity_result.get("success"):
            # In a real system, you might want to handle this error differently
            workflow.logger.error(f"Failed to create messages: {activity_result.get('error')}")

        # Wait for all VPs to respond
        await workflow.wait_condition(lambda: len(self._vp_responses) >= len(self._required_vps))

        # Wait for CEO final decision
        await workflow.wait_condition(lambda: self._final_decision is not None)

        return {
            "proposal": self._proposal,
            "vp_responses": {k: v.__dict__ for k, v in self._vp_responses.items()},
            "final_decision": self._final_decision,
            "status": "completed",
        }

    @workflow.signal
    async def vp_response(self, user_id: str, decision: str, reason: str) -> None:
        self._vp_responses[user_id] = Decision(
            user_id=user_id, decision=decision, reason=reason, timestamp=datetime.now().isoformat()
        )

    @workflow.signal
    async def ceo_final_decision(self, decision: str) -> None:
        self._final_decision = decision

    @workflow.query
    def get_status(self) -> dict[str, any]:
        pending_vps = [vp for vp in self._required_vps if vp not in self._vp_responses]
        return {
            "proposal": self._proposal,
            "responses_received": len(self._vp_responses),
            "responses_needed": len(self._required_vps),
            "pending_vps": pending_vps,
            "vp_responses": {k: v.__dict__ for k, v in self._vp_responses.items()},
            "awaiting_ceo_decision": self._final_decision is None
            and len(self._vp_responses) >= len(self._required_vps),
            "final_decision": self._final_decision,
        }


@workflow.defn
class CompetitorAnalysisWorkflow:
    """
    Sales VP reports competitor threat, Engineering & Legal provide analysis,
    CEO decides on response strategy
    """

    def __init__(self) -> None:
        self._threat: CompetitorThreat | None = None
        self._engineering_analysis: str | None = None
        self._legal_analysis: str | None = None
        self._ceo_strategy: str | None = None

    @workflow.run
    async def run(
        self,
        competitor_name: str,
        threat_description: str,
        market_segment: str,
        urgency: str,
        initiator_id: str = "john",
    ) -> dict[str, any]:
        self._threat = CompetitorThreat(
            competitor_name=competitor_name,
            threat_description=threat_description,
            market_segment=market_segment,
            urgency=urgency,
        )

        # Create inbox messages for Engineering and Legal via OrganizationalTwin activity
        activity_result = await workflow.execute_activity(
            Activities.create_competitor_analysis_messages,
            args=[
                workflow.info().workflow_id,
                initiator_id,
                competitor_name,
                threat_description,
                market_segment,
                urgency,
            ],
            schedule_to_close_timeout=timedelta(seconds=30),
        )

        if not activity_result.get("success"):
            workflow.logger.error(f"Failed to create messages: {activity_result.get('error')}")

        # Wait for both engineering and legal analysis
        await workflow.wait_condition(
            lambda: self._engineering_analysis is not None and self._legal_analysis is not None
        )

        # Wait for CEO strategy decision
        await workflow.wait_condition(lambda: self._ceo_strategy is not None)

        # Notify completion via activity
        result = {
            "threat": self._threat.__dict__,
            "engineering_analysis": self._engineering_analysis,
            "legal_analysis": self._legal_analysis,
            "ceo_strategy": self._ceo_strategy,
            "status": "completed",
        }

        await workflow.execute_activity(
            Activities.sayName,
            "Competitor analysis completed",
            schedule_to_close_timeout=timedelta(seconds=10),
        )

        return result

    @workflow.signal
    async def engineering_analysis(self, analysis: str) -> None:
        self._engineering_analysis = analysis

    @workflow.signal
    async def legal_analysis(self, analysis: str) -> None:
        self._legal_analysis = analysis

    @workflow.signal
    async def ceo_strategy(self, strategy: str) -> None:
        self._ceo_strategy = strategy

    @workflow.query
    def get_status(self) -> dict[str, any]:
        return {
            "threat": self._threat.__dict__ if self._threat else None,
            "engineering_analysis_received": self._engineering_analysis is not None,
            "legal_analysis_received": self._legal_analysis is not None,
            "awaiting_engineering": self._engineering_analysis is None,
            "awaiting_legal": self._legal_analysis is None,
            "awaiting_ceo_strategy": (
                self._engineering_analysis is not None
                and self._legal_analysis is not None
                and self._ceo_strategy is None
            ),
            "engineering_analysis": self._engineering_analysis,
            "legal_analysis": self._legal_analysis,
            "ceo_strategy": self._ceo_strategy,
        }

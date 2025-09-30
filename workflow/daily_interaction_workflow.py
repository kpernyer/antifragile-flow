
from dataclasses import dataclass, field
from datetime import timedelta

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from shared.models.types import InteractionMode
    from agent_activity.ai_activities import run_catchball, synthesize_wisdom

@dataclass
class DailyInteractionRequest:
    mode: InteractionMode
    users: list[str]
    prompt: str
    initial_state: dict[str, any] = field(default_factory=dict)

@dataclass
class DailyInteractionResult:
    success: bool
    message: str
    final_state: dict[str, any]

@workflow.defn
class DailyInteractionWorkflow:
    def __init__(self):
        self._pending_actions: dict[str, str] = {}
        self._status: str = "running"
        self._feedback: list[str] = []

    @workflow.run
    async def run(self, request: DailyInteractionRequest) -> DailyInteractionResult:
        workflow.logger.info(f"Starting daily interaction workflow in {request.mode.value} mode.")

        if request.mode == InteractionMode.CATCHBALL:
            result = await self._run_catchball_mode(request)
        elif request.mode == InteractionMode.WISDOM:
            result = await self._run_wisdom_mode(request)
        else:
            self._status = "failed"
            return DailyInteractionResult(success=False, message=f"Invalid mode: {request.mode.value}", final_state={})

        self._status = "completed"
        return result

    async def _run_catchball_mode(self, request: DailyInteractionRequest) -> DailyInteractionResult:
        current_user_index = 0
        current_state = request.initial_state

        for _ in range(len(request.users) * 2): # Allow for a few rounds of catchball
            current_user = request.users[current_user_index]
            self._pending_actions = {current_user: "review_and_refine"}

            await workflow.wait_condition(lambda: self._pending_actions.get(current_user) == "approved")

            self._pending_actions = {}

            response = await workflow.execute_activity(
                run_catchball,
                (current_user, request.prompt, current_state),
                start_to_close_timeout=timedelta(minutes=10)
            )
            current_state = response

            current_user_index = (current_user_index + 1) % len(request.users)

        return DailyInteractionResult(success=True, message="Catchball completed.", final_state=current_state)

    async def _run_wisdom_mode(self, request: DailyInteractionRequest) -> DailyInteractionResult:
        self._pending_actions = {user: "provide_feedback" for user in request.users}

        await workflow.wait_condition(lambda: not self._pending_actions)

        synthesis = await workflow.execute_activity(
            synthesize_wisdom,
            (request.prompt, self._feedback),
            start_to_close_timeout=timedelta(minutes=15)
        )

        return DailyInteractionResult(success=True, message="Wisdom synthesis completed.", final_state=synthesis)

    @workflow.query
    def status(self) -> str:
        return self._status

    @workflow.query
    def pending_actions(self) -> dict[str, str]:
        return self._pending_actions

    @workflow.signal
    def approve_step(self, user: str):
        if self._pending_actions.get(user):
            self._pending_actions[user] = "approved"

    @workflow.signal
    def reject_step(self, user: str):
        if self._pending_actions.get(user):
            self._pending_actions[user] = "rejected"

    @workflow.signal
    def provide_feedback(self, user: str, feedback: str):
        if self._pending_actions.get(user):
            self._feedback.append(feedback)
            del self._pending_actions[user]

    @workflow.signal
    def handoff_to_manager(self, manager_user_id: str):
        self._pending_actions = {manager_user_id: "review_and_approve"}

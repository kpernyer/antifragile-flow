"""
Example of how to integrate the prompt management system with agents.

Shows practical usage patterns for loading and rendering prompts
in Temporal activities and workflows.
"""

import asyncio
from typing import Any

from shared.prompts import PromptRegistry, RenderContext, load_prompt
from shared.prompts.schemas.base import TemplateRenderError


class DocumentProcessorAgent:
    """Example agent using the prompt management system."""

    def __init__(self):
        """Initialize the agent with prompt registry."""
        self.prompt_registry = PromptRegistry()

    async def analyze_document(
        self,
        document_type: str,
        document_title: str,
        document_content: str,
        specific_focus: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> str:
        """Analyze a document using the document processor prompt.

        Args:
            document_type: Type of document (contract, report, etc.)
            document_title: Title of the document
            document_content: Full text content
            specific_focus: Optional specific focus area
            user_id: User making the request
            session_id: Session identifier

        Returns:
            Rendered prompt ready for LLM API call

        Raises:
            TemplateRenderError: If prompt rendering fails
        """
        try:
            # Method 1: Using the convenience function
            return load_prompt(
                "document_processor.analyze_document",
                document_type=document_type,
                document_title=document_title,
                document_content=document_content,
                specific_focus=specific_focus,
            )

        except TemplateRenderError as e:
            # Log error and provide fallback
            print(f"Prompt rendering failed: {e}")
            return self._fallback_document_analysis_prompt(
                document_type, document_title, document_content
            )

    async def analyze_document_with_context(
        self,
        document_type: str,
        document_title: str,
        document_content: str,
        conversation_history: list[dict[str, str]] | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        **additional_context,
    ) -> tuple[str | None, str]:
        """Analyze document with full context support.

        Returns:
            Tuple of (system_prompt, user_prompt)
        """
        context = RenderContext(
            variables={
                "document_type": document_type,
                "document_title": document_title,
                "document_content": document_content,
                **additional_context,
            },
            user_id=user_id,
            session_id=session_id,
            conversation_history=conversation_history or [],
        )

        # Method 2: Using registry directly for more control
        system_prompt, user_prompt = self.prompt_registry.get_system_and_user_prompts(
            "document_processor.analyze_document", context
        )

        return system_prompt, user_prompt

    def _fallback_document_analysis_prompt(
        self, document_type: str, document_title: str, document_content: str
    ) -> str:
        """Fallback prompt if template rendering fails."""
        return f"""
        Please analyze this {document_type} document titled "{document_title}".

        Document content:
        {document_content[:2000]}...

        Please provide:
        1. A brief summary
        2. Key information extracted
        3. Strategic insights
        4. Any recommendations
        """


class ConsensusBuilderAgent:
    """Example consensus building agent."""

    def __init__(self):
        self.prompt_registry = PromptRegistry()

    async def facilitate_decision(
        self,
        decision_topic: str,
        decision_context: dict[str, Any],
        participants: list[dict[str, Any]],
        agreement_level: int,
        time_remaining: str,
        user_id: str | None = None,
    ) -> str:
        """Facilitate a group decision using consensus building prompts."""
        try:
            context = RenderContext(
                variables={
                    "decision_topic": decision_topic,
                    "decision_context": decision_context,
                    "participants": participants,
                    "agreement_level": agreement_level,
                    "time_remaining": time_remaining,
                },
                user_id=user_id,
            )

            return self.prompt_registry.get_rendered_prompt(
                "consensus_builder.facilitate_decision", context
            )

        except Exception as e:
            print(f"Error in consensus facilitation: {e}")
            return self._fallback_consensus_prompt(decision_topic, participants)

    def _fallback_consensus_prompt(
        self, decision_topic: str, participants: list[dict[str, Any]]
    ) -> str:
        """Simple fallback for consensus building."""
        participant_summary = ", ".join([p.get("name", "Unknown") for p in participants])
        return f"""
        Help facilitate a decision on: {decision_topic}

        Participants: {participant_summary}

        Please provide:
        1. Analysis of different viewpoints
        2. Areas of agreement and disagreement
        3. Suggested path forward
        4. Recommendations for consensus building
        """


class CEOPersonaAgent:
    """Example persona agent for CEO role."""

    def __init__(self):
        self.prompt_registry = PromptRegistry()

    async def strategic_thinking(
        self,
        decision_type: str,
        situation_description: str,
        team_inputs: list[dict[str, Any]] | None = None,
        financial_impact: float | None = None,
        **context_vars,
    ) -> str:
        """Generate CEO-level strategic thinking on a decision."""
        variables = {
            "decision_type": decision_type,
            "situation_description": situation_description,
            "team_inputs": team_inputs or [],
            **context_vars,
        }

        if financial_impact:
            variables["financial_impact"] = financial_impact

        return load_prompt("persona.ceo.strategic_thinking", **variables)

    async def crisis_response(
        self,
        crisis_type: str,
        severity_level: int,
        crisis_description: str,
        immediate_impacts: list[str],
        key_stakeholders: list[dict[str, str]],
    ) -> str:
        """Generate CEO crisis response."""
        return load_prompt(
            "persona.ceo.crisis_leadership",
            crisis_type=crisis_type,
            severity_level=severity_level,
            discovery_time="Just discovered",
            crisis_description=crisis_description,
            immediate_impacts=immediate_impacts,
            key_stakeholders=key_stakeholders,
        )


class WorkflowCoordinator:
    """Example workflow coordinator using prompts."""

    def __init__(self):
        self.prompt_registry = PromptRegistry()

    async def initiate_consensus_process(
        self,
        process_title: str,
        decision_topic: str,
        decision_owner: str,
        decision_deadline: str,
        participants: list[dict[str, Any]],
        success_criteria: list[str],
        **additional_context,
    ) -> str:
        """Initiate a consensus building process."""
        variables = {
            "process_title": process_title,
            "decision_topic": decision_topic,
            "decision_owner": decision_owner,
            "decision_deadline": decision_deadline,
            "participants": participants,
            "success_criteria": success_criteria,
            "impact_level": "high",  # default
            "background_context": "Decision requires stakeholder consensus",  # default
            **additional_context,
        }

        return load_prompt("workflow.consensus.initiate_process", **variables)

    async def gather_stakeholder_input(
        self,
        decision_topic: str,
        participant_role: str,
        participant_expertise: str,
        current_situation: str,
        options: list[dict[str, Any]],
        input_deadline: str,
        **context,
    ) -> str:
        """Generate input gathering prompt for stakeholders."""
        return load_prompt(
            "workflow.consensus.gather_input",
            decision_topic=decision_topic,
            participant_role=participant_role,
            participant_expertise=participant_expertise,
            current_situation=current_situation,
            options=options,
            input_deadline=input_deadline,
            **context,
        )


# Example usage patterns
async def example_usage():
    """Demonstrate various usage patterns."""

    # Example 1: Simple document analysis
    doc_agent = DocumentProcessorAgent()
    analysis_prompt = await doc_agent.analyze_document(
        document_type="contract",
        document_title="Software License Agreement",
        document_content="This agreement governs the use of...",
        specific_focus="legal_obligations",
    )
    print("Document Analysis Prompt:")
    print(analysis_prompt)
    print("\n" + "=" * 50 + "\n")

    # Example 2: CEO strategic thinking
    ceo_agent = CEOPersonaAgent()
    strategic_prompt = await ceo_agent.strategic_thinking(
        decision_type="strategic",
        situation_description="Considering acquisition of competitor",
        financial_impact=50000000.0,
        team_inputs=[
            {
                "role": "VP Engineering",
                "recommendation": "Proceed with caution",
                "rationale": "Technical integration will be complex",
            }
        ],
    )
    print("CEO Strategic Thinking Prompt:")
    print(strategic_prompt)
    print("\n" + "=" * 50 + "\n")

    # Example 3: Workflow initiation
    coordinator = WorkflowCoordinator()
    process_prompt = await coordinator.initiate_consensus_process(
        process_title="Q2 Budget Allocation",
        decision_topic="Allocate Q2 budget across departments",
        decision_owner="Mary Chen, CEO",
        decision_deadline="End of month",
        participants=[
            {
                "name": "John Smith",
                "role": "VP Sales",
                "expertise": "Revenue forecasting",
                "stake": "Sales team budget",
            }
        ],
        success_criteria=[
            "All departments agree on allocation",
            "Budget aligns with strategic goals",
        ],
    )
    print("Consensus Process Initiation:")
    print(process_prompt)


# Utility functions for common patterns
def get_all_available_prompts() -> dict[str, list[str]]:
    """Get all available prompts organized by category."""
    registry = PromptRegistry()
    prompts_by_category = {}

    for template in registry.list_prompts():
        category = template.metadata.category
        if category not in prompts_by_category:
            prompts_by_category[category] = []
        prompts_by_category[category].append(template.metadata.id)

    return prompts_by_category


def validate_all_prompts() -> dict[str, list[str]]:
    """Validate all prompts and return any errors."""
    registry = PromptRegistry()
    return registry.validate_all_templates()


if __name__ == "__main__":
    asyncio.run(example_usage())

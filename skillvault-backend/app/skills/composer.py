from typing import Any
from pydantic import BaseModel, Field
from app.services.llm_provider import LLMProvider
from app.skills.graph_validator import GraphValidator, WorkflowValidationResult


class WorkflowStepProposal(BaseModel):
    step_number: int = Field(..., description="1-based step index in execution order")
    skill_id: str = Field(..., description="Target Skill ID to execute")
    input_mapping: dict[str, Any] = Field(
        default_factory=dict,
        description="Mapping of inputs e.g. {'data': '{{task.data}}', 'input_file': '{{steps.1.result}}'}",
    )
    output_mapping: dict[str, Any] = Field(
        default_factory=dict,
        description="Output result property mapping",
    )


class WorkflowProposal(BaseModel):
    name: str = Field(..., description="Descriptive workflow name")
    description: str = Field(..., description="Workflow capability summary")
    steps: list[WorkflowStepProposal] = Field(..., description="Ordered list of workflow steps")


class SkillComposer:
    def __init__(self, llm_provider: LLMProvider):
        self.llm_provider = llm_provider
        self.validator = GraphValidator()

    async def compose_workflow(
        self,
        task: str,
        available_skills: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Synthesizes a multi-step Skill Workflow graph using LLM structured output,
        validating graph DAG properties prior to execution.
        """
        skill_catalog = [
            {
                "id": s.get("id") or s.get("skill_id"),
                "name": s.get("name"),
                "capability": s.get("capability"),
                "input_schema": s.get("input_schema"),
                "output_schema": s.get("output_schema"),
            }
            for s in available_skills
        ]

        system_prompt = (
            "You are an expert AI Capability Workflow Architect. "
            "Given a user task and a list of available Skills, construct a multi-step execution workflow graph. "
            "Return a structured WorkflowProposal where each step references a valid skill_id from the catalog and "
            "specifies parameter input_mapping using Jinja-like placeholders such as '{{task.input}}' or '{{steps.1.output}}'."
        )

        user_prompt = (
            f"User Task: {task}\n\n"
            f"Available Skills Catalog:\n{skill_catalog}\n\n"
            "Propose the optimal workflow graph."
        )

        proposal: WorkflowProposal = await self.llm_provider.generate_structured(
            prompt=user_prompt,
            response_model=WorkflowProposal,
            system_prompt=system_prompt,
        )

        existing_skill_ids = {s["id"] for s in skill_catalog if s["id"]}
        steps_dict = [s.model_dump() for s in proposal.steps]

        validation: WorkflowValidationResult = self.validator.validate_graph(
            steps=steps_dict,
            existing_skill_ids=existing_skill_ids,
        )

        if not validation.valid:
            raise ValueError(f"Workflow composition validation failed: {'; '.join(validation.errors)}")

        return {
            "name": proposal.name,
            "description": proposal.description,
            "steps": steps_dict,
            "validation": validation.model_dump(),
        }

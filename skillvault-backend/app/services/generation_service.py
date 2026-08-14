from typing import Any
from app.agent.prompts import SKILL_GENERATION_PROMPT, TASK_ANALYSIS_PROMPT
from app.schemas.skill import GeneratedSkill
from app.schemas.task import TaskAnalysis
from app.services.llm_provider import LLMProvider
from app.skills.generator import DefaultSkillGenerator, SkillGenerationContext, SkillGenerator
from app.skills.validator import PythonASTValidator, SkillValidator, ValidationResult


class GenerationService:
    """
    Orchestrates Task Analysis, Skill Generation via SkillGenerator,
    Static AST Validation via SkillValidator, and Duplicate Skill Detection.
    """

    def __init__(
        self,
        llm_provider: LLMProvider,
        generator: SkillGenerator | None = None,
        validator: SkillValidator | None = None,
    ):
        self.llm = llm_provider
        self.generator = generator or DefaultSkillGenerator(llm_provider)
        self.validator = validator or PythonASTValidator()

    async def analyze_task(self, user_input: str) -> TaskAnalysis:
        prompt = f"Analyze this user request:\n\n\"{user_input}\""
        return await self.llm.generate_structured(
            prompt=prompt,
            schema_cls=TaskAnalysis,
            system_prompt=TASK_ANALYSIS_PROMPT,
        )

    async def generate_skill(
        self,
        user_input: str,
        task_analysis: TaskAnalysis,
        retrieved_skills: list[dict[str, Any]] | None = None,
        retrieval_scores: list[float] | None = None,
    ) -> GeneratedSkill:
        context = SkillGenerationContext(
            task_description=user_input,
            retrieved_skills=retrieved_skills or [],
            retrieval_scores=retrieval_scores or [],
            failure_reason="No candidate skill met the required capability matching threshold.",
            available_capabilities=task_analysis.required_capabilities,
        )

        return await self.generator.generate(
            task_description=user_input,
            context=context,
        )

    async def validate_skill(self, skill: GeneratedSkill) -> ValidationResult:
        return await self.validator.validate(skill)

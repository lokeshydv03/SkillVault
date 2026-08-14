from typing import Any, Protocol
from pydantic import BaseModel, Field

from app.schemas.skill import GeneratedSkill
from app.services.llm_provider import LLMProvider


class SkillGenerationContext(BaseModel):
    task_description: str
    task_input: dict[str, Any] | None = None
    retrieved_skills: list[dict[str, Any]] = Field(default_factory=list)
    retrieval_scores: list[float] = Field(default_factory=list)
    failure_reason: str | None = None
    available_capabilities: list[str] = Field(default_factory=list)


class SkillGenerator(Protocol):
    async def generate(
        self,
        task_description: str,
        context: SkillGenerationContext,
    ) -> GeneratedSkill:
        ...


SYSTEM_PROMPT = """You are SkillVault's Skill Generator.

Your job is to synthesize a reusable, deterministic Python Skill that solves the user's task requirement.

RULES FOR THE GENERATED SKILL:
1. The entrypoint function MUST be named `run(input_data: dict) -> dict`.
2. The function MUST take a dictionary as input and return a JSON-serializable dictionary.
3. ABSOLUTELY FORBIDDEN OPERATIONS:
   - Do NOT use `exec`, `eval`, `compile`, or `__import__`.
   - Do NOT use `subprocess`, `os.system`, `os.popen`, or shell commands.
   - Do NOT make network or socket calls (`requests`, `urllib`, `socket`, `http.client`).
   - Do NOT access system configuration, secrets, or host environment variables.
   - Do NOT attempt to access SkillVault's internal database.
4. Do NOT hardcode specific user query strings; make the code general and reusable.
5. Provide clear input_schema and output_schema definitions as JSON objects.
6. Declare any third-party Python packages required in `dependencies` (e.g., ["pandas", "numpy"]).
7. Do NOT wrap code in markdown code fences in the JSON response field.
8. Output ONLY valid JSON matching the required schema for GeneratedSkill.
"""


class DefaultSkillGenerator:
    """Standard implementation of SkillGenerator protocol using configured LLMProvider."""

    def __init__(self, llm: LLMProvider):
        self.llm = llm

    async def generate(
        self,
        task_description: str,
        context: SkillGenerationContext,
    ) -> GeneratedSkill:
        retrieved_summary = []
        for s in context.retrieved_skills:
            retrieved_summary.append(
                f"- Skill: '{s.get('name')}', Score: {s.get('score')}, Capability: {s.get('capability')}"
            )
        skills_str = "\n".join(retrieved_summary) if retrieved_summary else "None"

        prompt = f"""USER TASK REQUEST:
{task_description}

CANDIDATE SKILLS RETRIEVED:
{skills_str}

REASON WHY EXISTING SKILLS ARE INSUFFICIENT:
{context.failure_reason or 'No candidate skill met the required capability matching threshold.'}

Generate a clean, reusable Python skill that fulfills this request following all system rules.
"""

        return await self.llm.generate_structured(
            prompt=prompt,
            schema_cls=GeneratedSkill,
            system_prompt=SYSTEM_PROMPT,
        )

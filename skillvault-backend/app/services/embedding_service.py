from typing import Any
from app.services.llm_provider import LLMProvider


class EmbeddingService:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider

    async def generate_embedding(self, text: str) -> list[float]:
        if not text.strip():
            text = "empty query"
        return await self.llm.embed(text)

    async def generate_skill_embedding(
        self,
        name: str,
        description: str,
        capability: str,
        input_schema: dict[str, Any] | None = None,
        output_schema: dict[str, Any] | None = None,
    ) -> list[float]:
        formatted_text = f"""Name:
{name}

Description:
{description}

Capability:
{capability}

Input Schema:
{input_schema or {}}

Output Schema:
{output_schema or {}}"""

        return await self.generate_embedding(formatted_text)

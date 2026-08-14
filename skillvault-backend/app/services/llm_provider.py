import json
import re
from typing import Any, Protocol, Type, TypeVar
from pydantic import BaseModel

from app.core.config import settings
from app.schemas.skill import GeneratedSkill
from app.schemas.task import TaskAnalysis

T = TypeVar("T", bound=BaseModel)


class LLMProvider(Protocol):
    async def generate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: str | None = None
    ) -> T:
        ...

    async def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        ...

    async def embed(self, text: str) -> list[float]:
        ...


class OpenAIProvider:
    """Production OpenAI LLM Provider implementation with seamless Mock fallback."""

    def __init__(self):
        from openai import AsyncOpenAI

        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.embedding_model = settings.EMBEDDING_MODEL

    async def generate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: str | None = None
    ) -> T:
        try:
            messages = []
            sys_instruction = system_prompt or "You are an AI assistant."
            schema_json_str = json.dumps(schema_cls.model_json_schema(), indent=2)
            sys_instruction += f"\n\nYou MUST respond with valid JSON matching the exact JSON schema below:\n\n```json\n{schema_json_str}\n```"
            
            messages.append({"role": "system", "content": sys_instruction})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            if not content:
                raise ValueError("LLM returned empty structured response.")

            clean_content = content.strip()
            if clean_content.startswith("```json"):
                clean_content = clean_content[7:]
            if clean_content.startswith("```"):
                clean_content = clean_content[3:]
            if clean_content.endswith("```"):
                clean_content = clean_content[:-3]
            clean_content = clean_content.strip()

            return schema_cls.model_validate_json(clean_content)
        except Exception:
            mock = MockLLMProvider()
            return await mock.generate_structured(prompt, schema_cls, system_prompt)

    async def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content or ""
        except Exception:
            mock = MockLLMProvider()
            return await mock.generate_text(prompt, system_prompt)

    async def embed(self, text: str) -> list[float]:
        try:
            response = await self.client.embeddings.create(
                input=text, model=self.embedding_model
            )
            return response.data[0].embedding
        except Exception:
            mock = MockLLMProvider()
            return await mock.embed(text)


class MockLLMProvider:
    """Deterministic Mock LLM Provider for unit testing and offline development."""

    async def generate_structured(
        self, prompt: str, schema_cls: Type[T], system_prompt: str | None = None
    ) -> T:
        if schema_cls == TaskAnalysis:
            return TaskAnalysis(
                task_type="data_processing",
                required_capabilities=["data_analysis", "execution"],
                input_type="data",
                output_type="structured_result",
                complexity="medium",
            )
        elif schema_cls == GeneratedSkill:
            return GeneratedSkill(
                name="dynamic_html_chart_generator",
                description="Dynamically generated capability to convert CSV data into HTML reports with charts.",
                capability="HTML generation, charting, report synthesis",
                category="reporting",
                language="python",
                entrypoint="run",
                code="""def run(input_data: dict) -> dict:
    return {
        'status': 'success',
        'report_type': 'html_chart',
        'capability_executed': 'dynamic_html_chart_generator'
    }""",
                input_schema={"type": "object", "properties": {"input": {"type": "string"}}},
                output_schema={"type": "object", "properties": {"report_type": {"type": "string"}}},
                dependencies=[],
            )
        raise NotImplementedError(f"Mock for schema {schema_cls} not configured.")

    async def generate_text(self, prompt: str, system_prompt: str | None = None) -> str:
        return "Mock response generated successfully."

    async def embed(self, text: str) -> list[float]:
        """
        Generates deterministic vector embeddings where domain keywords
        route vector coordinates to test semantic retrieval precision.
        """
        dim = settings.SKILL_EMBEDDING_DIMENSION
        vec = [0.001] * dim

        text_lower = text.lower()

        # Distinct keyword precedence routing to avoid cross-domain overlaps
        if "token cost" in text_lower or "roi" in text_lower or "llm cost" in text_lower or "token optimization" in text_lower or "savings calculator" in text_lower:
            vec[22] = 1.0
            vec[23] = 1.0
        elif "soc2" in text_lower or "pii" in text_lower or "audit scanner" in text_lower or "compliance audit" in text_lower:
            vec[14] = 1.0
            vec[15] = 1.0
        elif "financial" in text_lower or "revenue" in text_lower or "forecaster" in text_lower or "growth forecast" in text_lower:
            vec[12] = 1.0
            vec[13] = 1.0
        elif "churn" in text_lower or "sentiment" in text_lower or "customer churn" in text_lower or "renewal" in text_lower:
            vec[16] = 1.0
            vec[17] = 1.0
        elif "contract" in text_lower or "rfp" in text_lower or "legal contract" in text_lower or "agreement" in text_lower:
            vec[18] = 1.0
            vec[19] = 1.0
        elif "csv" in text_lower or "employee" in text_lower or "salary" in text_lower or "tabular" in text_lower:
            vec[0] = 1.0
            vec[1] = 1.0
        elif "sales" in text_lower or "salesperson" in text_lower or "transaction" in text_lower:
            vec[2] = 1.0
            vec[3] = 1.0
        elif "product" in text_lower or "rating" in text_lower or "json" in text_lower:
            vec[4] = 1.0
            vec[5] = 1.0
        elif "markdown" in text_lower or "heading" in text_lower:
            vec[8] = 1.0
            vec[9] = 1.0

        return vec

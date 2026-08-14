import time
import traceback
from typing import Any, Protocol

from app.db.models.skill_version import SkillVersion
from app.schemas.execution import ExecutionResult
from app.skills.builtin import BUILTIN_SKILLS_MAP


class SkillExecutor(Protocol):
    async def execute(
        self, skill_version: SkillVersion | None, input_data: dict[str, Any]
    ) -> ExecutionResult:
        ...


class LocalSkillExecutor:
    """
    Local implementation of SkillExecutor protocol.
    For trusted built-in skills, dispatches directly to module functions.
    For generated skills, executes code within a controlled local namespace.
    """

    async def execute(
        self, skill_version: SkillVersion | None, input_data: dict[str, Any]
    ) -> ExecutionResult:
        start_time = time.perf_counter()

        if not skill_version:
            return ExecutionResult(
                status="FAILED",
                output_data={},
                error="No skill version provided for execution.",
                latency_ms=round((time.perf_counter() - start_time) * 1000, 2),
            )

        try:
            # Check built-in dispatch map first
            slug = skill_version.skill.slug if (skill_version and skill_version.skill) else ""
            if not slug and skill_version.code and skill_version.code.startswith("BUILTIN:"):
                slug = skill_version.code.replace("BUILTIN:", "")
            
            normalized_slug = slug.replace("_", "-")

            if normalized_slug in BUILTIN_SKILLS_MAP:
                func = BUILTIN_SKILLS_MAP[normalized_slug]
                output = func(input_data)
                elapsed = (time.perf_counter() - start_time) * 1000
                return ExecutionResult(
                    status="SUCCESS",
                    output_data=output if isinstance(output, dict) else {"result": output},
                    latency_ms=round(elapsed, 2),
                )

            # Dynamic code execution fallback
            code_str = skill_version.code
            entrypoint = skill_version.entrypoint or "run"

            local_scope: dict[str, Any] = {}
            global_scope: dict[str, Any] = {"__builtins__": __builtins__}

            exec(code_str, global_scope, local_scope)

            if entrypoint not in local_scope and entrypoint not in global_scope:
                raise ValueError(f"Entrypoint '{entrypoint}' not found in executed skill code.")

            fn = local_scope.get(entrypoint) or global_scope.get(entrypoint)
            output = fn(input_data)

            elapsed = (time.perf_counter() - start_time) * 1000
            return ExecutionResult(
                status="SUCCESS",
                output_data=output if isinstance(output, dict) else {"result": output},
                latency_ms=round(elapsed, 2),
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            err_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
            return ExecutionResult(
                status="FAILED",
                output_data={},
                error=err_msg,
                latency_ms=round(elapsed, 2),
            )

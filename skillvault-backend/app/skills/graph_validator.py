from typing import Any
from pydantic import BaseModel, Field


class WorkflowValidationResult(BaseModel):
    valid: bool = True
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class GraphValidator:
    def __init__(self, max_depth: int = 20, max_steps: int = 30):
        self.max_depth = max_depth
        self.max_steps = max_steps

    def validate_graph(
        self,
        steps: list[dict[str, Any]],
        existing_skill_ids: set[str],
    ) -> WorkflowValidationResult:
        result = WorkflowValidationResult(valid=True, errors=[], warnings=[])

        # Step count check
        if len(steps) > self.max_steps:
            result.valid = False
            result.errors.append(
                f"Workflow step count ({len(steps)}) exceeds maximum allowed steps limit ({self.max_steps})."
            )

        if not steps:
            result.valid = False
            result.errors.append("Workflow graph contains no steps.")
            return result

        # Check skill existence & step numbers
        graph: dict[int, list[int]] = {}
        step_numbers = set()

        for idx, step in enumerate(steps, start=1):
            step_num = step.get("step_number", idx)
            step_numbers.add(step_num)
            skill_id = step.get("skill_id")

            if skill_id not in existing_skill_ids:
                result.valid = False
                result.errors.append(f"Step {step_num} references non-existent Skill ID '{skill_id}'.")

            # Dependencies / predecessors
            input_mapping = step.get("input_mapping", {})
            depends_on = []
            for k, val in input_mapping.items():
                if isinstance(val, str) and val.startswith("steps."):
                    try:
                        prev_step = int(val.split(".")[1])
                        depends_on.append(prev_step)
                    except (IndexError, ValueError):
                        pass

            graph[step_num] = depends_on

        # Cycle Detection via DFS
        visited = set()
        rec_stack = set()

        def dfs_has_cycle(v: int, depth: int) -> bool:
            if depth > self.max_depth:
                result.valid = False
                result.errors.append(f"Workflow graph depth exceeds maximum allowed limit ({self.max_depth}).")
                return True

            visited.add(v)
            rec_stack.add(v)

            for neighbor in graph.get(v, []):
                if neighbor not in visited:
                    if dfs_has_cycle(neighbor, depth + 1):
                        return True
                elif neighbor in rec_stack:
                    return True

            rec_stack.remove(v)
            return False

        for node in step_numbers:
            if node not in visited:
                if dfs_has_cycle(node, 1):
                    result.valid = False
                    result.errors.append("Cyclic dependency detected in workflow step execution graph.")
                    break

        return result

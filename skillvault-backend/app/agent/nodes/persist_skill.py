from typing import Any
from app.agent.state import AgentState
from app.schemas.skill import GeneratedSkill, SkillCreate
from app.services.skill_service import SkillService
from app.skills.validator import PythonASTValidator


async def persist_skill_node(
    state: AgentState, skill_service: SkillService
) -> dict[str, Any]:
    gen_data = state.get("generated_skill")
    if not gen_data:
        return {
            "error": "No generated skill data to persist.",
            "generation_status": "VALIDATION_FAILED",
        }

    generated_skill = GeneratedSkill(**gen_data)

    # Static AST Security Validation
    ast_validator = PythonASTValidator()
    val_res = await ast_validator.validate(generated_skill)
    if not val_res.valid:
        error_msg = f"AST Validation Failed for generated skill: {', '.join(val_res.errors)}"
        return {
            "error": error_msg,
            "generation_status": "VALIDATION_FAILED",
            "generation_errors": val_res.errors,
            "validation_result": val_res.model_dump(),
        }

    # Duplicate Skill Detection (Check if similar capability already exists in vault)
    try:
        search_query = f"{generated_skill.name} {generated_skill.description} {generated_skill.capability}"
        search_emb = await skill_service.embedding_service.generate_embedding(search_query)
        similar_candidates = await skill_service.skill_repo.search_similar(search_emb, limit=1)
        if similar_candidates:
            existing_skill, similarity = similar_candidates[0]
            if similarity >= 0.90:
                selected_skill = {
                    "skill_id": existing_skill.id,
                    "name": existing_skill.name,
                    "slug": existing_skill.slug,
                    "description": existing_skill.description,
                    "capability": existing_skill.capability,
                    "score": round(similarity, 4),
                    "semantic_score": round(similarity, 4),
                    "reliability_score": 0.8,
                    "status": existing_skill.status,
                    "source_type": existing_skill.source_type,
                }
                return {
                    "selected_skill": selected_skill,
                    "generation_status": "REUSED_DUPLICATE",
                    "generated_skill_id": existing_skill.id,
                    "validation_result": val_res.model_dump(),
                }
    except Exception:
        pass

    # Create Skill with explicit GENERATED provenance and DRAFT status
    skill_create = SkillCreate(
        name=generated_skill.name,
        description=generated_skill.description,
        capability=generated_skill.capability,
        category=generated_skill.category or "general",
        status="DRAFT",
        source_type="GENERATED",
        created_by="AGENT",
        risk_level="UNTRUSTED",
        input_schema=generated_skill.input_schema,
        output_schema=generated_skill.output_schema,
        dependencies=generated_skill.dependencies,
        code=generated_skill.code,
        language=generated_skill.language or "python",
        entrypoint=generated_skill.entrypoint or "run",
    )

    skill = await skill_service.create_skill(skill_create)

    selected_skill = {
        "skill_id": skill.id,
        "name": skill.name,
        "slug": skill.slug,
        "description": skill.description,
        "capability": skill.capability,
        "score": 1.0,
        "semantic_score": 1.0,
        "reliability_score": 0.7,
        "success_rate": 0.0,
        "status": skill.status,
        "source_type": skill.source_type,
    }

    return {
        "selected_skill": selected_skill,
        "generation_status": "PERSISTED_DRAFT",
        "generated_skill_id": skill.id,
        "validation_result": val_res.model_dump(),
    }

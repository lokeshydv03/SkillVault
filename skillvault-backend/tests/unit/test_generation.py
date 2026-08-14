import pytest
from unittest.mock import AsyncMock, MagicMock

from app.schemas.skill import GeneratedSkill
from app.skills.generator import DefaultSkillGenerator, SkillGenerationContext
from app.skills.validator import PythonASTValidator


@pytest.mark.asyncio
async def test_generator_mock_llm():
    mock_llm = MagicMock()
    mock_skill = GeneratedSkill(
        name="JSON to XML Converter",
        slug="json-to-xml-converter",
        description="Convert JSON formatted data into structured XML string.",
        capability="JSON parsing, XML generation, format conversion",
        category="data_transformation",
        language="python",
        entrypoint="run",
        code="def run(input_data: dict) -> dict:\n    return {'xml': '<root></root>'}",
        input_schema={"data": "object"},
        output_schema={"xml": "string"},
        dependencies=["lxml"],
        reasoning="No existing skill converts JSON to XML.",
    )
    mock_llm.generate_structured = AsyncMock(return_value=mock_skill)

    generator = DefaultSkillGenerator(mock_llm)
    context = SkillGenerationContext(task_description="Convert JSON to XML.")
    res = await generator.generate("Convert JSON to XML.", context)

    assert res.name == "JSON to XML Converter"
    assert res.slug == "json-to-xml-converter"
    assert res.entrypoint == "run"
    assert "def run" in res.code


@pytest.mark.asyncio
async def test_validator_valid_code():
    validator = PythonASTValidator()
    skill = GeneratedSkill(
        name="Valid Skill",
        slug="valid-skill",
        description="Valid Python Skill",
        capability="data processing",
        category="data",
        code="def run(input_data: dict) -> dict:\n    val = input_data.get('x', 0)\n    return {'result': val * 2}",
        input_schema={},
        output_schema={},
        dependencies=["math", "json"],
    )
    res = await validator.validate(skill)

    assert res.valid is True
    assert len(res.errors) == 0


@pytest.mark.asyncio
async def test_validator_invalid_syntax():
    validator = PythonASTValidator()
    skill = GeneratedSkill(
        name="Invalid Syntax Skill",
        slug="invalid-syntax-skill",
        description="Invalid Syntax Skill",
        capability="data processing",
        category="data",
        code="def run(input_data: dict)\n    this is invalid python syntax!",
        input_schema={},
        output_schema={},
    )
    res = await validator.validate(skill)

    assert res.valid is False
    assert any("Syntax Error" in err for err in res.errors)


@pytest.mark.asyncio
async def test_validator_missing_entrypoint():
    validator = PythonASTValidator()
    skill = GeneratedSkill(
        name="Missing Entrypoint Skill",
        slug="missing-entrypoint-skill",
        description="Missing Entrypoint Skill",
        capability="data processing",
        category="data",
        code="def process_data(data):\n    return {'result': data}",
        input_schema={},
        output_schema={},
    )
    res = await validator.validate(skill)

    assert res.valid is False
    assert any("Required entrypoint function 'run'" in err for err in res.errors)


@pytest.mark.asyncio
async def test_validator_forbidden_calls():
    validator = PythonASTValidator()

    for forbidden_call in ["eval('1 + 1')", "exec('import os')", "os.system('ls')"]:
        skill = GeneratedSkill(
            name="Forbidden Call Skill",
            slug="forbidden-call-skill",
            description="Forbidden Call Skill",
            capability="data processing",
            category="data",
            code=f"import os\ndef run(input_data: dict) -> dict:\n    {forbidden_call}\n    return {{}}",
            input_schema={},
            output_schema={},
        )
        res = await validator.validate(skill)

        assert res.valid is False
        assert len(res.errors) > 0


@pytest.mark.asyncio
async def test_validator_forbidden_imports():
    validator = PythonASTValidator()

    for forbidden_mod in ["subprocess", "socket", "http.client", "requests", "urllib"]:
        skill = GeneratedSkill(
            name="Forbidden Import Skill",
            slug="forbidden-import-skill",
            description="Forbidden Import Skill",
            capability="data processing",
            category="data",
            code=f"import {forbidden_mod}\ndef run(input_data: dict) -> dict:\n    return {{}}",
            input_schema={},
            output_schema={},
        )
        res = await validator.validate(skill)

        assert res.valid is False
        assert any("Forbidden import" in err for err in res.errors)


@pytest.mark.asyncio
async def test_validator_path_traversal_warning():
    validator = PythonASTValidator()
    skill = GeneratedSkill(
        name="Path Traversal Skill",
        slug="path-traversal-skill",
        description="Path Traversal Skill",
        capability="data processing",
        category="data",
        code="def run(input_data: dict) -> dict:\n    path = '/etc/passwd'\n    return {'path': path}",
        input_schema={},
        output_schema={},
    )
    res = await validator.validate(skill)

    assert any("Suspicious path pattern '/etc'" in w for w in res.warnings)


@pytest.mark.asyncio
async def test_validator_dependency_allowlist():
    validator = PythonASTValidator()
    skill = GeneratedSkill(
        name="Unapproved Dep Skill",
        slug="unapproved-dep-skill",
        description="Unapproved Dep Skill",
        capability="data processing",
        category="data",
        code="def run(input_data: dict) -> dict:\n    return {}",
        input_schema={},
        output_schema={},
        dependencies=["unapproved_secret_pkg"],
    )
    res = await validator.validate(skill)

    assert any("unapproved_secret_pkg" in w for w in res.warnings)

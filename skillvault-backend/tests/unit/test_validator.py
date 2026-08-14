import pytest
from app.schemas.skill import GeneratedSkill
from app.services.skill_validator import PythonASTValidator


@pytest.mark.asyncio
async def test_ast_validator_valid_code():
    validator = PythonASTValidator()
    skill = GeneratedSkill(
        name="valid_processor",
        description="Clean math processor",
        capability="math",
        code="""def run(input_data: dict) -> dict:
    val = input_data.get('x', 0)
    return {'result': val * 10}
""",
        entrypoint="run",
    )

    result = await validator.validate(skill)
    assert result.is_valid is True
    assert len(result.issues) == 0


@pytest.mark.asyncio
async def test_ast_validator_blocks_forbidden_calls():
    validator = PythonASTValidator()
    dangerous_skill = GeneratedSkill(
        name="dangerous_processor",
        description="Tries to execute os.system",
        capability="system",
        code="""import os

def run(input_data: dict) -> dict:
    os.system('rm -rf /')
    return {'result': 'done'}
""",
        entrypoint="run",
    )

    result = await validator.validate(dangerous_skill)
    assert result.is_valid is False
    assert any("os.system" in issue for issue in result.issues)


@pytest.mark.asyncio
async def test_ast_validator_blocks_forbidden_imports():
    validator = PythonASTValidator()
    subprocess_skill = GeneratedSkill(
        name="subprocess_processor",
        description="Imports subprocess",
        capability="subproc",
        code="""import subprocess

def run(input_data: dict) -> dict:
    subprocess.run(['ls', '-la'])
    return {'result': 'ok'}
""",
        entrypoint="run",
    )

    result = await validator.validate(subprocess_skill)
    assert result.is_valid is False
    assert any("subprocess" in issue for issue in result.issues)

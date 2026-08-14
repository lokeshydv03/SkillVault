import ast
from typing import Protocol
from pydantic import BaseModel, Field

from app.schemas.skill import GeneratedSkill

APPROVED_DEPENDENCY_ALLOWLIST = {
    "pandas",
    "numpy",
    "python-dateutil",
    "beautifulsoup4",
    "lxml",
    "markdown",
    "openpyxl",
    "pillow",
    "math",
    "json",
    "re",
    "datetime",
    "collections",
    "itertools",
    "csv",
    "typing",
}

FORBIDDEN_IMPORTS = {
    "subprocess",
    "socket",
    "http",
    "http.client",
    "requests",
    "urllib",
    "urllib3",
    "importlib",
    "ctypes",
    "multiprocessing",
    "shutil",
    "pickle",
    "asyncio.subprocess",
}

FORBIDDEN_CALLS = {
    "eval",
    "exec",
    "compile",
    "__import__",
    "system",
    "os.system",
    "popen",
    "os.popen",
    "rmtree",
    "shutil.rmtree",
}

FORBIDDEN_PATH_PATTERNS = ["/etc", "/var", "/home", "~/", "../"]


class ValidationResult(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return self.valid

    @property
    def issues(self) -> list[str]:
        return self.errors


class SkillValidator(Protocol):
    async def validate(self, skill: GeneratedSkill) -> ValidationResult:
        ...


class PythonASTValidator:
    """
    Static AST Code Security & Contract Validator for generated skills.
    Parses generated Python code into AST nodes and enforces strict security rules.
    """

    async def validate(self, skill: GeneratedSkill) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        code = skill.code
        entrypoint = skill.entrypoint or "run"

        # 1. Parse AST to check syntax
        try:
            tree = ast.parse(code)
        except SyntaxError as se:
            errors.append(f"Python Syntax Error at line {se.lineno}: {se.msg}")
            return ValidationResult(valid=False, errors=errors, warnings=warnings)

        # 2. Check required entrypoint exists
        has_entrypoint = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == entrypoint:
                has_entrypoint = True
                # Check function parameter exists
                if len(node.args.args) < 1:
                    errors.append(f"Entrypoint function '{entrypoint}' must accept at least 1 input parameter (e.g., input_data).")
                break

        if not has_entrypoint:
            errors.append(f"Required entrypoint function '{entrypoint}' not found in generated code.")

        # 3. AST Node Security Inspection
        for node in ast.walk(tree):
            # Check imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    pkg = alias.name.split(".")[0].lower()
                    if pkg in FORBIDDEN_IMPORTS:
                        errors.append(f"Forbidden import '{alias.name}' detected.")
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    pkg = node.module.split(".")[0].lower()
                    if pkg in FORBIDDEN_IMPORTS:
                        errors.append(f"Forbidden import from '{node.module}' detected.")

            # Check calls
            elif isinstance(node, ast.Call):
                func = node.func
                func_names = []
                if isinstance(func, ast.Name):
                    func_names.append(func.id)
                elif isinstance(func, ast.Attribute):
                    func_names.append(func.attr)
                    if isinstance(func.value, ast.Name):
                        func_names.append(f"{func.value.id}.{func.attr}")

                for fn_name in func_names:
                    if fn_name in FORBIDDEN_CALLS:
                        errors.append(f"Forbidden function call '{fn_name}' detected.")

            # Check path traversal in string literals
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                for pattern in FORBIDDEN_PATH_PATTERNS:
                    if pattern in val:
                        warnings.append(f"Suspicious path pattern '{pattern}' detected in string constant.")

        # 4. Dependency Allowlist Validation
        for dep in skill.dependencies or []:
            norm_dep = dep.strip().lower()
            if norm_dep and norm_dep not in APPROVED_DEPENDENCY_ALLOWLIST:
                warnings.append(f"Dependency '{dep}' is not in approved allowlist. Will require sandbox review.")

        valid = len(errors) == 0
        return ValidationResult(valid=valid, errors=errors, warnings=warnings)

class SkillVaultException(Exception):
    """Base exception for SkillVault application."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class SkillNotFoundError(SkillVaultException):
    def __init__(self, skill_id: str):
        super().__init__(f"Skill with ID '{skill_id}' was not found.", code="SKILL_NOT_FOUND")


class TaskNotFoundError(SkillVaultException):
    def __init__(self, task_id: str):
        super().__init__(f"Task with ID '{task_id}' was not found.", code="TASK_NOT_FOUND")


class ExecutionNotFoundError(SkillVaultException):
    def __init__(self, execution_id: str):
        super().__init__(f"Execution with ID '{execution_id}' was not found.", code="EXECUTION_NOT_FOUND")


class SkillGenerationError(SkillVaultException):
    def __init__(self, details: str):
        super().__init__(f"Failed to generate skill: {details}", code="SKILL_GENERATION_FAILED")


class SkillExecutionError(SkillVaultException):
    def __init__(self, details: str):
        super().__init__(f"Skill execution failed: {details}", code="SKILL_EXECUTION_FAILED")


class EmbeddingError(SkillVaultException):
    def __init__(self, details: str):
        super().__init__(f"Failed to generate embedding: {details}", code="EMBEDDING_FAILED")


class InvalidSkillError(SkillVaultException):
    def __init__(self, details: str):
        super().__init__(f"Invalid skill definition: {details}", code="INVALID_SKILL")

"""Custom exceptions for Controle PGM backend."""

from __future__ import annotations


class ControlePGMError(Exception):
    """Base exception for all application errors."""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class NotFoundError(ControlePGMError):
    """Resource not found error (404)."""

    def __init__(self, message: str = "Recurso não encontrado"):
        super().__init__(message, status_code=404)


class UnauthorizedError(ControlePGMError):
    """Authentication required error (401)."""

    def __init__(self, message: str = "Autenticação necessária"):
        super().__init__(message, status_code=401)


class ForbiddenError(ControlePGMError):
    """Access denied error (403)."""

    def __init__(self, message: str = "Acesso negado"):
        super().__init__(message, status_code=403)


class BadRequestError(ControlePGMError):
    """Invalid request error (400)."""

    def __init__(self, message: str = "Requisição inválida"):
        super().__init__(message, status_code=400)


class ConflictError(ControlePGMError):
    """Conflict error, typically used for concurrency issues (409)."""

    def __init__(self, message: str = "Conflito de concorrência"):
        super().__init__(message, status_code=409)


class ValidationError(BadRequestError):
    """Data validation error (400)."""

    def __init__(self, message: str = "Dados inválidos"):
        super().__init__(message)


class PasswordPolicyError(BadRequestError):
    """Password doesn't meet policy requirements (400)."""

    def __init__(
        self,
        message: str = "Senha não atende aos requisitos mínimos (8 caracteres, 1 letra, 1 número)",
    ):
        super().__init__(message)


class UserDeactivatedError(UnauthorizedError):
    """User account is deactivated (401)."""

    def __init__(self, message: str = "Conta de usuário desativada"):
        super().__init__(message)


class InvalidCredentialsError(UnauthorizedError):
    """Invalid login credentials (401)."""

    def __init__(self, message: str = "E-mail ou senha incorretos"):
        super().__init__(message)


class TokenExpiredError(UnauthorizedError):
    """JWT token has expired (401)."""

    def __init__(self, message: str = "Sessão expirada"):
        super().__init__(message)


class SequenceGenerationError(ConflictError):
    """Failed to generate sequence number after retries (409)."""

    def __init__(self, message: str = "Erro ao gerar número. Por favor, tente novamente."):
        super().__init__(message)

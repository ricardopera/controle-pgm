"""Pydantic models for Controle PGM."""

from .document_type import (
    DocumentTypeCreate,
    DocumentTypeEntity,
    DocumentTypeListResponse,
    DocumentTypeResponse,
    DocumentTypeUpdate,
)
from .number_log import (
    CorrectionRequest,
    CorrectionResponse,
    HistoryFilter,
    HistoryResponse,
    NumberLogEntity,
    NumberLogResponse,
)
from .sequence import (
    GenerateNumberRequest,
    GenerateNumberResponse,
    SequenceEntity,
    SequenceListResponse,
    SequenceResponse,
)
from .user import (
    ChangePasswordRequest,
    CurrentUser,
    LoginRequest,
    LoginResponse,
    UserCreate,
    UserEntity,
    UserResponse,
    UserUpdate,
)

__all__ = [
    # User models
    "UserEntity",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "LoginRequest",
    "LoginResponse",
    "ChangePasswordRequest",
    "CurrentUser",
    # Document type models
    "DocumentTypeEntity",
    "DocumentTypeCreate",
    "DocumentTypeUpdate",
    "DocumentTypeResponse",
    "DocumentTypeListResponse",
    # Sequence models
    "SequenceEntity",
    "SequenceResponse",
    "SequenceListResponse",
    "GenerateNumberRequest",
    "GenerateNumberResponse",
    # Number log models
    "NumberLogEntity",
    "NumberLogResponse",
    "HistoryFilter",
    "HistoryResponse",
    "CorrectionRequest",
    "CorrectionResponse",
]

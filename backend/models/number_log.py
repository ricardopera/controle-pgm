"""NumberLog Pydantic models for Controle PGM."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class NumberLogEntity(BaseModel):
    """Number log entity as stored in Azure Tables.

    Primary key structure:
    - PartitionKey: "{document_type_code}_{year}" (e.g., "OF_2025")
    - RowKey: Inverse timestamp + UUID for sorting (newest first)
    """

    # Azure Tables keys
    PartitionKey: str  # "{document_type_code}_{year}"
    RowKey: str  # Inverse timestamp for chronological ordering

    # Log fields
    DocumentTypeCode: str
    Year: int
    Number: int
    Action: Literal["generated", "corrected"]
    UserId: str
    UserName: str
    PreviousNumber: int | None = None  # For corrections only
    Notes: str | None = None
    CreatedAt: datetime

    model_config = {
        "from_attributes": True,
        "extra": "ignore"
    }


class NumberLogResponse(BaseModel):
    """Number log data returned in API responses."""

    id: str
    document_type_code: str
    year: int
    number: int
    action: Literal["generated", "corrected"]
    user_id: str
    user_name: str
    previous_number: int | None
    notes: str | None
    created_at: datetime

    @classmethod
    def from_entity(cls, entity: NumberLogEntity) -> NumberLogResponse:
        """Create response from entity."""
        return cls(
            id=entity.RowKey,
            document_type_code=entity.DocumentTypeCode,
            year=entity.Year,
            number=entity.Number,
            action=entity.Action,
            user_id=entity.UserId,
            user_name=entity.UserName,
            previous_number=entity.PreviousNumber,
            notes=entity.Notes,
            created_at=entity.CreatedAt,
        )


class HistoryFilter(BaseModel):
    """Filter parameters for history queries."""

    document_type_code: str | None = None
    year: int | None = Field(None, ge=2020, le=2100)
    user_id: str | None = None
    action: Literal["generated", "corrected"] | None = None
    page: int = Field(1, ge=1)
    page_size: int = Field(50, ge=1, le=10000)


class HistoryResponse(BaseModel):
    """Response for history listing."""

    items: list[NumberLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CorrectionRequest(BaseModel):
    """Request body for correcting a sequence number."""

    document_type_code: str = Field(..., min_length=1, max_length=10)
    year: int = Field(..., ge=2020, le=2100)
    new_number: int = Field(..., ge=0)
    notes: str = Field(..., min_length=10, max_length=500)


class CorrectionResponse(BaseModel):
    """Response for sequence correction."""

    previous_number: int
    new_number: int
    document_type_code: str
    year: int
    notes: str

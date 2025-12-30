"""Sequence Pydantic models for Controle PGM."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from core.config import get_current_year


class SequenceEntity(BaseModel):
    """Sequence entity as stored in Azure Tables.

    Primary key structure:
    - PartitionKey: "{document_type_code}_{year}" (e.g., "OF_2025")
    - RowKey: "SEQUENCE"
    """

    # Azure Tables keys
    PartitionKey: str  # "{document_type_code}_{year}"
    RowKey: str = "SEQUENCE"

    # Sequence fields
    DocumentTypeCode: str
    Year: int
    CurrentNumber: int = 0
    UpdatedAt: datetime

    # ETag for optimistic concurrency
    _etag: str | None = None

    class Config:
        """Pydantic model configuration."""

        from_attributes = True


class SequenceResponse(BaseModel):
    """Sequence data returned in API responses."""

    document_type_code: str
    year: int
    current_number: int
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: SequenceEntity) -> SequenceResponse:
        """Create response from entity."""
        return cls(
            document_type_code=entity.DocumentTypeCode,
            year=entity.Year,
            current_number=entity.CurrentNumber,
            updated_at=entity.UpdatedAt,
        )


class GenerateNumberRequest(BaseModel):
    """Request body for generating a new document number.

    Year is optional - defaults to current year in Brazil timezone.
    """

    document_type_code: str = Field(..., min_length=1, max_length=10)
    year: int | None = Field(default=None, ge=2020, le=2100)

    @field_validator("year", mode="before")
    @classmethod
    def set_default_year(cls, v):
        """Set default year to current year in Brazil timezone if not provided."""
        if v is None:
            return get_current_year()
        return v


class GenerateNumberResponse(BaseModel):
    """Response for generated document number."""

    number: int
    document_type_code: str
    document_type_name: str
    year: int
    formatted: str  # e.g., "OF 0042/2025"


class SequenceListResponse(BaseModel):
    """Response for listing sequences."""

    items: list[SequenceResponse]
    total: int

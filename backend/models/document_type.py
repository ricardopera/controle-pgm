"""DocumentType Pydantic models for Controle PGM."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentTypeEntity(BaseModel):
    """Document type entity as stored in Azure Tables."""

    # Azure Tables keys
    PartitionKey: str = "DOCTYPE"
    RowKey: str  # UUID

    # Document type fields
    Code: str  # e.g., "OF", "MEM", "CI"
    Name: str  # e.g., "Ofício", "Memorando"
    IsActive: bool = True
    CreatedAt: datetime
    UpdatedAt: datetime

    model_config = {"from_attributes": True, "extra": "ignore"}


class DocumentTypeCreate(BaseModel):
    """Request body for creating a document type."""

    code: str = Field(..., min_length=1, max_length=10, pattern=r"^[A-Z0-9]+$")
    name: str = Field(..., min_length=2, max_length=100)


class DocumentTypeUpdate(BaseModel):
    """Request body for updating a document type."""

    name: str | None = Field(None, min_length=2, max_length=100)
    is_active: bool | None = None


class DocumentTypeResponse(BaseModel):
    """Document type data returned in API responses."""

    id: str
    code: str
    name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, entity: DocumentTypeEntity) -> DocumentTypeResponse:
        """Create response from entity."""
        return cls(
            id=entity.RowKey,
            code=entity.Code,
            name=entity.Name,
            is_active=entity.IsActive,
            created_at=entity.CreatedAt,
            updated_at=entity.UpdatedAt,
        )


class DocumentTypeListResponse(BaseModel):
    """Response for listing document types."""

    items: list[DocumentTypeResponse]
    total: int

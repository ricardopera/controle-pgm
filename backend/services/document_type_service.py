"""Document Type service for Controle PGM."""

from datetime import datetime
from uuid import uuid4

from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import UpdateMode

from core.exceptions import ConflictError, NotFoundError
from core.security import sanitize_odata_string
from core.tables import get_document_types_table
from models.document_type import (
    DocumentTypeCreate,
    DocumentTypeEntity,
    DocumentTypeUpdate,
)


class DocumentTypeService:
    """Service for document type operations."""

    @staticmethod
    def list_all() -> list[DocumentTypeEntity]:
        """List all document types.

        Returns:
            List of all DocumentTypeEntity objects.
        """
        table = get_document_types_table()
        entities = list(table.query_entities(query_filter="PartitionKey eq 'DOCTYPE'"))
        return [DocumentTypeEntity(**entity) for entity in entities]

    @staticmethod
    def list_active() -> list[DocumentTypeEntity]:
        """List all active document types.

        Returns:
            List of active DocumentTypeEntity objects, sorted by code.
        """
        table = get_document_types_table()
        entities = list(
            table.query_entities(query_filter="PartitionKey eq 'DOCTYPE' and IsActive eq true")
        )
        doc_types = [DocumentTypeEntity(**entity) for entity in entities]
        return sorted(doc_types, key=lambda x: x.Code)

    @staticmethod
    def get_by_id(doc_type_id: str) -> DocumentTypeEntity | None:
        """Get a document type by ID.

        Args:
            doc_type_id: Document type's unique ID (RowKey).

        Returns:
            DocumentTypeEntity if found, None otherwise.
        """
        table = get_document_types_table()

        try:
            entity = table.get_entity(partition_key="DOCTYPE", row_key=doc_type_id)
            return DocumentTypeEntity(**entity)
        except ResourceNotFoundError:
            return None

    @staticmethod
    def get_by_code(code: str) -> DocumentTypeEntity | None:
        """Get a document type by code.

        Args:
            code: Document type code (e.g., "OF").

        Returns:
            DocumentTypeEntity if found, None otherwise.
        """
        table = get_document_types_table()

        safe_code = sanitize_odata_string(code.upper())
        query_filter = f"Code eq '{safe_code}'"
        entities = list(table.query_entities(query_filter=query_filter))

        if not entities:
            return None

        return DocumentTypeEntity(**entities[0])

    @staticmethod
    def create(data: DocumentTypeCreate) -> DocumentTypeEntity:
        """Create a new document type.

        Args:
            data: Document type creation data.

        Returns:
            Created DocumentTypeEntity.

        Raises:
            ConflictError: If code already exists.
        """
        # Check if code already exists
        existing = DocumentTypeService.get_by_code(data.code)
        if existing:
            raise ConflictError(f"Tipo de documento com código '{data.code}' já existe")

        table = get_document_types_table()
        now = datetime.utcnow()

        entity = DocumentTypeEntity(
            PartitionKey="DOCTYPE",
            RowKey=str(uuid4()),
            Code=data.code.upper(),
            Name=data.name,
            IsActive=True,
            CreatedAt=now,
            UpdatedAt=now,
        )

        table.create_entity(entity.model_dump())

        return entity

    @staticmethod
    def update(doc_type_id: str, data: DocumentTypeUpdate) -> DocumentTypeEntity:
        """Update a document type.

        Args:
            doc_type_id: Document type's unique ID.
            data: Update data.

        Returns:
            Updated DocumentTypeEntity.

        Raises:
            NotFoundError: If document type not found.
        """
        doc_type = DocumentTypeService.get_by_id(doc_type_id)
        if not doc_type:
            raise NotFoundError("Tipo de documento não encontrado")

        table = get_document_types_table()

        # Update only provided fields
        updates = data.model_dump(exclude_unset=True)
        
        # Map snake_case to PascalCase for Azure Tables
        mapped_updates = {}
        if "name" in updates:
            mapped_updates["Name"] = updates["name"]
        if "is_active" in updates:
            mapped_updates["IsActive"] = updates["is_active"]

        entity_dict = doc_type.model_dump()
        entity_dict.update(mapped_updates)
        entity_dict["UpdatedAt"] = datetime.utcnow()

        table.update_entity(entity_dict, mode=UpdateMode.REPLACE)

        return DocumentTypeEntity(**entity_dict)

    @staticmethod
    def deactivate(doc_type_id: str) -> DocumentTypeEntity:
        """Deactivate a document type.

        Args:
            doc_type_id: Document type's unique ID.

        Returns:
            Updated DocumentTypeEntity.

        Raises:
            NotFoundError: If document type not found.
        """
        return DocumentTypeService.update(doc_type_id, DocumentTypeUpdate(is_active=False))

    @staticmethod
    def activate(doc_type_id: str) -> DocumentTypeEntity:
        """Activate a document type.

        Args:
            doc_type_id: Document type's unique ID.

        Returns:
            Updated DocumentTypeEntity.

        Raises:
            NotFoundError: If document type not found.
        """
        return DocumentTypeService.update(doc_type_id, DocumentTypeUpdate(is_active=True))

    @staticmethod
    def delete_permanently(doc_type_id: str) -> None:
        """Delete a document type permanently (Hard Delete).

        Args:
            doc_type_id: Document type's unique ID.

        Raises:
            NotFoundError: If document type not found.
            ConflictError: If document type has generated numbers.
        """
        doc_type = DocumentTypeService.get_by_id(doc_type_id)
        if not doc_type:
            raise NotFoundError("Tipo de documento não encontrado")

        # Check if there are any numbers generated for this type
        # We need to query NumberLogs table
        from core.tables import get_table_client
        
        # NumberLog PartitionKey is {code}_{year}
        # We can check if any partition starts with the code
        # But Table Storage doesn't support "starts with" on PartitionKey easily without range query
        # Range query: PartitionKey >= 'CODE_' and PartitionKey < 'CODE_~'
        
        logs_table = get_table_client("NumberLogs")
        start_pk = f"{doc_type.Code}_"
        end_pk = f"{doc_type.Code}_\uffff"
        
        query = f"PartitionKey ge '{start_pk}' and PartitionKey lt '{end_pk}'"
        # We only need to know if ONE exists
        logs = list(logs_table.query_entities(query_filter=query, results_per_page=1))
        
        if logs:
            raise ConflictError(
                f"Não é possível excluir o tipo de documento '{doc_type.Name}' pois existem números gerados para ele."
            )

        table = get_document_types_table()
        table.delete_entity(partition_key="DOCTYPE", row_key=doc_type_id)

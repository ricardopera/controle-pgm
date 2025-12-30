"""Number service for Controle PGM - handles document number generation."""

from uuid import uuid4

from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import UpdateMode

from core.config import get_brazil_now
from core.exceptions import (
    NotFoundError,
    SequenceGenerationError,
)
from core.tables import get_number_logs_table, get_sequences_table
from models.number_log import NumberLogEntity
from models.sequence import SequenceEntity
from models.user import CurrentUser
from .document_type_service import DocumentTypeService


class NumberService:
    """Service for document number generation with atomic increments."""

    MAX_RETRIES = 5  # Max retries for ETag conflicts

    @staticmethod
    def _get_partition_key(document_type_code: str, year: int) -> str:
        """Generate partition key for sequences and logs."""
        return f"{document_type_code}_{year}"

    @staticmethod
    def get_current_sequence(document_type_code: str, year: int) -> SequenceEntity:
        """Get current sequence for a document type and year.

        Creates sequence if it doesn't exist.

        Args:
            document_type_code: Document type code (e.g., "OF").
            year: Year for the sequence.

        Returns:
            SequenceEntity with current number.
        """
        table = get_sequences_table()
        partition_key = NumberService._get_partition_key(document_type_code, year)

        try:
            entity = table.get_entity(partition_key=partition_key, row_key="SEQUENCE")
            seq = SequenceEntity(**entity)
            seq._etag = entity.get("_metadata", {}).get("etag")
            return seq
        except ResourceNotFoundError:
            # Create new sequence starting at 0
            now = get_brazil_now()
            seq = SequenceEntity(
                PartitionKey=partition_key,
                RowKey="SEQUENCE",
                DocumentTypeCode=document_type_code,
                Year=year,
                CurrentNumber=0,
                UpdatedAt=now,
            )
            table.create_entity(seq.model_dump(exclude={"_etag"}))

            # Re-fetch to get ETag
            entity = table.get_entity(partition_key=partition_key, row_key="SEQUENCE")
            seq = SequenceEntity(**entity)
            seq._etag = entity.get("_metadata", {}).get("etag")
            return seq

    @staticmethod
    def generate_number(
        document_type_code: str, year: int, user: CurrentUser
    ) -> tuple[int, str, str]:
        """Generate next document number atomically.

        Uses ETag-based optimistic concurrency to ensure atomic increment.
        Retries on conflict up to MAX_RETRIES times.

        Args:
            document_type_code: Document type code (e.g., "OF").
            year: Year for the sequence.
            user: Current authenticated user.

        Returns:
            Tuple of (number, formatted_string, document_type_name).

        Raises:
            NotFoundError: If document type doesn't exist or is inactive.
            SequenceGenerationError: If unable to generate number after retries.
        """
        # Verify document type exists and is active
        doc_type = DocumentTypeService.get_by_code(document_type_code)
        if not doc_type:
            raise NotFoundError(f"Tipo de documento '{document_type_code}' não encontrado")
        if not doc_type.IsActive:
            raise NotFoundError(f"Tipo de documento '{document_type_code}' está inativo")

        document_type_name = doc_type.Name
        table = get_sequences_table()
        partition_key = NumberService._get_partition_key(document_type_code, year)

        for attempt in range(NumberService.MAX_RETRIES):
            # Get current sequence
            seq = NumberService.get_current_sequence(document_type_code, year)

            # Increment number
            new_number = seq.CurrentNumber + 1

            # Prepare update
            updated_entity = {
                "PartitionKey": partition_key,
                "RowKey": "SEQUENCE",
                "DocumentTypeCode": document_type_code,
                "Year": year,
                "CurrentNumber": new_number,
                "UpdatedAt": get_brazil_now(),
            }

            try:
                # Update with ETag check for optimistic concurrency
                table.update_entity(
                    updated_entity,
                    mode=UpdateMode.REPLACE,
                    etag=seq._etag,
                    match_condition="IfMatch",
                )

                # Log the generation
                NumberService._log_action(
                    document_type_code=document_type_code,
                    year=year,
                    number=new_number,
                    action="generated",
                    user=user,
                )

                # Format the number
                formatted = NumberService.format_number(document_type_code, new_number, year)

                return new_number, formatted, document_type_name

            except Exception as e:
                if "412" in str(e) or "PreconditionFailed" in str(e):
                    # ETag conflict - retry
                    continue
                raise

        raise SequenceGenerationError(
            f"Não foi possível gerar número após {NumberService.MAX_RETRIES} tentativas. "
            "Tente novamente."
        )

    @staticmethod
    def correct_sequence(
        document_type_code: str,
        year: int,
        new_number: int,
        notes: str,
        user: CurrentUser,
    ) -> tuple[int, int]:
        """Correct a sequence number (admin only).

        Args:
            document_type_code: Document type code.
            year: Year for the sequence.
            new_number: New sequence number to set.
            notes: Justification for the correction.
            user: Current authenticated user (must be admin).

        Returns:
            Tuple of (previous_number, new_number).

        Raises:
            NotFoundError: If document type doesn't exist.
        """
        # Verify document type exists
        doc_type = DocumentTypeService.get_by_code(document_type_code)
        if not doc_type:
            raise NotFoundError(f"Tipo de documento '{document_type_code}' não encontrado")

        table = get_sequences_table()
        partition_key = NumberService._get_partition_key(document_type_code, year)

        # Get current sequence
        seq = NumberService.get_current_sequence(document_type_code, year)
        previous_number = seq.CurrentNumber

        # Update sequence
        updated_entity = {
            "PartitionKey": partition_key,
            "RowKey": "SEQUENCE",
            "DocumentTypeCode": document_type_code,
            "Year": year,
            "CurrentNumber": new_number,
            "UpdatedAt": get_brazil_now(),
        }

        table.upsert_entity(updated_entity, mode=UpdateMode.REPLACE)

        # Log the correction
        NumberService._log_action(
            document_type_code=document_type_code,
            year=year,
            number=new_number,
            action="corrected",
            user=user,
            previous_number=previous_number,
            notes=notes,
        )

        return previous_number, new_number

    @staticmethod
    def _log_action(
        document_type_code: str,
        year: int,
        number: int,
        action: str,
        user: CurrentUser,
        previous_number: int | None = None,
        notes: str | None = None,
    ) -> None:
        """Log a number generation or correction action."""
        table = get_number_logs_table()
        now = get_brazil_now()

        # Create inverse timestamp for chronological ordering (newest first)
        inverse_timestamp = 9999999999 - int(now.timestamp())
        row_key = f"{inverse_timestamp}_{uuid4()}"

        log_entity = NumberLogEntity(
            PartitionKey=NumberService._get_partition_key(document_type_code, year),
            RowKey=row_key,
            DocumentTypeCode=document_type_code,
            Year=year,
            Number=number,
            Action=action,
            UserId=user.user_id,
            UserName=user.name,
            PreviousNumber=previous_number,
            Notes=notes,
            CreatedAt=now,
        )

        table.create_entity(log_entity.model_dump())

    @staticmethod
    def format_number(code: str, number: int, year: int) -> str:
        """Format a document number for display.

        Args:
            code: Document type code.
            number: Sequence number.
            year: Year.

        Returns:
            Formatted string (e.g., "OF 0042/2025").
        """
        return f"{code} {str(number).zfill(4)}/{year}"

    @staticmethod
    def list_sequences() -> list[SequenceEntity]:
        """List all sequences.

        Returns:
            List of all SequenceEntity objects.
        """
        table = get_sequences_table()
        entities = list(table.query_entities(query_filter="RowKey eq 'SEQUENCE'"))
        return [SequenceEntity(**entity) for entity in entities]

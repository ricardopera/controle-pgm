"""History service for Controle PGM - handles number log queries and exports."""

from __future__ import annotations

import csv
import io

from core.security import sanitize_odata_string
from core.tables import get_number_logs_table
from models.number_log import (
    HistoryFilter,
    HistoryResponse,
    NumberLogEntity,
    NumberLogResponse,
)


class HistoryService:
    """Service for querying number generation history."""

    @staticmethod
    def list_history(filters: HistoryFilter) -> HistoryResponse:
        """List number logs with optional filters and pagination.

        Args:
            filters: Filter parameters including document type, year, user, action, pagination.

        Returns:
            HistoryResponse with paginated items and metadata.
        """
        table = get_number_logs_table()

        # Build OData filter query with sanitized inputs
        filter_parts = []

        if filters.document_type_code and filters.year:
            # Query specific partition
            safe_code = sanitize_odata_string(filters.document_type_code)
            partition_key = f"{safe_code}_{filters.year}"
            filter_parts.append(f"PartitionKey eq '{partition_key}'")
        elif filters.document_type_code:
            # Query by document type prefix
            safe_code = sanitize_odata_string(filters.document_type_code)
            filter_parts.append(f"DocumentTypeCode eq '{safe_code}'")
        elif filters.year:
            # Query by year (integer, no sanitization needed)
            filter_parts.append(f"Year eq {filters.year}")

        if filters.user_id:
            safe_user_id = sanitize_odata_string(filters.user_id)
            filter_parts.append(f"UserId eq '{safe_user_id}'")

        if filters.action:
            safe_action = sanitize_odata_string(filters.action)
            filter_parts.append(f"Action eq '{safe_action}'")

        # Combine filters
        filter_query = " and ".join(filter_parts) if filter_parts else None

        # Query Azure Tables
        if filter_query:
            entities = list(table.query_entities(query_filter=filter_query))
        else:
            entities = list(table.list_entities())

        # Sort by RowKey (inverse timestamp - newest first)
        entities.sort(key=lambda e: e.get("RowKey", ""), reverse=False)

        # Convert to response models
        all_items = [
            NumberLogResponse.from_entity(NumberLogEntity(**entity)) for entity in entities
        ]

        # Apply pagination
        total = len(all_items)
        total_pages = (total + filters.page_size - 1) // filters.page_size if total > 0 else 1

        start_idx = (filters.page - 1) * filters.page_size
        end_idx = start_idx + filters.page_size
        page_items = all_items[start_idx:end_idx]

        return HistoryResponse(
            items=page_items,
            total=total,
            page=filters.page,
            page_size=filters.page_size,
            total_pages=total_pages,
        )

    @staticmethod
    def export_csv(
        document_type_code: str | None = None,
        year: int | None = None,
        user_id: str | None = None,
        action: str | None = None,
    ) -> str:
        """Export history to CSV format.

        Args:
            document_type_code: Optional filter by document type.
            year: Optional filter by year.
            user_id: Optional filter by user.
            action: Optional filter by action type.

        Returns:
            CSV string with all matching records.
        """
        # Get all records matching filters (no pagination for export)
        filters = HistoryFilter(
            document_type_code=document_type_code,
            year=year,
            user_id=user_id,
            action=action,  # type: ignore
            page=1,
            page_size=10000,  # Large enough to get all records
        )

        result = HistoryService.list_history(filters)

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        # Write header
        writer.writerow(
            [
                "Data/Hora",
                "Tipo Documento",
                "Ano",
                "Número",
                "Ação",
                "Usuário",
                "Número Anterior",
                "Observações",
            ]
        )

        # Write data rows
        for item in result.items:
            created_at_str = item.created_at.strftime("%d/%m/%Y %H:%M:%S")
            action_label = "Gerado" if item.action == "generated" else "Corrigido"

            writer.writerow(
                [
                    created_at_str,
                    item.document_type_code,
                    item.year,
                    item.number,
                    action_label,
                    item.user_name,
                    item.previous_number if item.previous_number else "",
                    item.notes if item.notes else "",
                ]
            )

        return output.getvalue()

    @staticmethod
    def get_by_id(log_id: str) -> NumberLogResponse | None:
        """Get a specific log entry by ID.

        Args:
            log_id: The RowKey of the log entry.

        Returns:
            NumberLogResponse if found, None otherwise.
        """
        table = get_number_logs_table()

        # Search across all partitions (log_id is the RowKey)
        entities = list(table.query_entities(query_filter=f"RowKey eq '{log_id}'"))

        if not entities:
            return None

        entity = entities[0]
        return NumberLogResponse.from_entity(NumberLogEntity(**entity))

    @staticmethod
    def get_statistics(
        document_type_code: str | None = None,
        year: int | None = None,
    ) -> dict:
        """Get statistics for number generation.

        Args:
            document_type_code: Optional filter by document type.
            year: Optional filter by year.

        Returns:
            Dictionary with statistics.
        """
        filters = HistoryFilter(
            document_type_code=document_type_code,
            year=year,
            page=1,
            page_size=10000,
        )

        result = HistoryService.list_history(filters)

        # Count by action
        generated_count = sum(1 for item in result.items if item.action == "generated")
        corrected_count = sum(1 for item in result.items if item.action == "corrected")

        # Count by document type
        by_type: dict[str, int] = {}
        for item in result.items:
            by_type[item.document_type_code] = by_type.get(item.document_type_code, 0) + 1

        # Count by user
        by_user: dict[str, int] = {}
        for item in result.items:
            by_user[item.user_name] = by_user.get(item.user_name, 0) + 1

        return {
            "total": result.total,
            "generated": generated_count,
            "corrected": corrected_count,
            "by_document_type": by_type,
            "by_user": by_user,
        }

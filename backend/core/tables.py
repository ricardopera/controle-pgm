"""Azure Tables client factory for Controle PGM."""

from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from azure.data.tables import TableClient, TableServiceClient

from core.config import settings

if TYPE_CHECKING:
    pass


# Table names
TABLE_USERS = "Users"
TABLE_DOCUMENT_TYPES = "DocumentTypes"
TABLE_SEQUENCES = "Sequences"
TABLE_NUMBER_LOGS = "NumberLogs"
TABLE_AUDIT_LOGS = "AuditLogs"


@lru_cache
def get_table_service_client() -> TableServiceClient:
    """Get cached TableServiceClient instance."""
    return TableServiceClient.from_connection_string(
        conn_str=settings.azure_tables_connection_string
    )


def get_table_client(table_name: str) -> TableClient:
    """
    Get a TableClient for the specified table.

    Creates the table if it doesn't exist.

    Args:
        table_name: Name of the table to access.

    Returns:
        TableClient instance for the specified table.
    """
    import contextlib

    service_client = get_table_service_client()
    table_client = service_client.get_table_client(table_name)

    # Create table if it doesn't exist (idempotent)
    # Table might already exist or we might not have permissions
    # In production, tables should be created via Bicep
    with contextlib.suppress(Exception):
        service_client.create_table_if_not_exists(table_name)

    return table_client


def get_users_table() -> TableClient:
    """Get TableClient for Users table."""
    return get_table_client(TABLE_USERS)


def get_document_types_table() -> TableClient:
    """Get TableClient for DocumentTypes table."""
    return get_table_client(TABLE_DOCUMENT_TYPES)


def get_sequences_table() -> TableClient:
    """Get TableClient for Sequences table."""
    return get_table_client(TABLE_SEQUENCES)


def get_number_logs_table() -> TableClient:
    """Get TableClient for NumberLogs table."""
    return get_table_client(TABLE_NUMBER_LOGS)


def get_audit_logs_table() -> TableClient:
    """Get TableClient for AuditLogs table."""
    return get_table_client(TABLE_AUDIT_LOGS)

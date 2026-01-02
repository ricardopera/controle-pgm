"""Audit logging service for Controle PGM."""

from __future__ import annotations

import logging
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from core.config import get_brazil_now, settings
from core.tables import get_table_client

logger = logging.getLogger(__name__)


class AuditAction(str, Enum):
    """Enumeration of auditable actions."""

    # User management
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DEACTIVATED = "user_deactivated"
    USER_REACTIVATED = "user_reactivated"
    USER_PASSWORD_RESET = "user_password_reset"
    USER_PASSWORD_CHANGED = "user_password_changed"
    USER_ROLE_CHANGED = "user_role_changed"

    # Document type management
    DOCTYPE_CREATED = "doctype_created"
    DOCTYPE_UPDATED = "doctype_updated"
    DOCTYPE_DEACTIVATED = "doctype_deactivated"

    # Authentication
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILED = "login_failed"
    LOGOUT = "logout"

    # Number generation
    NUMBER_GENERATED = "number_generated"
    NUMBER_CORRECTED = "number_corrected"


def get_audit_logs_table():
    """Get the audit logs table client."""
    return get_table_client("AuditLogs")


class AuditService:
    """Service for logging audit events."""

    @staticmethod
    def log(
        action: AuditAction,
        actor_id: str | None,
        actor_email: str | None,
        target_type: str | None = None,
        target_id: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> None:
        """
        Log an audit event.

        Args:
            action: The action being performed.
            actor_id: ID of the user performing the action.
            actor_email: Email of the user performing the action.
            target_type: Type of the target entity (e.g., "user", "document_type").
            target_id: ID of the target entity.
            details: Additional details about the action.
            ip_address: IP address of the request.
        """
        try:
            table = get_audit_logs_table()
            now = get_brazil_now()

            # Create partition key based on date for efficient querying
            partition_key = now.strftime("%Y-%m")

            # Create row key with inverse timestamp for newest-first ordering
            inverse_timestamp = str(9999999999 - int(now.timestamp()))
            row_key = f"{inverse_timestamp}_{uuid4().hex[:8]}"

            entity = {
                "PartitionKey": partition_key,
                "RowKey": row_key,
                "Action": action.value,
                "ActorId": actor_id or "system",
                "ActorEmail": actor_email or "system",
                "TargetType": target_type,
                "TargetId": target_id,
                "Details": str(details) if details else None,
                "IpAddress": ip_address,
                "Timestamp": now.isoformat(),
                "Environment": settings.environment,
            }

            table.create_entity(entity)

            # Also log to application logs for real-time monitoring
            logger.info(
                f"AUDIT: {action.value} by {actor_email or 'system'} "
                f"on {target_type}:{target_id} - {details}"
            )

        except Exception as e:
            # Never let audit logging break the main flow
            logger.error(f"Failed to write audit log: {e}")

    @staticmethod
    def log_user_action(
        action: AuditAction,
        actor: dict[str, Any],
        target_user_id: str | None = None,
        target_user_email: str | None = None,
        details: dict[str, Any] | None = None,
        ip_address: str | None = None,
    ) -> None:
        """
        Convenience method for logging user-related actions.

        Args:
            action: The action being performed.
            actor: The current_user dict from authentication.
            target_user_id: ID of the target user.
            target_user_email: Email of the target user (for details).
            details: Additional details.
            ip_address: IP address of the request.
        """
        full_details = details or {}
        if target_user_email:
            full_details["target_email"] = target_user_email

        AuditService.log(
            action=action,
            actor_id=actor.get("user_id"),
            actor_email=actor.get("email"),
            target_type="user",
            target_id=target_user_id,
            details=full_details,
            ip_address=ip_address,
        )

    @staticmethod
    def get_recent_logs(
        limit: int = 100,
        action_filter: AuditAction | None = None,
        actor_id: str | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get recent audit logs.

        Args:
            limit: Maximum number of logs to return.
            action_filter: Filter by specific action.
            actor_id: Filter by actor ID.

        Returns:
            List of audit log entries.
        """
        try:
            table = get_audit_logs_table()

            # Build filter
            filters = []
            if action_filter:
                filters.append(f"Action eq '{action_filter.value}'")
            if actor_id:
                filters.append(f"ActorId eq '{actor_id}'")

            filter_query = " and ".join(filters) if filters else None

            if filter_query:
                entities = list(table.query_entities(query_filter=filter_query))
            else:
                entities = list(table.list_entities())

            # Sort by RowKey (inverse timestamp means newest first)
            entities.sort(key=lambda x: x.get("RowKey", ""))

            return entities[:limit]

        except Exception as e:
            logger.error(f"Failed to read audit logs: {e}")
            return []

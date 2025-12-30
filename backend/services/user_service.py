"""User service for Controle PGM."""

from datetime import datetime
from uuid import uuid4

from azure.core.exceptions import ResourceNotFoundError
from azure.data.tables import UpdateMode

from core.auth import hash_password, verify_password
from core.exceptions import (
    ConflictError,
    ForbiddenError,
    InvalidCredentialsError,
    NotFoundError,
)
from core.tables import get_users_table
from models.user import UserCreate, UserEntity


class UserService:
    """Service for user operations."""

    @staticmethod
    def get_by_email(email: str) -> UserEntity | None:
        """Get a user by email address.

        Args:
            email: User's email address.

        Returns:
            UserEntity if found, None otherwise.
        """
        table = get_users_table()

        # Query by email (case-insensitive)
        query_filter = f"Email eq '{email.lower()}'"
        entities = list(table.query_entities(query_filter=query_filter))

        if not entities:
            return None

        entity = entities[0]
        return UserEntity(**entity)

    @staticmethod
    def get_by_id(user_id: str) -> UserEntity | None:
        """Get a user by ID.

        Args:
            user_id: User's unique ID (RowKey).

        Returns:
            UserEntity if found, None otherwise.
        """
        table = get_users_table()

        try:
            entity = table.get_entity(partition_key="USER", row_key=user_id)
            return UserEntity(**entity)
        except ResourceNotFoundError:
            return None

    @staticmethod
    def verify_credentials(email: str, password: str) -> UserEntity:
        """Verify user credentials for login.

        Args:
            email: User's email address.
            password: User's password.

        Returns:
            UserEntity if credentials are valid.

        Raises:
            InvalidCredentialsError: If credentials are invalid.
            ForbiddenError: If user is inactive.
        """
        user = UserService.get_by_email(email)

        if not user:
            raise InvalidCredentialsError("E-mail ou senha inválidos")

        if not verify_password(password, user.PasswordHash):
            raise InvalidCredentialsError("E-mail ou senha inválidos")

        if not user.IsActive:
            raise ForbiddenError("Usuário inativo")

        return user

    @staticmethod
    def create(data: UserCreate) -> UserEntity:
        """Create a new user.

        Args:
            data: User creation data.

        Returns:
            Created UserEntity.

        Raises:
            ConflictError: If email already exists.
        """
        # Check if email already exists
        existing = UserService.get_by_email(data.email)
        if existing:
            raise ConflictError("E-mail já cadastrado")

        table = get_users_table()
        now = datetime.utcnow()

        entity = UserEntity(
            PartitionKey="USER",
            RowKey=str(uuid4()),
            Email=data.email.lower(),
            Name=data.name,
            PasswordHash=hash_password(data.password),
            Role=data.role,
            IsActive=True,
            MustChangePassword=True,  # Force password change on first login
            CreatedAt=now,
            UpdatedAt=now,
        )

        table.create_entity(entity.model_dump())

        return entity

    @staticmethod
    def update(user_id: str, updates: dict) -> UserEntity:
        """Update a user.

        Args:
            user_id: User's unique ID.
            updates: Dictionary of fields to update.

        Returns:
            Updated UserEntity.

        Raises:
            NotFoundError: If user not found.
        """
        user = UserService.get_by_id(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")

        table = get_users_table()

        # Update fields
        entity_dict = user.model_dump()
        entity_dict.update(updates)
        entity_dict["UpdatedAt"] = datetime.utcnow()

        table.update_entity(entity_dict, mode=UpdateMode.REPLACE)

        return UserEntity(**entity_dict)

    @staticmethod
    def change_password(user_id: str, current_password: str, new_password: str) -> None:
        """Change a user's password.

        Args:
            user_id: User's unique ID.
            current_password: Current password for verification.
            new_password: New password to set.

        Raises:
            NotFoundError: If user not found.
            InvalidCredentialsError: If current password is incorrect.
        """
        user = UserService.get_by_id(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")

        if not verify_password(current_password, user.PasswordHash):
            raise InvalidCredentialsError("Senha atual incorreta")

        UserService.update(
            user_id,
            {
                "PasswordHash": hash_password(new_password),
                "MustChangePassword": False,
            },
        )

    @staticmethod
    def reset_password(user_id: str) -> str:
        """Reset a user's password to a temporary value.

        Args:
            user_id: User's unique ID.

        Returns:
            Temporary password.

        Raises:
            NotFoundError: If user not found.
        """
        import secrets
        import string

        user = UserService.get_by_id(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")

        # Generate temporary password
        alphabet = string.ascii_letters + string.digits
        temp_password = "".join(secrets.choice(alphabet) for _ in range(12))
        # Ensure it meets policy
        temp_password = f"Tmp{temp_password}1"

        UserService.update(
            user_id,
            {
                "PasswordHash": hash_password(temp_password),
                "MustChangePassword": True,
            },
        )

        return temp_password

    @staticmethod
    def list_all() -> list[UserEntity]:
        """List all users.

        Returns:
            List of all UserEntity objects.
        """
        table = get_users_table()
        entities = list(table.query_entities(query_filter="PartitionKey eq 'USER'"))
        return [UserEntity(**entity) for entity in entities]

    @staticmethod
    def deactivate(user_id: str, current_admin_id: str) -> UserEntity:
        """Deactivate a user.

        Args:
            user_id: User's unique ID.
            current_admin_id: ID of the admin performing the action.

        Returns:
            Updated UserEntity.

        Raises:
            NotFoundError: If user not found.
            ForbiddenError: If trying to deactivate self or last admin.
        """
        if user_id == current_admin_id:
            raise ForbiddenError("Não é possível desativar a si mesmo")

        user = UserService.get_by_id(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")

        # Check if this is the last active admin
        if user.Role == "admin":
            all_users = UserService.list_all()
            active_admins = [
                u for u in all_users if u.Role == "admin" and u.IsActive and u.RowKey != user_id
            ]
            if not active_admins:
                raise ForbiddenError("Não é possível desativar o último administrador ativo")

        return UserService.update(user_id, {"IsActive": False})

    @staticmethod
    def remove_admin_role(user_id: str, current_admin_id: str) -> UserEntity:
        """Remove admin role from a user.

        Args:
            user_id: User's unique ID.
            current_admin_id: ID of the admin performing the action.

        Returns:
            Updated UserEntity.

        Raises:
            NotFoundError: If user not found.
            ForbiddenError: If trying to remove own admin role or last admin.
        """
        if user_id == current_admin_id:
            raise ForbiddenError("Não é possível remover o próprio papel de administrador")

        user = UserService.get_by_id(user_id)
        if not user:
            raise NotFoundError("Usuário não encontrado")

        if user.Role != "admin":
            return user  # Already not an admin

        # Check if this is the last active admin
        all_users = UserService.list_all()
        active_admins = [
            u for u in all_users if u.Role == "admin" and u.IsActive and u.RowKey != user_id
        ]
        if not active_admins:
            raise ForbiddenError(
                "Não é possível remover o papel de administrador do último administrador ativo"
            )

        return UserService.update(user_id, {"Role": "user"})

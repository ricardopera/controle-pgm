"""Pytest configuration and fixtures for Controle PGM backend tests."""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

# Set test environment variables before importing application code
os.environ["AZURE_TABLES_CONNECTION_STRING"] = "UseDevelopmentStorage=true"
os.environ["JWT_SECRET"] = "test-secret-key-for-testing-only-min-32-chars"
os.environ["JWT_EXPIRATION_HOURS"] = "8"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"


@pytest.fixture
def mock_table_client():
    """Create a mock TableClient for testing."""
    client = MagicMock()
    client.query_entities = MagicMock(return_value=[])
    client.get_entity = MagicMock()
    client.create_entity = MagicMock()
    client.update_entity = MagicMock()
    client.upsert_entity = MagicMock()
    client.delete_entity = MagicMock()
    return client


@pytest.fixture
def mock_table_service(mock_table_client):
    """Create a mock TableServiceClient with table access."""
    with patch("core.tables.TableServiceClient") as mock_service:
        instance = MagicMock()
        instance.get_table_client.return_value = mock_table_client
        mock_service.from_connection_string.return_value = instance
        yield mock_service


@pytest.fixture
def sample_user_entity():
    """Create a sample user entity for testing."""
    from core.auth import hash_password

    now = datetime.utcnow()
    return {
        "PartitionKey": "USER",
        "RowKey": str(uuid4()),
        "Email": "test@example.com",
        "Name": "Test User",
        "PasswordHash": hash_password("TestPassword123"),
        "Role": "user",
        "IsActive": True,
        "MustChangePassword": False,
        "CreatedAt": now,
        "UpdatedAt": now,
    }


@pytest.fixture
def sample_admin_entity():
    """Create a sample admin entity for testing."""
    from core.auth import hash_password

    now = datetime.utcnow()
    return {
        "PartitionKey": "USER",
        "RowKey": str(uuid4()),
        "Email": "admin@example.com",
        "Name": "Admin User",
        "PasswordHash": hash_password("AdminPassword123"),
        "Role": "admin",
        "IsActive": True,
        "MustChangePassword": False,
        "CreatedAt": now,
        "UpdatedAt": now,
    }


@pytest.fixture
def sample_document_type_entity():
    """Create a sample document type entity for testing."""
    now = datetime.utcnow()
    return {
        "PartitionKey": "DOCTYPE",
        "RowKey": str(uuid4()),
        "Code": "OF",
        "Name": "Ofício",
        "IsActive": True,
        "CreatedAt": now,
        "UpdatedAt": now,
    }


@pytest.fixture
def sample_sequence_entity():
    """Create a sample sequence entity for testing."""
    now = datetime.utcnow()
    return {
        "PartitionKey": "OF_2025",
        "RowKey": "SEQUENCE",
        "DocumentTypeCode": "OF",
        "Year": 2025,
        "CurrentNumber": 42,
        "UpdatedAt": now,
    }


@pytest.fixture
def sample_number_log_entity():
    """Create a sample number log entity for testing."""
    now = datetime.utcnow()
    return {
        "PartitionKey": "OF_2025",
        "RowKey": f"{9999999999 - int(now.timestamp())}_{uuid4()}",
        "DocumentTypeCode": "OF",
        "Year": 2025,
        "Number": 42,
        "Action": "generated",
        "UserId": str(uuid4()),
        "UserName": "Test User",
        "PreviousNumber": None,
        "Notes": None,
        "CreatedAt": now,
    }


@pytest.fixture
def auth_token(sample_user_entity):
    """Create a valid authentication token for testing."""
    from core.auth import create_token

    return create_token(
        user_id=sample_user_entity["RowKey"],
        email=sample_user_entity["Email"],
        name=sample_user_entity["Name"],
        role=sample_user_entity["Role"],
    )


@pytest.fixture
def admin_auth_token(sample_admin_entity):
    """Create a valid admin authentication token for testing."""
    from core.auth import create_token

    return create_token(
        user_id=sample_admin_entity["RowKey"],
        email=sample_admin_entity["Email"],
        name=sample_admin_entity["Name"],
        role=sample_admin_entity["Role"],
    )


@pytest.fixture
def mock_http_request():
    """Create a mock Azure Functions HTTP request."""
    import azure.functions as func

    def create_request(
        method: str = "GET",
        url: str = "/api/test",
        body: bytes = b"",
        headers: dict = None,
        params: dict = None,
    ):
        req = MagicMock(spec=func.HttpRequest)
        req.method = method
        req.url = url
        req.get_body.return_value = body
        req.headers = headers or {}
        req.params = params or {}
        return req

    return create_request


@pytest.fixture
def mock_http_request_with_cookie(mock_http_request, auth_token):
    """Create a mock request with authentication cookie."""

    def create_request(**kwargs):
        req = mock_http_request(**kwargs)
        req.headers["Cookie"] = f"auth_token={auth_token}"
        return req

    return create_request


# Azurite fixtures for integration tests
@pytest.fixture(scope="session")
def azurite_connection_string():
    """Connection string for Azurite (local Azure Storage emulator)."""
    return "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"


@pytest.fixture
def integration_table_client(azurite_connection_string):
    """Create a real TableClient for integration tests with Azurite.

    Requires Azurite to be running:
    npm install -g azurite
    azurite-table
    """
    pytest.importorskip("azure.data.tables")

    from azure.data.tables import TableServiceClient

    try:
        service = TableServiceClient.from_connection_string(azurite_connection_string)
        # Create test table
        table_name = f"TestTable{uuid4().hex[:8]}"
        table_client = service.create_table_if_not_exists(table_name)
        yield table_client
        # Cleanup
        service.delete_table(table_name)
    except Exception as e:
        pytest.skip(f"Azurite not available: {e}")

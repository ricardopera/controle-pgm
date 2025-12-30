#!/usr/bin/env python3
"""Seed script for Controle PGM - creates initial admin user and document types."""

import os
import sys
from datetime import datetime
from uuid import uuid4

# Add backend to path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, "backend"))

from azure.data.tables import TableServiceClient

from backend.core.auth import hash_password
from backend.core.config import settings


def create_tables(service: TableServiceClient) -> None:
    """Create required tables if they don't exist."""
    tables = ["Users", "DocumentTypes", "Sequences", "NumberLogs"]
    
    for table_name in tables:
        try:
            service.create_table(table_name)
            print(f"✅ Table '{table_name}' created")
        except Exception as e:
            if "TableAlreadyExists" in str(e):
                print(f"ℹ️  Table '{table_name}' already exists")
            else:
                raise


def seed_admin_user(service: TableServiceClient) -> None:
    """Create initial admin user."""
    table = service.get_table_client("Users")
    
    # Check if admin already exists
    existing = list(table.query_entities(query_filter="Email eq 'admin@pgm.itajai.sc.gov.br'"))
    if existing:
        print("ℹ️  Admin user already exists")
        return
    
    now = datetime.utcnow()
    
    # Default admin password - MUST be changed on first login
    default_password = "Admin@PGM2025"
    
    admin_entity = {
        "PartitionKey": "USER",
        "RowKey": str(uuid4()),
        "Email": "admin@pgm.itajai.sc.gov.br",
        "Name": "Administrador PGM",
        "PasswordHash": hash_password(default_password),
        "Role": "admin",
        "IsActive": True,
        "MustChangePassword": True,
        "CreatedAt": now,
        "UpdatedAt": now,
    }
    
    table.create_entity(admin_entity)
    print(f"✅ Admin user created")
    print(f"   Email: admin@pgm.itajai.sc.gov.br")
    print(f"   Password: {default_password}")
    print(f"   ⚠️  Please change the password on first login!")


def seed_document_types(service: TableServiceClient) -> None:
    """Create initial document types."""
    table = service.get_table_client("DocumentTypes")
    
    document_types = [
        ("OF", "Ofício"),
        ("MEM", "Memorando"),
        ("CI", "Comunicação Interna"),
        ("PAR", "Parecer"),
        ("INF", "Informação"),
        ("DES", "Despacho"),
        ("PORT", "Portaria"),
        ("DEC", "Decreto"),
        ("CONT", "Contrato"),
        ("CONV", "Convênio"),
    ]
    
    now = datetime.utcnow()
    created_count = 0
    
    for code, name in document_types:
        # Check if already exists
        existing = list(table.query_entities(query_filter=f"Code eq '{code}'"))
        if existing:
            print(f"ℹ️  Document type '{code}' already exists")
            continue
        
        entity = {
            "PartitionKey": "DOCTYPE",
            "RowKey": str(uuid4()),
            "Code": code,
            "Name": name,
            "IsActive": True,
            "CreatedAt": now,
            "UpdatedAt": now,
        }
        
        table.create_entity(entity)
        print(f"✅ Document type '{code}' ({name}) created")
        created_count += 1
    
    if created_count == 0:
        print("ℹ️  All document types already exist")


def main():
    """Run seed script."""
    print("=" * 60)
    print("Controle PGM - Seed Script")
    print("=" * 60)
    print()
    
    # Get connection string
    connection_string = settings.azure_tables_connection_string
    
    if not connection_string:
        print("❌ AZURE_TABLES_CONNECTION_STRING not set")
        print("   Set this environment variable or create a .env file")
        sys.exit(1)
    
    # Check if using Azurite (local development)
    if "UseDevelopmentStorage" in connection_string or "127.0.0.1" in connection_string:
        print("🔧 Using Azurite (local development storage)")
    else:
        print("☁️  Using Azure Table Storage")
    
    print()
    
    # Connect to table service
    try:
        service = TableServiceClient.from_connection_string(connection_string)
        print("✅ Connected to Table Storage")
        print()
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        sys.exit(1)
    
    # Create tables
    print("📦 Creating tables...")
    create_tables(service)
    print()
    
    # Seed admin user
    print("👤 Seeding admin user...")
    seed_admin_user(service)
    print()
    
    # Seed document types
    print("📄 Seeding document types...")
    seed_document_types(service)
    print()
    
    print("=" * 60)
    print("✅ Seed completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()

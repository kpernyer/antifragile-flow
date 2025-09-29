# Scripts Directory

This directory contains utility scripts and tools for managing the Organizational Twin system.

## 🔧 Database & Migration Scripts

- **`migrate_to_neo4j.py`** - Migrate data to Neo4j graph database
- **`migrate_to_postgres.py`** - Migrate data to PostgreSQL database
- **`create_users.py`** - Create and set up system users
- **`test_connections.py`** - Test database and service connections

## 🎭 Demo & Testing Scripts

- **`demo_runner.py`** - Run system demonstrations
- **`seed_demo_inbox.py`** - Seed the inbox with demo data
- **`demo-data/`** - Directory containing demo data files
- **`organizational_twin.db`** - SQLite database with demo data

## 📊 Visualization & Analysis

- **`plot_workflows.py`** - Generate workflow visualization diagrams

## 🔑 Configuration Files

- **`serviceAccountKey.json`** - Firebase service account key (move to env vars in production)
- **`app-postgres-init.sql`** - PostgreSQL initialization script
- **`neo4j-init/`** - Neo4j initialization scripts

## 🚨 Security Note

The `serviceAccountKey.json` file contains sensitive credentials. In production:
1. Move this to environment variables
2. Use secure secret management (e.g., Google Secret Manager)
3. Never commit real keys to version control

## Usage

Most scripts can be run from the project root:

```bash
# Test database connections
uv run python scripts/test_connections.py

# Create demo users
uv run python scripts/create_users.py

# Seed demo data
uv run python scripts/seed_demo_inbox.py

# Run demo
uv run python scripts/demo_runner.py
```

These scripts use the same dependencies as the main project and should be run with the `uv run` prefix to use the correct Python environment.

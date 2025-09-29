#!/usr/bin/env python3
"""
Migration script to replace hardcoded values with centralized configuration.

This script identifies and can optionally replace hardcoded localhost URLs
and port numbers with calls to the centralized configuration system.
"""

from pathlib import Path
import re


def find_hardcoded_values(directory: str) -> list[tuple[str, int, str, str]]:
    """
    Find all hardcoded temporal addresses and monitoring URLs.

    Returns list of (filepath, line_number, old_text, suggested_replacement)
    """
    results = []

    # Patterns to find
    patterns = [
        (r'Client\.connect\("localhost:7233"\)', "Client.connect(get_temporal_address())"),
        (
            r'await Client\.connect\("localhost:7233"\)',
            "await Client.connect(get_temporal_address())",
        ),
        (r'os\.environ\.get\("TEMPORAL_ADDRESS",\s*"localhost:7233"\)', "get_temporal_address()"),
        (
            r'"http://localhost:8233/namespaces/default/workflows/\{\w+\}"',
            "get_temporal_ui_url({workflow_id})",
        ),
        (
            r'f"http://localhost:8233/namespaces/default/workflows/\{[^}]+\}"',
            "get_temporal_ui_url({workflow_id})",
        ),
    ]

    # Files to check
    python_files = Path(directory).rglob("*.py")

    for file_path in python_files:
        # Skip virtual environments and caches
        if any(skip in str(file_path) for skip in [".venv", "__pycache__", ".mypy_cache"]):
            continue

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                for pattern, replacement in patterns:
                    if re.search(pattern, line):
                        results.append((str(file_path), line_num, line.strip(), replacement))
        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    return results


def show_migration_opportunities():
    """Show all files that could benefit from migration."""
    print("🔍 SCANNING FOR HARDCODED VALUES")
    print("=" * 60)

    results = find_hardcoded_values(".")

    if not results:
        print("✅ No hardcoded values found!")
        return

    # Group by file
    files = {}
    for filepath, line_num, old_text, replacement in results:
        if filepath not in files:
            files[filepath] = []
        files[filepath].append((line_num, old_text, replacement))

    print(f"Found {len(results)} hardcoded values in {len(files)} files:")
    print()

    for filepath, issues in files.items():
        print(f"📁 {filepath}")
        for line_num, old_text, replacement in issues:
            print(f"   Line {line_num}: {old_text}")
            print(f"   Suggested: {replacement}")
            print()


def show_import_suggestions():
    """Show which files need import statements added."""
    print("📋 IMPORT STATEMENTS NEEDED")
    print("=" * 60)

    results = find_hardcoded_values(".")
    files_needing_imports = set()

    for filepath, _, _, replacement in results:
        if "get_temporal_address" in replacement or "get_temporal_ui_url" in replacement:
            files_needing_imports.add(filepath)

    for filepath in sorted(files_needing_imports):
        print(f"📁 {filepath}")
        print(
            "   Add: from shared.config.defaults import get_temporal_address, get_temporal_ui_url"
        )
        print()


def show_environment_variables():
    """Show recommended environment variable setup."""
    print("🌍 ENVIRONMENT VARIABLES")
    print("=" * 60)
    print("Add these to your .env file or environment:")
    print()
    print("# Temporal Configuration")
    print("TEMPORAL_ADDRESS=localhost:7233")
    print("TEMPORAL_UI_ADDRESS=http://localhost:8233")
    print()
    print("# Frontend Configuration (for React)")
    print("REACT_APP_TEMPORAL_ADDRESS=localhost:7233")
    print("REACT_APP_TEMPORAL_UI_ADDRESS=http://localhost:8233")
    print("REACT_APP_API_URL=http://localhost:8080")
    print("REACT_APP_FRONTEND_URL=http://localhost:3000")
    print()
    print("# GraphQL Knowledge Base Configuration")
    print("GRAPHQL_HOST=localhost")
    print("GRAPHQL_PORT=4000")
    print("GRAPHQL_URL=http://localhost:4000")
    print("GRAPHQL_ENDPOINT=http://localhost:4000/graphql")
    print("GRAPHQL_PLAYGROUND=http://localhost:4000/playground")
    print("GRAPHQL_SUBSCRIPTIONS=ws://localhost:4000/graphql")
    print()
    print("# GraphQL Frontend Configuration")
    print("REACT_APP_GRAPHQL_URL=http://localhost:4000")
    print("REACT_APP_GRAPHQL_ENDPOINT=http://localhost:4000/graphql")
    print("REACT_APP_GRAPHQL_SUBSCRIPTIONS=ws://localhost:4000/graphql")
    print()
    print("# Knowledge Base Features")
    print("KB_FULL_TEXT_SEARCH=true")
    print("KB_SEMANTIC_SEARCH=true")
    print("KB_SEARCH_LIMIT=50")
    print("KB_DATABASE_BACKEND=postgresql")
    print("KB_VECTOR_DATABASE=pinecone")
    print()


def main():
    """Main migration analysis."""
    print("🔧 HARDCODED VALUES MIGRATION ANALYSIS")
    print("=" * 60)
    print()

    show_migration_opportunities()
    show_import_suggestions()
    show_environment_variables()

    print("🚀 NEXT STEPS:")
    print("1. Review the suggested changes above")
    print("2. Add import statements to files that need them")
    print("3. Replace hardcoded values with centralized config calls")
    print("4. Test that everything still works")
    print("5. Set up environment variables for different environments")
    print()
    print("💡 Example migration (already done in actor/ceo/starter.py):")
    print("   Before: await Client.connect('localhost:7233')")
    print("   After:  await Client.connect(get_temporal_address())")
    print()


if __name__ == "__main__":
    main()

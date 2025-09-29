#!/usr/bin/env python3
"""
Command-line interface for managing prompts and templates.

Provides tools for validating, testing, and managing prompt definitions.
"""

import argparse
import json
from pathlib import Path
import sys

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from .loader import PromptLoader
from .registry import PromptRegistry
from .schemas.base import RenderContext

console = Console()


def validate_prompts(args: argparse.Namespace) -> None:
    """Validate all prompt definitions."""
    console.print("[bold blue]Validating prompt definitions...[/bold blue]")

    loader = PromptLoader(args.prompts_dir)
    results = loader.validate_all_prompts()

    if not results:
        console.print("[yellow]No prompt files found.[/yellow]")
        return

    # Summary
    total_files = len(results)
    error_files = sum(1 for errors in results.values() if errors)
    success_files = total_files - error_files

    console.print("\n[bold]Validation Summary:[/bold]")
    console.print(f"  Total files: {total_files}")
    console.print(f"  [green]Successful: {success_files}[/green]")
    console.print(f"  [red]With errors: {error_files}[/red]")

    # Show errors
    if error_files > 0:
        console.print("\n[bold red]Validation Errors:[/bold red]")
        for file_path, errors in results.items():
            if errors:
                console.print(f"\n[yellow]{file_path}[/yellow]")
                for error in errors:
                    console.print(f"  [red]✗[/red] {error}")
    else:
        console.print("\n[bold green]✓ All prompt files are valid![/bold green]")

    sys.exit(1 if error_files > 0 else 0)


def list_prompts(args: argparse.Namespace) -> None:
    """List all available prompts."""
    console.print("[bold blue]Loading prompts...[/bold blue]")

    registry = PromptRegistry(args.prompts_dir)
    prompts = registry.list_prompts(
        category=args.category, tags=args.tags.split(",") if args.tags else None
    )

    if not prompts:
        console.print("[yellow]No prompts found.[/yellow]")
        return

    # Create table
    table = Table(title="Available Prompts")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="magenta")
    table.add_column("Category", style="green")
    table.add_column("Version", style="yellow")
    table.add_column("Usage", style="blue")

    for prompt in prompts:
        table.add_row(
            prompt.metadata.id,
            prompt.metadata.name,
            prompt.metadata.category,
            prompt.metadata.version,
            str(prompt.metadata.usage_count),
        )

    console.print(table)

    if args.verbose:
        console.print(f"\n[bold]Total prompts:[/bold] {len(prompts)}")


def show_prompt(args: argparse.Namespace) -> None:
    """Show details of a specific prompt."""
    registry = PromptRegistry(args.prompts_dir)

    try:
        template = registry.get_template(args.prompt_id)
    except KeyError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

    # Show metadata
    metadata = template.metadata
    console.print(
        Panel.fit(
            f"[bold]{metadata.name}[/bold]\n"
            f"ID: {metadata.id}\n"
            f"Category: {metadata.category}\n"
            f"Version: {metadata.version}\n"
            f"Author: {metadata.author}\n"
            f"Description: {metadata.description}",
            title="Prompt Metadata",
        )
    )

    # Show template
    if template.system_prompt:
        console.print("\n[bold]System Prompt:[/bold]")
        console.print(
            Panel(Syntax(template.system_prompt, "text", theme="monokai"), title="System Prompt")
        )

    console.print("\n[bold]Template:[/bold]")
    console.print(
        Panel(Syntax(template.template, "jinja2", theme="monokai"), title="Jinja2 Template")
    )

    # Show variables
    if template.variables:
        console.print("\n[bold]Variables:[/bold]")
        var_table = Table()
        var_table.add_column("Name", style="cyan")
        var_table.add_column("Type", style="yellow")
        var_table.add_column("Required", style="green")
        var_table.add_column("Description", style="white")

        for var in template.variables:
            var_table.add_row(var.name, var.type, "✓" if var.required else "✗", var.description)

        console.print(var_table)

    # Show examples
    if template.examples:
        console.print(f"\n[bold]Examples:[/bold] {len(template.examples)} available")


def test_prompt(args: argparse.Namespace) -> None:
    """Test rendering a prompt with provided variables."""
    registry = PromptRegistry(args.prompts_dir)

    try:
        template = registry.get_template(args.prompt_id)
    except KeyError as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

    # Load variables from file or command line
    variables = {}
    if args.variables_file:
        with open(args.variables_file) as f:
            variables = json.load(f)

    if args.variables:
        # Parse key=value pairs
        for var_pair in args.variables:
            if "=" not in var_pair:
                console.print(f"[red]Invalid variable format: {var_pair}[/red]")
                console.print("Use format: key=value")
                sys.exit(1)
            key, value = var_pair.split("=", 1)
            variables[key] = value

    # Create context
    context = RenderContext(variables=variables, user_id=args.user_id, session_id=args.session_id)

    try:
        if args.system_user_split:
            system_prompt, user_prompt = registry.get_system_and_user_prompts(
                args.prompt_id, context
            )

            if system_prompt:
                console.print("[bold]System Prompt:[/bold]")
                console.print(Panel(system_prompt, title="System"))

            console.print("\n[bold]User Prompt:[/bold]")
            console.print(Panel(user_prompt, title="User"))

        else:
            rendered = registry.get_rendered_prompt(args.prompt_id, context)
            console.print("[bold]Rendered Prompt:[/bold]")
            console.print(Panel(rendered, title="Complete Prompt"))

    except Exception as e:
        console.print(f"[red]Rendering failed: {e}[/red]")
        sys.exit(1)


def usage_stats(args: argparse.Namespace) -> None:
    """Show usage statistics for prompts."""
    registry = PromptRegistry(args.prompts_dir)
    stats = registry.get_usage_stats()

    console.print(
        Panel.fit(
            f"Total Prompts: {stats['total_prompts']}\n"
            f"Used Prompts: {stats['used_prompts']}\n"
            f"Unused Prompts: {stats['unused_prompts']}\n"
            f"Total Usage: {stats['total_usage']}\n"
            f"Most Used: {stats['most_used_prompt']} ({stats['most_used_count']} times)",
            title="Prompt Usage Statistics",
        )
    )

    if args.details:
        # Show per-prompt usage
        prompts = registry.list_prompts()
        used_prompts = [p for p in prompts if p.metadata.usage_count > 0]

        if used_prompts:
            usage_table = Table(title="Prompt Usage Details")
            usage_table.add_column("Prompt ID", style="cyan")
            usage_table.add_column("Usage Count", style="yellow")
            usage_table.add_column("Last Used", style="green")

            for prompt in sorted(used_prompts, key=lambda p: p.metadata.usage_count, reverse=True):
                last_used = (
                    prompt.metadata.last_used.strftime("%Y-%m-%d %H:%M")
                    if prompt.metadata.last_used
                    else "Never"
                )
                usage_table.add_row(prompt.metadata.id, str(prompt.metadata.usage_count), last_used)

            console.print("\n")
            console.print(usage_table)


def create_example_prompt(args: argparse.Namespace) -> None:
    """Create an example prompt file."""
    example_content = """version: "1.0"
prompts:
  - metadata:
      id: "example.hello_world"
      name: "Hello World Example"
      description: "A simple example prompt for testing"
      category: "common"
      version: "1.0.0"
      tags: ["example", "test"]
      preferred_models: ["anthropic/claude-3-sonnet"]
      max_tokens: 500
      temperature: 0.7
    role: "user"
    system_prompt: |
      You are a helpful assistant providing examples and demonstrations.
    template: |
      Hello {{ name }}!

      {% if greeting_type == "formal" %}
      I hope this message finds you well.
      {% else %}
      How are you doing?
      {% endif %}

      {% if include_time %}
      Current time: {{ now | format_timestamp }}
      {% endif %}

      {{ custom_message | default("Have a great day!") }}
    variables:
      - name: name
        type: string
        description: "Name of the person to greet"
        required: true
        examples: ["Alice", "Bob", "Dr. Smith"]
      - name: greeting_type
        type: string
        description: "Type of greeting (formal or casual)"
        required: false
        default: "casual"
        examples: ["formal", "casual"]
      - name: include_time
        type: bool
        description: "Whether to include current timestamp"
        required: false
        default: false
      - name: custom_message
        type: string
        description: "Custom message to include"
        required: false
    examples:
      - variables:
          name: "Alice"
          greeting_type: "formal"
          include_time: true
"""

    output_file = Path(args.output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w") as f:
        f.write(example_content)

    console.print(f"[green]Created example prompt file: {output_file}[/green]")


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Prompt management CLI", formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("--prompts-dir", type=Path, help="Directory containing prompt definitions")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate prompt definitions")

    # List command
    list_parser = subparsers.add_parser("list", help="List available prompts")
    list_parser.add_argument("--category", help="Filter by category")
    list_parser.add_argument("--tags", help="Filter by tags (comma-separated)")
    list_parser.add_argument("--verbose", "-v", action="store_true", help="Show additional details")

    # Show command
    show_parser = subparsers.add_parser("show", help="Show details of a specific prompt")
    show_parser.add_argument("prompt_id", help="Prompt ID to show")

    # Test command
    test_parser = subparsers.add_parser("test", help="Test rendering a prompt")
    test_parser.add_argument("prompt_id", help="Prompt ID to test")
    test_parser.add_argument(
        "--variables", "-v", action="append", help="Variables as key=value pairs"
    )
    test_parser.add_argument("--variables-file", "-f", help="JSON file with variables")
    test_parser.add_argument("--user-id", help="User ID for context")
    test_parser.add_argument("--session-id", help="Session ID for context")
    test_parser.add_argument(
        "--system-user-split", action="store_true", help="Show system and user prompts separately"
    )

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show usage statistics")
    stats_parser.add_argument(
        "--details", action="store_true", help="Show detailed usage information"
    )

    # Create example command
    example_parser = subparsers.add_parser("create-example", help="Create an example prompt file")
    example_parser.add_argument("output_file", help="Output file path")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        if args.command == "validate":
            validate_prompts(args)
        elif args.command == "list":
            list_prompts(args)
        elif args.command == "show":
            show_prompt(args)
        elif args.command == "test":
            test_prompt(args)
        elif args.command == "stats":
            usage_stats(args)
        elif args.command == "create-example":
            create_example_prompt(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()

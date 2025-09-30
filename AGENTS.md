# Repository Guidelines

## Project Structure & Module Organization
Temporal orchestration code sits in `workflow/` (starters) and `worker/` (long-running workers), while reusable activities live in `activity/` and agent-specific routines in `agent_activity/`. Domain models, configuration, and prompt templates are centralized in `shared/`; adapters for PostgreSQL, Neo4j, and MinIO sit in `service/`. The React + TypeScript client lives in `frontend/`, and Python prototypes plus training jobs reside in `python/`. Scenario and regression suites live in `test/`, keeping fixtures beside the cases they support.

## Build, Test, and Development Commands
`make install` bootstraps Python and Node dependencies, and `make build` compiles shared assets. Use `make test`, `make lint`, and `make format` while coding, or `make quality` before publishing changes. Bring up local infrastructure with `make docker-up`; prompt helpers include `make prompts-validate`, `make prompts-list`, and `make prompts-stats`. For iterative runs, start workers with `uv run poe dev` and launch the UI through `cd frontend && pnpm start`.

## Coding Style & Naming Conventions
Python code is formatted by Ruff (four-space indentation, double quotes, 100-character lines) and passes strict MyPy checks. Group modules by capability with descriptive filenames such as `organizational_twin.py` or `consensus_facilitator`. Tests should mirror the modules they cover and use `test_*.py` naming. Frontend components in `frontend/src` follow PascalCase, while hooks and utilities keep camelCase; run `ruff check --fix` and `ruff format` before committing.

## Testing Guidelines
Pytest is configured via `pyproject.toml` with `unit`, `integration`, and `slow` markers—tag new suites so CI filtering stays meaningful. Run backend tests with `uv run poe test`, and add coverage when needed using `pytest --cov=. --cov-report=term`. Validate the UI with `pnpm test`, and extend scenario suites in `test/` whenever workflows or prompts change to cover both success paths and fallback behavior.

## Commit & Pull Request Guidelines
Git history favors Conventional Commit prefixes (`feat:`, `docs:`, `security:`); keep subjects under 72 characters and use bodies for context or issue links. Ensure `make quality` passes before opening a PR. Pull requests should summarize intent, list verification steps, record follow-up work, and attach screenshots or Temporal run IDs for user-facing changes; update documentation and prompt metadata alongside code.

## Agent & Prompt Tips
Place new agent behaviors under `agent_activity/` and shared prompt templates in `shared/prompts/`, namespacing identifiers such as `consensus.decide`. After editing templates, run `make prompts-validate` to catch missing variables or schemas. Capture reusable personas or workflow playbooks in `doc/` so operational teams can adopt them quickly.

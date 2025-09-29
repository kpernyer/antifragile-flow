#!/usr/bin/env bash

name="$1"

if [ -z "$name" ]; then
  echo "Usage: $0 {Mary|Isac|John|Priya|Bob}"
  exit 1
fi

# Detect repo name if in git
if git rev-parse --show-toplevel >/dev/null 2>&1; then
  repo=$(basename "$(git rev-parse --show-toplevel)")
else
  repo=$(basename "$PWD")
fi

case "$name" in
  Mary)  PROMPT="[$repo] 👑 Mary 👉 " ;;
  Isac)  PROMPT="[$repo] 🛠️ Isac 👉 " ;;
  John)  PROMPT="[$repo] 💼 John 👉 " ;;
  Priya) PROMPT="[$repo] ⚖️ Priya 👉 " ;;
  Bob)   export PROMPT="[$repo] 🖥️ Bob 👉 " ;;
  *)     echo "Unknown name: $name (use Mary|Isac|John|Priya|Bob)" && exit 1 ;;
esac

# Call your Python program
uv run ./user_client.py "$name"

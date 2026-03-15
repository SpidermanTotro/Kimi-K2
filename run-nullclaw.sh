#!/usr/bin/env bash
# run-nullclaw.sh — Quick launcher for NullClaw
#
# Usage:
#   ./run-nullclaw.sh [project_dir] [model]
#
# Examples:
#   ./run-nullclaw.sh ~/projects/gemini-cli
#   ./run-nullclaw.sh ~/projects/gemini-cli qwen2.5-coder:latest
#   ./run-nullclaw.sh ~/projects/myapp codellama:latest

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${1:-${NULLCLAW_PROJECT:-${HOME}/projects/null-claw-workspace}}"
MODEL="${2:-${NULLCLAW_MODEL:-qwen2.5-coder:latest}}"

echo "🦀  NullClaw"
echo "    project : ${PROJECT_DIR}"
echo "    model   : ${MODEL}"
echo ""

cd "${SCRIPT_DIR}"
python3 nullclaw.py repair "${PROJECT_DIR}" "${MODEL}"

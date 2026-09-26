#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if ! command -v python3 >/dev/null 2>&1; then
  if [[ "${1:-help}" == help || "${1:-}" == -h || "${1:-}" == --help ]]; then
    printf '%s\n' 'help doctor dev test lint: configuration PENDING; Python >=3.11 required'
    exit 0
  fi
  printf '%s\n' 'PENDING: Python >=3.11 required; install explicitly' >&2
  exit 3
fi
export PYTHONDONTWRITEBYTECODE=1
exec python3 -B "$ROOT/scripts/project_runner.py" "$@"

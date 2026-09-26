"""Bounded reference unittest entrypoint; not a generic live acceptance runner."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="reference-tests-") as state:
        # Python children inherit this loopback-only guard; no inherited secret/proxy env.
        guard = Path(state) / "sitecustomize.py"
        guard.write_text((root / "scripts/test_network_guard.py").read_text())
        env = {k: os.environ[k] for k in ("PATH", "LANG", "LC_CTYPE") if k in os.environ}
        env.update(HOME=state, TMPDIR=state, PYTHONPATH=state, PYTHONDONTWRITEBYTECODE="1")
        try:
            return subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v", *sys.argv[1:]],
                cwd=root, env=env, timeout=180, check=False,
            ).returncode
        except subprocess.TimeoutExpired:
            print("FAIL: reference test timeout (180s); no PASS evidence", file=sys.stderr)
            return 124


if __name__ == "__main__":
    raise SystemExit(main())

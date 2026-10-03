"""Bounded reference unittest entrypoint; not a generic live acceptance runner."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TIMEOUT_SECONDS = 360


def main():
    root = Path(__file__).resolve().parents[1]
    with tempfile.TemporaryDirectory(prefix="reference-tests-") as state:
        # Python children inherit this loopback-only guard; no inherited secret/proxy env.
        guard = Path(state) / "sitecustomize.py"
        guard.write_text((root / "scripts/test_network_guard.py").read_text())
        # Expose only the reviewed Compose executable to the isolated test HOME.
        # Docker configuration, credentials and the original HOME stay excluded.
        plugin = Path.home() / ".docker" / "cli-plugins" / "docker-compose"
        if shutil.which("docker") and plugin.is_file() and os.access(plugin, os.X_OK):
            isolated_plugin = Path(state) / ".docker" / "cli-plugins" / "docker-compose"
            isolated_plugin.parent.mkdir(parents=True)
            isolated_plugin.symlink_to(plugin.resolve())
        env = {k: os.environ[k] for k in ("PATH", "LANG", "LC_CTYPE") if k in os.environ}
        env.update(HOME=state, TMPDIR=state, PYTHONPATH=state, PYTHONDONTWRITEBYTECODE="1")
        try:
            return subprocess.run(
                [sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v", *sys.argv[1:]],
                cwd=root, env=env, timeout=TIMEOUT_SECONDS, check=False,
            ).returncode
        except subprocess.TimeoutExpired:
            print(f"FAIL: reference test timeout ({TIMEOUT_SECONDS}s); no PASS evidence", file=sys.stderr)
            return 124


if __name__ == "__main__":
    raise SystemExit(main())

"""Read-only reference health probe; no startup, install, DB or remote provider access."""

import argparse
import ipaddress
import json
import urllib.error
import urllib.request
from pathlib import Path

from health_scaffold import settings


def main():
    import os
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    # Probe the public host mapping, not the container listen port.
    profile = json.loads((root / "execution-profile.json").read_text())
    probe_profile = json.loads(json.dumps(profile))
    probe_profile["runtime"]["runtime_mode"] = "native"
    host, port, health = settings(root, os.environ, profile=probe_profile["runtime"])
    if host == "0.0.0.0":
        host = "127.0.0.1"
    if args.port is not None:
        port = args.port
    if not ipaddress.IPv4Address(host).is_loopback or not 1 <= port <= 65535:
        print("PENDING: reference probe requires explicit loopback endpoint")
        return 3
    # Ignore inherited proxy configuration; this is exclusively a local health check.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(f"http://{host}:{port}{health}", timeout=3) as response:
            if json.load(response) != {"status": "ok"}:
                raise ValueError("Unexpected health contract")
        print("HEALTH PASS (local reference only; no business/release acceptance)")
        return 0
    except (OSError, ValueError, urllib.error.URLError):
        print("PENDING: reference health unavailable; runtime was not started")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())

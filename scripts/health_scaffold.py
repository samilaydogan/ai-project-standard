"""Business-neutral, stateless native/container health reference; no resolver."""

import argparse
import ipaddress
import json
import os
import sys
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path


class Handler(BaseHTTPRequestHandler):
    health_path = "/health"

    def log_message(self, format, *args):
        # Do not log raw paths, headers, bodies, errors or caller-supplied request IDs.
        print(json.dumps({"event": "http_response", "request_id": getattr(self, "request_id", str(uuid.uuid4())),
                          "status": getattr(self, "response_status", None)}), file=sys.stderr)

    def send_response(self, code, message=None):
        self.response_status = code
        super().send_response(code, message)

    def do_GET(self):
        self.request_id = str(uuid.uuid4())
        if self.path != self.health_path:
            self.send_error(404)
            return
        body = b'{"status":"ok"}\n'
        self.send_response(200)
        self.send_header("X-Request-ID", self.request_id)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def settings(root, environ, profile=None):
    profile = profile or json.loads((root / "execution-profile.json").read_text())["runtime"]
    network = profile["network"]
    env = {}
    local = root / profile["environment"]["env_path"]
    if local.is_file() and not local.is_symlink():
        for line in local.read_text().splitlines():
            if line.strip() and not line.lstrip().startswith("#"):
                key, sep, value = line.partition("=")
                if not sep:
                    raise ValueError("Local env requires KEY=value; no shell expansion")
                env[key] = value
    env.update(environ)
    container = profile["runtime_mode"] == "docker"
    host_key = "APP_CONTAINER_LISTEN_HOST" if container else "APP_BIND_HOST"
    port_key = "APP_CONTAINER_PORT" if container else "APP_HOST_PORT"
    host_default = network["container_listen_host"] if container else network["bind_host"]
    port_default = network["container_port"] if container else network["host_port"]
    return env.get(host_key, host_default), int(env.get(port_key, port_default)), env.get(
        "APP_HEALTH_PATH", network["health_path"]
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--health-path")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    host, port, health_path = settings(root, os.environ)
    host = args.host if args.host is not None else host
    port = args.port if args.port is not None else port
    health_path = args.health_path if args.health_path is not None else health_path
    ipaddress.IPv4Address(host)
    if not 0 <= port <= 65535 or not health_path.startswith("/") or any(
        c in health_path for c in " ?#\n\r"
    ):
        raise ValueError("Invalid scaffold network configuration")
    Handler.health_path = health_path
    with HTTPServer((host, port), Handler) as server:
        print(f"Reference health: http://{host}:{server.server_port}{health_path}", flush=True)
        server.serve_forever()


if __name__ == "__main__":
    main()

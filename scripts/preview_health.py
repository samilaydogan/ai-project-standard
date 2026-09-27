"""Stateless reference preview: actual isolated loopback HTTP startup/health/stop."""
import importlib.util
import json
import os
import threading
import urllib.request
from http.server import HTTPServer
from pathlib import Path


def main():
    root = Path(__file__).resolve().parents[1]
    spec = importlib.util.spec_from_file_location('preview_reference_health', root / 'scripts/health_scaffold.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    result = {'nonce': os.environ['PREVIEW_NONCE'], 'startup': False, 'health': False, 'stop': False}
    with HTTPServer(('127.0.0.1', 0), module.Handler) as server:
        thread = threading.Thread(target=server.serve_forever, kwargs={'poll_interval': 0.01}, daemon=True)
        thread.start()
        result['startup'] = thread.is_alive()
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(f'http://127.0.0.1:{server.server_port}/health', timeout=3) as reply:
                result['health'] = reply.status == 200 and json.loads(reply.read(1024)) == {'status': 'ok'}
        finally:
            server.shutdown()
            thread.join(timeout=3)
            result['stop'] = not thread.is_alive()
    Path(os.environ['PREVIEW_RESULT_PATH']).write_text(json.dumps(result))
    return 0 if all(result[k] for k in ('startup', 'health', 'stop')) else 1


if __name__ == '__main__':
    raise SystemExit(main())

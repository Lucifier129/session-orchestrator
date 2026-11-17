#!/usr/bin/env python3
"""Send one native Codex queue request; read its JSON parameters from stdin."""

import argparse
import json
import os
import selectors
import subprocess
import sys
import time


OPERATIONS = ("add", "list", "update", "delete", "reorder")


def call(operation, params, timeout=30):
    if operation not in OPERATIONS:
        raise ValueError("Unsupported queue operation: " + operation)
    if not isinstance(params, dict):
        raise ValueError("stdin must contain a JSON object")
    method = "thread/queue/" + operation
    process = subprocess.Popen(
        ["codex", "app-server", "--stdio"],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE,
    )
    selector = selectors.DefaultSelector()
    pending = bytearray()

    def send(value):
        process.stdin.write((json.dumps(value) + "\n").encode("utf-8"))
        process.stdin.flush()

    def receive(request_id):
        deadline = time.monotonic() + timeout
        while True:
            while b"\n" in pending:
                line, _, rest = pending.partition(b"\n")
                pending[:] = rest
                if not line.strip():
                    continue
                response = json.loads(line)
                if response.get("id") == request_id:
                    return response
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not selector.select(remaining):
                raise TimeoutError("No response to " + method + "; inspect before retrying")
            chunk = os.read(process.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError("Codex app-server closed before answering " + method)
            pending.extend(chunk)

    try:
        selector.register(process.stdout, selectors.EVENT_READ)
        send({"id": 0, "method": "initialize", "params": {
            "clientInfo": {"name": "session_orchestrator", "version": "0.1.0"},
            "capabilities": {"experimentalApi": True},
        }})
        initialized = receive(0)
        if "error" in initialized:
            return initialized
        send({"method": "initialized", "params": {}})
        send({"id": 1, "method": method, "params": params})
        return receive(1)
    finally:
        selector.close()
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        process.stdin.close()
        process.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=OPERATIONS)
    parser.add_argument("--timeout", type=float, default=30, help="Response timeout in seconds")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    try:
        response = call(args.operation, json.load(sys.stdin), args.timeout)
    except (OSError, ValueError, RuntimeError, TimeoutError) as error:
        print("codex_queue: " + str(error), file=sys.stderr)
        return 1
    print(json.dumps(response, ensure_ascii=False))
    return 1 if "error" in response else 0


if __name__ == "__main__":
    sys.exit(main())

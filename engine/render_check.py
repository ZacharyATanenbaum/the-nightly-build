#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["websocket-client"]
# ///
"""Probe the PR's rendered article in headless Chrome for CI.

The file-level proof cannot see how a page renders, so validate runs this
after check.py: it loads the built article at phone width and asserts no
horizontal overflow, that the stylesheet attached (an unstyled page computes
the browser's fallback serif, which is how an invented body class shipped
unstyled once), and that the page threw no errors. A missing or unstartable
browser is a failed machine gate, not a publishable article.

Usage: python3 render_check.py --site <built-site-dir> --article
library/<series>/<slug>.html
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import websocket

VIEWPORT = 390
CHROME_CANDIDATES = (
    os.environ.get("CHROME_BIN"),
    "google-chrome",
    "chromium-browser",
    "chromium",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)


def find_chrome():
    for candidate in CHROME_CANDIDATES:
        if not candidate:
            continue
        found = shutil.which(candidate) or (
            candidate if os.path.isfile(candidate) else None
        )
        if found:
            return found
    return None


def free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_for_page_target(port, proc):
    for _ in range(75):
        if proc.poll() is not None:
            return None
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/json", timeout=1
            ) as resp:
                tabs = json.load(resp)
            for tab in tabs:
                if tab.get("type") == "page":
                    return tab
        except (
            urllib.error.URLError,
            ConnectionError,
            json.JSONDecodeError,
            OSError,
        ):
            pass
        time.sleep(0.2)
    return None


def stop_process(proc):
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def probe(chrome, page_path):
    port = free_port()
    env = os.environ.copy()
    no_proxy = [part for part in env.get("NO_PROXY", "").split(",") if part]
    for host in ("localhost", "127.0.0.1"):
        if host not in no_proxy:
            no_proxy.append(host)
    env["NO_PROXY"] = ",".join(no_proxy)
    env["no_proxy"] = env["NO_PROXY"]

    with tempfile.TemporaryDirectory(prefix="render-check-profile-") as profile:
        fd, log_path = tempfile.mkstemp(prefix="render-check-chrome-", suffix=".log")
        os.close(fd)
        log_handle = open(log_path, "w", encoding="utf-8")
        proc = subprocess.Popen(
            [
                chrome,
                "--headless",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-sandbox",
                "--no-first-run",
                "--no-default-browser-check",
                "--remote-debugging-address=127.0.0.1",
                f"--remote-debugging-port={port}",
                "--remote-allow-origins=*",
                f"--user-data-dir={profile}",
                "about:blank",
            ],
            stdout=log_handle,
            stderr=subprocess.STDOUT,
            env=env,
        )
        try:
            target = wait_for_page_target(port, proc)
            if target is None:
                stop_process(proc)
                log_handle.flush()
                details = Path(log_path).read_text(
                    encoding="utf-8", errors="replace"
                ).strip()
                if len(details) > 2000:
                    details = details[-2000:]
                exit_detail = f"exit code {proc.returncode}"
                if details:
                    exit_detail += f"; Chrome output: {details}"
                raise RuntimeError(exit_detail)

            ws = websocket.create_connection(
                target["webSocketDebuggerUrl"], timeout=30, http_proxy_host=None
            )
            msg_id = 0
            errors = []

            def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                ws.send(
                    json.dumps(
                        {"id": msg_id, "method": method, "params": params or {}}
                    )
                )
                while True:
                    resp = json.loads(ws.recv())
                    if resp.get("method") == "Runtime.exceptionThrown":
                        detail = resp["params"]["exceptionDetails"]
                        errors.append(detail.get("text", "exception"))
                    if resp.get("id") == msg_id:
                        return resp.get("result", {})

            send("Runtime.enable")
            send(
                "Emulation.setDeviceMetricsOverride",
                {
                    "width": VIEWPORT,
                    "height": 1200,
                    "deviceScaleFactor": 1,
                    "mobile": True,
                },
            )
            send("Page.navigate", {"url": "file://" + os.path.abspath(page_path)})
            # Poll until the file: document (not the about:blank Chrome started
            # on) finishes loading; a static local page takes tens of ms, and the
            # 5s cap only defers to the fact checks below, which fail loudly.
            for _ in range(100):
                loaded = send(
                    "Runtime.evaluate",
                    {
                        "expression": (
                            "location.protocol === 'file:' "
                            "&& document.readyState === 'complete'"
                        )
                    },
                )
                if loaded.get("result", {}).get("value"):
                    break
                time.sleep(0.05)
            result = send(
                "Runtime.evaluate",
                {
                    "expression": (
                        "JSON.stringify({"
                        "scrollWidth: document.documentElement.scrollWidth,"
                        "innerWidth: window.innerWidth,"
                        "bodyFont: getComputedStyle(document.body).fontFamily})"
                    )
                },
            )
            facts = json.loads(result["result"]["value"])
            facts["exceptions"] = errors
            ws.close()
            return facts
        finally:
            stop_process(proc)
            log_handle.close()
            try:
                os.unlink(log_path)
            except FileNotFoundError:
                pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--site", required=True, help="built site directory")
    ap.add_argument("--article", required=True, help="library/<series>/<slug>.html")
    args = ap.parse_args()

    page = os.path.join(args.site, args.article)
    if not os.path.isfile(page):
        print(f"render probe FAIL: no page at {page}")
        return 1
    chrome = find_chrome()
    if chrome is None:
        print("render probe FAIL: no Chrome executable in this environment")
        return 1
    try:
        facts = probe(chrome, page)
    except Exception as exc:
        print(f"render probe FAIL: Chrome did not start: {exc}")
        return 1

    failures = []
    # Mobile emulation grows the layout viewport to fit overflowing content,
    # so compare against the configured width, not window.innerWidth.
    if facts["scrollWidth"] > VIEWPORT + 2:
        failures.append(
            f"horizontal overflow: content is {facts['scrollWidth']}px wide "
            f"in a {VIEWPORT}px viewport"
        )
    if "times" in facts["bodyFont"].lower():
        failures.append(
            "stylesheet did not attach: body computed font is the browser "
            f"fallback ({facts['bodyFont']}); check the body class and asset links"
        )
    for error in facts["exceptions"]:
        failures.append(f"page error: {error}")

    if failures:
        for failure in failures:
            print(f"render probe FAIL: {failure}")
        return 1
    print(
        f"render probe ok: {VIEWPORT}px viewport, no overflow, "
        f"styles attached ({facts['bodyFont'].split(',')[0]}), no page errors"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
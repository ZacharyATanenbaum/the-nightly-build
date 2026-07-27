#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["websocket-client"]
# ///
"""Probe the PR's rendered article in headless Chrome for CI.

The file-level proof cannot see how a page renders, so validate runs this
after check.py: it serves the built site over loopback, loads the article at
phone width, and asserts that the intended page loaded, the article stylesheet
attached, the page has no horizontal overflow, and no runtime exception fired.
A missing or unstartable browser is a failed machine gate, not a publishable
article.

Usage: python3 render_check.py --site <built-site-dir> --article
library/<series>/<slug>.html
"""

import argparse
import contextlib
import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
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


def stop_process(proc):
    if proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait(timeout=5)


def wait_for_http(url, proc):
    for _ in range(50):
        if proc.poll() is not None:
            return False
        try:
            with urllib.request.urlopen(url, timeout=1) as response:
                return response.status == 200
        except (urllib.error.URLError, OSError):
            time.sleep(0.1)
    return False


@contextlib.contextmanager
def serve(site):
    port = free_port()
    root_url = f"http://127.0.0.1:{port}/"
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "http.server",
            str(port),
            "--bind",
            "127.0.0.1",
            "--directory",
            os.path.abspath(site),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        if not wait_for_http(root_url, proc):
            raise RuntimeError(f"local HTTP server did not start (exit {proc.poll()})")
        yield root_url
    finally:
        stop_process(proc)


def wait_for_page_target(port, proc):
    for _ in range(75):
        if proc.poll() is not None:
            return None
        try:
            with urllib.request.urlopen(
                f"http://127.0.0.1:{port}/json", timeout=1
            ) as response:
                tabs = json.load(response)
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


def probe(chrome, page_url):
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
        log_handle = Path(log_path).open("w", encoding="utf-8")
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
                detail = f"exit code {proc.returncode}"
                if details:
                    detail += f"; Chrome output: {details}"
                raise RuntimeError(detail)

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
                    response = json.loads(ws.recv())
                    if response.get("method") == "Runtime.exceptionThrown":
                        detail = response["params"]["exceptionDetails"]
                        errors.append(detail.get("text", "exception"))
                    if response.get("id") == msg_id:
                        return response.get("result", {})

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
            navigation = send("Page.navigate", {"url": page_url})
            if navigation.get("errorText"):
                raise RuntimeError(f"navigation failed: {navigation['errorText']}")

            loaded = False
            for _ in range(100):
                state = send(
                    "Runtime.evaluate",
                    {
                        "expression": (
                            "JSON.stringify({href: location.href, "
                            "ready: document.readyState})"
                        )
                    },
                )
                raw = state.get("result", {}).get("value")
                if raw:
                    current = json.loads(raw)
                    if current["href"] == page_url and current["ready"] == "complete":
                        loaded = True
                        break
                time.sleep(0.05)
            if not loaded:
                raise RuntimeError("article URL did not finish loading")

            result = send(
                "Runtime.evaluate",
                {
                    "expression": (
                        "(() => {"
                        "const body = getComputedStyle(document.body);"
                        "const readingEl = document.querySelector('article.nb-reading');"
                        "const titleEl = document.querySelector('h1.nb-title');"
                        "const reading = readingEl ? getComputedStyle(readingEl) : null;"
                        "const title = titleEl ? getComputedStyle(titleEl) : null;"
                        "return JSON.stringify({"
                        "hasViewport: !!document.querySelector('meta[name=viewport]'),"
                        "hasArticleClass: document.body.classList.contains('nb-article'),"
                        "hasReading: !!readingEl,"
                        "hasTitle: !!titleEl,"
                        "scrollWidth: document.documentElement.scrollWidth,"
                        "innerWidth: window.innerWidth,"
                        "bodyDisplay: body.display,"
                        "bodyMargin: body.margin,"
                        "bodyFont: body.fontFamily,"
                        "readingMaxWidth: reading ? reading.maxWidth : null,"
                        "readingPaddingLeft: reading ? reading.paddingLeft : null,"
                        "titleWeight: title ? title.fontWeight : null"
                        "});"
                        "})()"
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
            Path(log_path).unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True, help="built site directory")
    parser.add_argument(
        "--article", required=True, help="library/<series>/<slug>.html"
    )
    args = parser.parse_args()

    page = os.path.join(args.site, args.article)
    if not os.path.isfile(page):
        print(f"render probe FAIL: no page at {page}")
        return 1
    chrome = find_chrome()
    if chrome is None:
        print("render probe FAIL: no Chrome executable in this environment")
        return 1

    try:
        with serve(args.site) as root_url:
            page_url = urllib.parse.urljoin(root_url, urllib.parse.quote(args.article))
            facts = probe(chrome, page_url)
    except Exception as exc:
        print(f"render probe FAIL: browser probe could not run: {exc}")
        return 1

    failures = []
    if not facts["hasViewport"]:
        failures.append("missing viewport metadata")
    if (
        not facts["hasArticleClass"]
        or not facts["hasReading"]
        or not facts["hasTitle"]
    ):
        failures.append("required article chrome is missing")
    if facts["scrollWidth"] > VIEWPORT + 2:
        failures.append(
            f"horizontal overflow: content is {facts['scrollWidth']}px wide "
            f"in a {VIEWPORT}px viewport"
        )
    if facts["bodyDisplay"] != "flex" or facts["bodyMargin"] != "0px":
        failures.append(
            "stylesheet did not attach: expected body display flex and zero margin, "
            f"got display={facts['bodyDisplay']} margin={facts['bodyMargin']}"
        )
    if facts["readingMaxWidth"] != "800px" or facts["readingPaddingLeft"] != "20px":
        failures.append(
            "article stylesheet did not attach: expected .nb-reading max-width 800px "
            f"and 20px padding, got max-width={facts['readingMaxWidth']} "
            f"padding-left={facts['readingPaddingLeft']}"
        )
    if facts["titleWeight"] != "600":
        failures.append(
            "article title style did not attach: expected font-weight 600, "
            f"got {facts['titleWeight']}"
        )
    for error in facts["exceptions"]:
        failures.append(f"page error: {error}")

    if failures:
        for failure in failures:
            print(f"render probe FAIL: {failure}")
        return 1
    print(
        f"render probe ok: {VIEWPORT}px viewport, no overflow, "
        f"article styles attached ({facts['bodyFont'].split(',')[0]}), no page errors"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

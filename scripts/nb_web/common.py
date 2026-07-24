"""Shared primitives for the repository-native night shift."""

from __future__ import annotations

import datetime as dt
import email.utils
import html
import json
import os
import pathlib
import re
import subprocess
import urllib.parse
from typing import Any

import requests
from bs4 import BeautifulSoup

ROOT = pathlib.Path(__file__).resolve().parents[2]
WORK = ROOT / ".nb-web"
USER_AGENT = (
    "Mozilla/5.0 (compatible; NightlyBuild/1.0; "
    "+https://github.com/ZacharyATanenbaum/the-nightly-build)"
)
TIMEOUT = (10, 30)
MAX_DOWNLOAD = 4 * 1024 * 1024
CITATION_RE = re.compile(r"\[\[([A-Za-z0-9_-]+)\]\]")
SAFE_ID_RE = re.compile(r"[^a-z0-9-]+")

# Search and news aggregators never own the claims behind the links they carry.
# This check runs before a caller-provided hint so stale metadata cannot turn an
# aggregator URL into a primary source.
AGGREGATOR_HOSTS = frozenset(
    {
        "bing.com",
        "www.bing.com",
        "google.com",
        "www.google.com",
        "news.google.com",
    }
)

# Google spans several unrelated products and aggregators, so list its known
# owner-authored surfaces explicitly instead of treating every *.google.com URL
# as primary. The suffix list is reserved for organizations whose whole domain
# is an owner-authored surface in this paper's beats.
PRIMARY_EXACT_HOSTS = frozenset(
    {
        "about.google",
        "ai.google",
        "blog.google",
        "cloud.google.com",
        "developers.google.com",
        "developers.googleblog.com",
        "research.google",
        "security.googleblog.com",
    }
)
PRIMARY_HOST_SUFFIXES = (
    "openai.com",
    "anthropic.com",
    "deepmind.google",
    "microsoft.com",
    "meta.com",
    "ai.meta.com",
    "nvidia.com",
    "github.com",
    "github.blog",
    "arxiv.org",
    "doi.org",
    "sec.gov",
    "federalregister.gov",
    "whitehouse.gov",
    "congress.gov",
    "courtlistener.com",
    "justice.gov",
    "ftc.gov",
    "nist.gov",
    "europa.eu",
    "oecd.org",
)


def ensure_work() -> None:
    WORK.mkdir(parents=True, exist_ok=True)


def write_output(key: str, value: str) -> None:
    path = os.environ.get("GITHUB_OUTPUT")
    if not path:
        return
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(f"{key}={value}\n")


def run(*args: str, cwd: pathlib.Path | None = None, check: bool = True) -> str:
    done = subprocess.run(
        args,
        cwd=str(cwd or ROOT),
        text=True,
        capture_output=True,
        timeout=180,
    )
    if check and done.returncode != 0:
        raise RuntimeError(
            f"command failed ({done.returncode}): {' '.join(args)}\n"
            f"{done.stdout}\n{done.stderr}"
        )
    return done.stdout


def utc_now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def parse_date(value: Any) -> dt.datetime | None:
    if not value:
        return None
    text = str(value).strip()
    try:
        parsed = email.utils.parsedate_to_datetime(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except (TypeError, ValueError, OverflowError):
        pass
    try:
        parsed = dt.datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=dt.timezone.utc)
        return parsed.astimezone(dt.timezone.utc)
    except ValueError:
        return None


def strip_markup(value: str) -> str:
    soup = BeautifulSoup(value or "", "html.parser")
    return " ".join(soup.get_text(" ", strip=True).split())


def clean_title(value: str) -> str:
    text = strip_markup(value)
    return re.sub(r"\s+[|—-]\s+[^|—-]{1,40}$", "", text).strip()


def normalize_url(value: str) -> str | None:
    if not value:
        return None
    value = html.unescape(value.strip())
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    query = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
    query = [
        (key, item)
        for key, item in query
        if not key.lower().startswith("utm_")
        and key.lower() not in {"gclid", "fbclid", "mc_cid", "mc_eid"}
    ]
    return urllib.parse.urlunsplit(
        (
            parsed.scheme,
            parsed.netloc.lower(),
            parsed.path or "/",
            urllib.parse.urlencode(query),
            "",
        )
    )


def host_for(url: str) -> str:
    return (urllib.parse.urlsplit(url).hostname or "").lower()


def primary_hint(url: str, fallback: str | None = None) -> str:
    """Return a conservative ownership label for a source URL.

    A primary source owns the underlying claim. Search aggregators are always
    secondary even when a caller accidentally carries a primary hint forward.
    An explicit hint otherwise wins because official feeds know their publisher
    even when a page redirects through a CDN.
    """
    host = host_for(url)
    if host in AGGREGATOR_HOSTS:
        return "secondary"
    if fallback in {"primary", "secondary"}:
        return fallback
    if host in PRIMARY_EXACT_HOSTS:
        return "primary"
    if any(
        host == suffix or host.endswith(f".{suffix}")
        for suffix in PRIMARY_HOST_SUFFIXES
    ):
        return "primary"
    if host.endswith(".gov") or host.endswith(".edu"):
        return "primary"
    return "secondary"


def request(url: str, *, max_bytes: int = MAX_DOWNLOAD) -> requests.Response:
    response = requests.get(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.8"},
        timeout=TIMEOUT,
        allow_redirects=True,
        stream=True,
    )
    response.raise_for_status()
    chunks: list[bytes] = []
    size = 0
    for chunk in response.iter_content(64 * 1024):
        if not chunk:
            continue
        size += len(chunk)
        if size > max_bytes:
            raise ValueError(f"response exceeds {max_bytes} bytes")
        chunks.append(chunk)
    response._content = b"".join(chunks)
    response._content_consumed = True
    return response


def parse_action_json(path: pathlib.Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8").strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start < 0 or end <= start:
            raise ValueError(f"model response is not JSON: {raw[:500]}") from None
        value = json.loads(raw[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("model response must be a JSON object")
    return value


def slugify(value: str) -> str:
    value = SAFE_ID_RE.sub("-", value.lower()).strip("-")
    return value[:64].rstrip("-") or "nightly-read"

import contextlib
import pathlib
import sys
import urllib.request

import pytest

import render_check


GOOD_FACTS = {
    "hasViewport": True,
    "hasArticleClass": True,
    "hasReading": True,
    "hasTitle": True,
    "scrollWidth": render_check.VIEWPORT,
    "innerWidth": render_check.VIEWPORT,
    "bodyDisplay": "flex",
    "bodyMargin": "0px",
    "bodyFont": "Newsreader, Georgia, serif",
    "readingMaxWidth": "800px",
    "readingPaddingLeft": "20px",
    "titleWeight": "600",
    "exceptions": [],
}


def article_site(tmp_path: pathlib.Path) -> tuple[pathlib.Path, str]:
    site = tmp_path / "site"
    article = site / "library" / "the-one" / "test.html"
    article.parent.mkdir(parents=True)
    article.write_text("<!doctype html><title>test</title>")
    return site, "library/the-one/test.html"


def run_main(monkeypatch, tmp_path: pathlib.Path, facts: dict) -> int:
    site, article = article_site(tmp_path)

    @contextlib.contextmanager
    def fake_serve(_site):
        yield "http://127.0.0.1:8000/"

    monkeypatch.setattr(render_check, "find_chrome", lambda: "/bin/true")
    monkeypatch.setattr(render_check, "serve", fake_serve)
    monkeypatch.setattr(render_check, "probe", lambda _chrome, _url: facts)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "render_check.py",
            "--site",
            str(site),
            "--article",
            article,
        ],
    )
    return render_check.main()


def test_local_server_exposes_the_built_site(tmp_path: pathlib.Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("ok")

    with (
        render_check.serve(site) as root_url,
        urllib.request.urlopen(root_url, timeout=2) as response,
    ):
        assert response.status == 200
        assert response.read() == b"ok"


def test_valid_render_facts_pass(monkeypatch, tmp_path: pathlib.Path) -> None:
    assert run_main(monkeypatch, tmp_path, GOOD_FACTS.copy()) == 0


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"hasViewport": False}, "missing viewport metadata"),
        ({"hasArticleClass": False}, "required article chrome is missing"),
        ({"scrollWidth": 900}, "horizontal overflow"),
        ({"bodyDisplay": "block"}, "stylesheet did not attach"),
        ({"readingMaxWidth": "none"}, "article stylesheet did not attach"),
        ({"titleWeight": "700"}, "article title style did not attach"),
        ({"exceptions": ["boom"]}, "page error: boom"),
    ],
)
def test_render_findings_fail_closed(
    monkeypatch, tmp_path: pathlib.Path, capsys, change: dict, message: str
) -> None:
    facts = GOOD_FACTS.copy()
    facts.update(change)

    assert run_main(monkeypatch, tmp_path, facts) == 1
    assert message in capsys.readouterr().out


def test_browser_start_failure_fails_closed(
    monkeypatch, tmp_path: pathlib.Path, capsys
) -> None:
    site, article = article_site(tmp_path)

    @contextlib.contextmanager
    def fake_serve(_site):
        yield "http://127.0.0.1:8000/"

    def fail_probe(_chrome, _url):
        raise RuntimeError("did not start")

    monkeypatch.setattr(render_check, "find_chrome", lambda: "/bin/false")
    monkeypatch.setattr(render_check, "serve", fake_serve)
    monkeypatch.setattr(render_check, "probe", fail_probe)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "render_check.py",
            "--site",
            str(site),
            "--article",
            article,
        ],
    )

    assert render_check.main() == 1
    assert "browser probe could not run" in capsys.readouterr().out


def test_missing_browser_fails_closed(
    monkeypatch, tmp_path: pathlib.Path, capsys
) -> None:
    site, article = article_site(tmp_path)
    monkeypatch.setattr(render_check, "find_chrome", lambda: None)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "render_check.py",
            "--site",
            str(site),
            "--article",
            article,
        ],
    )

    assert render_check.main() == 1
    assert "no Chrome executable" in capsys.readouterr().out

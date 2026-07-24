from pathlib import Path

collect_path = Path("scripts/nb_web/collect.py")
collect = collect_path.read_text(encoding="utf-8")

import_marker = """    write_output,\n)\n\nFEEDS:"""
import_replacement = """    write_output,\n)\nfrom nb_web.cluster import build_commissioning_clusters\nfrom nb_web.research import search_bing, search_gdelt, search_google_news\n\nBROAD_QUERIES = (\n    \"artificial intelligence\",\n    \"AI model release\",\n    \"AI regulation software\",\n)\n\nFEEDS:"""
if import_marker not in collect:
    raise SystemExit("collect import marker not found")
collect = collect.replace(import_marker, import_replacement, 1)

start = collect.index("def prompt_candidates(")
end = collect.index("\n\ndef prepare(", start)
replacement = '''def collect_search(query: str) -> tuple[list[dict[str, Any]], str | None]:
    rows: list[dict[str, Any]] = []
    for search in (search_gdelt, search_bing, search_google_news):
        rows.extend(search(query))
    return rows, None


def prompt_candidates(ordered: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_commissioning_clusters(ordered)


'''
collect = collect[:start] + replacement + collect[end + 2 :]

future_marker = """        futures = [pool.submit(collect_feed, *feed) for feed in FEEDS]\n        for future in concurrent.futures.as_completed(futures):"""
future_replacement = """        futures = [pool.submit(collect_feed, *feed) for feed in FEEDS]\n        futures.extend(pool.submit(collect_search, query) for query in BROAD_QUERIES)\n        for future in concurrent.futures.as_completed(futures):"""
if future_marker not in collect:
    raise SystemExit("collect futures marker not found")
collect = collect.replace(future_marker, future_replacement, 1)

collect = collect.replace(
    "    recent = recent_library(library)\n",
    "    recent = recent_library(library)\n    commissioning = prompt_candidates(ordered)\n",
    1,
)
collect = collect.replace(
    "json.dumps(prompt_candidates(ordered), indent=2, ensure_ascii=False)",
    "json.dumps(commissioning, indent=2, ensure_ascii=False)",
    1,
)
collect = collect.replace(
    "    ready = len(ordered) >= 12 and primary >= 2 and secondary >= 4\n",
    "    ready = (\n        len(ordered) >= 12\n        and primary >= 2\n        and secondary >= 4\n        and bool(commissioning)\n    )\n",
    1,
)
collect = collect.replace(
    'f"collected {len(ordered)} candidates ({primary} primary, {secondary} secondary)",',
    'f"collected {len(ordered)} candidates ({primary} primary, {secondary} secondary) and {len(commissioning)} source-diverse clusters",',
    1,
)
collect_path.write_text(collect, encoding="utf-8")

cluster_path = Path("scripts/nb_web/cluster.py")
cluster = cluster_path.read_text(encoding="utf-8")
cluster = cluster.replace(
    "        document_frequency.update(counts)\n",
    "        document_frequency.update(counts.keys())\n",
    1,
)
cluster_path.write_text(cluster, encoding="utf-8")

Path(__file__).unlink()

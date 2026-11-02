#!/usr/bin/env python3
"""Check generated HTML under public/ for broken internal links and fragments."""

from __future__ import annotations

import html
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

SITE_HOSTS = {"vchord.pgsty.com", "www.vchord.pgsty.com"}
SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


class DocParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[tuple[str, str]] = []
        self.meta_refresh: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k.lower(): (v or "") for k, v in attrs}
        for key in ("id", "name"):
            val = attr.get(key)
            if val:
                self.ids.add(val)

        if tag in {"a", "link", "area"} and "href" in attr:
            self.links.append((tag, attr["href"]))
        elif tag in {"img", "script", "source", "iframe", "video", "audio"} and "src" in attr:
            self.links.append((tag, attr["src"]))
        elif tag == "meta" and attr.get("http-equiv", "").lower() == "refresh":
            content = attr.get("content", "")
            for part in content.split(";"):
                part = part.strip()
                if part.lower().startswith("url="):
                    self.meta_refresh = part[4:].strip().strip("'\"")


def resolve_path(public_root: Path, page_file: Path, raw_path: str) -> Path | None:
    path = unquote(html.unescape(raw_path))
    if not path:
        return page_file

    if path.startswith("/"):
        rel = path.lstrip("/")
        base = public_root / rel
    else:
        if page_file.name == "index.html":
            page_dir = page_file.parent
        else:
            page_dir = page_file.parent
        base = (page_dir / path).resolve()
        try:
            base.relative_to(public_root)
        except ValueError:
            return None

    if raw_path.endswith("/"):
        candidate = base / "index.html"
        return candidate if candidate.is_file() else None

    if base.is_file():
        return base

    index_candidate = base / "index.html"
    if index_candidate.is_file():
        return index_candidate

    html_candidate = base.with_suffix(".html")
    if html_candidate.is_file():
        return html_candidate

    return None


def main() -> int:
    public_root = Path(sys.argv[1] if len(sys.argv) > 1 else "public").resolve()
    if not public_root.is_dir():
        print(f"error: public root not found: {public_root}", file=sys.stderr)
        return 2

    html_files = sorted(public_root.rglob("*.html"))
    docs: dict[Path, DocParser] = {}
    for file in html_files:
        parser = DocParser()
        parser.feed(file.read_text(encoding="utf-8", errors="replace"))
        docs[file] = parser

    def effective_ids(target: Path, seen: set[Path] | None = None) -> set[str]:
        seen = seen or set()
        if target in seen or target not in docs:
            return set()
        seen.add(target)
        doc = docs[target]
        ids = set(doc.ids)
        if doc.meta_refresh:
            ref_parts = urlsplit(doc.meta_refresh)
            if not ref_parts.scheme or ref_parts.hostname in SITE_HOSTS:
                redirected = resolve_path(public_root, target, ref_parts.path)
                if redirected is not None:
                    ids |= effective_ids(redirected, seen)
        return ids

    missing_targets: list[tuple[Path, str, str]] = []
    missing_fragments: list[tuple[Path, str, Path, str]] = []

    for file, doc in docs.items():
        for tag, raw in doc.links:
            raw = raw.strip()
            if not raw or raw.startswith(SKIP_SCHEMES):
                continue

            parts = urlsplit(raw)
            if parts.scheme and parts.hostname not in SITE_HOSTS:
                continue

            target = resolve_path(public_root, file, parts.path)
            if target is None:
                missing_targets.append((file.relative_to(public_root), tag, raw))
                continue

            fragment = unquote(parts.fragment)
            if fragment and target.suffix == ".html":
                ids = effective_ids(target)
                if fragment not in ids and parts.fragment not in ids:
                    missing_fragments.append(
                        (
                            file.relative_to(public_root),
                            raw,
                            target.relative_to(public_root),
                            fragment,
                        )
                    )

    print(f"Scanned {len(html_files)} HTML files under {public_root}")
    print(f"Missing internal targets: {len(missing_targets)}")
    print(f"Missing HTML fragments:  {len(missing_fragments)}")

    for src, tag, href in missing_targets[:100]:
        print(f"TARGET   {src} <{tag}> -> {href}")
    for src, href, dst, frag in missing_fragments[:100]:
        print(f"FRAGMENT {src} -> {href} (missing #{frag} in {dst})")

    return 1 if (missing_targets or missing_fragments) else 0


if __name__ == "__main__":
    raise SystemExit(main())

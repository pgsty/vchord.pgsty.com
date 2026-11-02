# AGENTS.md — `vchord.pgsty.com`

## 1. Mission & Identity

This repository builds **`https://vchord.pgsty.com/`**, the documentation and blog website for **`pgsty/vchord`** (the Pigsty-maintained fork of **VectorChord**, scalable and disk-friendly vector search for PostgreSQL).

- **Framework**: Hugo Extended `0.168.0` + Go `1.27.3` + `github.com/pgsty/oink v1.4.0`
- **Upstream Docs Source**: `https://github.com/tensorchord/pgvecto.rs-docs` (`https://docs.vectorchord.ai/`)
- **Upstream Blog Source**: `https://blog.vectorchord.ai/`
- **Code Repository**: `https://github.com/pgsty/vchord`

---

## 2. Hard Rules

1. **Pure OINK 1.4.0**:
   - Rely on `github.com/pgsty/oink v1.4.0` layouts, shortcodes, and `data/home/en.yaml` sections. Do not copy or fork OINK templates into `layouts/` unless strictly necessary.
   - Always run Hugo with `GOWORK=off HUGO_MODULE_WORKSPACE=off`.
   - Never enable `--panicOnWarning` or `HUGO_PANICONWARNING`.

2. **Clean Git Tree**:
   - Never commit `public/`, `resources/`, `.hugo_build.lock`, `.venv-check/`, or temporary build directories.
   - Keep raw scrape/import artifacts in `/tmp/`, never inside the repository.

3. **Markdown & Component Conventions**:
   - **Callouts**: Use OINK GitHub-style blockquotes (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`, `> [!DETAILS] Title`), never VitePress `:::` fences.
   - **Math**: Goldmark passthrough is configured with `inline: [['\(', '\)']]` and `block: [['$$', '$$'], ['\[', '\]']]` so currency values (`$1`, `$250`) are never swallowed as math. Pages using math must set `math: true` in front matter.
   - **Headings**: Never put shortcodes (`{{< badge ... >}}`) inside Markdown headings.
   - **Provenance**: Pages adapted from upstream must carry `upstream_source` (or inherit it via `cascade`) and `upstream_link`.

4. **Verification Gate**:
   - Every change must pass `make check`:
     ```bash
     make check
     ```
   - `make check` runs `go mod verify`, `hugo build --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings`, and `python3 bin/check_internal_links.py public` (requiring 0 missing internal targets and 0 missing HTML fragments).

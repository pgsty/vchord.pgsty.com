# AGENTS.md — `vchord.pgsty.com`

## 1. Mission & Identity

This repository builds **`https://vchord.pgsty.com/`**, the documentation and blog website for **`pgsty/vchord`** (the Pigsty-maintained fork of **VectorChord**, scalable and disk-friendly vector search for PostgreSQL).

- **Framework**: Hugo Extended `0.168.0` + Go `1.27.3` + `github.com/pgsty/oink v1.6.0`
- **Upstream Docs Source**: `https://github.com/tensorchord/pgvecto.rs-docs` (`https://docs.vectorchord.ai/`)
- **Upstream BM25 & Tokenizer Sources**: `https://github.com/supervc-stack/VectorChord-bm25` and `https://github.com/supervc-stack/pg_tokenizer.rs`
- **Upstream Blog Source**: `https://blog.vectorchord.ai/`
- **Code Repositories**: `https://github.com/pgsty/vchord`, `https://github.com/pgsty/vchord_bm25`, and `https://github.com/pgsty/pg_tokenizer`

---

## 2. Hard Rules

1. **Pure OINK**:
   - Rely on the pinned `github.com/pgsty/oink` (see `go.mod`) layouts, shortcodes, and `data/home/en.yaml` sections. Do not copy or fork OINK templates into `layouts/` unless strictly necessary.
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

---

## 3. Writing the Docs

The docs have two readers: a person deciding whether this project is worth trusting, and an agent carrying out a task. Serve both by saying why before how, and by making every instruction executable as written.

1. **Page shape**:
   - Open with what the feature is, the problem it solves, and when to use it (or something else), in at most three sentences. Do not restate the title.
   - Then: the mechanism, only as far as the reader needs it to make decisions → a minimal working example → decisions and tuning → limits → reference.
   - Each product explains its query path once (for `vchordrq`: route → estimate → rerank). Tuning sections build on that explanation instead of listing knobs.

2. **What belongs in the docs**:
   - Describe the current release. Fixed bugs, version history, SQLSTATE codes, WAL and page internals, and toolchain versions belong in release notes. Name a version only where it changes what the reader does ("parallel builds need PostgreSQL 17+").
   - Unreleased work on `main` does not appear.
   - Apply the deletion test to every sentence: if it were gone, what would the reader do wrong? Delete sentences without an answer. Keep every condition and limit a real workload hits, stated once in a "Limits" or "Result order" section rather than in callouts throughout.
   - Approximation (recall, near-tie order, short results under selective filters, approximate sphere bounds) is explained once per product, with the SQL remedy, and linked from elsewhere.
   - Give decisions, not catalogues: the default, when to change it, and a tuning loop that ends by persisting the result.
   - Every number has a source: benchmark figures name the dataset and hardware and link to the run.
   - Legacy APIs live on one legacy or migration page, never beside the current workflow.

3. **Reference**:
   - Each setting, option, and function is defined in exactly one place, as a `{.fields meta="type default"}` table whose description says what the value trades off. Guides link to that entry.
   - When restructuring, keep anchors that other pages or the code repositories link to (add `<a id="...">` aliases) and keep old page URLs in `aliases`.

4. **Style**:
   - Plain, specific sentences. No marketing adjectives ("seamless", "powerful", "drastically"), no bold Title-Case lead-ins on every bullet, no `since vX` badges unless the reader needs the version.
   - Examples run in order and work on the documented release. Quote error messages verbatim so they can be searched.
   - Chinese pages are written as Chinese technical prose, not sentence-by-sentence translation. Paired pages share heading IDs, order, `weight`, and `aliases`.
   - Prefer native OINK forms: `{.steps}` for procedures, `{.fields}` for parameters. Use callouts only for something that loses data or breaks a deployment.
   - `content/docs/vchord/getting-started/overview.md` and `content/docs/vchord/usage/indexing.md` are the reference pages for tone and structure.

5. **Facts**: check behaviour against the code at the released tag of `pgsty/vchord`, `pgsty/vchord_bm25`, and `pgsty/pg_tokenizer` (their `docs/release-notes/`, SQL install scripts, GUC definitions, and tests), not against older docs.

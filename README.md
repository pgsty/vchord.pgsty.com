# vchord.pgsty.com

Source repository for **[vchord.pgsty.com](https://vchord.pgsty.com/)**, the documentation and engineering blog for the **Vchord** PostgreSQL extension suite — **[`vchord` `1.3.0` (`pgsty/vchord`)](https://github.com/pgsty/vchord)**, **[`vchord_bm25` `1.1.0` (`pgsty/vchord_bm25`)](https://github.com/pgsty/vchord_bm25)**, and **[`pg_tokenizer` `1.1.0` (`pgsty/pg_tokenizer`)](https://github.com/pgsty/pg_tokenizer)** — scalable vector and BM25 lexical search for PostgreSQL, maintained by [PGSTY](https://pigsty.io/).

Built with [Hugo Extended `0.168.0`](https://gohugo.io/) and the [OINK `v1.5.1`](https://github.com/pgsty/oink) documentation theme.

## Structure

| Path | Description |
| :--- | :--- |
| `content/docs/` | **Vchord Documentation Hub** (`/docs/`) indexing all six extensions |
| `content/docs/about/` | Licensing, SBOM, upstream attribution, and trademark policy (`/docs/about/`) |
| `content/docs/vchord/` | **`vchord` (`1.3.0`)** documentation (`getting-started`, `usage`, `use-case`, `benchmark`, `admin`, `customer-stories`) |
| `content/docs/bm25/` | **`vchord_bm25` (`1.1.0`)** documentation (`getting-started`, `usage`, `reference`) |
| `content/docs/tokenizer/` | **`pg_tokenizer` (`1.1.0`)** documentation (`installation`, `overview`, `text-analyzer`, `models`, `multilingual`, `reference`) |
| `content/docs/vector/` | **`pgvector` (`0.8.7`)** documentation (`getting-started`, `querying`, `indexing`, `quantization`, `reference`) |
| `content/docs/vectors/` | **`pgvecto.rs`** legacy documentation and migration reference |
| `content/docs/bestmatch/` | **`pg_bestmatch`** legacy documentation (`getting-started`, `usage`, `reference`) |
| `content/download.md` | **Download & Availability Matrix** (`/download/`), synced via `bin/sync_download.py` |
| `content/blog/` | **Vchord Blog** — release notes (`content/release/`) and deep-dive engineering articles (`content/blog/post/`) |
| `content/authors/` | **Blog Authors** — OINK 1.5.1 author taxonomy profiles and avatars |
| `data/home/en.yaml`, `data/home/zh.yaml` | OINK 1.5.1 declarative homepage composition |

## Local Development

`make sync-download` rewrites `content/download.md` and `content/download.zh.md` using the package tables in the sibling `pgext.cloud/content/e/` directory. Edit release-specific text in the script's page templates. Set `PGEXT_SITE_DIR` to use another catalog checkout, or pass the page directory to `python3 bin/sync_download.py --pgext-dir <directory>`.

```bash
# Start local development server at http://localhost:1313
make dev

# Production build and internal link / fragment verification
make check
```

## License

Site documentation is licensed under [CC-BY-4.0](LICENSE). Upstream attribution details are documented in [NOTICE.md](NOTICE.md) and `/docs/about/attribution/`.

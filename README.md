# vchord.pgsty.com

Source repository for **[vchord.pgsty.com](https://vchord.pgsty.com/)**, the documentation and engineering blog for the **Vchord** PostgreSQL extension suite — **[`vchord` (`pgsty/vchord`)](https://github.com/pgsty/vchord)**, **[`vchord_bm25` (`pgsty/vchord_bm25`)](https://github.com/pgsty/vchord_bm25)**, and **[`pg_tokenizer` (`pgsty/pg_tokenizer`)](https://github.com/pgsty/pg_tokenizer)** — scalable vector and BM25 lexical search for PostgreSQL, maintained by [PGSTY](https://pigsty.io/).

Built with [Hugo Extended `0.168.0`](https://gohugo.io/) and the [OINK `v1.4.0`](https://github.com/pgsty/oink) documentation theme.

## Structure

| Path | Description |
| :--- | :--- |
| `content/docs/` | **`vchord`** documentation (`getting-started`, `usage`, `use-case`, `benchmark`, `admin`, `customer-stories`) |
| `content/bm25/` | **`vchord_bm25` & `pg_tokenizer`** documentation (`getting-started`, `usage`, `tokenizer`, `reference`) |
| `content/cloud/` | **Cloud Archive** — reference guides for managed cluster architecture |
| `content/pgvecto-rs/` | **`pgvecto.rs`** legacy documentation and migration reference |
| `content/blog/` | **Vchord Blog** — release notes (`content/blog/release/`) and deep-dive engineering articles (`content/blog/post/`) |
| `content/about/` | Licensing, upstream attribution, and trademark policy |
| `data/home/en.yaml`, `data/home/zh.yaml` | OINK 1.4.0 declarative homepage composition |

## Local Development

```bash
# Start local development server at http://localhost:1313
make dev

# Production build and internal link / fragment verification
make check
```

## License

Site documentation is licensed under [CC-BY-4.0](LICENSE). Upstream attribution details are documented in [NOTICE.md](NOTICE.md) and `/about/attribution/`.

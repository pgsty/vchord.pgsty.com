# vchord.pgsty.com

Source repository for **[vchord.pgsty.com](https://vchord.pgsty.com/)**, the documentation and engineering blog for **[VectorChord (`pgsty/vchord`)](https://github.com/pgsty/vchord)** — scalable, fast, and disk-friendly vector similarity search for PostgreSQL, maintained by the [Pigsty](https://pigsty.io/) community.

Built with [Hugo Extended `0.168.0`](https://gohugo.io/) and the [OINK `v1.4.0`](https://github.com/pgsty/oink) documentation theme.

## Structure

| Path | Description |
| :--- | :--- |
| `content/docs/` | **VectorChord** documentation (`getting-started`, `usage`, `use-case`, `benchmark`, `admin`, `customer-stories`) |
| `content/cloud/` | **VectorChord Cloud** guides, cluster management, monitoring, and billing reference |
| `content/pgvecto-rs/` | **pgvecto.rs** legacy documentation and migration reference |
| `content/blog/` | **VectorChord Blog** — release notes (`content/blog/release/`) and deep-dive engineering articles (`content/blog/post/`) |
| `content/about/` | Licensing, upstream attribution, and trademark policy |
| `data/home/en.yaml` | OINK 1.4.0 declarative homepage composition |

## Local Development

```bash
# Start local development server at http://localhost:1313
make dev

# Production build and internal link / fragment verification
make check
```

## License

Site documentation is licensed under [CC-BY-4.0](LICENSE). Upstream attribution details are documented in [NOTICE.md](NOTICE.md) and `/about/attribution/`.

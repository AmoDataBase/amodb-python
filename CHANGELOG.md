# Changelog

All notable changes to this project are listed here. Versions follow semantic versioning.

## 0.1.0 - 2026-10-18

Initial release.

- Sync `Client` and async `AsyncClient` built on httpx.
- TMDB v3 read endpoints, amodb extras, OMDb compatible endpoint, plans and image helpers.
- Retry on HTTP 429 with `Retry-After`, typed errors, typed response dictionaries.

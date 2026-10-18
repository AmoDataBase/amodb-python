# Changelog

All notable changes to this project are listed here. Versions follow semantic versioning.

## Unreleased

Align extension types with the live API.

- `amodb.types` has real typed shapes for `Moods`, `Soundtracks`, `Ratings`, `Wikidata` and `Showtimes`, plus `MoodsSection`, `SoundtracksSection` and `RatingsSection` for the forms inside `append_to_response`, which have no `id`.
- Moods use `source` (`measured`, `estimated` or `None`) and `results` of `{name, avg, values}` on a 0 to 10 scale.
- Ratings use `{value, votes}` or `None` per provider. Wikidata money fields use `value`.
- Showtimes work without a country and return per country counts in `countries`. With a country, `results` lists venues with their `showtimes`.
- `ExternalSource` now lists all 12 `external_source` values, including `kinopoisk_id`, and moved to `amodb.types`. `find` results are typed with `media_type`.
- Added `MovieExternalIds`, `TvExternalIds` and `PersonExternalIds`, and a `kinopoisk_id` string in movie and TV external ids.
- Fixed `TvDetails` and `MovieDetails` fields: removed `type` from TV, added `origin_country`, `networks`, `production_companies` and other served fields.
- Removed `tv.aggregate_credits`. The API answers 404 for that path.
- Added `movies.latest`, `movies.lists`, `tv.latest`, `tv.lists`, `tv.episode_groups`, `tv.translations`, `tv.alternative_titles`, `tv.showtimes` and `keywords.movies`.
- README examples use the real field names and list the paths that are not offered.

## 0.1.0 - 2026-10-18

Initial release.

- Sync `Client` and async `AsyncClient` built on httpx.
- TMDB v3 read endpoints, amodb extras, OMDb compatible endpoint, plans and image helpers.
- Retry on HTTP 429 with `Retry-After`, typed errors, typed response dictionaries.

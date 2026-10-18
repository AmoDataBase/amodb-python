# Contributing

Thanks for helping. Keep changes small and focused.

1. Open an issue first for anything larger than a bug fix or a doc fix.
2. Fork the repository and create a branch from `main`.
3. Run the checks before you open a pull request:

```sh
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest
ruff check .
mypy
```

4. Add or update tests for the behavior you change.
5. Write commit messages in the imperative mood, one short line, no trailing period.

Text in docs and comments: short, concrete sentences, sentence case headings, no long dashes.

Never commit API keys. Use environment variables and `.env` files that are ignored by git.

## Releasing

For maintainers.

1. Update `CHANGELOG.md` and set the new version in `src/amodb/_version.py`.
2. Commit, then tag the commit and push the tag: `git tag v0.2.0 && git push origin v0.2.0`.
3. The Release workflow checks that the tag matches the version, builds the package, publishes it to PyPI and creates the GitHub release.

PyPI uses trusted publishing, so no token is stored. One time setup:

1. On PyPI add a trusted publisher for the project `amodb` with owner `amodb-dev`, repository `amodb-python`, workflow `release.yml` and environment `pypi`.
2. In the repository settings create an environment named `pypi`.

By contributing you agree that your work is released under the MIT license of this repository.

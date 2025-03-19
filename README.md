# AudioIntel: Local interactive intelligent agent

These docs are a work in progress.

## Quickstart
To ask questions that can be answered by Wikipedia, first install [uv](https://docs.astral.sh/uv/) (`brew install uv` if on a Mac).  Then run:

```
$> git clone https://github.com/bmuller/audiointel.git
$> cd audiointel
$> uv sync --dev --all-extras
$> uv run python examples/wikipedia_agent.py
```

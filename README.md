# AudioIntel: Local interactive intelligent agent

These docs are a work in progress.

## Quickstart
To ask questions that can be answered by Wikipedia, first install [uv](https://docs.astral.sh/uv/) and [ollama](https://ollama.com) (`brew install uv ollama` if on a Mac).  Then, make sure `ollama` is running (you can run `ollama serve` in another terminal session if you don't have the service running by default).

Then, run:

```shell
$> ollama pull mistral
$> git clone https://github.com/bmuller/audiointel.git
$> cd audiointel
$> uv sync --dev --all-extras
$> uv run python examples/wikipedia_agent.py
```

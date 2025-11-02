## Quick context

This repository contains small, independent components rather than a monolithic app:

- `main.py` (root): a small FastAPI service that writes/reads phrase data to a Notion database. It expects `NOTION_TOKEN` and `NOTION_DATABASE_ID` as environment variables. Uses `requests`, `pydantic`, and `fastapi`.
- `VideoSorter/main.py`: a standalone script that extracts audio from videos, uses OpenAI Whisper to transcribe, uses GPT (chat completion) to classify the transcript into categories, then moves files into `sorted/<category>/`. It expects `OPENAI_API_KEY` in the environment or in a `.env` loaded by `python-dotenv`.

If you need to change behavior, modify the file closest to the behavior. There are no web frameworks sharing state across these components.

## Contracts (short)

- Root `main.py` (API): Inputs: JSON payloads matching `Phrase` (normalphrase, slangphrase, accent). Outputs: JSON status or a list of `Phrase` objects. Error mode: propagates Notion HTTP errors as FastAPI HTTPExceptions.
- `VideoSorter/main.py`: Inputs: files under `VIDEO_DIR` (default is a Windows path at top of file) and `OPENAI_API_KEY`. Output: videos moved under `sorted/<category>/`. Error mode: prints exceptions and continues.

## Important patterns & examples (copyable)

- Run the FastAPI app locally (from repo root):

  - Use uvicorn: `uvicorn main:app --reload --host 0.0.0.0 --port 8000`
  - Required env vars: `NOTION_TOKEN`, `NOTION_DATABASE_ID`.

- Run the VideoSorter script:

  - Ensure OpenAI key is available: either set `OPENAI_API_KEY` in environment or create a `.env` file at repo root and use the existing dotenv loading.
  - Execute: `python VideoSorter/main.py`

- Example relevant lines:
  - Notion write in `main.py`: `requests.post("https://api.notion.com/v1/pages", headers=HEADERS, json=notion_payload)`
  - Whisper transcribe call in `VideoSorter/main.py`: `openai.Audio.transcribe("whisper-1", audio_file)`
  - GPT classification: `openai.ChatCompletion.create(model="gpt-4", messages=[...])` (function `classify_transcript`)

## Environment & dependencies

- Root `requirements.txt` currently lists: `fastapi`, `uvicorn`, `requests`.
- VideoSorter has additional runtime requirements not included in `requirements.txt`: `openai`, `moviepy`, `python-dotenv`. If you run VideoSorter, install these with `pip install openai moviepy python-dotenv` or update `requirements.txt`.

## Project-specific conventions and gotchas

- VideoSorter uses an absolute Windows `VIDEO_DIR` default (line near top of `VideoSorter/main.py`). Update that constant before running on another machine, or set it via environment and refactor to read it.
- The Notion integration reads `NOTION_*` env vars directly; there is no `.env` loader in the root `main.py`. Set those in your shell/CI.
- Error handling is minimal: both components print and continue on transient failures. If you change to raise on errors, consider adding structured logging.
- There are no unit tests in the repo. Small scripts mean quick manual runs are the main validation path.

## Integration points

- External services used:
  - Notion REST API (v1) from root `main.py`.
  - OpenAI APIs (Whisper + ChatCompletion) from `VideoSorter/main.py`.

## What to look for when editing

- If you add new runtime libraries, update `requirements.txt` and document any system-level requirements (e.g., ffmpeg for `moviepy`).
- Prefer making credential usage consistent: either (A) load via `.env` everywhere or (B) require explicit environment variables. Right now, the repo mixes both approaches.

## Helpful next tasks (for contributors)

- Add `openai`, `moviepy`, and `python-dotenv` to `requirements.txt`.
- Move `VIDEO_DIR` to be configurable via env var (e.g., `VIDEO_DIR = os.getenv('VIDEO_DIR', '<default>')`).
- Add a short CI job that lints Python and checks `pip install -r requirements.txt`.

---

If any of these points are incomplete or you want me to expand examples (run commands, small refactors, or add the missing entries to `requirements.txt`), tell me which item to do next and I will update the repo accordingly.

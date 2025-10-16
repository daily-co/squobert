# Repository Guidelines

## Project Structure & Module Organization
Active code lives in three peers: `bot/` (Pipecat agent with processors in `bot/processors/`), `client/` (Next.js UI under `client/src/app` with assets in `public/`), and `squobertos/` (Textual TUI plus `install.sh`). Legacy UI sits in `client-old/`, while reference assets are in `photos/`, `parts/`, and `squobertos/assets/`. Boot helpers such as `startup.sh` launch the deployed face.

Reference https://docs.pipecat.ai for more information about the Pipecat framework. Also check https://github.com/pipecat-ai/pipecat or ../pipecat for the Pipecat source code if you need to research specific Pipecat behavior.

## Build, Test, and Development Commands
- `cd bot && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python bot.py -t daily` boots the local Daily transport loop.
- `cd bot && ./build.sh && pcc deploy` packages and deploys to Pipecat Cloud; tweak `bot/pcc-deploy.toml` as needed.
- `cd client && npm install && npm run dev` starts the UI; use `npm run build` for production bundles and `npm run lint` for checks.
- `cd squobertos && uv sync && uv run python squobertos.py` mirrors the kiosk experience without rebooting.

## Coding Style & Naming Conventions
Python code uses four-space indents, snake_case files, and grouped imports (`bot/bot.py` is the model). Keep processors small and async-friendly, and load secrets via `dotenv`. The UI follows Next.js ESLint defaults with two-space indents, single quotes, and PascalCase components; Tailwind utility classes control layout. Update `client/src/config.ts` when adding transports.

## Testing Guidelines
There is no automated suite yet, so run each surface before pushing: `python bot.py -t daily` for pipeline sanity, `npm run dev` plus browser smoke tests for the face, and `uv run python squobertos.py` for the TUI. New features should ship with lightweight checks (for example, a `tests/` module or recorded test script) and document manual steps in the PR. Treat `npm run lint` as mandatory.

## Commit & Pull Request Guidelines
Commits are short, present-tense summaries (e.g. `local cam detection in botfile`) that scope to one feature or bug. PRs should outline intent, call out environment changes (`bot/env.example`, `client/env.example`), and add screenshots or clips when UI or hardware behavior changes. Mention any deployment or hardware setup required for reviewers.

## Configuration & Secrets
Duplicate `.env.example` files before local runs. The bot needs Deepgram, Cartesia, Daily, and Google keys; the UI requires `BOT_START_URL` plus `BOT_START_PUBLIC_API_KEY`. Store secrets outside git and rely on GitHub Actions secrets when updating the cloud deployment workflow.

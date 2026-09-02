# 01 — Bootstrap the Reproducible Development Environment

**What to build:** A developer can configure the project, install locked Python dependencies with uv and JavaScript dependencies with pnpm, start the web application, API, PostgreSQL, Ollama, and MLflow locally or through Docker Compose, and run local quality checks before a normal push.

**Blocked by:** None — can start immediately.

**Status:** complete

- [x] A fresh workspace can be configured from documented environment variables and started in local and Docker Compose modes.
- [x] Python dependencies use uv and a committed lockfile; JavaScript dependencies use pnpm and `pnpm-lock.yaml`; local hooks block formatter, linter, and type-check failures.

## Comments

- Bootstrapped the Git monorepo, hybrid local runtime, full Docker Compose runtime, locked uv and pnpm dependencies, and tracked Git quality hook.

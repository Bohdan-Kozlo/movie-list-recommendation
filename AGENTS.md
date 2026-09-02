## Agent skills

### Issue tracker

Issues are tracked as local Markdown files under `.scratch/`. See `docs/agents/issue-tracker.md`.

### Triage labels

The repository uses the five default triage labels. See `docs/agents/triage-labels.md`.

### Domain docs

This is a single-context repository. See `docs/agents/domain.md`.

## Working instructions

### Read requirements first

Before planning, implementing, reviewing, or changing the project, review every file in `docs/` for project context. Then read the applicable local ticket in `.scratch/`, `CONTEXT.md` when it exists, and any relevant ADRs in `docs/adr/`.

### Do not invent requirements

Do not hallucinate product requirements, business rules, data sources, API behavior, library behavior, or implementation decisions. When a requirement is unclear, incomplete, or conflicts with another source, ask the user for clarification before proceeding. The user's latest explicit instruction takes precedence over older project documentation.

### Dependency approval

Do not add a new production or development library, package, SDK, framework, or external service without first explaining why it is needed and receiving explicit user approval. Existing approved dependencies may be used according to `docs/LIBRARIES.md`.

### Code quality

Write code that is simple, concise, and readable for a developer. Prefer clear names, small focused modules, straightforward control flow, and explicit behavior over clever abstractions or premature generalization. Keep comments for non-obvious reasoning rather than restating code.

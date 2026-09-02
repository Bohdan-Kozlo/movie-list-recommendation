# Domain Docs

## Layout

This is a single-context repository.

- `CONTEXT.md` at the repository root is the domain glossary when it exists.
- `docs/adr/` contains architecture decision records when they exist.

## Consumer Rules

Before exploring or changing an area, engineering skills should read the root `CONTEXT.md` and any relevant ADRs in `docs/adr/`.

If either location does not exist yet, continue silently. Do not create glossary entries or ADRs merely because they are absent; create them when a domain term or architectural decision is actually resolved.

Use glossary terminology in ticket titles, specifications, tests, and architecture discussions. If a proposed change conflicts with an ADR, surface that conflict explicitly instead of silently overriding it.

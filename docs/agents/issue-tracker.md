# Issue tracker: Local Markdown

Issues for this repository live as Markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`.
- Implementation tickets are one file per issue at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`.
- A ticket declares its state in a `Status:` line and its dependencies in a `Blocked by:` line.
- Comments and conversation history append under a `## Comments` heading.
- The current product specification is maintained in `docs/SPEC.md`.

## When a skill publishes to the issue tracker

Create a feature directory under `.scratch/` and place one Markdown file per implementation ticket in its `issues/` directory.

## When a skill fetches a ticket

Read the referenced Markdown file. The user normally provides its path or ticket number.

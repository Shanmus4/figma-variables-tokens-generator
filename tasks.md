# Task Tracking

## Completed
- Set up `figma-skills-creator` repository.
- Rename folders to `kebab-case`.
- Add Apache 2.0 license.
- Enforce strict `.zip` output.
- Fix dropdown UI bug for Turn 2 in `SKILL-A.md`.
- Implement Phased Generation strategy in `SKILL-B.md` to prevent Claude timeouts during massive JSON generation.
- Refine Scoping Instructions in `SKILL-C.md` and architecture references to handle Figma JSON import bug.
- Create global rule compliant `README.md` and `tasks.md`.

## In Progress
- Final rule verification round.

## Backlog
- None at this time.

## Blockers / Known Issues
- **Figma JSON Import Bug:** Figma does not recognize "empty scope" arrays in JSON. It defaults them to "All Scopes". The current workaround is a mandatory manual de-scoping step for end-users, documented in `SKILL-C.md`.

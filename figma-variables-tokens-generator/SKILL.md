---
name: figma-variables-tokens-generator
description: >
  Create production-grade Figma Variables JSON ZIP files for any design system.
  Triggered when user asks to create Figma variables, design tokens, a design system,
  or token ZIP files. Also triggered for "build a design system", "create tokens",
  "Figma token export", "variables for Figma", or any request to set up colours/spacing/
  typography as Figma variables. Asks a guided questionnaire first using continuous
  dropdown batches — no filler responses between turns. Generates all ZIP files with
  zero import errors, guaranteed ID stability across modes, automated backfilling,
  and clean naming. Loads reference files progressively across four load stages — never
  all at once.
---

# Figma Variables Tokens Generator

Generate production-ready Figma Variables JSON ZIPs that import with zero errors.
Approach each system as both senior product designer and senior frontend engineer.
Enforce ID stability across modes and absolute path normalization throughout.

**Output format:** Deliver only `.zip` files containing the JSON tokens. Do not output `.skill` files or dump raw Python scripts — users expect ready-to-import ZIPs, not code, and dumping scripts into the chat causes context truncation that breaks the generation.

## Read Order — STAGED LOADING

To prevent context pollution, read only the files required for your current load stage:

### Load Stage 1: Discovery & Strategy (Read at Turn 1)
| # | File | Purpose |
|---|------|---------|
| 1 | `instructions/01-interview-setup.md` | Initial setup & Turns 1–3 |
| 2 | `instructions/02-questionnaire-and-generation.md` | Questionnaire Turns 4–10, generation |
| 3 | `references/01-architecture.md` | **Mandatory Strategy:** Understanding layering and alias rules. |

### Load Stage 2: Architecture Confirmation (Read before Phase 2)
| # | File | Purpose |
|---|------|---------|
| 4 | `references/05a-collections-core.md` | Design specs for Core collections |
| 5 | `references/05b-collections-semantic-components.md` | Design specs for Semantic/Component collections |

### Load Stage 3: Generation Logic (Read before Phase 3)
| # | File | Purpose |
|---|------|---------|
| 6 | `references/02-scoping-rules.md` | Technical scoping tables |
| 7 | `references/03-json-format.md` | Exact W3C JSON structure |
| 8 | `references/04-primitives.md` | Raw hex/spacing/font data |
| 9 | `references/06-generator-utility.md` | Python generation script patterns |
| 10 | `scripts/generator_core.py` | Executable Python engine (for local/IDE environments) |

### Load Stage 4: Delivery & Handoff (Read after ZIP delivery and token count reporting are complete)
| # | File | Purpose |
|---|------|---------|
| 11| `instructions/03-import-and-handoff.md` | Import guide & ZIP reference table |

> Do not read Load Stage 3 implementation files (scoping rules, JSON format, generator utility) until the interview is 100% complete. Reading them early fills context with technical data that is not needed yet.

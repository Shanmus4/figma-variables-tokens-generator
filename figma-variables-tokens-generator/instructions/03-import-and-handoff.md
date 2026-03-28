# Figma Variables — Handoff

### 🏁 READ LOAD STAGE 4: Delivery & Handoff
Read this file ONLY after Generation (Turn C) and Token Count Reporting (Turn D) are complete.

## PHASE 4 — IMPORT INSTRUCTIONS

Tell the user:
> "Use the **Figma Variables Importer plugin** to import your ZIP. The plugin reads the numbered folder structure and imports collections in the correct dependency order automatically."

> [!IMPORTANT]
> **For the AI:** The ZIP's numbered folder prefixes (e.g. `1. Primitives/`, `2. Theme/`) are critical — the plugin uses them to determine import order. Always generate folders with correct numbering as shown in the ZIP Structure Reference below.

---

## PHASE 5 — FOLLOW UP

Ask: "Anything you'd like to change, add, or adjust?"

---

## ZIP Structure Reference

| Folder (inside Master ZIP) | Figma collection name | Mode file(s) |
|---|---|---|
| `1. Primitives/` | `Primitives` | `primitives.tokens.json` |
| `2. Theme/` | `Theme` | `light.tokens.json`, `dark.tokens.json` |
| `3. Responsive/` | `Responsive` | `mobile.tokens.json`, `tablet.tokens.json`, `desktop.tokens.json` |
| `4. Density/` | `Density` | `compact.tokens.json`, `comfortable.tokens.json`, `spacious.tokens.json` |
| `5. Layout/` | `Layout` | `xs.tokens.json` … `xxl.tokens.json` |
| `6. Effects/` | `Effects` | `effects.tokens.json` |
| `7. Typography/` | `Typography` | `typography.tokens.json` |
| `8. Semantic/` | `Semantic` | `semantic.tokens.json` |
| `9. Component Colors/` | `Component Colors` | `component-colors.tokens.json` |
| `10. Component Dimensions/` | `Component Dimensions` | `component-dimensions.tokens.json` |

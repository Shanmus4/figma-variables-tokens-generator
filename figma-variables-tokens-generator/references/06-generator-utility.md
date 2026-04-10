# Generator Utility — Smart SDK Reference

The `generator_core.py` file is a **Smart SDK** for generating Figma-compatible design token JSON. It provides three layers of API:

| Layer | API | When to Use |
|---|---|---|
| **Layer 3** | `build_*()` methods | Standard collections — zero manual wiring |
| **Layer 2** | `make_family()`, `prebuild_ids()` | Pattern helpers for custom scales |
| **Layer 1** | `create_token()` | Full flexibility for custom/unusual tokens |

> [!IMPORTANT]
> **Use Layer 3 builders for all standard collections.** Only drop to Layer 1 for custom collections or tokens that don't fit any standard pattern.

---

## Quick Start — Complete 3-Tier System in ~40 Lines

```python
from generator_core import DesignTokenGenerator

AZURE = [
    ("50","#F0F5FF"),("100","#D6E4FF"),("200","#ADC8FF"),("300","#84A9FF"),
    ("400","#6690FF"),("500","#3B82F6"),("600","#2563EB"),("700","#1D4ED8"),
    ("800","#1E40AF"),("900","#1E3A8A"),("950","#172554"),
]

gen = DesignTokenGenerator("BrandName", tier=3, syntax_format="css", platforms=["WEB"])

# 1. Primitives — brand colors + grey preset + all scales
gen.build_primitives(
    brand_colors={"azure": AZURE},
    grey_family="slate",                           # preset: slate/gray/stone/zinc/neutral
    font_families={"sans": "Inter", "serif": "Playfair Display", "mono": "JetBrains Mono"},
)

# 2. Semantic — auto light/dark with shade inversion
gen.build_semantic(brand="azure", grey="slate")

# 3-9. Remaining collections
gen.build_responsive()
gen.build_density()
gen.build_layout()
gen.build_effects()
gen.build_typography(body_font="sans", display_font="sans", mono_font="mono")
gen.build_component_colors(components=["button", "input", "card", "modal", "dropdown"])
gen.build_component_dimensions()

# Verify + build
gen.verify_all_aliases()
gen.build_zip(output_dir="exports", filename="design-tokens")
```

> **This is the entire script.** No manual scope assignment, no hiddenFromPublishing flags, no alias wiring, no ID pre-building for standard collections.

---

## Initialization

```python
gen = DesignTokenGenerator(
    brand_name="BrandName",    # Used in metadata
    tier=3,                    # 2, 3, or 4 — determines chain topology
    syntax_format="css",       # "css" (--var-name) | "camel" (varName)
    platforms=["WEB"],         # ["WEB"] | ["WEB","ANDROID","iOS"]
)
```

---

## Layer 3: Collection Builders

### `build_primitives(brand_colors, grey_family, ...)`

Generates the entire Primitives collection: color families (brand + grey + feedback), white/black alphas, spacing, sizes, radius, border width, blur, shadow geometry, z-index, font tokens, and layout primitives.

| Parameter | Type | Description |
|---|---|---|
| `brand_colors` | `dict` | `{"family": [(shade, hex), ...]}` — Brand color families |
| `grey_family` | `str` or `list` | Preset name (`"slate"`, `"gray"`, `"stone"`, `"zinc"`, `"neutral"`) or custom `[(shade, hex), ...]` |
| `font_families` | `dict` | `{"sans": "Inter", "serif": "Playfair", "mono": "JetBrains Mono"}` |
| `extra_spacing` | `list` | Additional spacing values to merge with defaults |
| `extra_font_sizes` | `list` | Additional font sizes to merge with defaults |
| `extra_line_heights` | `list` | Additional line heights to merge with defaults |

**Auto-generated scales:**
- **11 shades** per color family (50-950) + 9 alpha variants
- **22 spacing** values: 0, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32, 36, 40, 48, 56, 64, 80, 96, 128, 160
- **25 font sizes**: 8-72
- **8 radius**: none, xs, sm, md, lg, xl, 2xl, full
- **6 border widths**: hairline, thin, soft, sm, md, lg
- **6 blur levels**: none, sm, md, lg, xl, 2xl
- **4 shadow scales**: sm, md, lg, xl (x, y, blur, spread each)
- **7 z-index levels**: base, raised, dropdown, sticky, modal, toast, tooltip
- **6 layout breakpoints**: xs-xxl (columns, margin, gutter, minWidth, maxWidth)

### `build_semantic(brand, grey, extra_tokens=None)`

Generates the Semantic collection with ~94 tokens across: surface (12), text (15), border (11), interactive (24), feedback (16), icon (9), overlay (3), shadow (4).

| Parameter | Type | Description |
|---|---|---|
| `brand` | `str` | Brand family name (must exist in Primitives) |
| `grey` | `str` | Grey family name (must exist in Primitives) |
| `extra_tokens` | `dict` | `{"path": {"light": (family, shade), "dark": (family, shade), "scope": [...]}}` |

**Behavior by tier:**
- **2/3-Tier**: light + dark mode files, aliases Primitives
- **4-Tier**: single semantic.tokens.json, aliases Theme

### `build_theme(brand, grey, extra_tokens=None)`

**4-Tier only.** Same token structure as `build_semantic()` but with light/dark modes, aliasing Primitives. Automatically skipped for 2/3-Tier.

### `build_responsive(scale="standard")`

Generates Responsive collection with mobile/tablet/desktop breakpoint modes.

**Auto-generated tokens:**
- `font/size/{role}` — 12 typography roles (display through code)
- `font/lineHeight/{role}` — matching line heights
- `font/letterSpacing/{role}` — matching letter spacing
- `radius/{name}` — 8 radius tokens per breakpoint
- `borderWidth/{name}` — 6 border width tokens

### `build_density()`

Generates Density collection with compact/comfortable/spacious modes.

**Auto-generated tokens:**
- `padding/x/{size}` — horizontal padding: xs, sm, md, lg, xl
- `padding/y/{size}` — vertical padding: xs, sm, md, lg, xl
- `gap/{size}` — gap: xs through 4xl

### `build_layout()`

Generates Layout collection with xs-xxl breakpoint modes.

**Auto-generated tokens:** `column/count`, `column/margin`, `column/gutter`, `column/minWidth`, `column/maxWidth`

### `build_effects()`

Generates Effects collection (single mode).

**Auto-generated tokens:**
- `shadow/{scale}/color` — aliases Semantic (2/3-Tier) or Theme (4-Tier)
- `shadow/{scale}/{x,y,blur,spread}` — aliases Primitives
- `blur/{level}` — aliases Primitives

### `build_typography(body_font, display_font, mono_font, roles=None)`

Generates Typography collection (single mode).

| Parameter | Type | Description |
|---|---|---|
| `body_font` | `str` | Primitives font family key (e.g. `"sans"`) |
| `display_font` | `str` | Display font key |
| `mono_font` | `str` | Monospace font key |
| `roles` | `dict` or `None` | Custom role config or `None` for standard 12 roles |

**Per-role tokens:**
- `{role}/fontSize` → Responsive
- `{role}/lineHeight` → Responsive
- `{role}/letterSpacing` → Responsive
- `{role}/fontFamily` → Primitives
- `{role}/fontWeight` → Primitives

**Plus color tokens:** `color/primary`, `color/secondary`, etc. → Semantic or Theme

### `build_component_colors(components=None)`

**3/4-Tier only.** Generates Component Colors collection.

| Parameter | Type | Description |
|---|---|---|
| `components` | `list` | Component names, e.g. `["button", "input", "card"]` |

**Auto-generated groups:** icon variants, divider, container, plus per-component tokens (primary/secondary × states × parts).

### `build_component_dimensions()`

**3/4-Tier only.** Generates Component Dimensions: padding/gap → Density, radius/borderWidth → Responsive.

---

## Layer 1: Manual `create_token()` — For Custom Work

Use this for custom collections, unusual tokens, or when you need full control.

```python
token = gen.create_token(
    name="custom/path",             # Token path (forward slashes)
    ns=90,                          # ID namespace (90-99 for custom)
    type="color",                   # "color" | "number" | "string" | "boolean"
    value={"colorSpace":"srgb",...}, # Direct value (auto-set for color aliases)
    scope=["FRAME_FILL"],           # Optional — auto-derived if omitted
    alias_target="primitives/...",  # Optional — target path with collection prefix
    alias_set="Primitives",         # Optional — target collection name
    vid=None,                       # Optional — pre-built ID
    hidden_from_publishing=None,    # Optional — auto-derived if omitted
)
gen.nest_token(tree, "custom/path", token)
```

**Key defaults:**
- `scope=None` → auto-derived from path + type via `get_scope()`
- `hidden_from_publishing=None` → auto-derived from tier + collection

### Mixing with builders

Builders populate the shared registry, so manual tokens can alias builder-created tokens:

```python
# Standard collections
gen.build_primitives(brand_colors={"blue": BLUE})
gen.build_semantic(brand="blue", grey="slate")

# Custom collection using manual API
custom = {}
t = gen.create_token("team/primary", 90, "color",
    alias_target="primitives/color/blue/500",
    alias_set="Primitives", scope=["ALL_FILLS"])
gen.nest_token(custom, "team/primary", t)
gen.save_mode("10. Team Colors", "default", custom)
```

---

## Auto-Scope Rules

The `get_scope()` function auto-derives Figma scopes from the token path. Example patterns:

| Path Pattern | Type | Scope |
|---|---|---|
| `text/*`, `*/text`, `*/on-*` | color | `TEXT_FILL` |
| `border/*`, `*/border` | color | `STROKE` |
| `icon/*`, `*/icon` | color | `SHAPE_FILL`, `STROKE` |
| `surface/*`, `background/*` | color | `FRAME_FILL`, `SHAPE_FILL` |
| `shadow/*/color` | color | `EFFECT_COLOR` |
| `overlay/scrim`, `overlay/backdrop` | color | `ALL_FILLS` |
| `*/link/*` | color | `TEXT_FILL` |
| primitives `color/*` | color | `ALL_FILLS` |
| `spacing/*`, `gap/*`, `padding/*` | number | `GAP` |
| `radius/*` | number | `CORNER_RADIUS` |
| `borderwidth/*` | number | `STROKE_FLOAT` |
| `font/size/*`, `*/fontSize` | number | `FONT_SIZE` |
| `font/lineHeight/*`, `*/lineHeight` | number | `LINE_HEIGHT` |
| `font/letterSpacing/*`, `*/letterSpacing` | number | `LETTER_SPACING` |
| `shadow/*/x,y,blur,spread` | number | `EFFECT_FLOAT` |
| `blur/*` | number | `EFFECT_FLOAT` |
| `font/family/*` | string | `FONT_FAMILY` |
| `font/weight/*` | string | `FONT_STYLE` |

**Override:** Pass `scope=[...]` explicitly to `create_token()` for any non-standard pattern.

---

## Auto-Hide Rules

`hiddenFromPublishing` is auto-derived from tier + collection:

| Collection | 2-Tier | 3-Tier | 4-Tier |
|---|---|---|---|
| Primitives | hidden | hidden | hidden |
| Theme | — | — | hidden |
| Semantic | **visible** | hidden | hidden |
| Responsive | hidden | hidden | hidden |
| Density | hidden | hidden | hidden |
| Layout | hidden | hidden | hidden |
| Effects | visible | visible | visible |
| Typography | visible | visible | visible |
| Component Colors | — | **visible** | **visible** |
| Component Dimensions | — | **visible** | **visible** |

**Override:** Pass `hidden_from_publishing=True/False` explicitly.

---

## Auto-Backfill

When aliasing a **number primitive** that doesn't exist in the registry, the SDK auto-creates it if the value can be derived from the path (e.g., `spacing/12` → value `12`). A warning is logged.

**Color** and **string** primitives are NOT auto-backfilled — errors are collected and reported in the generation report.

---

## Batch Error Reporting

Instead of crashing on the first error, the SDK collects all errors and prints a summary:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  GENERATION REPORT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  AUTO-FIXED (3):
    ✓ Auto-backfilled: spacing/6 = 6
    ✓ Auto-backfilled: font/size/44 = 44

  ERRORS (1) — ZIP generated but may have broken aliases:
    ✗ MISSING TARGET: 'color/purple/950' not found in Primitives

  Total tokens in registry: 662
  Total files: 19
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

The ZIP is still generated. Tokens with missing targets get `VariableID:0:0` placeholders.

---

## Verification

Always call `verify_all_aliases()` before `build_zip()`:

```python
gen.verify_all_aliases()   # Runs 3 checks:
# 1. verify_chain_completeness() — all alias chains resolve
# 2. verify_emitted_alias_targets() — targets exist in emitted JSON
# 3. verify_emitted_scope_families() — scopes match path semantics
gen.build_zip(...)
```

---

## Built-in Presets

### Grey Family Presets
- `"slate"` — Cool blue-grey (default)
- `"gray"` — True neutral grey
- `"stone"` — Warm brownish grey
- `"zinc"` — Cool neutral grey
- `"neutral"` — Pure neutral grey

### Feedback Colors (always included)
- `"red"` — Error/destructive
- `"green"` — Success
- `"yellow"` — Warning
- `"blue"` — Info

### Typography Roles (standard, 12 roles)
display, heading, subheading, body-lg, body, body-sm, label-lg, label, label-sm, caption, overline, code

# Collection Specs Reference

---

## Primitives
**Mode file:** `primitives.tokens.json`
**$metadata.modeName:** `"primitives"`
See `04-primitives.md` for full token list.
Key rule: NO scope key on any token. NO aliasData. All values hardcoded.

---

## Theme Collection
**Mode files:** `light.tokens.json`, `dark.tokens.json`
**Aliases:** Primitives
**Default mode:** light

Theme is a middle-chain collection but every token gets a semantically correct scope. This is so variables are correctly categorised in Figma even though Component Colors is the picker tip.

**Shadow colour tokens live here (NEW):**
```
theme/shadow/sm/color    EFFECT_COLOR → primitives/color/black/a16 (light) / primitives/color/white/a8 (dark)
theme/shadow/md/color    EFFECT_COLOR → primitives/color/black/a24 (light) / primitives/color/white/a16 (dark)
theme/shadow/lg/color    EFFECT_COLOR → primitives/color/black/a32 (light) / primitives/color/white/a24 (dark)
theme/shadow/xl/color    EFFECT_COLOR → primitives/color/black/a40 (light) / primitives/color/white/a32 (dark)
```

### surface group → FRAME_FILL + SHAPE_FILL
```
theme/surface/page
theme/surface/default
theme/surface/raised
theme/surface/overlay
theme/surface/sunken
theme/surface/inverted
theme/surface/disabled
theme/surface/brand
```

### text group → TEXT_FILL
```
theme/text/primary
theme/text/secondary
theme/text/tertiary
theme/text/placeholder
theme/text/disabled
theme/text/inverse
theme/text/link
theme/text/link-hover
theme/text/on-brand
theme/text/on-danger
theme/text/on-surface-variant
theme/text/on-feedback-error
theme/text/on-feedback-success
```

### The "On" Pattern (Theme)
Theme defines the primary "on" tokens that Semantic will later alias.
- `on-brand`: → `primitives/white` (light/dark)
- `on-feedback-*`: → `primitives/white`
- `on-surface-variant`: → `theme/text/secondary`

### border group → STROKE
```
theme/border/default
theme/border/subtle
theme/border/strong
theme/border/focus
theme/border/error
theme/border/disabled
theme/border/inverse
theme/border/brand
```

### interactive group
```
theme/interactive/primary/default      FRAME_FILL+SHAPE_FILL
theme/interactive/primary/hover        FRAME_FILL+SHAPE_FILL
theme/interactive/primary/pressed      FRAME_FILL+SHAPE_FILL
theme/interactive/primary/disabled     FRAME_FILL+SHAPE_FILL
theme/interactive/primary/text         TEXT_FILL
theme/interactive/secondary/default    FRAME_FILL+SHAPE_FILL
theme/interactive/secondary/hover      FRAME_FILL+SHAPE_FILL
theme/interactive/secondary/pressed    FRAME_FILL+SHAPE_FILL
theme/interactive/secondary/text       TEXT_FILL
theme/interactive/ghost/hover          FRAME_FILL+SHAPE_FILL
theme/interactive/ghost/pressed        FRAME_FILL+SHAPE_FILL
theme/interactive/destructive/default  FRAME_FILL+SHAPE_FILL
theme/interactive/destructive/hover    FRAME_FILL+SHAPE_FILL
theme/interactive/destructive/pressed  FRAME_FILL+SHAPE_FILL
theme/interactive/destructive/text     TEXT_FILL
```

### feedback group
```
theme/feedback/error/surface     FRAME_FILL+SHAPE_FILL
theme/feedback/error/border      STROKE
theme/feedback/error/text        TEXT_FILL
theme/feedback/error/icon        SHAPE_FILL+STROKE
theme/feedback/success/surface   FRAME_FILL+SHAPE_FILL
theme/feedback/success/border    STROKE
theme/feedback/success/text      TEXT_FILL
theme/feedback/success/icon      SHAPE_FILL+STROKE
theme/feedback/warning/surface   FRAME_FILL+SHAPE_FILL
theme/feedback/warning/border    STROKE
theme/feedback/warning/text      TEXT_FILL
theme/feedback/warning/icon      SHAPE_FILL+STROKE
theme/feedback/info/surface      FRAME_FILL+SHAPE_FILL
theme/feedback/info/border       STROKE
theme/feedback/info/text         TEXT_FILL
theme/feedback/info/icon         SHAPE_FILL+STROKE
```

### overlay group → ALL_FILLS
```
theme/overlay/scrim         ALL_FILLS → primitives/color/black/a48 (light) / black/a64 (dark)
theme/overlay/tooltip       FRAME_FILL+SHAPE_FILL
```

---

## Responsive Collection (NEW)
**Mode files:** `mobile.tokens.json`, `tablet.tokens.json`, `desktop.tokens.json`
**$metadata.modeName:** `"mobile"`, `"tablet"`, `"desktop"`
**Default mode:** mobile
**Aliases:** Primitives
**Scopes:** FONT_SIZE, LINE_HEIGHT, LETTER_SPACING, CORNER_RADIUS, STROKE_FLOAT

This collection provides breakpoint-aware values for all numerical tokens used by Typography and Component Dimensions. It aliases Primitives but maps values design-appropriately per breakpoint — NOT a blind 1:1 forward.

> [!IMPORTANT]
> **COVERAGE AUDIT:** Before generating the Responsive JSON, you MUST run `validate_responsive_coverage()` to ensure every value you intend to use (e.g. `lineheight: 52`) already exists as a path in your Primitives registry. If it doesn't, you must backfill it in Primitives BEFORE saving the Primitives mode file.

### font/size/* → FONT_SIZE
Each token aliases a Primitives font/size value. Mobile uses smaller values, desktop uses larger.
```
responsive/font/size/display       mobile→40  tablet→48  desktop→60
responsive/font/size/heading       mobile→28  tablet→32  desktop→36
responsive/font/size/subheading    mobile→18  tablet→20  desktop→20
responsive/font/size/body-lg       mobile→16  tablet→17  desktop→18
responsive/font/size/body          mobile→14  tablet→15  desktop→16
responsive/font/size/body-sm       mobile→12  tablet→13  desktop→14
responsive/font/size/label-lg      mobile→14  tablet→15  desktop→16
responsive/font/size/label         mobile→13  tablet→13  desktop→14
responsive/font/size/label-sm      mobile→11  tablet→11  desktop→12
responsive/font/size/caption       mobile→11  tablet→11  desktop→12
responsive/font/size/overline      mobile→10  tablet→10  desktop→11
responsive/font/size/code          mobile→12  tablet→13  desktop→14
```
(If user chose Extended scale, add: display-sm, heading-sm, heading-lg, body-strong, numeric)

### font/lineHeight/* → LINE_HEIGHT
```
responsive/font/lineHeight/display      mobile→44  tablet→56  desktop→72
responsive/font/lineHeight/heading      mobile→36  tablet→40  desktop→44
responsive/font/lineHeight/subheading   mobile→26  tablet→28  desktop→28
responsive/font/lineHeight/body-lg      mobile→24  tablet→26  desktop→28
responsive/font/lineHeight/body         mobile→20  tablet→22  desktop→24
responsive/font/lineHeight/body-sm      mobile→18  tablet→18  desktop→20
responsive/font/lineHeight/label        mobile→18  tablet→18  desktop→20
responsive/font/lineHeight/caption      mobile→16  tablet→16  desktop→16
responsive/font/lineHeight/overline     mobile→14  tablet→14  desktop→16
responsive/font/lineHeight/code         mobile→18  tablet→18  desktop→20
```

### font/letterSpacing/* → LETTER_SPACING
```
responsive/font/letterSpacing/display     mobile→-1  tablet→-2  desktop→-2
responsive/font/letterSpacing/heading     mobile→0   tablet→-1  desktop→-1
responsive/font/letterSpacing/body        mobile→0   tablet→0   desktop→0
responsive/font/letterSpacing/caption     mobile→1   tablet→1   desktop→1
responsive/font/letterSpacing/overline    mobile→2   tablet→2   desktop→2

**RC4: Extended Roles letterSpacing (CRITICAL):**
If use chooses Extended Scale, you MUST generate unique Responsive paths for every role to prevent ID collapsing:
- `display-sm` → -2
- `heading-lg` → -1
- `heading-sm` → 0
- `body-strong` → 0
- `label-lg` → 0
- `label` → 0
- `label-sm` → 1
- `numeric` → 0
- `caption` → 1
- `overline` → 2
```

### radius/* → CORNER_RADIUS
Values are design-appropriate per breakpoint (NOT a blind forward).
```
responsive/radius/none    mobile→0     tablet→0     desktop→0
responsive/radius/xs      mobile→2     tablet→2     desktop→2
responsive/radius/sm      mobile→3     tablet→4     desktop→4
responsive/radius/md      mobile→6     tablet→7     desktop→8
responsive/radius/lg      mobile→10    tablet→11    desktop→12
responsive/radius/xl      mobile→14    tablet→15    desktop→16
responsive/radius/2xl     mobile→20    tablet→22    desktop→24
responsive/radius/full    mobile→9999  tablet→9999  desktop→9999
```

### borderWidth/* → STROKE_FLOAT
Border widths are generally consistent across breakpoints (same alias from Primitives in all 3 modes).
```
responsive/borderWidth/hairline   0.3  (all modes)
responsive/borderWidth/thin       0.5  (all modes)
responsive/borderWidth/soft       0.8  (all modes)
responsive/borderWidth/sm         1    (all modes)
responsive/borderWidth/md         2    (all modes)
responsive/borderWidth/lg         4    (all modes)
```

---

## Density Collection
**Mode files:** `compact.tokens.json`, `comfortable.tokens.json`, `spacious.tokens.json`
**$metadata.modeName:** `"compact"`, `"comfortable"`, `"spacious"`
**Default mode:** comfortable
**Aliases:** Primitives/spacing/*
**Scope:** GAP on ALL tokens

Padding tokens cover the 6 directions (x, y, top, bottom, left, right). Each direction contains a full size scale (xs through 4xl). Values scale significantly across density modes. Gap tokens also range from xs through 4xl.

```
density/padding/x/xs       GAP   compact=2,   comfortable=4,   spacious=6
density/padding/x/sm       GAP   compact=4,   comfortable=6,   spacious=8
density/padding/x/md       GAP   compact=8,   comfortable=12,  spacious=16
density/padding/y/xs       GAP   compact=2,   comfortable=4,   spacious=6
density/padding/y/sm       GAP   compact=4,   comfortable=6,   spacious=8
density/padding/y/md       GAP   compact=8,   comfortable=12,  spacious=16
... (apply the same xs→4xl nested scale across top, bottom, left, right)
density/gap/xs          GAP   compact=2,   comfortable=4,   spacious=6
density/gap/sm          GAP   compact=4,   comfortable=8,   spacious=12
density/gap/md          GAP   compact=8,   comfortable=12,  spacious=16
density/gap/lg          GAP   compact=12,  comfortable=16,  spacious=24
density/gap/xl          GAP   compact=16,  comfortable=24,  spacious=32
density/gap/2xl         GAP   compact=24,  comfortable=40,  spacious=64
density/gap/3xl         GAP   compact=40,  comfortable=64,  spacious=96
density/gap/4xl         GAP   compact=64,  comfortable=96,  spacious=128
```

---

## Layout Collection
**Mode files:** `xs.tokens.json`, `sm.tokens.json`, `md.tokens.json`, `lg.tokens.json`, `xl.tokens.json`, `xxl.tokens.json`
**$metadata.modeName:** `"xs"`, `"sm"`, `"md"`, `"lg"`, `"xl"`, `"xxl"`
**Aliases:** Primitives `layout/*`
**Scope:** WIDTH_HEIGHT on ALL tokens

Layout tokens MUST use aliasData pointing at `layout/{breakpoint}/{property}` in Primitives. Never hardcode values.

```
layout/column/count     → Primitives: layout/{breakpoint}/columns
layout/column/margin    → Primitives: layout/{breakpoint}/margin
layout/column/gutter    → Primitives: layout/{breakpoint}/gutter
layout/column/minWidth  → Primitives: layout/{breakpoint}/minWidth
layout/column/maxWidth  → Primitives: layout/{breakpoint}/maxWidth
```

---

## Effects Collection
**Mode file:** `effects.tokens.json` (SINGLE MODE — no light/dark)
**$metadata.modeName:** `"effects"`
**Default mode:** N/A (single mode)
**Shadow colours:** alias Theme
**Shadow geometry:** alias Primitives
**Scope:** EFFECT_COLOR on colours, EFFECT_FLOAT on numbers

Shadow colour tokens point at Theme. When designer switches Theme mode (light↔dark), shadow colours automatically update in Effects. No modes needed on Effects itself.

```
effects/shadow/sm/color    EFFECT_COLOR → theme/shadow/sm/color
effects/shadow/sm/x        EFFECT_FLOAT → primitives/shadow/sm/x
effects/shadow/sm/y        EFFECT_FLOAT → primitives/shadow/sm/y
effects/shadow/sm/blur     EFFECT_FLOAT → primitives/shadow/sm/blur
effects/shadow/sm/spread   EFFECT_FLOAT → primitives/shadow/sm/spread

effects/shadow/md/color    EFFECT_COLOR → theme/shadow/md/color
effects/shadow/md/x        EFFECT_FLOAT → primitives/shadow/md/x
effects/shadow/md/y        EFFECT_FLOAT → primitives/shadow/md/y
effects/shadow/md/blur     EFFECT_FLOAT → primitives/shadow/md/blur
effects/shadow/md/spread   EFFECT_FLOAT → primitives/shadow/md/spread

effects/shadow/lg/color    EFFECT_COLOR → theme/shadow/lg/color
effects/shadow/lg/x        EFFECT_FLOAT → primitives/shadow/lg/x
effects/shadow/lg/y        EFFECT_FLOAT → primitives/shadow/lg/y
effects/shadow/lg/blur     EFFECT_FLOAT → primitives/shadow/lg/blur
effects/shadow/lg/spread   EFFECT_FLOAT → primitives/shadow/lg/spread

effects/shadow/xl/color    EFFECT_COLOR → theme/shadow/xl/color
effects/shadow/xl/x        EFFECT_FLOAT → primitives/shadow/xl/x
effects/shadow/xl/y        EFFECT_FLOAT → primitives/shadow/xl/y
effects/shadow/xl/blur     EFFECT_FLOAT → primitives/shadow/xl/blur
effects/shadow/xl/spread   EFFECT_FLOAT → primitives/shadow/xl/spread

effects/blur/sm    EFFECT_FLOAT → primitives/blur/sm
effects/blur/md    EFFECT_FLOAT → primitives/blur/md
effects/blur/lg    EFFECT_FLOAT → primitives/blur/lg
effects/blur/xl    EFFECT_FLOAT → primitives/blur/xl
```

Variable IDs: same variableId in the single effects.tokens.json file. No mode duplication needed.

---

## Typography Collection
**Mode file:** `typography.tokens.json` (SINGLE MODE)
**$metadata.modeName:** `"typography"`
**Aliases:** Responsive (numerical values) + Primitives (font/family, font/weight) + Theme (colour tokens)

Typography colour tokens alias Theme (not Semantic) because Typography is a cross-cutting concern used across all layers.

> [!IMPORTANT]
> **BACKFILLING CHECK:** Before aliasing any `fontSize`, `lineHeight`, or `letterSpacing` value from `Responsive`, verify that the raw numerical value exists in your **Primitives** collection (e.g. if `subheading` mobile needs `26px`, `font/lineHeight/26` MUST exist in Primitives). If missing, add it to Primitives first.

### Tokens per role — numerical values alias Responsive
```
typography/{role}/fontSize       FONT_SIZE      → Responsive: font/size/{role}
typography/{role}/lineHeight     LINE_HEIGHT    → Responsive: font/lineHeight/{role}
typography/{role}/letterSpacing  LETTER_SPACING → Responsive: font/letterSpacing/{role}
                                                  (if no matching letterSpacing role, alias closest)
typography/{role}/fontFamily     FONT_FAMILY    → Primitives: font/family/{name}  ← direct to Primitives
typography/{role}/fontWeight     FONT_STYLE     → Primitives: font/weight/{name}  ← direct to Primitives

> **RC5: LetterSpacing Path Mapping (CRITICAL)**
> There is a schema mismatch between Primitives and Responsive for `letterSpacing`:
> - **Primitives**: Uses semantic names (e.g. `font/letterspacing/tight`).
> - **Responsive**: Uses role names (e.g. `responsive/font/letterspacing/display`).
> When building Typography, you MUST alias **Responsive** for numerical compatibility across breakpoints. Do NOT alias Primitives directly for letterSpacing roles.
```

### Font colour tokens → alias Theme
```
typography/color/primary    TEXT_FILL → theme/text/primary
typography/color/secondary  TEXT_FILL → theme/text/secondary
typography/color/tertiary   TEXT_FILL → theme/text/tertiary
typography/color/disabled   TEXT_FILL → theme/text/disabled
typography/color/inverse    TEXT_FILL → theme/text/inverse
typography/color/link       TEXT_FILL → theme/text/link
typography/color/error      TEXT_FILL → theme/feedback/error/text
typography/color/success    TEXT_FILL → theme/feedback/success/text
typography/color/warning    TEXT_FILL → theme/feedback/warning/text
typography/color/on-brand   TEXT_FILL → theme/text/on-brand
```

### Standard type roles
| Role | fontWeight | Notes |
|---|---|---|
| display | Bold | Largest, hero text |
| heading | SemiBold | Page titles |
| subheading | SemiBold | Section headers |
| body-lg | Regular | Large body text |
| body | Regular | Default body |
| body-sm | Regular | Small body |
| label-lg | Medium | Large UI labels |
| label | Medium | Standard UI labels |
| label-sm | Medium | Small labels |
| caption | Regular | Captions, footnotes |
| overline | Medium | Eyebrow/overline text |
| code | Regular | Monospace |

---


> Continued in `05b-collections-semantic-components.md` — Semantic, Component Colors, Component Dimensions

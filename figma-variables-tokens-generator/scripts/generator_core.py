"""
DesignTokenGenerator — Smart SDK for Figma Variable JSON generation.

Executable version of the class documented in references/06-generator-utility.md.
This file is written to the user's project by the AI for local environments.

Layer 1: create_token() — full flexibility, now with auto-scope/auto-hide defaults
Layer 2: make_family(), prebuild_ids() — pattern helpers
Layer 3: build_*() — collection builders for standard patterns

Usage:
    from generator_core import DesignTokenGenerator, prebuild_ids, make_family
"""

import json
import zipfile
import os
from io import BytesIO


# ─── Built-in Scale Constants ─────────────────────────────────────────────────

DEFAULT_FONT_SIZES = [
    8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 20, 22, 24,
    28, 30, 32, 36, 40, 44, 48, 52, 56, 60, 72
]

DEFAULT_LINE_HEIGHTS = [
    12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 36,
    40, 44, 48, 52, 56, 60, 72, 80
]

DEFAULT_LETTER_SPACING = {
    "tight": -2, "normal": 0, "wide": 1, "wider": 2, "widest": 4
}

DEFAULT_SPACING = [
    0, 2, 4, 6, 8, 10, 12, 14, 16, 20, 24, 28, 32,
    36, 40, 48, 56, 64, 80, 96, 128, 160
]

DEFAULT_SIZES = [
    16, 20, 24, 28, 32, 36, 40, 44, 48, 56, 64, 80, 96, 120, 160
]

DEFAULT_RADIUS = {
    "none": 0, "xs": 2, "sm": 4, "md": 8, "lg": 12,
    "xl": 16, "2xl": 24, "full": 9999
}

DEFAULT_BORDER_WIDTH = {
    "hairline": 0.3, "thin": 0.5, "soft": 0.8,
    "sm": 1, "md": 2, "lg": 4
}

DEFAULT_BLUR = {
    "none": 0, "sm": 4, "md": 8, "lg": 16, "xl": 24, "2xl": 40
}

DEFAULT_SHADOW = {
    "sm":  {"x": 0, "y": 2,  "blur": 8,  "spread": 0},
    "md":  {"x": 0, "y": 4,  "blur": 16, "spread": 0},
    "lg":  {"x": 0, "y": 8,  "blur": 24, "spread": 0},
    "xl":  {"x": 0, "y": 16, "blur": 48, "spread": 0},
}

DEFAULT_ZINDEX = {
    "base": 0, "raised": 10, "dropdown": 100, "sticky": 200,
    "modal": 300, "toast": 400, "tooltip": 500
}

DEFAULT_LAYOUT = {
    "xs":  {"columns": 4,  "margin": 16, "gutter": 8,  "minWidth": 0,    "maxWidth": 599},
    "sm":  {"columns": 4,  "margin": 24, "gutter": 16, "minWidth": 600,  "maxWidth": 904},
    "md":  {"columns": 8,  "margin": 32, "gutter": 24, "minWidth": 905,  "maxWidth": 1239},
    "lg":  {"columns": 12, "margin": 48, "gutter": 24, "minWidth": 1240, "maxWidth": 1439},
    "xl":  {"columns": 12, "margin": 64, "gutter": 32, "minWidth": 1440, "maxWidth": 1919},
    "xxl": {"columns": 12, "margin": 80, "gutter": 32, "minWidth": 1920, "maxWidth": 9999},
}

DEFAULT_FONT_WEIGHTS = {
    "thin": "Thin", "light": "Light", "regular": "Regular",
    "medium": "Medium", "semibold": "SemiBold", "bold": "Bold",
    "extrabold": "ExtraBold", "black": "Black"
}

# Color shade index: 50 through 950 (11 shades)
DEFAULT_SHADES = ["50", "100", "200", "300", "400", "500", "600", "700", "800", "900", "950"]
DEFAULT_ALPHA_STEPS = [
    (0.08, "a8"), (0.16, "a16"), (0.24, "a24"), (0.32, "a32"),
    (0.40, "a40"), (0.48, "a48"), (0.56, "a56"), (0.64, "a64"), (1.0, "a100")
]

# Built-in grey presets — {family_name: [(shade_key, hex), ...]}
GREY_PRESETS = {
    "slate": [
        ("50", "#F8FAFC"), ("100", "#F1F5F9"), ("200", "#E2E8F0"), ("300", "#CBD5E1"),
        ("400", "#94A3B8"), ("500", "#64748B"), ("600", "#475569"), ("700", "#334155"),
        ("800", "#1E293B"), ("900", "#0F172A"), ("950", "#020617"),
    ],
    "gray": [
        ("50", "#F9FAFB"), ("100", "#F3F4F6"), ("200", "#E5E7EB"), ("300", "#D1D5DB"),
        ("400", "#9CA3AF"), ("500", "#6B7280"), ("600", "#4B5563"), ("700", "#374151"),
        ("800", "#1F2937"), ("900", "#111827"), ("950", "#030712"),
    ],
    "stone": [
        ("50", "#FAFAF9"), ("100", "#F5F5F4"), ("200", "#E7E5E4"), ("300", "#D6D3D1"),
        ("400", "#A8A29E"), ("500", "#78716C"), ("600", "#57534E"), ("700", "#44403C"),
        ("800", "#292524"), ("900", "#1C1917"), ("950", "#0C0A09"),
    ],
    "zinc": [
        ("50", "#FAFAFA"), ("100", "#F4F4F5"), ("200", "#E4E4E7"), ("300", "#D4D4D8"),
        ("400", "#A1A1AA"), ("500", "#71717A"), ("600", "#52525B"), ("700", "#3F3F46"),
        ("800", "#27272A"), ("900", "#18181B"), ("950", "#09090B"),
    ],
    "neutral": [
        ("50", "#FAFAFA"), ("100", "#F5F5F5"), ("200", "#E5E5E5"), ("300", "#D4D4D4"),
        ("400", "#A3A3A3"), ("500", "#737373"), ("600", "#525252"), ("700", "#404040"),
        ("800", "#262626"), ("900", "#171717"), ("950", "#0A0A0A"),
    ],
}

# Default feedback color families
DEFAULT_FEEDBACK_COLORS = {
    "red": [
        ("50", "#FEF2F2"), ("100", "#FEE2E2"), ("200", "#FECACA"), ("300", "#FCA5A5"),
        ("400", "#F87171"), ("500", "#EF4444"), ("600", "#DC2626"), ("700", "#B91C1C"),
        ("800", "#991B1B"), ("900", "#7F1D1D"), ("950", "#450A0A"),
    ],
    "green": [
        ("50", "#F0FDF4"), ("100", "#DCFCE7"), ("200", "#BBF7D0"), ("300", "#86EFAC"),
        ("400", "#4ADE80"), ("500", "#22C55E"), ("600", "#16A34A"), ("700", "#15803D"),
        ("800", "#166534"), ("900", "#14532D"), ("950", "#052E16"),
    ],
    "yellow": [
        ("50", "#FEFCE8"), ("100", "#FEF9C3"), ("200", "#FEF08A"), ("300", "#FDE047"),
        ("400", "#FACC15"), ("500", "#EAB308"), ("600", "#CA8A04"), ("700", "#A16207"),
        ("800", "#854D0E"), ("900", "#713F12"), ("950", "#422006"),
    ],
    "blue": [
        ("50", "#EFF6FF"), ("100", "#DBEAFE"), ("200", "#BFDBFE"), ("300", "#93C5FD"),
        ("400", "#60A5FA"), ("500", "#3B82F6"), ("600", "#2563EB"), ("700", "#1D4ED8"),
        ("800", "#1E40AF"), ("900", "#1E3A8A"), ("950", "#172554"),
    ],
}

# Namespace constants
NS_PRIMITIVES = 10
NS_RESPONSIVE = 20
NS_TYPOGRAPHY = 25
NS_EFFECTS = 30
NS_THEME = 40
NS_DENSITY = 50
NS_LAYOUT = 55
NS_SEMANTIC = 60
NS_COMPONENT_COLORS = 70
NS_COMPONENT_DIMENSIONS = 80

# Visibility table: {collection_key: {tier: is_hidden}}
# True = hidden, False = visible (published to user)
VISIBILITY_TABLE = {
    "Primitives":            {1: False, 2: True, 3: True, 4: True},
    "Semantic":              {2: False, 3: True, 4: True},
    "Theme":                 {4: True},
    "Responsive":            {2: True, 3: True, 4: True},
    "Density":               {2: True, 3: True, 4: True},
    "Layout":                {2: True, 3: True, 4: True},
    "Effects":               {2: False, 3: False, 4: False},
    "Typography":            {2: False, 3: False, 4: False},
    "Component Colors":      {3: False, 4: False},
    "Component Dimensions":  {3: False, 4: False},
}

# ─── Responsive scale defaults ────────────────────────────────────────────────

RESPONSIVE_FONT_SIZE = {
    "display":     {"mobile": 40, "tablet": 48, "desktop": 60},
    "heading":     {"mobile": 28, "tablet": 32, "desktop": 36},
    "subheading":  {"mobile": 18, "tablet": 20, "desktop": 20},
    "body-lg":     {"mobile": 16, "tablet": 17, "desktop": 18},
    "body":        {"mobile": 14, "tablet": 15, "desktop": 16},
    "body-sm":     {"mobile": 12, "tablet": 13, "desktop": 14},
    "label-lg":    {"mobile": 14, "tablet": 15, "desktop": 16},
    "label":       {"mobile": 13, "tablet": 13, "desktop": 14},
    "label-sm":    {"mobile": 11, "tablet": 11, "desktop": 12},
    "caption":     {"mobile": 11, "tablet": 11, "desktop": 12},
    "overline":    {"mobile": 10, "tablet": 10, "desktop": 11},
    "code":        {"mobile": 12, "tablet": 13, "desktop": 14},
}

RESPONSIVE_LINE_HEIGHT = {
    "display":     {"mobile": 44, "tablet": 56, "desktop": 72},
    "heading":     {"mobile": 36, "tablet": 40, "desktop": 44},
    "subheading":  {"mobile": 26, "tablet": 28, "desktop": 28},
    "body-lg":     {"mobile": 24, "tablet": 26, "desktop": 28},
    "body":        {"mobile": 20, "tablet": 22, "desktop": 24},
    "body-sm":     {"mobile": 18, "tablet": 18, "desktop": 20},
    "label":       {"mobile": 18, "tablet": 18, "desktop": 20},
    "caption":     {"mobile": 16, "tablet": 16, "desktop": 16},
    "overline":    {"mobile": 14, "tablet": 14, "desktop": 16},
    "code":        {"mobile": 18, "tablet": 18, "desktop": 20},
}

RESPONSIVE_LETTER_SPACING = {
    "display":  {"mobile": -1, "tablet": -2, "desktop": -2},
    "heading":  {"mobile": 0,  "tablet": -1, "desktop": -1},
    "body":     {"mobile": 0,  "tablet": 0,  "desktop": 0},
    "caption":  {"mobile": 1,  "tablet": 1,  "desktop": 1},
    "overline": {"mobile": 2,  "tablet": 2,  "desktop": 2},
}

RESPONSIVE_RADIUS = {
    "none": {"mobile": 0,    "tablet": 0,    "desktop": 0},
    "xs":   {"mobile": 2,    "tablet": 2,    "desktop": 2},
    "sm":   {"mobile": 3,    "tablet": 4,    "desktop": 4},
    "md":   {"mobile": 6,    "tablet": 7,    "desktop": 8},
    "lg":   {"mobile": 10,   "tablet": 11,   "desktop": 12},
    "xl":   {"mobile": 14,   "tablet": 15,   "desktop": 16},
    "2xl":  {"mobile": 20,   "tablet": 22,   "desktop": 24},
    "full": {"mobile": 9999, "tablet": 9999, "desktop": 9999},
}

RESPONSIVE_BORDER_WIDTH = {
    "hairline": 0.3, "thin": 0.5, "soft": 0.8,
    "sm": 1, "md": 2, "lg": 4,
}

# ─── Density defaults ─────────────────────────────────────────────────────────

DENSITY_PADDING = {
    "padding/x/xs": {"compact": 2,  "comfortable": 4,   "spacious": 6},
    "padding/x/sm": {"compact": 4,  "comfortable": 6,   "spacious": 8},
    "padding/x/md": {"compact": 8,  "comfortable": 12,  "spacious": 16},
    "padding/x/lg": {"compact": 12, "comfortable": 16,  "spacious": 24},
    "padding/x/xl": {"compact": 16, "comfortable": 24,  "spacious": 32},
    "padding/y/xs": {"compact": 2,  "comfortable": 4,   "spacious": 6},
    "padding/y/sm": {"compact": 4,  "comfortable": 6,   "spacious": 8},
    "padding/y/md": {"compact": 8,  "comfortable": 12,  "spacious": 16},
    "padding/y/lg": {"compact": 12, "comfortable": 16,  "spacious": 24},
    "padding/y/xl": {"compact": 16, "comfortable": 24,  "spacious": 32},
}

DENSITY_GAP = {
    "gap/xs":  {"compact": 2,  "comfortable": 4,   "spacious": 6},
    "gap/sm":  {"compact": 4,  "comfortable": 8,   "spacious": 12},
    "gap/md":  {"compact": 8,  "comfortable": 12,  "spacious": 16},
    "gap/lg":  {"compact": 12, "comfortable": 16,  "spacious": 24},
    "gap/xl":  {"compact": 16, "comfortable": 24,  "spacious": 32},
    "gap/2xl": {"compact": 24, "comfortable": 40,  "spacious": 64},
    "gap/3xl": {"compact": 40, "comfortable": 64,  "spacious": 96},
    "gap/4xl": {"compact": 64, "comfortable": 96,  "spacious": 128},
}

# ─── Semantic Shade Mapping (light/dark) ───────────────────────────────────────
# Keys use placeholders: {brand} = brand family name, {grey} = grey family name
# Values: (family, shade) — family is "white"/"black" or "{brand}"/"{grey}"

SEMANTIC_SURFACE_MAP = {
    "surface/page":      {"light": ("white", "a100"), "dark": ("{grey}", "950")},
    "surface/default":   {"light": ("white", "a100"), "dark": ("{grey}", "900")},
    "surface/raised":    {"light": ("{grey}", "50"),   "dark": ("{grey}", "800")},
    "surface/overlay":   {"light": ("white", "a100"), "dark": ("{grey}", "800")},
    "surface/sunken":    {"light": ("{grey}", "100"),  "dark": ("{grey}", "950")},
    "surface/inverted":  {"light": ("{grey}", "900"),  "dark": ("white", "a100")},
    "surface/disabled":  {"light": ("{grey}", "100"),  "dark": ("{grey}", "800")},
    "surface/brand":     {"light": ("{brand}", "500"), "dark": ("{brand}", "600")},
    "surface/input":     {"light": ("white", "a100"), "dark": ("{grey}", "900")},
    "surface/card":      {"light": ("white", "a100"), "dark": ("{grey}", "800")},
    "surface/modal":     {"light": ("white", "a100"), "dark": ("{grey}", "800")},
    "surface/popover":   {"light": ("white", "a100"), "dark": ("{grey}", "800")},
}

SEMANTIC_TEXT_MAP = {
    "text/primary":          {"light": ("{grey}", "900"),  "dark": ("{grey}", "50")},
    "text/secondary":        {"light": ("{grey}", "600"),  "dark": ("{grey}", "400")},
    "text/tertiary":         {"light": ("{grey}", "500"),  "dark": ("{grey}", "500")},
    "text/placeholder":      {"light": ("{grey}", "400"),  "dark": ("{grey}", "600")},
    "text/disabled":         {"light": ("{grey}", "300"),  "dark": ("{grey}", "700")},
    "text/inverse":          {"light": ("white", "a100"), "dark": ("{grey}", "900")},
    "text/link":             {"light": ("{brand}", "600"), "dark": ("{brand}", "400")},
    "text/link-hover":       {"light": ("{brand}", "700"), "dark": ("{brand}", "300")},
    "text/on-brand":         {"light": ("white", "a100"), "dark": ("white", "a100")},
    "text/on-danger":        {"light": ("white", "a100"), "dark": ("white", "a100")},
    "text/on-error":         {"light": ("white", "a100"), "dark": ("white", "a100")},
    "text/on-success":       {"light": ("white", "a100"), "dark": ("white", "a100")},
    "text/on-warning":       {"light": ("{grey}", "900"),  "dark": ("{grey}", "900")},
    "text/on-info":          {"light": ("white", "a100"), "dark": ("white", "a100")},
    "text/on-surface-variant": {"light": ("{grey}", "600"), "dark": ("{grey}", "400")},
}

SEMANTIC_BORDER_MAP = {
    "border/default":  {"light": ("{grey}", "200"),    "dark": ("{grey}", "700")},
    "border/subtle":   {"light": ("{grey}", "100"),    "dark": ("{grey}", "800")},
    "border/strong":   {"light": ("{grey}", "400"),    "dark": ("{grey}", "500")},
    "border/focus":    {"light": ("{brand}", "500"),   "dark": ("{brand}", "400")},
    "border/error":    {"light": ("red", "500"),       "dark": ("red", "400")},
    "border/disabled": {"light": ("{grey}", "200"),    "dark": ("{grey}", "800")},
    "border/inverse":  {"light": ("white", "a100"),   "dark": ("{grey}", "900")},
    "border/brand":    {"light": ("{brand}", "500"),   "dark": ("{brand}", "400")},
    "border/success":  {"light": ("green", "500"),     "dark": ("green", "400")},
    "border/warning":  {"light": ("yellow", "500"),    "dark": ("yellow", "400")},
    "border/info":     {"light": ("blue", "500"),      "dark": ("blue", "400")},
}

SEMANTIC_INTERACTIVE_MAP = {
    "interactive/primary/default":    {"light": ("{brand}", "600"), "dark": ("{brand}", "500"), "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/primary/hover":      {"light": ("{brand}", "700"), "dark": ("{brand}", "400"), "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/primary/pressed":    {"light": ("{brand}", "800"), "dark": ("{brand}", "600"), "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/primary/disabled":   {"light": ("{grey}", "200"),  "dark": ("{grey}", "800"),  "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/primary/text":       {"light": ("white", "a100"), "dark": ("white", "a100"),  "scope": ["TEXT_FILL"]},
    "interactive/primary/border":     {"light": ("{brand}", "600"), "dark": ("{brand}", "500"), "scope": ["STROKE"]},
    "interactive/secondary/default":  {"light": ("{grey}", "100"),  "dark": ("{grey}", "800"),  "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/secondary/hover":    {"light": ("{grey}", "200"),  "dark": ("{grey}", "700"),  "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/secondary/pressed":  {"light": ("{grey}", "300"),  "dark": ("{grey}", "600"),  "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/secondary/disabled": {"light": ("{grey}", "100"),  "dark": ("{grey}", "900"),  "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/secondary/text":     {"light": ("{grey}", "900"),  "dark": ("{grey}", "100"),  "scope": ["TEXT_FILL"]},
    "interactive/secondary/border":   {"light": ("{grey}", "300"),  "dark": ("{grey}", "600"),  "scope": ["STROKE"]},
    "interactive/ghost/hover":        {"light": ("{grey}", "100"),  "dark": ("{grey}", "800"),  "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/ghost/pressed":      {"light": ("{grey}", "200"),  "dark": ("{grey}", "700"),  "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/ghost/text":         {"light": ("{grey}", "900"),  "dark": ("{grey}", "100"),  "scope": ["TEXT_FILL"]},
    "interactive/destructive/default":  {"light": ("red", "600"), "dark": ("red", "500"),   "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/destructive/hover":    {"light": ("red", "700"), "dark": ("red", "400"),   "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/destructive/pressed":  {"light": ("red", "800"), "dark": ("red", "600"),   "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/destructive/disabled": {"light": ("{grey}", "200"), "dark": ("{grey}", "800"), "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "interactive/destructive/text":     {"light": ("white", "a100"), "dark": ("white", "a100"), "scope": ["TEXT_FILL"]},
    "interactive/destructive/border":   {"light": ("red", "600"), "dark": ("red", "500"),   "scope": ["STROKE"]},
    "interactive/link/default":  {"light": ("{brand}", "600"), "dark": ("{brand}", "400"), "scope": ["TEXT_FILL"]},
    "interactive/link/hover":    {"light": ("{brand}", "700"), "dark": ("{brand}", "300"), "scope": ["TEXT_FILL"]},
    "interactive/link/visited":  {"light": ("{brand}", "800"), "dark": ("{brand}", "500"), "scope": ["TEXT_FILL"]},
}

SEMANTIC_FEEDBACK_MAP = {
    "feedback/error/surface": {"light": ("red", "50"),    "dark": ("red", "900"),   "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "feedback/error/border":  {"light": ("red", "200"),   "dark": ("red", "700"),   "scope": ["STROKE"]},
    "feedback/error/text":    {"light": ("red", "700"),   "dark": ("red", "300"),   "scope": ["TEXT_FILL"]},
    "feedback/error/icon":    {"light": ("red", "500"),   "dark": ("red", "400"),   "scope": ["SHAPE_FILL", "STROKE"]},
    "feedback/success/surface": {"light": ("green", "50"),  "dark": ("green", "900"), "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "feedback/success/border":  {"light": ("green", "200"), "dark": ("green", "700"), "scope": ["STROKE"]},
    "feedback/success/text":    {"light": ("green", "700"), "dark": ("green", "300"), "scope": ["TEXT_FILL"]},
    "feedback/success/icon":    {"light": ("green", "500"), "dark": ("green", "400"), "scope": ["SHAPE_FILL", "STROKE"]},
    "feedback/warning/surface": {"light": ("yellow", "50"),  "dark": ("yellow", "900"), "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "feedback/warning/border":  {"light": ("yellow", "200"), "dark": ("yellow", "700"), "scope": ["STROKE"]},
    "feedback/warning/text":    {"light": ("yellow", "700"), "dark": ("yellow", "300"), "scope": ["TEXT_FILL"]},
    "feedback/warning/icon":    {"light": ("yellow", "500"), "dark": ("yellow", "400"), "scope": ["SHAPE_FILL", "STROKE"]},
    "feedback/info/surface":    {"light": ("blue", "50"),  "dark": ("blue", "900"), "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "feedback/info/border":     {"light": ("blue", "200"), "dark": ("blue", "700"), "scope": ["STROKE"]},
    "feedback/info/text":       {"light": ("blue", "700"), "dark": ("blue", "300"), "scope": ["TEXT_FILL"]},
    "feedback/info/icon":       {"light": ("blue", "500"), "dark": ("blue", "400"), "scope": ["SHAPE_FILL", "STROKE"]},
}

SEMANTIC_ICON_MAP = {
    "icon/default":  {"light": ("{grey}", "700"),    "dark": ("{grey}", "300")},
    "icon/muted":    {"light": ("{grey}", "400"),    "dark": ("{grey}", "600")},
    "icon/brand":    {"light": ("{brand}", "600"),   "dark": ("{brand}", "400")},
    "icon/inverse":  {"light": ("white", "a100"),   "dark": ("{grey}", "900")},
    "icon/disabled": {"light": ("{grey}", "300"),    "dark": ("{grey}", "700")},
    "icon/error":    {"light": ("red", "500"),       "dark": ("red", "400")},
    "icon/success":  {"light": ("green", "500"),     "dark": ("green", "400")},
    "icon/warning":  {"light": ("yellow", "500"),    "dark": ("yellow", "400")},
    "icon/info":     {"light": ("blue", "500"),      "dark": ("blue", "400")},
}

SEMANTIC_OVERLAY_MAP = {
    "overlay/scrim":    {"light": ("black", "a48"), "dark": ("black", "a64"), "scope": ["ALL_FILLS"]},
    "overlay/tooltip":  {"light": ("{grey}", "900"), "dark": ("{grey}", "100"), "scope": ["FRAME_FILL", "SHAPE_FILL"]},
    "overlay/backdrop": {"light": ("black", "a32"), "dark": ("black", "a48"), "scope": ["ALL_FILLS"]},
}

SEMANTIC_SHADOW_MAP = {
    "shadow/sm/color": {"light": ("black", "a16"), "dark": ("white", "a8")},
    "shadow/md/color": {"light": ("black", "a24"), "dark": ("white", "a16")},
    "shadow/lg/color": {"light": ("black", "a32"), "dark": ("white", "a24")},
    "shadow/xl/color": {"light": ("black", "a40"), "dark": ("white", "a32")},
}

# Typography role defaults
TYPOGRAPHY_ROLES_STANDARD = {
    "display":    {"fontWeight": "bold",     "fontFamily": "display"},
    "heading":    {"fontWeight": "semibold", "fontFamily": "body"},
    "subheading": {"fontWeight": "semibold", "fontFamily": "body"},
    "body-lg":    {"fontWeight": "regular",  "fontFamily": "body"},
    "body":       {"fontWeight": "regular",  "fontFamily": "body"},
    "body-sm":    {"fontWeight": "regular",  "fontFamily": "body"},
    "label-lg":   {"fontWeight": "medium",   "fontFamily": "body"},
    "label":      {"fontWeight": "medium",   "fontFamily": "body"},
    "label-sm":   {"fontWeight": "medium",   "fontFamily": "body"},
    "caption":    {"fontWeight": "regular",  "fontFamily": "body"},
    "overline":   {"fontWeight": "medium",   "fontFamily": "body"},
    "code":       {"fontWeight": "regular",  "fontFamily": "mono"},
}

TYPOGRAPHY_COLOR_MAP = {
    "color/primary":   "text/primary",
    "color/secondary": "text/secondary",
    "color/tertiary":  "text/tertiary",
    "color/disabled":  "text/disabled",
    "color/inverse":   "text/inverse",
    "color/link":      "text/link",
    "color/error":     "feedback/error/text",
    "color/success":   "feedback/success/text",
    "color/warning":   "feedback/warning/text",
    "color/on-brand":  "text/on-brand",
}


# ─── Scope Auto-Derivation ────────────────────────────────────────────────────

def get_scope(path, token_type, is_primitive=False):
    """
    Returns correct Figma scope(s) derived from path + type.
    Matches the logic defined in references/02-scoping-rules.md.
    """
    p = path.lower()

    if token_type == "color":
        if is_primitive:
            return ["ALL_FILLS"]
        # Root-level forms first
        if p.startswith("text/") or p.startswith("label/"):
            return ["TEXT_FILL"]
        if p.startswith("border/") or p.startswith("outline/"):
            return ["STROKE"]
        if p.startswith("icon/"):
            return ["SHAPE_FILL", "STROKE"]
        if p.startswith("surface/") or p.startswith("background/") or p.startswith("overlay/"):
            # Special case: overlay with alpha → ALL_FILLS
            if "scrim" in p or "backdrop" in p:
                return ["ALL_FILLS"]
            return ["FRAME_FILL", "SHAPE_FILL"]
        # End-of-path semantic suffixes (critical for nested paths like
        # interactive/primary/text, feedback/error/border, etc.)
        if p.endswith("/text") or p.endswith("/label"):
            return ["TEXT_FILL"]
        if p.endswith("/border") or p.endswith("/outline"):
            return ["STROKE"]
        if p.endswith("/icon"):
            return ["SHAPE_FILL", "STROKE"]
        # Icon sub-variants: stroke-only, fill-only
        if "/icon/" in p:
            if p.endswith("/stroke"):
                return ["STROKE"]
            if p.endswith("/fill") or p.endswith("/duotone"):
                return ["SHAPE_FILL"]
            return ["SHAPE_FILL", "STROKE"]
        if p.endswith("/surface") or p.endswith("/background"):
            return ["FRAME_FILL", "SHAPE_FILL"]
        # Nested forms (mid-path)
        if ("/shadow/" in p or p.startswith("shadow/")) and p.endswith("/color"):
            return ["EFFECT_COLOR"]
        if "/icon/" in p:
            return ["SHAPE_FILL", "STROKE"]
        if "/link/" in p or p.endswith("/link"):
            return ["TEXT_FILL"]
        if any(x in p for x in ["/text/", "/label/", "/on-"]):
            return ["TEXT_FILL"]
        if any(x in p for x in ["/border/", "/outline/"]):
            return ["STROKE"]
        if any(x in p for x in ["/background/", "/surface/", "/fill/",
                                "/container/", "/scrim/", "/overlay/"]):
            return ["FRAME_FILL", "SHAPE_FILL"]
        # Color fallback
        return ["FRAME_FILL", "SHAPE_FILL"]

    if token_type == "number":
        # Shadow geometry
        if any(x in p for x in ["/shadow/", "shadow/"]):
            if any(x in p for x in ["/blur", "/spread", "/x", "/y"]):
                return ["EFFECT_FLOAT"]
        # Blur
        if p.startswith("blur/") or "/blur/" in p or p.endswith("/blur"):
            return ["EFFECT_FLOAT"]
        # Opacity
        if "/opacity" in p or p.startswith("opacity/"):
            return ["OPACITY"]
        # Font sizing
        if (p.startswith("font/size/") or "/fontsize" in p or
                "/font/size/" in p or p.endswith("/fontsize")):
            return ["FONT_SIZE"]
        if (p.startswith("font/lineheight/") or "/lineheight" in p or
                "/font/lineheight/" in p or p.endswith("/lineheight")):
            return ["LINE_HEIGHT"]
        if (p.startswith("font/letterspacing/") or "/letterspacing" in p or
                "/font/letterspacing/" in p or p.endswith("/letterspacing")):
            return ["LETTER_SPACING"]
        # Spacing and padding
        if (p.startswith("spacing/") or "/spacing/" in p or
                "/padding" in p or p.startswith("padding/") or
                "/gap" in p or p.startswith("gap/")):
            return ["GAP"]
        # Radius
        if "/radius" in p or p.startswith("radius/"):
            return ["CORNER_RADIUS"]
        # Border width
        if "/borderwidth" in p or p.startswith("borderwidth/"):
            return ["STROKE_FLOAT"]
        if "/border/width/" in p:
            return ["STROKE_FLOAT"]
        # Width/Height/sizing
        if any(x in p for x in ["/height/", "/width/", "/iconsize",
                                "/minwidth", "/maxwidth", "/columns",
                                "/margin", "/gutter"]):
            return ["WIDTH_HEIGHT"]
        if p.startswith("size/") or "/size/" in p:
            return ["WIDTH_HEIGHT"]
        if p.startswith("layout/"):
            return ["WIDTH_HEIGHT"]
        # Z-index
        if "zindex" in p or "z-index" in p:
            return ["WIDTH_HEIGHT"]
        # Number fallback for primitives
        if is_primitive:
            if "/spacing/" in p:
                return ["GAP"]
            if "/layout/" in p:
                return ["WIDTH_HEIGHT"]
        # Generic number fallback
        return ["WIDTH_HEIGHT"]

    if token_type == "string":
        if "/fontfamily" in p or "/font/family/" in p or p.startswith("font/family/"):
            return ["FONT_FAMILY"]
        if any(x in p for x in ["/fontstyle", "/fontweight", "/font/weight/"]):
            return ["FONT_STYLE"]
        if p.startswith("font/weight/"):
            return ["FONT_STYLE"]
        return ["TEXT_CONTENT"]

    if token_type == "boolean":
        return ["ALL_SCOPES"]

    # Unknown type fallback
    return ["ALL_SCOPES"]


# ─── Hex to RGB helper ─────────────────────────────────────────────────

def hex_to_rgb(hex_str):
    """Convert hex string to [r, g, b] floats (0-1)."""
    h = hex_str.lstrip("#")
    return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]


# ═══════════════════════════════════════════════════════════════════════════════
# DesignTokenGenerator Class
# ═══════════════════════════════════════════════════════════════════════════════

class DesignTokenGenerator:
    def __init__(self, brand_name, syntax_format="css", platforms=None, tier=3):
        self.brand_name = brand_name
        self.syntax_format = syntax_format
        self.platforms = platforms or ["WEB"]
        self.tier = tier
        self.output_files = {}    # { "1. Collection/mode.json": {} }
        self.token_registry = {}  # { "path/to/token": "VariableID:X:Y" }
        self.counters = {}        # { namespace: count }
        self._warnings = []       # auto-backfill warnings
        self._errors = []         # non-fatal collected errors
        self._current_collection = None  # set during builder calls
        self._is_primitive_context = False  # set during primitive building

        # Tracking: store primitives tree for auto-backfill injection
        self._primitives_tree = None
        self._primitives_saved = False

    def to_dict(self):
        """Export state as a plain dict (Zero-dependency persistence fix)"""
        return {
            "brand_name": self.brand_name,
            "syntax_format": self.syntax_format,
            "platforms": self.platforms,
            "tier": self.tier,
            "output_files": self.output_files,
            "token_registry": self.token_registry,
            "counters": self.counters
        }

    @classmethod
    def from_dict(cls, data):
        """Reconstruct generator from a plain dict"""
        obj = cls(data["brand_name"], data["syntax_format"],
                  data.get("platforms", ["WEB"]), data.get("tier", 3))
        obj.output_files = data["output_files"]
        obj.token_registry = data["token_registry"]
        obj.counters = data["counters"]
        return obj

    def next_id(self, ns):
        self.counters[ns] = self.counters.get(ns, 0) + 1
        return f"VariableID:{ns}:{self.counters[ns]}"

    def canonical_path(self, path):
        """Single source of truth for token path identity."""
        if not isinstance(path, str):
            raise TypeError(f"Token path must be a string, got {type(path)!r}")
        normalized = path.strip().replace("\\", "/")
        while "//" in normalized:
            normalized = normalized.replace("//", "/")
        return normalized

    def resolve_id(self, id_map, path):
        """Safe accessor for pre-built ID maps."""
        key = self.canonical_path(path)
        if key not in id_map:
            raise KeyError(
                f"PREBUILD MISS: Path '{key}' not found in ID map. "
                "Ensure it was added to prebuild_ids().")
        return id_map[key]

    # ─── Auto-Hide Logic ───────────────────────────────────────────────────

    def _should_hide(self, collection_name):
        """Determine hiddenFromPublishing based on tier and collection."""
        if collection_name is None:
            return False
        clean = collection_name
        # Strip number prefix if present (e.g. "1. Primitives" -> "Primitives")
        if ". " in clean:
            clean = clean.split(". ", 1)[1]
        vis = VISIBILITY_TABLE.get(clean, {})
        return vis.get(self.tier, False)

    # ─── Auto-Backfill ─────────────────────────────────────────────────────

    def _auto_backfill_number_primitive(self, target_path):
        """Auto-create a missing number primitive if the value can be derived from the path."""
        parts = target_path.split("/")
        # Try to extract a numeric value from the last path segment
        last_segment = parts[-1]

        # Map path prefix to scope
        prefix = parts[0] if parts else ""
        value = None

        # Direct numeric extraction
        try:
            value = float(last_segment)
            if value == int(value):
                value = int(value)
        except (ValueError, TypeError):
            pass

        # Named lookups for non-numeric segments
        if value is None and prefix == "radius":
            value = DEFAULT_RADIUS.get(last_segment)
        if value is None and prefix == "borderwidth":
            value = DEFAULT_BORDER_WIDTH.get(last_segment)
        if value is None and prefix == "blur":
            value = DEFAULT_BLUR.get(last_segment)

        if value is None:
            return False  # Cannot auto-determine value

        # Create the primitive token
        scope = get_scope(target_path, "number", is_primitive=True)
        vid = self.next_id(NS_PRIMITIVES)
        self.token_registry[target_path] = vid

        token = {
            "$type": "number",
            "$value": value,
            "$extensions": {
                "com.figma.variableId": vid,
                "com.figma.hiddenFromPublishing": True,
                "com.figma.scopes": scope,
                "com.figma.codeSyntax": self.get_full_syntax(target_path),
            }
        }

        # Inject into Primitives output file
        for filepath, data in self.output_files.items():
            if "Primitives/" in filepath:
                self._inject_token_into_tree(data, target_path, token)
                break

        self._warnings.append(f"Auto-backfilled: {target_path} = {value}")
        return True

    def _inject_token_into_tree(self, tree, path, token):
        """Inject a token into an existing saved tree."""
        parts = self.canonical_path(path).split("/")
        curr = tree
        for part in parts[:-1]:
            if part not in curr:
                curr[part] = {}
            curr = curr[part]
        curr[parts[-1]] = token

    # ─── Core Token Creation (Layer 1) ─────────────────────────────────────

    def create_token(self, name, ns, type, value=None, scope=None,
                     alias_target=None, alias_set=None, vid=None,
                     target_registry=None, hidden_from_publishing=None):
        """
        Create a single token. This is the low-level API.

        scope: Optional. If None, auto-derived from path + type using get_scope().
               Pass an explicit list to override.
        hidden_from_publishing: Optional. If None, auto-derived from tier + collection.
                                Pass True/False to override.
        """
        path = self.canonical_path(name)
        vid = vid or self.next_id(ns)
        self.token_registry[path] = vid

        # Auto-derive scope if not explicitly provided
        if scope is None:
            scope = get_scope(path, type, is_primitive=self._is_primitive_context)

        # Alias placeholder: black for colors, real value for numbers/strings
        if alias_target and alias_set:
            if type == "color":
                value = {"colorSpace": "srgb", "components": [0, 0, 0],
                         "alpha": 1, "hex": "#000000"}

        ext = {
            "com.figma.variableId": vid,
            "com.figma.codeSyntax": self.get_full_syntax(path)
        }
        if type == "string":
            ext["com.figma.type"] = "string"

        # Auto-derive hidden_from_publishing if not explicitly set
        if hidden_from_publishing is None:
            hidden_from_publishing = self._should_hide(self._current_collection)
        if hidden_from_publishing:
            ext["com.figma.hiddenFromPublishing"] = True

        if scope:
            ext["com.figma.scopes"] = scope

        if alias_target:
            target_path = self.canonical_path(alias_target)
            # Strip collection prefix from path
            known_sets = [
                "primitives/", "theme/", "responsive/", "density/",
                "layout/", "effects/", "typography/", "semantic/",
                "component colors/", "component dimensions/"
            ]
            if alias_set:
                known_sets.append(f"{self.canonical_path(alias_set).lower()}/")

            for s in known_sets:
                if target_path.startswith(s):
                    target_path = target_path.replace(s, "", 1)
                    break

            registry = (target_registry if target_registry is not None
                        else self.token_registry)
            target_vid = registry.get(target_path)

            # Auto-backfill for missing number primitives
            if not target_vid and alias_set == "Primitives":
                if type == "number" or (type == "color" and False):  # Only numbers
                    if self._auto_backfill_number_primitive(target_path):
                        target_vid = self.token_registry.get(target_path)

            # Collect error instead of crashing
            if not target_vid:
                self._errors.append(
                    f"MISSING TARGET: '{target_path}' not found in "
                    f"{alias_set} registry (referenced by '{path}')")
                target_vid = "VariableID:0:0"

            ext["com.figma.aliasData"] = {
                "targetVariableId": target_vid,
                "targetVariableName": target_path,
                "targetVariableSetName": alias_set
            }

        return {"$type": type, "$value": value, "$extensions": ext}

    def get_full_syntax(self, path):
        """Builds the com.figma.codeSyntax object based on active platforms."""
        syntax = {}
        for platform in self.platforms:
            syntax[platform] = self.format_syntax(path, platform)
        return syntax

    def format_syntax(self, path, platform="WEB"):
        p = self.canonical_path(path).replace('/', '-').replace(' ', '-')
        while '--' in p:
            p = p.replace('--', '-')
        if platform == "WEB":
            if self.syntax_format == "css":
                return f"--{p}"
            if self.syntax_format == "camel":
                parts = p.split('-')
                return parts[0] + ''.join(
                    w.capitalize() for w in parts[1:])
            return p
        elif platform == "ANDROID":
            return p.replace('-', '_')
        elif platform == "iOS":
            return ''.join(w.capitalize() for w in p.split('-'))
        return p

    def nest_token(self, tree, path, token):
        path = self.canonical_path(path)
        parts = path.split('/')
        curr = tree
        for part in parts[:-1]:
            if part not in curr:
                curr[part] = {}
            curr = curr[part]
        curr[parts[-1]] = token

    def save_mode(self, collection_name, mode_name, tree):
        tree["$metadata"] = {"modeName": mode_name}
        self.output_files[
            f"{collection_name}/{mode_name}.tokens.json"] = tree

    # ═══════════════════════════════════════════════════════════════════════
    # Layer 3: Collection Builder Methods
    # ═══════════════════════════════════════════════════════════════════════

    def build_primitives(self, brand_colors, grey_family="slate",
                         font_families=None, extra_spacing=None,
                         extra_font_sizes=None, extra_line_heights=None):
        """
        Build the complete Primitives collection.

        Args:
            brand_colors: dict of {family_name: [(shade, hex), ...]}
                          e.g. {"azure": [("50","#F0F5FF"), ("100","#D6E4FF"), ...]}
            grey_family: str preset name ("slate","gray","stone","zinc","neutral")
                         OR list of [(shade, hex), ...] for custom grey
            font_families: dict {"sans": "Inter", "serif": "Playfair", "mono": "JetBrains Mono"}
                           or None for defaults
            extra_spacing: list of additional spacing values
            extra_font_sizes: list of additional font sizes
            extra_line_heights: list of additional line heights
        """
        self._current_collection = "Primitives"
        self._is_primitive_context = True
        tree = {}
        hidden = self._should_hide("Primitives")

        # ── Color families ──
        for family_name, shades in brand_colors.items():
            # Determine alpha base (500 shade hex)
            alpha_hex = "#000000"
            for shade_key, hex_val in shades:
                if shade_key == "500":
                    alpha_hex = hex_val
                    break
            make_family(self, tree, family_name, shades, alpha_hex,
                        scope=["ALL_FILLS"], hidden_from_publishing=hidden)

        # Grey from preset or custom
        if isinstance(grey_family, str):
            grey_shades = GREY_PRESETS.get(grey_family, GREY_PRESETS["slate"])
            grey_name = grey_family
        else:
            grey_shades = grey_family
            grey_name = "grey"
        grey_alpha_hex = "#64748B"
        for shade_key, hex_val in grey_shades:
            if shade_key == "700":
                grey_alpha_hex = hex_val
                break
        make_family(self, tree, grey_name, grey_shades, grey_alpha_hex,
                    scope=["ALL_FILLS"], hidden_from_publishing=hidden)

        # Feedback colors (red, green, yellow, blue)
        for fb_name, fb_shades in DEFAULT_FEEDBACK_COLORS.items():
            alpha_hex = "#000000"
            for sk, hx in fb_shades:
                if sk == "600":
                    alpha_hex = hx
                    break
            make_family(self, tree, fb_name, fb_shades, alpha_hex,
                        scope=["ALL_FILLS"], hidden_from_publishing=hidden)

        # White and black alpha-only families
        for family, components, hex_str in [
            ("white", [1, 1, 1], "#FFFFFF"),
            ("black", [0, 0, 0], "#000000")
        ]:
            for a_val, a_key in DEFAULT_ALPHA_STEPS:
                p = f"color/{family}/{a_key}"
                t = self.create_token(p, NS_PRIMITIVES, "color",
                    value={"colorSpace": "srgb", "components": components,
                           "alpha": a_val, "hex": hex_str},
                    scope=["ALL_FILLS"], hidden_from_publishing=hidden)
                self.nest_token(tree, p, t)

        # ── Spacing ──
        spacing_values = sorted(set(DEFAULT_SPACING + (extra_spacing or [])))
        for v in spacing_values:
            p = f"spacing/{v}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["GAP"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        # ── Sizes ──
        for v in DEFAULT_SIZES:
            p = f"size/{v}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["WIDTH_HEIGHT"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        # ── Radius ──
        for name, v in DEFAULT_RADIUS.items():
            p = f"radius/{name}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["CORNER_RADIUS"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        # ── Border Width ──
        for name, v in DEFAULT_BORDER_WIDTH.items():
            p = f"borderwidth/{name}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["STROKE_FLOAT"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        # ── Blur ──
        for name, v in DEFAULT_BLUR.items():
            p = f"blur/{name}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["EFFECT_FLOAT"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        # ── Shadow Geometry ──
        for scale, props in DEFAULT_SHADOW.items():
            for prop, v in props.items():
                p = f"shadow/{scale}/{prop}"
                t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                      scope=["EFFECT_FLOAT"], hidden_from_publishing=hidden)
                self.nest_token(tree, p, t)

        # ── Z-Index ──
        for name, v in DEFAULT_ZINDEX.items():
            p = f"number/zIndex/{name}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["WIDTH_HEIGHT"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        # ── Font tokens ──
        font_fams = font_families or {"sans": "Inter", "serif": "Playfair Display", "mono": "JetBrains Mono"}
        for name, val in font_fams.items():
            p = f"font/family/{name}"
            t = self.create_token(p, NS_PRIMITIVES, "string", value=val,
                                  scope=["FONT_FAMILY"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        for name, val in DEFAULT_FONT_WEIGHTS.items():
            p = f"font/weight/{name}"
            t = self.create_token(p, NS_PRIMITIVES, "string", value=val,
                                  scope=["FONT_STYLE"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        font_sizes = sorted(set(DEFAULT_FONT_SIZES + (extra_font_sizes or [])))
        for v in font_sizes:
            p = f"font/size/{v}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["FONT_SIZE"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        line_heights = sorted(set(DEFAULT_LINE_HEIGHTS + (extra_line_heights or [])))
        for v in line_heights:
            p = f"font/lineHeight/{v}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["LINE_HEIGHT"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        for name, v in DEFAULT_LETTER_SPACING.items():
            p = f"font/letterSpacing/{name}"
            t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                  scope=["LETTER_SPACING"], hidden_from_publishing=hidden)
            self.nest_token(tree, p, t)

        # ── Layout ──
        for bp, props in DEFAULT_LAYOUT.items():
            for prop, v in props.items():
                p = f"layout/{bp}/{prop}"
                t = self.create_token(p, NS_PRIMITIVES, "number", value=v,
                                      scope=["WIDTH_HEIGHT"], hidden_from_publishing=hidden)
                self.nest_token(tree, p, t)

        self._primitives_tree = tree
        self.save_mode("1. Primitives", "primitives", tree)
        self._primitives_saved = True
        self._is_primitive_context = False
        self._current_collection = None

    def _resolve_semantic_target(self, family_shade_tuple, brand, grey):
        """Resolve (family, shade) → primitives path, replacing {brand}/{grey}."""
        family, shade = family_shade_tuple
        family = family.replace("{brand}", brand).replace("{grey}", grey)
        return f"color/{family}/{shade}"

    def _build_semantic_mode(self, mode, brand, grey, alias_set, id_map, all_paths):
        """Build one mode (light or dark) of the semantic/theme collection."""
        tree = {}

        def _add_color_group(mapping, default_scope=None):
            for sem_path, config in mapping.items():
                mode_data = config if isinstance(config, dict) else config
                scope_override = mode_data.get("scope") if isinstance(mode_data, dict) and "scope" in mode_data else default_scope
                target_family_shade = mode_data.get(mode, mode_data.get("light")) if isinstance(mode_data, dict) else None
                if target_family_shade is None:
                    continue
                prim_target = self._resolve_semantic_target(target_family_shade, brand, grey)
                vid = self.resolve_id(id_map, sem_path) if id_map else None
                t = self.create_token(
                    sem_path, NS_SEMANTIC if alias_set != "Primitives" or self.tier < 4 else NS_THEME,
                    "color",
                    alias_target=f"primitives/{prim_target}" if alias_set == "Primitives" else f"theme/{prim_target.replace('color/', '', 1) if '/' in prim_target else prim_target}",
                    alias_set=alias_set,
                    vid=vid,
                    scope=scope_override,
                )
                self.nest_token(tree, sem_path, t)

        _add_color_group(SEMANTIC_SURFACE_MAP, ["FRAME_FILL", "SHAPE_FILL"])
        _add_color_group(SEMANTIC_TEXT_MAP, ["TEXT_FILL"])
        _add_color_group(SEMANTIC_BORDER_MAP, ["STROKE"])
        _add_color_group(SEMANTIC_INTERACTIVE_MAP)
        _add_color_group(SEMANTIC_FEEDBACK_MAP)
        _add_color_group(SEMANTIC_ICON_MAP, ["SHAPE_FILL", "STROKE"])
        _add_color_group(SEMANTIC_OVERLAY_MAP)
        _add_color_group(SEMANTIC_SHADOW_MAP, ["EFFECT_COLOR"])

        return tree

    def _gather_semantic_paths(self):
        """Collect all semantic token paths from the mapping tables."""
        paths = []
        for mapping in [SEMANTIC_SURFACE_MAP, SEMANTIC_TEXT_MAP,
                        SEMANTIC_BORDER_MAP, SEMANTIC_INTERACTIVE_MAP,
                        SEMANTIC_FEEDBACK_MAP, SEMANTIC_ICON_MAP,
                        SEMANTIC_OVERLAY_MAP, SEMANTIC_SHADOW_MAP]:
            paths.extend(mapping.keys())
        return paths

    def build_semantic(self, brand, grey, extra_tokens=None):
        """
        Build the Semantic collection.

        In 2/3-Tier: has light/dark modes, aliases Primitives.
        In 4-Tier: single mode, aliases Theme.

        Args:
            brand: brand color family name (must exist in Primitives)
            grey: grey color family name (must exist in Primitives)
            extra_tokens: dict of {path: {"light": (family, shade), "dark": (family, shade)}}
        """
        folder_num = 2 if self.tier < 4 else 3
        self._current_collection = "Semantic"

        all_paths = self._gather_semantic_paths()
        if extra_tokens:
            all_paths.extend(extra_tokens.keys())

        if self.tier < 4:
            # 2/3-Tier: Semantic has light/dark modes, aliases Primitives
            id_map = prebuild_ids(self, all_paths, NS_SEMANTIC)

            for mode in ["light", "dark"]:
                tree = self._build_semantic_mode(mode, brand, grey, "Primitives", id_map, all_paths)
                if extra_tokens:
                    for path, config in extra_tokens.items():
                        target = self._resolve_semantic_target(config[mode], brand, grey)
                        vid = self.resolve_id(id_map, path)
                        scope = config.get("scope")
                        t = self.create_token(path, NS_SEMANTIC, "color",
                                              alias_target=f"primitives/{target}",
                                              alias_set="Primitives", vid=vid, scope=scope)
                        self.nest_token(tree, path, t)
                self.save_mode(f"{folder_num}. Semantic", mode, tree)
        else:
            # 4-Tier: Semantic aliases Theme, single mode
            tree = {}
            for mapping in [SEMANTIC_SURFACE_MAP, SEMANTIC_TEXT_MAP,
                            SEMANTIC_BORDER_MAP, SEMANTIC_INTERACTIVE_MAP,
                            SEMANTIC_FEEDBACK_MAP, SEMANTIC_ICON_MAP,
                            SEMANTIC_OVERLAY_MAP, SEMANTIC_SHADOW_MAP]:
                for sem_path, config in mapping.items():
                    scope_override = config.get("scope") if isinstance(config, dict) and "scope" in config else None
                    t = self.create_token(
                        sem_path, NS_SEMANTIC, "color",
                        alias_target=f"theme/{sem_path}",
                        alias_set="Theme",
                        scope=scope_override,
                    )
                    self.nest_token(tree, sem_path, t)
            self.save_mode(f"{folder_num}. Semantic", "semantic", tree)

        self._current_collection = None

    def build_theme(self, brand, grey, extra_tokens=None):
        """
        Build the Theme collection (4-Tier only).
        Has light/dark modes, aliases Primitives.
        """
        if self.tier != 4:
            return

        self._current_collection = "Theme"
        all_paths = self._gather_semantic_paths()
        if extra_tokens:
            all_paths.extend(extra_tokens.keys())

        id_map = prebuild_ids(self, all_paths, NS_THEME)

        for mode in ["light", "dark"]:
            tree = self._build_semantic_mode(mode, brand, grey, "Primitives", id_map, all_paths)
            if extra_tokens:
                for path, config in extra_tokens.items():
                    target = self._resolve_semantic_target(config[mode], brand, grey)
                    vid = self.resolve_id(id_map, path)
                    t = self.create_token(path, NS_THEME, "color",
                                          alias_target=f"primitives/{target}",
                                          alias_set="Primitives", vid=vid)
                    self.nest_token(tree, path, t)
            self.save_mode("2. Theme", mode, tree)

        self._current_collection = None

    def build_responsive(self, scale="standard"):
        """
        Build the Responsive collection with mobile/tablet/desktop modes.
        """
        folder_num = self._next_folder_number()
        coll_name = f"{folder_num}. Responsive"
        self._current_collection = "Responsive"

        # Gather all responsive paths
        all_paths = []
        for role in RESPONSIVE_FONT_SIZE:
            all_paths.append(f"font/size/{role}")
        for role in RESPONSIVE_LINE_HEIGHT:
            all_paths.append(f"font/lineHeight/{role}")
        for role in RESPONSIVE_LETTER_SPACING:
            all_paths.append(f"font/letterSpacing/{role}")
        for name in RESPONSIVE_RADIUS:
            all_paths.append(f"radius/{name}")
        for name in RESPONSIVE_BORDER_WIDTH:
            all_paths.append(f"borderWidth/{name}")

        id_map = prebuild_ids(self, all_paths, NS_RESPONSIVE)

        for mode in ["mobile", "tablet", "desktop"]:
            tree = {}

            # Font sizes
            for role, modes in RESPONSIVE_FONT_SIZE.items():
                p = f"font/size/{role}"
                v = modes[mode]
                t = self.create_token(p, NS_RESPONSIVE, "number", value=v,
                                      alias_target=f"primitives/font/size/{v}",
                                      alias_set="Primitives",
                                      vid=self.resolve_id(id_map, p),
                                      scope=["FONT_SIZE"])
                self.nest_token(tree, p, t)

            # Line heights
            for role, modes in RESPONSIVE_LINE_HEIGHT.items():
                p = f"font/lineHeight/{role}"
                v = modes[mode]
                t = self.create_token(p, NS_RESPONSIVE, "number", value=v,
                                      alias_target=f"primitives/font/lineHeight/{v}",
                                      alias_set="Primitives",
                                      vid=self.resolve_id(id_map, p),
                                      scope=["LINE_HEIGHT"])
                self.nest_token(tree, p, t)

            # Letter spacing
            for role, modes in RESPONSIVE_LETTER_SPACING.items():
                p = f"font/letterSpacing/{role}"
                v = modes[mode]
                # Letter spacing uses named primitives
                ls_name = "normal"
                if v < 0:
                    ls_name = "tight" if v >= -2 else "tight"
                elif v > 0:
                    if v == 1:
                        ls_name = "wide"
                    elif v == 2:
                        ls_name = "wider"
                    elif v >= 4:
                        ls_name = "widest"
                t = self.create_token(p, NS_RESPONSIVE, "number", value=v,
                                      alias_target=f"primitives/font/letterSpacing/{ls_name}",
                                      alias_set="Primitives",
                                      vid=self.resolve_id(id_map, p),
                                      scope=["LETTER_SPACING"])
                self.nest_token(tree, p, t)

            # Radius
            for name, modes in RESPONSIVE_RADIUS.items():
                p = f"radius/{name}"
                v = modes[mode]
                t = self.create_token(p, NS_RESPONSIVE, "number", value=v,
                                      alias_target=f"primitives/radius/{name}",
                                      alias_set="Primitives",
                                      vid=self.resolve_id(id_map, p),
                                      scope=["CORNER_RADIUS"])
                self.nest_token(tree, p, t)

            # Border width (same across all modes)
            for name, v in RESPONSIVE_BORDER_WIDTH.items():
                p = f"borderWidth/{name}"
                t = self.create_token(p, NS_RESPONSIVE, "number", value=v,
                                      alias_target=f"primitives/borderwidth/{name}",
                                      alias_set="Primitives",
                                      vid=self.resolve_id(id_map, p),
                                      scope=["STROKE_FLOAT"])
                self.nest_token(tree, p, t)

            self.save_mode(coll_name, mode, tree)

        self._current_collection = None

    def build_density(self):
        """Build the Density collection with compact/comfortable/spacious modes."""
        folder_num = self._next_folder_number()
        coll_name = f"{folder_num}. Density"
        self._current_collection = "Density"

        all_paths = list(DENSITY_PADDING.keys()) + list(DENSITY_GAP.keys())
        id_map = prebuild_ids(self, all_paths, NS_DENSITY)

        for mode in ["compact", "comfortable", "spacious"]:
            tree = {}

            for path, modes in {**DENSITY_PADDING, **DENSITY_GAP}.items():
                v = modes[mode]
                t = self.create_token(path, NS_DENSITY, "number", value=v,
                                      alias_target=f"primitives/spacing/{v}",
                                      alias_set="Primitives",
                                      vid=self.resolve_id(id_map, path),
                                      scope=["GAP"])
                self.nest_token(tree, path, t)

            self.save_mode(coll_name, mode, tree)

        self._current_collection = None

    def build_layout(self):
        """Build the Layout collection with xs-xxl breakpoint modes."""
        folder_num = self._next_folder_number()
        coll_name = f"{folder_num}. Layout"
        self._current_collection = "Layout"

        layout_paths = ["column/count", "column/margin", "column/gutter",
                        "column/minWidth", "column/maxWidth"]
        id_map = prebuild_ids(self, layout_paths, NS_LAYOUT)

        for bp, props in DEFAULT_LAYOUT.items():
            tree = {}
            prop_map = {
                "column/count": ("columns", f"layout/{bp}/columns"),
                "column/margin": ("margin", f"layout/{bp}/margin"),
                "column/gutter": ("gutter", f"layout/{bp}/gutter"),
                "column/minWidth": ("minWidth", f"layout/{bp}/minWidth"),
                "column/maxWidth": ("maxWidth", f"layout/{bp}/maxWidth"),
            }
            for path, (_, prim_path) in prop_map.items():
                v = props[prop_map[path][0]]
                t = self.create_token(path, NS_LAYOUT, "number", value=v,
                                      alias_target=f"primitives/{prim_path}",
                                      alias_set="Primitives",
                                      vid=self.resolve_id(id_map, path),
                                      scope=["WIDTH_HEIGHT"])
                self.nest_token(tree, path, t)

            self.save_mode(coll_name, bp, tree)

        self._current_collection = None

    def build_effects(self):
        """Build the Effects collection (single mode)."""
        folder_num = self._next_folder_number()
        coll_name = f"{folder_num}. Effects"
        self._current_collection = "Effects"
        tree = {}

        # Shadow color targets depend on tier
        color_set = "Semantic" if self.tier < 4 else "Theme"

        for scale in ["sm", "md", "lg", "xl"]:
            # Shadow color → Semantic/Theme
            p = f"shadow/{scale}/color"
            t = self.create_token(p, NS_EFFECTS, "color",
                                  alias_target=f"{color_set.lower()}/shadow/{scale}/color",
                                  alias_set=color_set,
                                  scope=["EFFECT_COLOR"])
            self.nest_token(tree, p, t)

            # Shadow geometry → Primitives
            for prop in ["x", "y", "blur", "spread"]:
                p = f"shadow/{scale}/{prop}"
                t = self.create_token(p, NS_EFFECTS, "number",
                                      value=DEFAULT_SHADOW[scale][prop],
                                      alias_target=f"primitives/shadow/{scale}/{prop}",
                                      alias_set="Primitives",
                                      scope=["EFFECT_FLOAT"])
                self.nest_token(tree, p, t)

        # Blur tokens → Primitives
        for name in ["sm", "md", "lg", "xl"]:
            if name in DEFAULT_BLUR:
                p = f"blur/{name}"
                t = self.create_token(p, NS_EFFECTS, "number",
                                      value=DEFAULT_BLUR[name],
                                      alias_target=f"primitives/blur/{name}",
                                      alias_set="Primitives",
                                      scope=["EFFECT_FLOAT"])
                self.nest_token(tree, p, t)

        self.save_mode(coll_name, "effects", tree)
        self._current_collection = None

    def build_typography(self, body_font="sans", display_font="sans",
                         mono_font="mono", roles=None):
        """
        Build the Typography collection (single mode).

        Args:
            body_font: primitive font family key (e.g. "sans")
            display_font: primitive font family key (e.g. "sans")
            mono_font: primitive font family key (e.g. "mono")
            roles: dict of role configs or "standard"/"extended" preset
        """
        folder_num = self._next_folder_number()
        coll_name = f"{folder_num}. Typography"
        self._current_collection = "Typography"
        tree = {}

        role_config = roles if isinstance(roles, dict) else TYPOGRAPHY_ROLES_STANDARD

        for role, config in role_config.items():
            # Font size → Responsive
            p = f"{role}/fontSize"
            t = self.create_token(p, NS_TYPOGRAPHY, "number",
                                  value=14,
                                  alias_target=f"responsive/font/size/{role}",
                                  alias_set="Responsive",
                                  scope=["FONT_SIZE"])
            self.nest_token(tree, p, t)

            # Line height → Responsive
            if role in RESPONSIVE_LINE_HEIGHT:
                p = f"{role}/lineHeight"
                t = self.create_token(p, NS_TYPOGRAPHY, "number",
                                      value=20,
                                      alias_target=f"responsive/font/lineHeight/{role}",
                                      alias_set="Responsive",
                                      scope=["LINE_HEIGHT"])
                self.nest_token(tree, p, t)

            # Letter spacing → Responsive
            ls_role = role
            # Map specific roles to their responsive letterSpacing role
            ls_map = {"body-lg": "body", "body-sm": "body",
                      "label-lg": "body", "label": "body",
                      "label-sm": "caption", "code": "body",
                      "subheading": "body", "heading": "heading",
                      "display": "display"}
            ls_role = ls_map.get(role, role)
            if ls_role in RESPONSIVE_LETTER_SPACING:
                p = f"{role}/letterSpacing"
                t = self.create_token(p, NS_TYPOGRAPHY, "number",
                                      value=0,
                                      alias_target=f"responsive/font/letterSpacing/{ls_role}",
                                      alias_set="Responsive",
                                      scope=["LETTER_SPACING"])
                self.nest_token(tree, p, t)

            # Font family → Primitives
            font_key = config.get("fontFamily", "body")
            if font_key == "body":
                font_key = body_font
            elif font_key == "display":
                font_key = display_font
            elif font_key == "mono":
                font_key = mono_font
            p = f"{role}/fontFamily"
            t = self.create_token(p, NS_TYPOGRAPHY, "string",
                                  value="Inter",
                                  alias_target=f"primitives/font/family/{font_key}",
                                  alias_set="Primitives",
                                  scope=["FONT_FAMILY"])
            self.nest_token(tree, p, t)

            # Font weight → Primitives
            weight_key = config.get("fontWeight", "regular")
            p = f"{role}/fontWeight"
            t = self.create_token(p, NS_TYPOGRAPHY, "string",
                                  value="Regular",
                                  alias_target=f"primitives/font/weight/{weight_key}",
                                  alias_set="Primitives",
                                  scope=["FONT_STYLE"])
            self.nest_token(tree, p, t)

        # Typography color tokens → Semantic (2/3-Tier) or Theme (4-Tier)
        color_set = "Semantic" if self.tier < 4 else "Theme"
        for typo_path, sem_target in TYPOGRAPHY_COLOR_MAP.items():
            p = typo_path
            t = self.create_token(p, NS_TYPOGRAPHY, "color",
                                  alias_target=f"{color_set.lower()}/{sem_target}",
                                  alias_set=color_set,
                                  scope=["TEXT_FILL"])
            self.nest_token(tree, p, t)

        self.save_mode(coll_name, "typography", tree)
        self._current_collection = None

    def build_component_colors(self, components=None):
        """
        Build Component Colors collection (3/4-Tier only).

        Args:
            components: list of component names e.g. ["button", "input", "card"]
        """
        if self.tier < 3:
            return

        folder_num = self._next_folder_number()
        coll_name = f"{folder_num}. Component Colors"
        self._current_collection = "Component Colors"
        tree = {}

        components = components or ["button", "input", "card"]

        # Icon tokens
        icon_variants = {
            "default": {"fill": "icon/default", "stroke": "icon/default", "duotone": "icon/muted"},
            "brand":   {"fill": "icon/brand",   "stroke": "icon/brand",   "duotone": "icon/muted"},
            "muted":   {"fill": "icon/muted",   "stroke": "icon/muted",   "duotone": "icon/disabled"},
            "inverse": {"fill": "icon/inverse",  "duotone": "icon/muted"},
            "error":   {"fill": "icon/error",    "duotone": "icon/muted"},
            "success": {"fill": "icon/success",  "duotone": "icon/muted"},
            "warning": {"fill": "icon/warning",  "duotone": "icon/muted"},
        }
        for variant, targets in icon_variants.items():
            for sub, sem_target in targets.items():
                p = f"color/icon/{variant}/{sub}"
                scope = ["SHAPE_FILL"] if sub in ["fill", "duotone"] else ["STROKE"]
                t = self.create_token(p, NS_COMPONENT_COLORS, "color",
                                      alias_target=f"semantic/{sem_target}",
                                      alias_set="Semantic",
                                      scope=scope)
                self.nest_token(tree, p, t)

        # Divider tokens
        for name, target in [("default", "border/default"), ("subtle", "border/subtle")]:
            p = f"color/divider/{name}"
            t = self.create_token(p, NS_COMPONENT_COLORS, "color",
                                  alias_target=f"semantic/{target}",
                                  alias_set="Semantic",
                                  scope=["STROKE"])
            self.nest_token(tree, p, t)

        # Container tokens
        containers = {
            "default": "surface/card", "raised": "surface/raised",
            "sunken": "surface/sunken", "brand": "surface/brand",
            "overlay": "surface/overlay",
        }
        for name, target in containers.items():
            p = f"color/container/{name}"
            t = self.create_token(p, NS_COMPONENT_COLORS, "color",
                                  alias_target=f"semantic/{target}",
                                  alias_set="Semantic",
                                  scope=["FRAME_FILL", "SHAPE_FILL"])
            self.nest_token(tree, p, t)

        # Per-component tokens
        for comp in components:
            self._build_component_tokens(tree, comp)

        self.save_mode(coll_name, "component-colors", tree)
        self._current_collection = None

    def _build_component_tokens(self, tree, component):
        """Generate standard component color tokens."""
        variants = {
            "primary": {
                "default": {"bg": "interactive/primary/default", "text": "interactive/primary/text", "border": "interactive/primary/border", "icon": "icon/inverse"},
                "hover":   {"bg": "interactive/primary/hover",   "text": "interactive/primary/text", "border": "interactive/primary/border"},
                "pressed": {"bg": "interactive/primary/pressed"},
                "focused": {"border": "border/focus"},
                "disabled":{"bg": "interactive/primary/disabled","text": "text/disabled", "border": "border/disabled"},
            },
            "secondary": {
                "default": {"bg": "interactive/secondary/default","text": "interactive/secondary/text","border": "interactive/secondary/border"},
                "hover":   {"bg": "interactive/secondary/hover",  "text": "interactive/secondary/text","border": "interactive/secondary/border"},
                "pressed": {"bg": "interactive/secondary/pressed"},
                "disabled":{"bg": "interactive/secondary/disabled","text": "text/disabled","border": "border/disabled"},
            },
        }
        if component == "button":
            variants["ghost"] = {
                "default": {"text": "interactive/ghost/text"},
                "hover":   {"bg": "interactive/ghost/hover", "text": "interactive/ghost/text"},
                "pressed": {"bg": "interactive/ghost/pressed"},
            }
            variants["danger"] = {
                "default": {"bg": "interactive/destructive/default", "text": "interactive/destructive/text", "border": "interactive/destructive/border"},
                "hover":   {"bg": "interactive/destructive/hover",   "text": "interactive/destructive/text"},
                "pressed": {"bg": "interactive/destructive/pressed"},
                "disabled":{"bg": "interactive/destructive/disabled","text": "text/disabled","border": "border/disabled"},
            }

        for variant_name, states in variants.items():
            for state, parts in states.items():
                for part, sem_target in parts.items():
                    p = f"color/{component}/{variant_name}/{state}/{part}"
                    if part in ["bg", "background"]:
                        scope = ["FRAME_FILL", "SHAPE_FILL"]
                        real_part = "background"
                    elif part == "text":
                        scope = ["TEXT_FILL"]
                        real_part = "text"
                    elif part == "border":
                        scope = ["STROKE"]
                        real_part = "border"
                    elif part == "icon":
                        scope = ["SHAPE_FILL", "STROKE"]
                        real_part = "icon"
                    else:
                        scope = None
                        real_part = part

                    p = f"color/{component}/{variant_name}/{state}/{real_part}"
                    t = self.create_token(p, NS_COMPONENT_COLORS, "color",
                                          alias_target=f"semantic/{sem_target}",
                                          alias_set="Semantic",
                                          scope=scope)
                    self.nest_token(tree, p, t)

    def build_component_dimensions(self):
        """Build Component Dimensions collection (3/4-Tier only)."""
        if self.tier < 3:
            return

        folder_num = self._next_folder_number()
        coll_name = f"{folder_num}. Component Dimensions"
        self._current_collection = "Component Dimensions"
        tree = {}

        # Padding/Gap → Density
        for path in DENSITY_PADDING:
            p = f"dimensions/{path}"
            t = self.create_token(p, NS_COMPONENT_DIMENSIONS, "number",
                                  value=8,
                                  alias_target=f"density/{path}",
                                  alias_set="Density",
                                  scope=["GAP"])
            self.nest_token(tree, p, t)

        for path in DENSITY_GAP:
            p = f"dimensions/{path}"
            t = self.create_token(p, NS_COMPONENT_DIMENSIONS, "number",
                                  value=8,
                                  alias_target=f"density/{path}",
                                  alias_set="Density",
                                  scope=["GAP"])
            self.nest_token(tree, p, t)

        # Radius → Responsive
        for name in DEFAULT_RADIUS:
            p = f"dimensions/radius/{name}"
            t = self.create_token(p, NS_COMPONENT_DIMENSIONS, "number",
                                  value=DEFAULT_RADIUS[name],
                                  alias_target=f"responsive/radius/{name}",
                                  alias_set="Responsive",
                                  scope=["CORNER_RADIUS"])
            self.nest_token(tree, p, t)

        # Border width → Responsive
        for name in DEFAULT_BORDER_WIDTH:
            p = f"dimensions/border/width/{name}"
            t = self.create_token(p, NS_COMPONENT_DIMENSIONS, "number",
                                  value=DEFAULT_BORDER_WIDTH[name],
                                  alias_target=f"responsive/borderWidth/{name}",
                                  alias_set="Responsive",
                                  scope=["STROKE_FLOAT"])
            self.nest_token(tree, p, t)

        self.save_mode(coll_name, "component-dimensions", tree)
        self._current_collection = None

    # ─── ZIP Builder ───────────────────────────────────────────────────────

    def build_zip(self, output_dir=None, filename="design-tokens"):
        """
        Build ZIP from all saved mode files.
        Prints a generation report with auto-fixes and remaining errors.
        """
        # Print generation report
        self._print_report()

        buf = BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for filepath, tree in self.output_files.items():
                zf.writestr(filepath, json.dumps(tree, indent=2))

        zip_bytes = buf.getvalue()

        if output_dir is None:
            output_dir = "exports"

        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            base_path = os.path.join(output_dir, f"{filename}.zip")
            if not os.path.exists(base_path):
                final_path = base_path
            else:
                counter = 1
                while True:
                    candidate = os.path.join(
                        output_dir, f"{filename} ({counter}).zip")
                    if not os.path.exists(candidate):
                        final_path = candidate
                        break
                    counter += 1
            with open(final_path, 'wb') as f:
                f.write(zip_bytes)
            abs_path = os.path.abspath(final_path)
            print(f"\n{'=' * 50}")
            print(f"  ZIP saved: {abs_path}")
            print(f"  Size: {len(zip_bytes):,} bytes")
            print(f"  Collections: {len(self.output_files)} files")
            print(f"{'=' * 50}\n")
            return zip_bytes, final_path

        return zip_bytes

    def _print_report(self):
        """Print generation report with warnings and errors."""
        print(f"\n{'━' * 60}")
        print("  GENERATION REPORT")
        print(f"{'━' * 60}")

        if self._warnings:
            print(f"\n  AUTO-FIXED ({len(self._warnings)}):")
            for w in self._warnings[:20]:
                print(f"    ✓ {w}")
            if len(self._warnings) > 20:
                print(f"    ...and {len(self._warnings) - 20} more")

        if self._errors:
            print(f"\n  ERRORS ({len(self._errors)}) — ZIP generated but may have broken aliases:")
            for e in self._errors[:30]:
                print(f"    ✗ {e}")
            if len(self._errors) > 30:
                print(f"    ...and {len(self._errors) - 30} more")

        if not self._warnings and not self._errors:
            print("\n  ✅ All tokens generated successfully. No issues found.")

        scope_count = len(self.token_registry)
        print(f"\n  Total tokens in registry: {scope_count}")
        print(f"  Total files: {len(self.output_files)}")
        print(f"{'━' * 60}\n")

    # ─── Folder Number Tracking ────────────────────────────────────────────

    def _next_folder_number(self):
        """Get the next folder number based on what's already saved."""
        max_num = 0
        for filepath in self.output_files:
            folder = filepath.split("/", 1)[0]
            if ". " in folder:
                try:
                    num = int(folder.split(". ", 1)[0])
                    max_num = max(max_num, num)
                except ValueError:
                    pass
        return max_num + 1

    # ─── Validation ────────────────────────────────────────────────────────

    def verify_chain_completeness(self):
        """Recursive alias chain verification."""
        broken = []
        for filename, data in self.output_files.items():
            self._walk_aliases(data, filename, broken)
        if broken:
            raise ValueError(
                f"CHAIN BREAK: {len(broken)} broken alias links:\n" +
                "\n".join(f"  ✗ {b}" for b in broken[:20]) +
                (f"\n  ...and {len(broken)-20} more" if len(broken) > 20 else "")
            )
        return True

    def _walk_aliases(self, node, context, broken):
        if isinstance(node, dict):
            ad = node.get("$extensions", {}).get("com.figma.aliasData")
            if ad:
                vid = ad.get("targetVariableId", "")
                name = ad.get("targetVariableName", "")
                if vid == "VariableID:0:0" or not vid:
                    broken.append(f"{context}: '{name}' → UNRESOLVED (0:0)")
                elif name and self.canonical_path(name) not in self.token_registry:
                    broken.append(f"{context}: '{name}' → NOT IN REGISTRY")
            for key, val in node.items():
                if not key.startswith("$"):
                    self._walk_aliases(val, f"{context}/{key}", broken)

    def flatten_emitted_paths(self):
        """Returns {collection_set_name: set(paths)} from emitted JSON."""
        emitted = {}
        for filepath, data in self.output_files.items():
            folder = filepath.split("/", 1)[0]
            collection_name = folder.split(". ", 1)[1] if ". " in folder else folder
            path_set = emitted.setdefault(collection_name, set())
            self._walk_paths(data, "", path_set)
        return emitted

    def verify_emitted_alias_targets(self):
        """Validates alias targets against emitted JSON artifact."""
        emitted = self.flatten_emitted_paths()
        broken = []
        for filepath, data in self.output_files.items():
            self._walk_emitted_aliases(data, filepath, emitted, broken)
        if broken:
            raise ValueError(
                f"EMITTED ARTIFACT BREAK: {len(broken)} invalid targets:\n" +
                "\n".join(f"  ✗ {b}" for b in broken[:20]) +
                (f"\n  ...and {len(broken)-20} more" if len(broken) > 20 else "")
            )
        return True

    def verify_emitted_scope_families(self):
        """Checks scope families on emitted artifact using get_scope()."""
        broken = []
        for filepath, data in self.output_files.items():
            self._walk_scopes(data, filepath, broken)
        if broken:
            raise ValueError(
                f"SCOPE BREAK: {len(broken)} emitted scope mismatches:\n" +
                "\n".join(f"  ✗ {b}" for b in broken[:20]) +
                (f"\n  ...and {len(broken)-20} more" if len(broken) > 20 else "")
            )
        return True

    def _walk_paths(self, node, prefix, out):
        if isinstance(node, dict):
            if "$value" in node:
                if prefix:
                    out.add(self.canonical_path(prefix))
                return
            for key, val in node.items():
                if key.startswith("$"):
                    continue
                next_prefix = f"{prefix}/{key}" if prefix else key
                self._walk_paths(val, next_prefix, out)

    def _walk_emitted_aliases(self, node, context, emitted, broken):
        if isinstance(node, dict):
            ad = node.get("$extensions", {}).get("com.figma.aliasData")
            if ad:
                target_set = ad.get("targetVariableSetName", "")
                target_name = self.canonical_path(ad.get("targetVariableName", ""))
                if target_set and target_name:
                    collection_paths = emitted.get(target_set)
                    if collection_paths is None:
                        broken.append(f"{context}: target set '{target_set}' missing from ZIP")
                    elif target_name not in collection_paths:
                        broken.append(f"{context}: '{target_name}' missing from '{target_set}'")
            for key, val in node.items():
                if not key.startswith("$"):
                    self._walk_emitted_aliases(val, f"{context}/{key}", emitted, broken)

    def _walk_scopes(self, node, context, broken):
        """Walk emitted JSON and verify scopes using the SAME get_scope() function."""
        if isinstance(node, dict):
            if "$value" in node:
                token_type = node.get("$type")
                scopes = node.get("$extensions", {}).get("com.figma.scopes", [])
                # Extract the token path from context: strip "N. Collection/mode.tokens.json/"
                parts = context.split("/")
                # Skip until we pass the collection folder and mode file
                # e.g., "1. Primitives/primitives.tokens.json/color/blue/500"
                # → token path = "color/blue/500"
                path_start = 0
                for i, part in enumerate(parts):
                    if part.endswith(".tokens.json"):
                        path_start = i + 1
                        break
                token_path = "/".join(parts[path_start:])
                if not token_path:
                    return

                # Determine if this is a primitive (collection folder starts with "1. Primitives")
                is_prim = "Primitives" in parts[0] if parts else False
                expected = get_scope(token_path, token_type, is_primitive=is_prim)
                # Skip validation when get_scope returns a generic fallback
                # (meaning the path is ambiguous and the builder knows best)
                FALLBACK_COLOR = ["FRAME_FILL", "SHAPE_FILL"]
                FALLBACK_NUMBER = ["WIDTH_HEIGHT"]
                is_fallback = (expected == FALLBACK_COLOR or expected == FALLBACK_NUMBER)
                if expected is not None and not is_fallback and sorted(scopes) != sorted(expected):
                    broken.append(f"{context}: expected {expected}, got {scopes}")
                return
            for key, val in node.items():
                if not key.startswith("$"):
                    self._walk_scopes(val, f"{context}/{key}", broken)

    def validate_responsive_coverage(self, resp_size, resp_lh, resp_ls=None):
        """Pre-flight audit for Responsive -> Primitive coverage."""
        missing = []
        for role, modes in resp_size.items():
            for v in (modes if isinstance(modes, list) else modes.values()):
                target = self.canonical_path(f"font/size/{v}")
                if target not in self.token_registry:
                    missing.append(target)
        for role, modes in resp_lh.items():
            for v in (modes if isinstance(modes, list) else modes.values()):
                candidates = [
                    self.canonical_path(f"font/lineHeight/{v}"),
                    self.canonical_path(f"font/lineheight/{v}"),
                ]
                if not any(c in self.token_registry for c in candidates):
                    missing.append(candidates[0])
        if missing:
            raise KeyError(
                f"BACKFILL REQUIRED: Missing paths in Primitives: "
                f"{list(set(missing))}")

    def validate_semantic_coverage(self, cc_map, sem_registry):
        """Pre-flight audit for Component Colors -> Semantic coverage."""
        missing = []
        for cc_path, target_sem_path in cc_map.items():
            clean_target = self.canonical_path(target_sem_path)
            if clean_target.startswith("semantic/"):
                clean_target = clean_target.replace("semantic/", "", 1)
            if clean_target not in sem_registry:
                missing.append(f"{cc_path} -> {target_sem_path}")
        if missing:
            raise KeyError(
                f"SEMANTIC GAP: Component tokens alias non-existent "
                f"Semantic paths: {missing}")

    def verify_all_aliases(self):
        """Cross-collection verification gate."""
        self.verify_chain_completeness()
        self.verify_emitted_alias_targets()
        self.verify_emitted_scope_families()
        return True


# ─── Standalone Helpers ────────────────────────────────────────────────────────

def prebuild_ids(gen, paths, ns):
    """
    Call ONCE before building any mode in a multi-mode collection.
    Returns {path: variableId} — pass this map into every mode builder.
    """
    id_map = {}
    for path in paths:
        id_map[gen.canonical_path(path)] = gen.next_id(ns)
    return id_map


def make_family(gen, tree, family, shades, alpha_hex,
                scope=None, hidden_from_publishing=False):
    """
    Generate a full colour family (shades + alpha variants).
    shades: list of (key, hex_str). alpha_hex: base hex for alpha variants.
    scope: list of Figma scopes (e.g. ["ALL_FILLS"] for Primitives).
    hidden_from_publishing: bool for parent collections.
    """
    for key, h in shades:
        r = int(h[1:3], 16) / 255
        g = int(h[3:5], 16) / 255
        b = int(h[5:7], 16) / 255
        token = gen.create_token(
            f"color/{family}/{key}", NS_PRIMITIVES, "color",
            value={"colorSpace": "srgb", "components": [r, g, b],
                   "alpha": 1, "hex": h},
            scope=scope,
            hidden_from_publishing=hidden_from_publishing)
        gen.nest_token(tree, f"color/{family}/{key}", token)

    ar = int(alpha_hex[1:3], 16) / 255
    ag = int(alpha_hex[3:5], 16) / 255
    ab = int(alpha_hex[5:7], 16) / 255
    for a_val, a_key in DEFAULT_ALPHA_STEPS:
        path = f"color/{family}/{a_key}"
        token = gen.create_token(
            path, NS_PRIMITIVES, "color",
            value={"colorSpace": "srgb", "components": [ar, ag, ab],
                   "alpha": a_val, "hex": alpha_hex},
            scope=scope,
            hidden_from_publishing=hidden_from_publishing)
        gen.nest_token(tree, path, token)

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from generator_core import DesignTokenGenerator, prebuild_ids, get_scope


def token_color():
    return {"colorSpace": "srgb", "components": [0, 0, 0], "alpha": 1, "hex": "#000000"}


# ─── Legacy Tests (Layer 1 API) ────────────────────────────────────────────────

def build_scope_fixture():
    """Tests that manual create_token with explicit scopes passes validation."""
    gen = DesignTokenGenerator("Fixture", syntax_format="camel", platforms=["WEB"])

    primitives = {}
    for path in [
        "color/brand/500",
        "color/grey/900",
        "color/grey/200",
        "color/white",
        "color/black/a32",
        "font/size/16",
        "font/lineHeight/24",
        "font/letterSpacing/normal",
    ]:
        token_type = "number" if path.startswith("font/") else "color"
        value = 16 if path == "font/size/16" else 24 if path == "font/lineHeight/24" else 0 if path == "font/letterSpacing/normal" else token_color()
        if token_type == "color":
            scope = ["ALL_FILLS"]
        elif path.startswith("font/size/"):
            scope = ["FONT_SIZE"]
        elif path.startswith("font/lineHeight/"):
            scope = ["LINE_HEIGHT"]
        else:
            scope = ["LETTER_SPACING"]
        token = gen.create_token(path, 10, token_type, value=value, scope=scope,
                                 hidden_from_publishing=True)
        gen.nest_token(primitives, path, token)
    gen.save_mode("1. Primitives", "primitives", primitives)

    theme = {}
    theme_cases = [
        ("text/primary", ["TEXT_FILL"], "color/grey/900"),
        ("text/on-brand", ["TEXT_FILL"], "color/white"),
        ("border/default", ["STROKE"], "color/grey/200"),
        ("icon/default", ["SHAPE_FILL", "STROKE"], "color/brand/500"),
        ("overlay/scrim", ["ALL_FILLS"], "color/black/a32"),
        ("shadow/sm/color", ["EFFECT_COLOR"], "color/black/a32"),
    ]
    for path, scope, target in theme_cases:
        token = gen.create_token(path, 40, "color", value=token_color(), scope=scope,
                                 alias_target=f"primitives/{target}", alias_set="Primitives",
                                 target_registry=gen.token_registry,
                                 hidden_from_publishing=True)
        gen.nest_token(theme, path, token)
    gen.save_mode("2. Theme", "light", theme)

    responsive = {}
    resp_cases = [
        ("font/size/body", ["FONT_SIZE"], "font/size/16", 16),
        ("font/lineHeight/body", ["LINE_HEIGHT"], "font/lineHeight/24", 24),
        ("font/letterSpacing/body", ["LETTER_SPACING"], "font/letterSpacing/normal", 0),
    ]
    ids = prebuild_ids(gen, [case[0] for case in resp_cases], 20)
    for path, scope, target, value in resp_cases:
        token = gen.create_token(path, 20, "number", value=value, scope=scope,
                                 alias_target=f"primitives/{target}", alias_set="Primitives",
                                 target_registry=gen.token_registry,
                                 hidden_from_publishing=True,
                                 vid=gen.resolve_id(ids, path))
        gen.nest_token(responsive, path, token)
    gen.save_mode("3. Responsive", "mobile", responsive)

    gen.verify_all_aliases()


def build_identity_fixture():
    """Tests that emitted path identity matches registry."""
    gen = DesignTokenGenerator("Fixture", syntax_format="camel", platforms=["WEB"])

    primitives = {}
    base = gen.create_token("color/brand/500", 10, "color", value=token_color(),
                            scope=["ALL_FILLS"], hidden_from_publishing=True)
    gen.nest_token(primitives, "color/brand/500", base)
    gen.save_mode("1. Primitives", "primitives", primitives)

    theme = {}
    ids = prebuild_ids(gen, ["text/on-brand", "text/link-hover", "surface/brand-subtle"], 40)
    cases = [
        ("text/on-brand", "color/brand/500"),
        ("text/link-hover", "color/brand/500"),
        ("surface/brand-subtle", "color/brand/500"),
    ]
    for path, target in cases:
        token = gen.create_token(path, 40, "color", value=token_color(),
                                 scope=["TEXT_FILL"] if path.startswith("text/") else ["FRAME_FILL", "SHAPE_FILL"],
                                 alias_target=f"primitives/{target}", alias_set="Primitives",
                                 target_registry=gen.token_registry,
                                 hidden_from_publishing=True,
                                 vid=gen.resolve_id(ids, path))
        gen.nest_token(theme, path, token)
    gen.save_mode("2. Theme", "light", theme)

    emitted = gen.flatten_emitted_paths()
    assert "text/on-brand" in emitted["Theme"]
    assert "text/link-hover" in emitted["Theme"]
    assert "surface/brand-subtle" in emitted["Theme"]
    gen.verify_all_aliases()


# ─── Auto-Scope Tests ──────────────────────────────────────────────────────────

def test_auto_scope():
    """Tests that get_scope() returns correct scopes for known path patterns."""
    test_cases = [
        # (path, type, is_primitive, expected)
        ("color/blue/500", "color", True, ["ALL_FILLS"]),
        ("text/primary", "color", False, ["TEXT_FILL"]),
        ("border/default", "color", False, ["STROKE"]),
        ("icon/default", "color", False, ["SHAPE_FILL", "STROKE"]),
        ("surface/brand", "color", False, ["FRAME_FILL", "SHAPE_FILL"]),
        ("overlay/scrim", "color", False, ["ALL_FILLS"]),
        ("shadow/sm/color", "color", False, ["EFFECT_COLOR"]),
        ("interactive/primary/text", "color", False, ["TEXT_FILL"]),
        ("interactive/primary/border", "color", False, ["STROKE"]),
        ("interactive/primary/default", "color", False, ["FRAME_FILL", "SHAPE_FILL"]),
        ("interactive/link/default", "color", False, ["TEXT_FILL"]),
        ("feedback/error/icon", "color", False, ["SHAPE_FILL", "STROKE"]),
        ("feedback/error/text", "color", False, ["TEXT_FILL"]),
        ("feedback/error/border", "color", False, ["STROKE"]),
        ("font/size/16", "number", True, ["FONT_SIZE"]),
        ("font/lineHeight/24", "number", True, ["LINE_HEIGHT"]),
        ("font/letterSpacing/normal", "number", True, ["LETTER_SPACING"]),
        ("spacing/16", "number", True, ["GAP"]),
        ("radius/md", "number", True, ["CORNER_RADIUS"]),
        ("borderwidth/sm", "number", True, ["STROKE_FLOAT"]),
        ("blur/md", "number", True, ["EFFECT_FLOAT"]),
        ("shadow/sm/y", "number", False, ["EFFECT_FLOAT"]),
        ("font/family/sans", "string", False, ["FONT_FAMILY"]),
        ("font/weight/bold", "string", False, ["FONT_STYLE"]),
    ]

    for path, typ, is_prim, expected in test_cases:
        result = get_scope(path, typ, is_primitive=is_prim)
        assert result == expected, f"get_scope('{path}', '{typ}', {is_prim}): expected {expected}, got {result}"

    print("  ✅ Auto-scope derivation: all patterns correct")


# ─── Auto-Hide Tests ──────────────────────────────────────────────────────────

def test_auto_hide():
    """Tests that hiddenFromPublishing is auto-derived from tier + collection."""
    gen = DesignTokenGenerator("Test", tier=3)
    gen._current_collection = "Primitives"
    assert gen._should_hide("Primitives") == True, "Primitives should be hidden in 3-tier"

    gen._current_collection = "Semantic"
    assert gen._should_hide("Semantic") == True, "Semantic should be hidden in 3-tier"

    gen._current_collection = "Component Colors"
    assert gen._should_hide("Component Colors") == False, "CC should be visible in 3-tier"

    gen2 = DesignTokenGenerator("Test", tier=2)
    assert gen2._should_hide("Primitives") == True, "Primitives hidden in 2-tier"
    assert gen2._should_hide("Semantic") == False, "Semantic visible in 2-tier"

    gen4 = DesignTokenGenerator("Test", tier=4)
    assert gen4._should_hide("Theme") == True, "Theme hidden in 4-tier"
    assert gen4._should_hide("Semantic") == True, "Semantic hidden in 4-tier"
    assert gen4._should_hide("Component Colors") == False, "CC visible in 4-tier"

    print("  ✅ Auto-hide derivation: all tiers correct")


# ─── Auto-Backfill Tests ──────────────────────────────────────────────────────

def test_auto_backfill():
    """Tests that missing number primitives are auto-backfilled."""
    gen = DesignTokenGenerator("Test", tier=3)

    # Manually create minimal primitives
    tree = {}
    gen._current_collection = "Primitives"
    gen._is_primitive_context = True
    t = gen.create_token("spacing/16", 10, "number", value=16,
                         scope=["GAP"], hidden_from_publishing=True)
    gen.nest_token(tree, "spacing/16", t)
    gen.save_mode("1. Primitives", "primitives", tree)
    gen._is_primitive_context = False

    # Now create a token aliasing a missing primitive — should auto-backfill
    gen._current_collection = "Density"
    sem_tree = {}
    t = gen.create_token("padding/x/md", 50, "number", value=12,
                         alias_target="primitives/spacing/12",
                         alias_set="Primitives")
    gen.nest_token(sem_tree, "padding/x/md", t)

    # Verify backfill happened
    assert "spacing/12" in gen.token_registry, "spacing/12 should have been auto-backfilled"
    assert len(gen._warnings) > 0, "Should have logged a backfill warning"
    assert any("spacing/12" in w for w in gen._warnings), "Warning should mention spacing/12"

    print("  ✅ Auto-backfill: missing number primitives created automatically")


# ─── Builder API Tests ─────────────────────────────────────────────────────────

def test_builders_3tier():
    """Full integration test using the builder API for a 3-tier system."""
    gen = DesignTokenGenerator("TestBrand", tier=3, syntax_format="css")

    azure = [
        ("50", "#F0F5FF"), ("100", "#D6E4FF"), ("200", "#ADC8FF"),
        ("300", "#84A9FF"), ("400", "#6690FF"), ("500", "#3B82F6"),
        ("600", "#2563EB"), ("700", "#1D4ED8"), ("800", "#1E40AF"),
        ("900", "#1E3A8A"), ("950", "#172554"),
    ]

    gen.build_primitives(brand_colors={"azure": azure}, grey_family="slate")
    gen.build_semantic(brand="azure", grey="slate")
    gen.build_responsive()
    gen.build_density()
    gen.build_layout()
    gen.build_effects()
    gen.build_typography(body_font="sans", display_font="sans", mono_font="mono")
    gen.build_component_colors(components=["button", "input", "card"])
    gen.build_component_dimensions()

    gen.verify_all_aliases()

    emitted = gen.flatten_emitted_paths()
    assert "Primitives" in emitted
    assert "Semantic" in emitted
    assert "Responsive" in emitted
    assert "Density" in emitted
    assert "Layout" in emitted
    assert "Effects" in emitted
    assert "Typography" in emitted
    assert "Component Colors" in emitted
    assert "Component Dimensions" in emitted
    assert len(emitted["Semantic"]) >= 55, f"Semantic floor: expected >=55 tokens, got {len(emitted['Semantic'])}"

    print(f"  ✅ Builder API 3-tier: {len(gen.token_registry)} tokens, all chains valid")


def test_builders_mixed():
    """Tests mixing builder methods with manual create_token calls."""
    gen = DesignTokenGenerator("Mixed", tier=3, syntax_format="css")

    blue = [
        ("50", "#EFF6FF"), ("100", "#DBEAFE"), ("200", "#BFDBFE"),
        ("300", "#93C5FD"), ("400", "#60A5FA"), ("500", "#3B82F6"),
        ("600", "#2563EB"), ("700", "#1D4ED8"), ("800", "#1E40AF"),
        ("900", "#1E3A8A"), ("950", "#172554"),
    ]

    # Use builder for standard collections
    gen.build_primitives(brand_colors={"blue": blue}, grey_family="slate")
    gen.build_semantic(brand="blue", grey="slate")

    # Use manual create_token for a custom collection
    gen._current_collection = "Team Colors"
    custom = {}
    t = gen.create_token("team/primary", 90, "color",
                         alias_target="primitives/color/blue/500",
                         alias_set="Primitives",
                         scope=["ALL_FILLS"])
    gen.nest_token(custom, "team/primary", t)
    gen.save_mode("10. Team Colors", "default", custom)
    gen._current_collection = None

    # Registry should have both builder and manual tokens
    assert "team/primary" in gen.token_registry

    print("  ✅ Mixed mode: builders + manual create_token work together")


# ─── Batch Error Reporting Tests ───────────────────────────────────────────────

def test_batch_errors():
    """Tests that missing color primitives are collected, not crashed."""
    gen = DesignTokenGenerator("Test", tier=3)

    tree = {}
    gen._current_collection = "Primitives"
    gen._is_primitive_context = True
    t = gen.create_token("color/blue/500", 10, "color",
                         value=token_color(), scope=["ALL_FILLS"],
                         hidden_from_publishing=True)
    gen.nest_token(tree, "color/blue/500", t)
    gen.save_mode("1. Primitives", "primitives", tree)
    gen._is_primitive_context = False

    # Now create a token pointing to a NON-EXISTENT color primitive
    gen._current_collection = "Semantic"
    sem = {}
    t = gen.create_token("surface/brand", 60, "color",
                         alias_target="primitives/color/purple/500",
                         alias_set="Primitives")
    gen.nest_token(sem, "surface/brand", t)

    # Should NOT crash — should collect error
    assert len(gen._errors) > 0, "Should have collected an error"
    assert any("purple/500" in e for e in gen._errors), "Error should mention purple/500"

    print("  ✅ Batch errors: missing color collected, not crashed")


def main():
    print("\n📋 Running generator_core regression tests...\n")

    build_scope_fixture()
    print("  ✅ Legacy scope fixture: passed")

    build_identity_fixture()
    print("  ✅ Legacy identity fixture: passed")

    test_auto_scope()
    test_auto_hide()
    test_auto_backfill()
    test_batch_errors()
    test_builders_3tier()
    test_builders_mixed()

    print("\n✅ ALL TESTS PASSED\n")


if __name__ == "__main__":
    main()

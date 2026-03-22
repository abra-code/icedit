#!/usr/bin/env python3

import argparse
import os
import shutil
import sys
import tempfile
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from icon_editor.core import IconEditor
from icon_editor.icon_validator import validate_icon


def create_test_svg(temp_dir: str, name: str, shape: str = "circle") -> str:
    svg_path = os.path.join(temp_dir, f"{name}.svg")
    if shape == "circle":
        content = '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/></svg>'
    elif shape == "rect":
        content = '<svg xmlns="http://www.w3.org/2000/svg"><rect x="10" y="10" width="80" height="80"/></svg>'
    elif shape == "heart":
        content = '<svg width="768" height="768" viewBox="0.00 29.00 768.00 709.99" xmlns="http://www.w3.org/2000/svg"><path d="M0.00,262.57 C0.00,427.31 138.05,589.34 356.16,728.56 C364.28,733.58 375.88,739.00 384.00,739.00 C392.12,739.00 403.72,733.58 412.23,728.56 C629.95,589.34 768.00,427.31 768.00,262.57 C768.00,125.68 674.03,29.00 548.74,29.00 C477.20,29.00 419.19,63.03 384.00,115.24 C349.58,63.42 290.80,29.00 219.26,29.00 C93.97,29.00 0.00,125.68 0.00,262.57 Z M62.26,262.57 C62.26,159.71 128.77,91.26 218.49,91.26 C291.19,91.26 332.95,136.51 357.70,175.18 C368.15,190.65 374.72,194.90 384.00,194.90 C393.28,194.90 399.08,190.26 410.30,175.18 C436.98,137.28 477.20,91.26 549.51,91.26 C639.23,91.26 705.74,159.71 705.74,262.57 C705.74,406.43 553.76,561.50 392.12,669.00 C388.25,671.71 385.55,673.64 384.00,673.64 C382.45,673.64 379.75,671.71 376.27,669.00 C214.24,561.50 62.26,406.43 62.26,262.57 Z " fill="currentColor"/></svg>'
    else:
        content = '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="30"/></svg>'

    with open(svg_path, "w") as f:
        f.write(content)
    return svg_path


def test_icon_variants(output_dir: Optional[str] = None, skip_validation: bool = False):
    if output_dir:
        temp_dir = output_dir
        os.makedirs(temp_dir, exist_ok=True)
        cleanup_temp_dir = False
    else:
        temp_dir = tempfile.mkdtemp()
        cleanup_temp_dir = True

    results = []

    try:
        svg_circle = create_test_svg(temp_dir, "circle", "circle")
        svg_heart = create_test_svg(temp_dir, "heart", "heart")

        test_cases = [
            (
                "basic_shared",
                "Basic icon with shared platform",
                lambda: IconEditor.create_new(
                    os.path.join(temp_dir, "basic_shared.icon"), "blue"
                ),
            ),
            (
                "glass_effect",
                "Icon with glass effect",
                lambda: _create_glass_effect(temp_dir, svg_circle),
            ),
            (
                "blend_mode",
                "Icon with blend mode",
                lambda: _create_blend_mode(temp_dir, svg_circle),
            ),
            (
                "shadow",
                "Icon with shadow",
                lambda: _create_shadow(temp_dir, svg_circle),
            ),
            (
                "translucency",
                "Icon with translucency",
                lambda: _create_translucency(temp_dir, svg_circle),
            ),
            (
                "multiple_layers",
                "Icon with multiple layers",
                lambda: _create_multiple_layers(temp_dir, svg_circle, svg_heart),
            ),
            (
                "scale_shift",
                "Icon with scale and shift",
                lambda: _create_scale_shift(temp_dir, svg_circle),
            ),
            (
                "solid_color",
                "Icon with solid color fill",
                lambda: _create_solid_color(temp_dir, svg_circle),
            ),
            (
                "auto_gradient",
                "Icon with automatic gradient",
                lambda: _create_auto_gradient(temp_dir, svg_circle),
            ),
            (
                "explicit_gradient",
                "Icon with explicit gradient",
                lambda: _create_explicit_gradient(temp_dir, svg_circle),
            ),
            (
                "bg_solid_layer_solid",
                "Background solid, layer solid",
                lambda: _create_bg_solid_layer_solid(temp_dir, svg_circle),
            ),
            (
                "bg_gradient_layer_solid",
                "Background gradient, layer solid",
                lambda: _create_bg_gradient_layer_solid(temp_dir, svg_circle),
            ),
            (
                "bg_solid_layer_gradient",
                "Background solid, layer gradient",
                lambda: _create_bg_solid_layer_gradient(temp_dir, svg_circle),
            ),
            (
                "bg_gradient_layer_gradient",
                "Background gradient, layer gradient",
                lambda: _create_bg_gradient_layer_gradient(temp_dir, svg_circle),
            ),
        ]

        for test_name, description, create_fn in test_cases:
            print(f"\n{'=' * 60}")
            print(f"Test: {test_name}")
            print(f"Description: {description}")
            print(f"{'=' * 60}")

            icon_dir = os.path.join(temp_dir, test_name + ".icon")
            if os.path.exists(icon_dir):
                shutil.rmtree(icon_dir)

            try:
                icon = create_fn()
                icon.save()

                icon_json_path = os.path.join(icon_dir, "icon.json")
                with open(icon_json_path, "r") as f:
                    content = f.read()
                print(f"icon.json:\n{content[:500]}...")

                if skip_validation:
                    print(f"\nSkipping validation - icon saved to: {icon_dir}")
                    print(f"  You can validate manually with Icon Composer.app")
                    results.append((test_name, "SKIPPED", None))
                else:
                    print(f"\nValidating with ictool...")
                    result = validate_icon(
                        icon_dir, os.path.join(temp_dir, f"output_{test_name}")
                    )

                    if result["valid"]:
                        print(f"  SUCCESS: {len(result['exports'])} exports")
                        results.append((test_name, "PASS", None))
                    else:
                        print(f"  FAILED: {len(result['errors'])} errors")
                        for err in result["errors"][:3]:
                            print(f"    {err}")
                        results.append((test_name, "FAIL", result["errors"]))

            except Exception as e:
                print(f"  ERROR: {e}")
                results.append((test_name, "ERROR", str(e)))

    finally:
        print(f"\n{'=' * 60}")
        print("SUMMARY")
        print(f"{'=' * 60}")
        passed = sum(1 for r in results if r[1] == "PASS")
        failed = sum(1 for r in results if r[1] == "FAIL")
        errors = sum(1 for r in results if r[1] == "ERROR")
        skipped = sum(1 for r in results if r[1] == "SKIPPED")

        for name, status, _ in results:
            print(f"  {name}: {status}")

        print(
            f"\nTotal: {len(results)} | Passed: {passed} | Failed: {failed} | Errors: {errors} | Skipped: {skipped}"
        )

        if cleanup_temp_dir:
            print(f"\nCleaning up {temp_dir}...")
            shutil.rmtree(temp_dir)
        else:
            print(f"\nIcons saved to: {temp_dir}")
            print(f"Use Icon Composer.app to validate manually")


def _create_glass_effect(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(os.path.join(temp_dir, "glass_effect.icon"), "blue")
    icon.add_svg_layer(svg_path, "shape", glass=True)
    return icon


def _create_blend_mode(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(os.path.join(temp_dir, "blend_mode.icon"), "blue")
    icon.add_svg_layer(svg_path, "shape", blend_mode="plus-darker")
    return icon


def _create_shadow(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(os.path.join(temp_dir, "shadow.icon"), "blue")
    icon.add_svg_layer(svg_path, "shape")
    icon.set_shadow("", "neutral", 0.5)
    return icon


def _create_translucency(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(os.path.join(temp_dir, "translucency.icon"), "blue")
    icon.add_svg_layer(svg_path, "shape")
    icon.change_translucency("", 0.5)
    return icon


def _create_multiple_layers(temp_dir: str, svg1: str, svg2: str) -> IconEditor:
    icon = IconEditor.create_new(os.path.join(temp_dir, "multiple_layers.icon"), "blue")
    icon.add_svg_layer(svg1, "circle")
    icon.add_svg_layer(svg2, "heart")
    return icon


def _create_scale_shift(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(os.path.join(temp_dir, "scale_shift.icon"), "blue")
    icon.add_svg_layer(svg_path, "shape")
    icon.scale_shift_layer("shape", 2.0, 50, -50)
    return icon


def _create_solid_color(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(os.path.join(temp_dir, "solid_color.icon"), "blue")
    icon.add_svg_layer(svg_path, "shape")
    icon.change_gradient("shape", "solid", "red")
    return icon


def _create_auto_gradient(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(os.path.join(temp_dir, "auto_gradient.icon"), "blue")
    icon.add_svg_layer(svg_path, "shape")
    icon.change_gradient("shape", "auto", "purple")
    return icon


def _create_explicit_gradient(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(
        os.path.join(temp_dir, "explicit_gradient.icon"), "blue"
    )
    icon.add_svg_layer(svg_path, "shape")
    icon.change_gradient("shape", "custom", "red", "blue")
    return icon


def _create_bg_solid_layer_solid(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(
        os.path.join(temp_dir, "bg_solid_layer_solid.icon"), "green"
    )
    icon.change_background_fill("solid", "orange")
    icon.add_svg_layer(svg_path, "shape")
    icon.change_gradient("shape", "solid", "red")
    return icon


def _create_bg_gradient_layer_solid(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(
        os.path.join(temp_dir, "bg_gradient_layer_solid.icon"), "green"
    )
    icon.change_background_fill("custom", "purple", "orange")
    icon.add_svg_layer(svg_path, "shape")
    icon.change_gradient("shape", "solid", "red")
    return icon


def _create_bg_solid_layer_gradient(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(
        os.path.join(temp_dir, "bg_solid_layer_gradient.icon"), "green"
    )
    icon.change_background_fill("solid", "blue")
    icon.add_svg_layer(svg_path, "shape")
    icon.change_gradient("shape", "auto", "white")
    return icon


def _create_bg_gradient_layer_gradient(temp_dir: str, svg_path: str) -> IconEditor:
    icon = IconEditor.create_new(
        os.path.join(temp_dir, "bg_gradient_layer_gradient.icon"), "green"
    )
    icon.change_background_fill("custom", "purple", "orange")
    icon.add_svg_layer(svg_path, "shape")
    icon.change_gradient("shape", "custom", "red", "blue")
    return icon


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate icon variants for testing")
    parser.add_argument(
        "-o",
        "--output",
        help="Output directory for icon packages (default: temp directory)",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip ictool validation and keep files for manual inspection",
    )
    args = parser.parse_args()

    test_icon_variants(output_dir=args.output, skip_validation=args.skip_validation)

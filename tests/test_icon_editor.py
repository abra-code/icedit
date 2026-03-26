#!/usr/bin/env python3

import json
import logging
import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from icon_editor.core import (
    IconEditor,
    resolve_color,
    _validate_scale,
    _validate_translucency,
    _validate_blend_mode,
    _validate_shadow_kind,
    _validate_shadow_opacity,
)

logging.basicConfig(level=logging.DEBUG, format="%(message)s")
logger = logging.getLogger(__name__)

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "IconExamples")
TEST_PNG = os.path.join(EXAMPLES_DIR, "Hat-png.icon", "Assets", "magic-hat.png")
TEST_JPEG = os.path.join(EXAMPLES_DIR, "Sunflower-jpeg.icon", "Assets", "sunflower.jpg")
TEST_TIFF = os.path.join(EXAMPLES_DIR, "abracode.tiff")


class TestColorResolverExtensions(unittest.TestCase):
    def test_short_hex_colors(self):
        self.assertColorEqual(
            resolve_color("#F00"), "extended-srgb:1.00000,0.00000,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#0F0"), "extended-srgb:0.00000,1.00000,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#00F"), "extended-srgb:0.00000,0.00000,1.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#FFF"), "extended-srgb:1.00000,1.00000,1.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#808"), "extended-srgb:0.53333,0.00000,0.53333,1.00000"
        )

    def test_short_hex_with_alpha(self):
        self.assertColorEqual(
            resolve_color("#F008"), "extended-srgb:1.00000,0.00000,0.00000,0.53333"
        )
        self.assertColorEqual(
            resolve_color("#0000"), "extended-srgb:0.00000,0.00000,0.00000,0.00000"
        )

    def test_hsl_colors(self):
        self.assertColorEqual(
            resolve_color("hsl(0, 100%, 50%)"),
            "extended-srgb:1.00000,0.00000,0.00000,1.00000",
        )
        self.assertColorEqual(
            resolve_color("hsl(120, 100%, 50%)"),
            "extended-srgb:0.00000,1.00000,0.00000,1.00000",
        )
        self.assertColorEqual(
            resolve_color("hsl(240, 100%, 50%)"),
            "extended-srgb:0.00000,0.00000,1.00000,1.00000",
        )
        self.assertColorEqual(
            resolve_color("hsl(0, 0%, 50%)"),
            "extended-srgb:0.50000,0.50000,0.50000,1.00000",
        )

    def test_hsla_colors(self):
        self.assertColorEqual(
            resolve_color("hsla(0, 100%, 50%, 0.5)"),
            "extended-srgb:1.00000,0.00000,0.00000,0.50000",
        )
        self.assertColorEqual(
            resolve_color("hsla(120, 100%, 50%, 0.5)"),
            "extended-srgb:0.00000,1.00000,0.00000,0.50000",
        )

    def test_hsl_without_percent(self):
        self.assertColorEqual(
            resolve_color("hsl(0, 100, 50)"),
            "extended-srgb:1.00000,0.00000,0.00000,1.00000",
        )

    def test_passthrough_display_p3(self):
        color = "display-p3:1.00000,0.00000,0.00000,1.00000"
        self.assertEqual(resolve_color(color), color)

    def test_passthrough_srgb(self):
        color = "srgb:0.00000,0.00000,1.00000,1.00000"
        self.assertEqual(resolve_color(color), color)

    def test_passthrough_extended_srgb(self):
        color = "extended-srgb:0.50000,0.50000,0.50000,1.00000"
        self.assertEqual(resolve_color(color), color)

    def test_passthrough_extended_gray(self):
        color = "extended-gray:0.75000,1.00000"
        self.assertEqual(resolve_color(color), color)

    def assertColorEqual(self, actual, expected):
        if actual.startswith("extended-srgb:"):
            actual = actual.replace("extended-srgb:", "")
        elif actual.startswith("extended-gray:"):
            actual = actual.replace("extended-gray:", "")
        else:
            self.fail(f"Unexpected color format: {actual}")
        if expected.startswith("extended-srgb:"):
            expected = expected.replace("extended-srgb:", "")
        elif expected.startswith("extended-gray:"):
            expected = expected.replace("extended-gray:", "")
        actual_parts = actual.split(",")
        expected_parts = expected.split(",")
        self.assertEqual(len(actual_parts), len(expected_parts))
        for a, e in zip(actual_parts, expected_parts):
            self.assertAlmostEqual(float(a), float(e), places=4)


class TestValidators(unittest.TestCase):
    def test_validate_scale_valid(self):
        self.assertEqual(_validate_scale(1.0), 1.0)
        self.assertEqual(_validate_scale(0.5), 0.5)
        self.assertEqual(_validate_scale(2.0), 2.0)

    def test_validate_scale_invalid(self):
        with self.assertRaises(ValueError):
            _validate_scale(0)
        with self.assertRaises(ValueError):
            _validate_scale(-1)
        # Large scales are allowed (SVGs can be tiny font glyphs)
        _validate_scale(100)
        _validate_scale(1000)

    def test_validate_translucency_valid(self):
        self.assertEqual(_validate_translucency(0.0), 0.0)
        self.assertEqual(_validate_translucency(0.5), 0.5)
        self.assertEqual(_validate_translucency(1.0), 1.0)

    def test_validate_translucency_invalid(self):
        with self.assertRaises(ValueError):
            _validate_translucency(-0.1)
        with self.assertRaises(ValueError):
            _validate_translucency(1.1)
        with self.assertRaises(ValueError):
            _validate_translucency(2)

    def test_validate_blend_mode_valid(self):
        self.assertEqual(_validate_blend_mode("plus-darker"), "plus-darker")
        self.assertEqual(_validate_blend_mode("multiply"), "multiply")
        self.assertEqual(_validate_blend_mode("screen"), "screen")

    def test_validate_blend_mode_invalid(self):
        with self.assertRaises(ValueError):
            _validate_blend_mode("invalid-mode")
        with self.assertRaises(ValueError):
            _validate_blend_mode("")

    def test_validate_shadow_kind_valid(self):
        self.assertEqual(_validate_shadow_kind("none"), "none")
        self.assertEqual(_validate_shadow_kind("neutral"), "neutral")
        self.assertEqual(_validate_shadow_kind("layer-color"), "layer-color")

    def test_validate_shadow_kind_invalid(self):
        with self.assertRaises(ValueError):
            _validate_shadow_kind("invalid")
        with self.assertRaises(ValueError):
            _validate_shadow_kind("")

    def test_validate_shadow_opacity_valid(self):
        self.assertEqual(_validate_shadow_opacity(0.0), 0.0)
        self.assertEqual(_validate_shadow_opacity(0.5), 0.5)
        self.assertEqual(_validate_shadow_opacity(1.0), 1.0)

    def test_validate_shadow_opacity_invalid(self):
        with self.assertRaises(ValueError):
            _validate_shadow_opacity(-0.1)
        with self.assertRaises(ValueError):
            _validate_shadow_opacity(1.1)


class TestIconEditor(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.svg_path = os.path.join(self.temp_dir, "test.svg")
        with open(self.svg_path, "w") as f:
            f.write(
                '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/></svg>'
            )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_create_new(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")

        self.assertTrue(os.path.exists(icon_path))
        self.assertTrue(os.path.exists(os.path.join(icon_path, "icon.json")))
        self.assertTrue(os.path.exists(os.path.join(icon_path, "Assets")))

        json_path = os.path.join(icon_path, "icon.json")
        with open(json_path) as f:
            data = json.load(f)
        self.assertIn("fill", data)
        self.assertIn("automatic-gradient", data["fill"])

    def test_load_existing(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        IconEditor.create_new(icon_path, "green")

        loaded = IconEditor.load(icon_path)
        self.assertIsNotNone(loaded.icon_data)
        self.assertEqual(loaded.icon_dir, icon_path)

    def test_load_nonexistent(self):
        with self.assertRaises(FileNotFoundError):
            IconEditor.load("/nonexistent/path")

    def test_load_missing_json(self):
        icon_path = os.path.join(self.temp_dir, "empty.icon")
        os.makedirs(icon_path)
        with self.assertRaises(FileNotFoundError):
            IconEditor.load(icon_path)

    def test_add_svg_layer(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle", "red")

        layers = icon.get_layers()
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0]["name"], "circle")
        self.assertIn("circle.svg", layers[0]["image-name"])

    def test_add_svg_layer_with_glass(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle", glass=True)

        layers = icon.get_layers()
        self.assertTrue(layers[0].get("glass"))

    def test_add_svg_layer_with_blend_mode(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle", blend_mode="plus-darker")

        layers = icon.get_layers()
        self.assertEqual(layers[0].get("blend-mode"), "plus-darker")

    def test_add_svg_layer_invalid_blend_mode(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        with self.assertRaises(ValueError):
            icon.add_svg_layer(self.svg_path, "circle", blend_mode="invalid-mode")

    def test_add_svg_layer_invalid_path(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        with self.assertRaises(FileNotFoundError):
            icon.add_svg_layer("/nonexistent.svg", "circle")

    def test_add_svg_layer_auto_name(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        name = icon.add_svg_layer(self.svg_path)

        self.assertEqual(name, "test")
        layers = icon.get_layers()
        self.assertEqual(layers[0]["name"], "test")
        self.assertEqual(layers[0]["image-name"], "test.svg")

    def test_add_svg_layer_auto_name_dedup(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        name1 = icon.add_svg_layer(self.svg_path)
        name2 = icon.add_svg_layer(self.svg_path)
        name3 = icon.add_svg_layer(self.svg_path)

        self.assertEqual(name1, "test")
        self.assertEqual(name2, "test.1")
        self.assertEqual(name3, "test.2")
        layers = icon.get_layers()
        self.assertEqual(len(layers), 3)

    def test_add_svg_layer_explicit_name_dedup(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        name1 = icon.add_svg_layer(self.svg_path, "circle")
        name2 = icon.add_svg_layer(self.svg_path, "circle")

        self.assertEqual(name1, "circle")
        self.assertEqual(name2, "circle.1")

    def test_add_layer_asset_file_conflict(self):
        """Adding an image with the same base name as an existing SVG layer
        should get a deduplicated name even though the extensions differ."""
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        svg_name = icon.add_svg_layer(self.svg_path, "shape")
        self.assertEqual(svg_name, "shape")

        img_name = icon.add_image_layer(TEST_PNG, "shape")
        # Layer name should be deduplicated since "shape" is taken
        self.assertEqual(img_name, "shape.1")
        # Both asset files should exist without overwriting
        self.assertTrue(os.path.isfile(os.path.join(icon_path, "Assets", "shape.svg")))
        self.assertTrue(os.path.isfile(os.path.join(icon_path, "Assets", "shape.1.png")))

    def test_add_image_layer_png(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")

        name = icon.add_image_layer(TEST_PNG)

        self.assertEqual(name, "magic-hat")
        layers = icon.get_layers()
        self.assertEqual(layers[0]["name"], "magic-hat")
        self.assertEqual(layers[0]["image-name"], "magic-hat.png")
        self.assertNotIn("fill", layers[0])
        self.assertTrue(os.path.isfile(os.path.join(icon_path, "Assets", "magic-hat.png")))

    def test_add_image_layer_with_name(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")

        name = icon.add_image_layer(TEST_PNG, "my-layer")

        self.assertEqual(name, "my-layer")
        layers = icon.get_layers()
        self.assertEqual(layers[0]["image-name"], "my-layer.png")

    def test_add_image_layer_invalid_path(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        with self.assertRaises(FileNotFoundError):
            icon.add_image_layer("/nonexistent.png")

    def test_add_image_layer_tiff_converts_to_png(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")

        name = icon.add_image_layer(TEST_TIFF)

        self.assertEqual(name, "abracode")
        layers = icon.get_layers()
        self.assertEqual(layers[0]["image-name"], "abracode.png")
        asset = os.path.join(icon_path, "Assets", "abracode.png")
        self.assertTrue(os.path.isfile(asset))

    def test_add_image_layer_jpeg(self):
        """JPEG files should be embedded as-is with .jpg extension."""
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")

        name = icon.add_image_layer(TEST_JPEG)
        layers = icon.get_layers()
        self.assertEqual(layers[0]["image-name"], "sunflower.jpg")
        self.assertTrue(os.path.isfile(os.path.join(icon_path, "Assets", "sunflower.jpg")))

    def test_scale_shift_layer(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.scale_shift_layer("circle", 0.5, 10, 20)

        layers = icon.get_layers()
        self.assertEqual(layers[0]["position"]["scale"], 0.5)
        self.assertEqual(layers[0]["position"]["translation-in-points"], [10, 20])

    def test_scale_shift_layer_invalid_scale(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        with self.assertRaises(ValueError):
            icon.scale_shift_layer("circle", -1.0, 10, 20)

    def test_change_fill_solid(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.change_fill("circle", "solid", "extended-srgb:1.0,0.0,0.0,1.0")

        layers = icon.get_layers()
        self.assertIn("solid", layers[0]["fill"])

    def test_change_fill_none(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.change_fill("circle", "none")

        layers = icon.get_layers()
        self.assertEqual(layers[0]["fill"], "none")

    def test_change_fill_automatic(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.change_fill("circle", "automatic")

        layers = icon.get_layers()
        self.assertEqual(layers[0]["fill"], "automatic")

    def test_change_fill_auto_gradient(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.change_fill("circle", "auto-gradient", "purple")

        layers = icon.get_layers()
        self.assertIn("automatic-gradient", layers[0]["fill"])

    def test_change_fill_gradient(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.change_fill("circle", "gradient", "red", "blue")

        layers = icon.get_layers()
        fill = layers[0]["fill"]
        self.assertIn("linear-gradient", fill)
        self.assertIsInstance(fill["linear-gradient"], list)
        self.assertEqual(len(fill["linear-gradient"]), 2)
        self.assertIn("orientation", fill)

    def test_change_fill_gradient_missing_color2(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        with self.assertRaises(ValueError):
            icon.change_fill("circle", "gradient", "red")

    def test_change_fill_solid_missing_color(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        with self.assertRaises(ValueError):
            icon.change_fill("circle", "solid")

    def test_change_background_fill_solid(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.change_background_fill("solid", "red")

        self.assertIn("solid", icon.icon_data["fill"])

    def test_change_background_fill_none(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.change_background_fill("none")

        self.assertEqual(icon.icon_data["fill"], "none")

    def test_change_background_fill_automatic(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.change_background_fill("automatic")

        self.assertEqual(icon.icon_data["fill"], "automatic")

    def test_change_background_fill_auto_gradient(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.change_background_fill("auto-gradient", "green")

        self.assertIn("automatic-gradient", icon.icon_data["fill"])

    def test_change_background_fill_gradient(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.change_background_fill("gradient", "red", "blue")

        fill = icon.icon_data["fill"]
        self.assertIn("linear-gradient", fill)
        self.assertIsInstance(fill["linear-gradient"], list)
        self.assertEqual(len(fill["linear-gradient"]), 2)
        self.assertIn("orientation", fill)

    def test_change_translucency(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.change_translucency(1, 0.5)

        groups = icon.get_groups()
        self.assertEqual(groups[0]["translucency"]["value"], 0.5)

    def test_change_translucency_invalid(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        with self.assertRaises(ValueError):
            icon.change_translucency(1, 1.5)

    def test_set_shadow(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_shadow(1, "neutral", 0.5)

        groups = icon.get_groups()
        self.assertEqual(groups[0]["shadow"]["kind"], "neutral")
        self.assertEqual(groups[0]["shadow"]["opacity"], 0.5)

    def test_set_shadow_chromatic(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_shadow(1, "layer-color", 0.75)

        groups = icon.get_groups()
        self.assertEqual(groups[0]["shadow"]["kind"], "layer-color")
        self.assertEqual(groups[0]["shadow"]["opacity"], 0.75)

    def test_set_shadow_none(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_shadow(1, "neutral", 0.5)
        icon.set_shadow(1, "none", 0.5)

        groups = icon.get_groups()
        self.assertEqual(groups[0]["shadow"]["kind"], "none")

    def test_set_shadow_invalid_kind(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        with self.assertRaises(ValueError):
            icon.set_shadow(1, "invalid", 0.5)

    def test_set_shadow_invalid_opacity(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        with self.assertRaises(ValueError):
            icon.set_shadow(1, "neutral", 1.5)

    def test_remove_layer(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.add_svg_layer(self.svg_path, "square")
        icon.remove_layer("circle")

        layers = icon.get_layers()
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0]["name"], "square")

    def test_reorder_layer(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.add_svg_layer(self.svg_path, "square")
        icon.add_svg_layer(self.svg_path, "triangle")

        # After insert-at-top, initial order is: triangle, square, circle
        # Move circle to position 0
        icon.reorder_layer("circle", 0)

        layers = icon.get_layers()
        self.assertEqual(layers[0]["name"], "circle")
        self.assertEqual(layers[1]["name"], "triangle")
        self.assertEqual(layers[2]["name"], "square")

    def test_uninitialized_access(self):
        icon = IconEditor()
        with self.assertRaises(RuntimeError):
            icon.add_svg_layer(self.svg_path, "circle")

    def test_multiple_groups(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.icon_data["groups"].append({"name": "Second", "layers": []})

        groups = icon.get_groups()
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0]["layers"][0]["name"], "circle")
        self.assertEqual(groups[1]["name"], "Second")

    def test_group_by_name(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.rename_group(1, "Front")
        icon.set_group_opacity("Front", 0.5)
        self.assertEqual(icon.get_groups()[0]["opacity"], 0.5)

    def test_group_by_name_ambiguous(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.rename_group(1, "Group")
        icon.icon_data["groups"].append({"name": "Group", "layers": []})
        icon.save()
        with self.assertRaises(ValueError) as ctx:
            icon.set_group_opacity("Group", 0.5)
        self.assertIn("Ambiguous", str(ctx.exception))

    def test_set_group_opacity(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_opacity(1, 0.98)
        self.assertEqual(icon.get_groups()[0]["opacity"], 0.98)

    def test_set_group_opacity_full_removes(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_opacity(1, 0.5)
        icon.set_group_opacity(1, 1.0)
        self.assertNotIn("opacity", icon.get_groups()[0])

    def test_set_group_blend_mode(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_blend_mode(1, "lighten")
        self.assertEqual(icon.get_groups()[0]["blend-mode"], "lighten")

    def test_set_group_blend_mode_normal_removes(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_blend_mode(1, "lighten")
        icon.set_group_blend_mode(1, "normal")
        self.assertNotIn("blend-mode", icon.get_groups()[0])

    def test_set_group_blur(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_blur(1, 0.95)
        self.assertEqual(icon.get_groups()[0]["blur-material"], 0.95)

    def test_set_group_lighting(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_lighting(1, "combined")
        self.assertEqual(icon.get_groups()[0]["lighting"], "combined")
        icon.set_group_lighting(1, "individual")
        self.assertEqual(icon.get_groups()[0]["lighting"], "individual")

    def test_set_group_lighting_invalid(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        with self.assertRaises(ValueError):
            icon.set_group_lighting(1, "bogus")

    def test_set_group_specular(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_specular(1, True)
        self.assertTrue(icon.get_groups()[0]["specular"])
        icon.set_group_specular(1, False)
        self.assertFalse(icon.get_groups()[0]["specular"])

    def test_set_group_hidden(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_hidden(1, True)
        specs = icon.get_groups()[0]["hidden-specializations"]
        self.assertEqual(len(specs), 1)
        self.assertEqual(specs[0]["idiom"], "square")
        self.assertTrue(specs[0]["value"])

    def test_set_group_hidden_toggle(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.set_group_hidden(1, True)
        icon.set_group_hidden(1, False)
        specs = icon.get_groups()[0]["hidden-specializations"]
        self.assertEqual(len(specs), 1)
        self.assertFalse(specs[0]["value"])

    def test_rename_group(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.rename_group(1, "Front")
        self.assertEqual(icon.get_groups()[0]["name"], "Front")

    def test_rename_group_duplicate_rejected(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.rename_group(1, "Front")
        icon.icon_data["groups"].append({"name": "Back", "layers": []})
        icon.save()
        with self.assertRaises(ValueError) as ctx:
            icon.rename_group(2, "Front")
        self.assertIn("unique", str(ctx.exception))

    def test_scale_shift_group(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.scale_shift_group(1, 0.82, 4, 6)
        specs = icon.get_groups()[0]["position-specializations"]
        self.assertEqual(len(specs), 1)
        self.assertEqual(specs[0]["idiom"], "square")
        self.assertEqual(specs[0]["value"]["scale"], 0.82)
        self.assertEqual(specs[0]["value"]["translation-in-points"], [4, 6])

    def test_scale_shift_group_updates_existing(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.scale_shift_group(1, 0.5, 0, 0)
        icon.scale_shift_group(1, 0.9, 10, -5)
        specs = icon.get_groups()[0]["position-specializations"]
        self.assertEqual(len(specs), 1)
        self.assertEqual(specs[0]["value"]["scale"], 0.9)
        self.assertEqual(specs[0]["value"]["translation-in-points"], [10, -5])

    # --- Layer identification by index ---

    def test_layer_by_index(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.add_svg_layer(self.svg_path, "square")
        # After insert-at-top: square (index 1), circle (index 2)
        icon.set_glass(1, False)  # by index: square
        layers = icon.get_layers()
        self.assertFalse(layers[0]["glass"])  # square
        self.assertTrue(layers[1]["glass"])   # circle untouched

    def test_layer_by_name(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.add_svg_layer(self.svg_path, "square")
        icon.set_glass("circle", False)
        layers = icon.get_layers()
        self.assertTrue(layers[0]["glass"])    # square
        self.assertFalse(layers[1]["glass"])   # circle

    def test_layer_by_name_ambiguous(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "shape")
        # Manually add a second layer with the same name
        icon.icon_data["groups"][0]["layers"].append(
            {"name": "shape", "image-name": "shape2.svg", "glass": True}
        )
        icon.save()
        with self.assertRaises(ValueError) as ctx:
            icon.set_glass("shape", False)
        self.assertIn("Ambiguous", str(ctx.exception))

    def test_layer_by_index_in_second_group(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "front-layer")
        icon.icon_data["groups"].append({"name": "Back", "layers": [
            {"name": "back-layer", "image-name": "back.svg", "glass": True,
             "position": {"scale": 1.0, "translation-in-points": [0, 0]}}
        ]})
        icon.save()
        icon.scale_shift_layer(1, 0.5, 10, 20, group=2)
        back_layer = icon.get_layers(group=2)[0]
        self.assertEqual(back_layer["position"]["scale"], 0.5)
        self.assertEqual(back_layer["position"]["translation-in-points"], [10, 20])

    def test_layer_by_name_in_named_group(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "front-layer")
        icon.rename_group(1, "Front")
        icon.icon_data["groups"].append({"name": "Back", "layers": [
            {"name": "back-layer", "image-name": "back.svg", "glass": True}
        ]})
        icon.save()
        icon.set_glass("back-layer", False, group="Back")
        back_layer = icon.get_layers(group="Back")[0]
        self.assertFalse(back_layer["glass"])

    def test_remove_layer_by_index(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.add_svg_layer(self.svg_path, "square")
        # square is index 1, circle is index 2
        icon.remove_layer(1)  # removes square
        layers = icon.get_layers()
        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0]["name"], "circle")

    def test_change_fill_by_index(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "circle")
        icon.change_fill(1, "solid", "extended-srgb:1.0,0.0,0.0,1.0")
        layers = icon.get_layers()
        self.assertIn("solid", layers[0]["fill"])

    def test_add_layer_to_second_group(self):
        icon_path = os.path.join(self.temp_dir, "test.icon")
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer(self.svg_path, "front-layer")
        icon.icon_data["groups"].append({"name": "Back", "layers": []})
        icon.save()
        icon.add_svg_layer(self.svg_path, "back-layer", group=2)
        self.assertEqual(len(icon.get_layers(group=1)), 1)
        self.assertEqual(len(icon.get_layers(group=2)), 1)
        self.assertEqual(icon.get_layers(group=2)[0]["name"], "back-layer")


class TestIconEditorIntegration(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.svg_path = os.path.join(self.temp_dir, "test.svg")
        with open(self.svg_path, "w") as f:
            f.write(
                '<svg xmlns="http://www.w3.org/2000/svg"><circle cx="50" cy="50" r="40"/></svg>'
            )

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_full_workflow(self):
        icon_path = os.path.join(self.temp_dir, "workflow.icon")

        icon = IconEditor.create_new(icon_path, "#FF0000")
        icon.add_svg_layer(
            self.svg_path, "circle", "blue", glass=True, blend_mode="plus-darker"
        )
        icon.scale_shift_layer("circle", 0.8, 10, -5)
        icon.change_translucency(1, 0.3)
        icon.set_shadow(1, "neutral", 0.4)
        icon.save()

        loaded = IconEditor.load(icon_path)
        layers = loaded.get_layers()
        groups = loaded.get_groups()

        self.assertEqual(len(layers), 1)
        self.assertEqual(layers[0]["name"], "circle")
        self.assertTrue(layers[0].get("glass"))
        self.assertEqual(layers[0].get("blend-mode"), "plus-darker")
        self.assertEqual(layers[0]["position"]["scale"], 0.8)
        self.assertEqual(groups[0]["translucency"]["value"], 0.3)
        self.assertEqual(groups[0]["shadow"]["kind"], "neutral")


if __name__ == "__main__":
    unittest.main()

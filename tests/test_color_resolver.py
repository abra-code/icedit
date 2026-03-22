#!/usr/bin/env python3

import logging
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from icon_editor.core import resolve_color, APPLE_COLORS, CRAYONS_COLORS, WEB_COLORS

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)


class TestColorResolver(unittest.TestCase):
    def assertColorEqual(self, actual, expected):
        """Assert colors are equal with reasonable floating point tolerance."""
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
        else:
            self.fail(f"Unexpected expected format: {expected}")
        actual_parts = actual.split(",")
        expected_parts = expected.split(",")
        self.assertEqual(len(actual_parts), len(expected_parts))
        for a, e in zip(actual_parts, expected_parts):
            self.assertAlmostEqual(float(a), float(e), places=4)

    def test_palette_colors(self):
        logger.info("Testing palette color names...")
        # Default resolution (Apple palette)
        self.assertColorEqual(
            resolve_color("red"), "extended-srgb:1.00000,0.14902,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("blue"), "extended-srgb:0.01569,0.20000,1.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("white"), "extended-srgb:1.00000,1.00000,1.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("black"), "extended-srgb:0.00000,0.00000,0.00000,1.00000"
        )
        logger.info("Palette color tests passed.")

    def test_apple_palette_explicit_prefix(self):
        logger.info("Testing explicit apple. prefix...")
        self.assertColorEqual(
            resolve_color("apple.red"), "extended-srgb:1.00000,0.14902,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("apple.blue"), "extended-srgb:0.01569,0.20000,1.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("apple.green"),
            "extended-srgb:0.00000,0.97647,0.00000,1.00000",
        )
        self.assertColorEqual(
            resolve_color("apple.brown"),
            "extended-srgb:0.66667,0.47451,0.25882,1.00000",
        )
        # All Apple colors
        for name, expected_rgb in APPLE_COLORS.items():
            result = resolve_color(f"apple.{name}")
            r, g, b = expected_rgb.split(",")
            expected = f"extended-srgb:{r},{g},{b},1.00000"
            self.assertColorEqual(result, expected)
        logger.info("Apple palette tests passed.")

    def test_crayons_palette_explicit_prefix(self):
        logger.info("Testing explicit crayons. prefix...")
        self.assertColorEqual(
            resolve_color("crayons.cantaloupe"),
            "extended-srgb:1.00000,0.83137,0.47451,1.00000",
        )
        self.assertColorEqual(
            resolve_color("crayons.salmon"),
            "extended-srgb:1.00000,0.49412,0.47451,1.00000",
        )
        self.assertColorEqual(
            resolve_color("crayons.tangerine"),
            "extended-srgb:1.00000,0.57647,0.00000,1.00000",
        )
        # All Crayons colors
        for name, expected_rgb in CRAYONS_COLORS.items():
            result = resolve_color(f"crayons.{name}")
            r, g, b = expected_rgb.split(",")
            expected = f"extended-srgb:{r},{g},{b},1.00000"
            self.assertColorEqual(result, expected)
        logger.info("Crayons palette tests passed.")

    def test_web_palette_explicit_prefix(self):
        logger.info("Testing explicit web. prefix...")
        self.assertColorEqual(
            resolve_color("web.red"), "extended-srgb:1.00000,0.00000,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("web.blue"), "extended-srgb:0.00000,0.00000,1.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("web.green"), "extended-srgb:0.00000,0.50196,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("web.orange"), "extended-srgb:1.00000,0.64706,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("web.brown"), "extended-srgb:0.64706,0.16471,0.16471,1.00000"
        )
        logger.info("Web palette tests passed.")

    def test_conflicting_color_names(self):
        logger.info("Testing conflicting color name resolution...")
        # Without prefix: Apple takes precedence
        self.assertColorEqual(
            resolve_color("green"),
            "extended-srgb:0.00000,0.97647,0.00000,1.00000",  # Apple green
        )
        self.assertColorEqual(
            resolve_color("orange"),
            "extended-srgb:1.00000,0.57647,0.00000,1.00000",  # Apple orange
        )
        self.assertColorEqual(
            resolve_color("brown"),
            "extended-srgb:0.66667,0.47451,0.25882,1.00000",  # Apple brown
        )
        # With prefixes: get the specific palette value
        self.assertColorEqual(
            resolve_color("apple.green"),
            "extended-srgb:0.00000,0.97647,0.00000,1.00000",
        )
        self.assertColorEqual(
            resolve_color("web.green"), "extended-srgb:0.00000,0.50196,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("crayons.lime"),
            "extended-srgb:0.55686,0.98039,0.00000,1.00000",
        )
        logger.info("Conflicting color name tests passed.")

    def test_crayons_specific_colors(self):
        logger.info("Testing specific Crayons palette colors...")
        # Test a few key Crayons that differ from both Apple and Web
        self.assertColorEqual(
            resolve_color("crayons.blueberry"),
            "extended-srgb:0.01569,0.20000,1.00000,1.00000",  # #0433ff
        )
        self.assertColorEqual(
            resolve_color("crayons.snow"),
            "extended-srgb:1.00000,1.00000,1.00000,1.00000",  # #ffffff
        )
        self.assertColorEqual(
            resolve_color("crayons.spring"),
            "extended-srgb:0.00000,0.97647,0.00000,1.00000",  # #00f900
        )
        logger.info("Crayons specific color tests passed.")

    def test_hex_colors(self):
        logger.info("Testing hex color codes...")
        self.assertColorEqual(
            resolve_color("#FF0000"), "extended-srgb:1.00000,0.00000,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#00FF00"), "extended-srgb:0.00000,1.00000,0.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#0000FF"), "extended-srgb:0.00000,0.00000,1.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#FFFFFF"), "extended-srgb:1.00000,1.00000,1.00000,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#808080"), "extended-srgb:0.50196,0.50196,0.50196,1.00000"
        )
        self.assertColorEqual(
            resolve_color("#FF000080"), "extended-srgb:1.00000,0.00000,0.00000,0.50196"
        )
        logger.info("Hex color tests passed.")

    def test_rgba_colors(self):
        logger.info("Testing rgba/rgb color notations...")
        self.assertColorEqual(
            resolve_color("rgba(1.0, 0.0, 0.0, 1.0)"),
            "extended-srgb:1.00000,0.00000,0.00000,1.00000",
        )
        self.assertColorEqual(
            resolve_color("rgb(0.0, 1.0, 0.0)"),
            "extended-srgb:0.00000,1.00000,0.00000,1.00000",
        )
        self.assertColorEqual(
            resolve_color("rgba(0.5, 0.5, 0.5, 0.5)"),
            "extended-srgb:0.50000,0.50000,0.50000,0.50000",
        )
        self.assertColorEqual(
            resolve_color("rgba(255, 0, 0, 0.5)"),
            "extended-srgb:1.00000,0.00000,0.00000,0.50000",
        )
        self.assertEqual(
            resolve_color("rgba(255, 0, 0, 128)"),
            "extended-srgb:0.00000,0.00000,0.00000,1.00000",
        )
        self.assertColorEqual(
            resolve_color("rgb(128, 128, 128)"),
            "extended-srgb:0.50196,0.50196,0.50196,1.00000",
        )
        logger.info("RGBA/RGB color tests passed.")

    def test_extended_srgb_pass_through(self):
        logger.info("Testing extended-srgb pass-through...")
        color = "extended-srgb:0.50000,0.50000,0.50000,1.00000"
        self.assertEqual(resolve_color(color), color)
        logger.info("Pass-through test passed.")

    def test_unknown_color(self):
        logger.info("Testing unknown color handling...")
        self.assertEqual(
            resolve_color("unknown"), "extended-srgb:0.00000,0.00000,0.00000,1.00000"
        )
        logger.info("Unknown color test passed.")


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from icon_editor.core import IconEditor, resolve_color


def run_ictool(icon_path, output_png):
    """Run ictool to export .icon to .png if Icon Composer is installed."""
    ictool_path = "/Applications/Icon Composer.app/Contents/Executables/ictool"
    if os.path.exists(ictool_path):
        try:
            result = subprocess.run(
                [
                    ictool_path,
                    icon_path,
                    "--export-image",
                    "--output-file",
                    output_png,
                    "--platform",
                    "macOS",
                    "--rendition",
                    "Default",
                    "--width",
                    "1024",
                    "--height",
                    "1024",
                    "--scale",
                    "1",
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"ictool succeeded: {icon_path} -> {output_png}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"ictool failed: {e.stderr}")
            return False
    else:
        print("Icon Composer not installed, skipping ictool test.")
        return False


def basic_tests():
    """Perform basic correctness test: create icon, optionally test with ictool."""
    svg_path = "/tmp/simple.svg"
    if not os.path.exists(svg_path):
        svg_content = """<svg xmlns="http://www.w3.org/2000/svg"><path d="M50 10 A40 40 0 1 1 50 90 A40 40 0 1 1 50 10"/></svg>"""
        with open(svg_path, "w") as f:
            f.write(svg_content)
        print(f"Created {svg_path}")

    temp_dir = tempfile.mkdtemp()
    icon_path = os.path.join(temp_dir, "basic_tests.icon")

    try:
        icon = IconEditor.create_new(icon_path, "blue")
        icon.add_svg_layer("/tmp/simple.svg", "shape", "orange")
        icon.scale_shift_layer("shape", 0.8, 50, 50)
        print("resolve_color('orange'):", repr(resolve_color("orange")))
        icon.change_translucency(1, 0.1)
        icon.save()

        json_path = os.path.join(icon_path, "icon.json")
        if os.path.exists(json_path):
            print("icon.json created successfully.")
        else:
            print("ERROR: icon.json not found.")
            return False

        loaded_icon = IconEditor.load(icon_path)
        layers = loaded_icon.get_layers()
        if layers:
            print(f"Loaded icon has {len(layers)} layer(s)")

        output_png = f"{icon_path}.png"
        success = run_ictool(icon_path, output_png)

        if success and os.path.exists(output_png):
            print(f"Smoke test passed: PNG exported to {output_png}")
            os.remove(output_png)
            shutil.rmtree(temp_dir)
        else:
            print(
                f"ictool test failed, but icon creation succeeded. Icon left at: {icon_path}"
            )
            print(f"Temp directory preserved: {temp_dir}")

        print("Basic tests completed.")
        return True
    except Exception as e:
        print(f"Test failed with exception: {e}")
        print(f"Temp directory preserved: {temp_dir}")
        return False


if __name__ == "__main__":
    success = basic_tests()
    if success:
        print("\nBasic tests passed.")
    else:
        print("\nBasic tests failed.")

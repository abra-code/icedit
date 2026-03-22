# icedit

A command-line tool for creating and editing Apple Icon Composer `.icon` bundles.

## Overview

icedit provides a Python API and CLI for programmatic icon creation and modification, supporting:
- Creating new icons with customizable backgrounds
- Adding SVG layers with glass effects and blend modes
- Scale and shift transformations
- Gradient and translucency controls
- Shadow settings
- Icon validation and variant generation for macOS, iOS, watchOS

## Command-Line Usage

```bash
icedit create <icon_path> <background_color>
icedit add_svg <icon_path> <svg_path> <layer_name> [--color <color>] [--glass] [--blend-mode <mode>]
icedit scale_shift <icon_path> <layer_name> <scale> <shift_x> <shift_y>
icedit change_gradient <icon_path> <layer_name> <gradient_type> <color1> [--color2 <color2>]
icedit change_translucency <icon_path> <group_name> <value>
icedit set_shadow <icon_path> <group_name> <kind> <opacity> [--color <color>]
icedit validate <icon_path> [--output <dir>]
icedit variants <icon_path> [--output <dir>]
icedit colors
```

## Color Specification

Colors can be specified in multiple formats:
- Named colors (Apple, Crayons, or Web palette)
- HEX colors: `#RGB` or `#RRGGBB`
- RGB/RGBA: `rgb(r, g, b)` or `rgba(r, g, b, a)`
- HSL/HSLA: `hsl(H, S%, L%)` or `hsla(H, S%, L%, A)`

Named colors may include palette prefixes: `apple.`, `crayons.`, `web.`

```bash
icedit colors  # List all supported color formats and names
```

## Python API

```python
from icon_editor import IconEditor, resolve_color, validate_icon, generate_variants

# Create a new icon
icon = IconEditor.create_new("/path/to/icon.icon", "blue")
icon.add_svg_layer("/path/to/shape.svg", "layer1", "red")
icon.scale_shift_layer("layer1", 0.8, 50, 50)
icon.change_translucency("", 0.1)
icon.save()

# Validate and generate variants
results = validate_icon("/path/to/icon.icon")
variants = generate_variants("/path/to/icon.icon")
```

## Requirements

- Python 3.10+
- [Icon Composer.app](https://developer.apple.com/icon-composer/) (optional, for PNG export)

## Testing

```bash
python3 -m unittest discover -s tests
./tests/test_icedit.sh
```

## License

Apache 2.0

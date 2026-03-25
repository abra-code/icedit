# icedit

A command-line tool for creating and editing Apple Icon Composer `.icon` bundles.

## Overview

icedit provides a Python API and CLI for programmatic icon creation and modification, supporting:
- Creating new icons with customizable backgrounds
- Adding and removing SVG layers with glass effects and blend modes
- Scale and shift transformations
- Fill types: none, automatic, solid, auto-gradient, gradient
- Translucency and shadow controls
- Icon validation and variant generation for macOS, iOS, watchOS

## Command-Line Usage

```bash
icedit create <icon_path> <background_color>
icedit add_svg <icon_path> <svg_path> [<layer_name>] [--color <color>] [--glass] [--blend-mode <mode>]
icedit add_image <icon_path> <image_path> [<layer_name>] [--glass] [--blend-mode <mode>]
icedit remove <icon_path> <layer_name>
icedit scale_shift <icon_path> <layer_name> <scale> <shift_x> <shift_y>
icedit change_fill <icon_path> <layer_name> <fill_type> [<color1>] [--color2 <color2>]
icedit change_translucency <icon_path> <group_name> <value>
icedit set_shadow <icon_path> <group_name> <kind> <opacity> [--color <color>]
icedit validate <icon_path> [--output <dir>]
icedit variants <icon_path> [--output <dir>]
icedit colors
```

### Fill Types

| Fill type | Colors required | JSON representation |
|---|---|---|
| `none` | 0 | `"none"` |
| `automatic` | 0 | `"automatic"` |
| `solid` | 1 | `{"solid": "color"}` |
| `auto-gradient` | 1 | `{"automatic-gradient": "color"}` |
| `gradient` | 2 | `{"linear-gradient": ["color1", "color2"], "orientation": {...}}` |

```bash
icedit change_fill icon.icon layer1 none
icedit change_fill icon.icon layer1 automatic
icedit change_fill icon.icon layer1 solid red
icedit change_fill icon.icon layer1 auto-gradient blue
icedit change_fill icon.icon layer1 gradient red --color2 blue
```

## Color Specification

Colors can be specified in multiple formats:
- Named colors (Apple, Crayons, or Web palette)
- HEX colors: `#RGB`, `#RRGGBB`, `#RRGGBBAA`
- RGB/RGBA: `rgb(r, g, b)` or `rgba(r, g, b, a)`
- HSL/HSLA: `hsl(H, S%, L%)` or `hsla(H, S%, L%, A)`
- Native Icon Composer formats: `extended-srgb:R,G,B,A`, `srgb:R,G,B,A`, `display-p3:R,G,B,A`, `extended-gray:V,A`

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
icon.change_fill("layer1", "auto-gradient", "purple")
icon.change_background_fill("gradient", "red", "blue")
icon.change_translucency("", 0.1)
icon.set_shadow("", "neutral", 0.5)
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

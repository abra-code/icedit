#!/bin/bash

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

PASS=0
FAIL=0
ICON="/tmp/test_cli_icon.icon"
SVG="/tmp/simple.svg"

# --- Helpers ---

find_ictool() {
    local candidate
    for candidate in \
        "/Applications/Icon Composer.app/Contents/Executables/ictool" \
        "/Applications/Xcode.app/Contents/Applications/Icon Composer.app/Contents/Executables/ictool"; do
        if [ -x "$candidate" ]; then
            echo "$candidate"
            return
        fi
    done
    
    local xcode_dev="$(xcode-select -p 2>/dev/null || true)"
    if [ -n "$xcode_dev" ]; then
        candidate="${xcode_dev%/Developer}/Applications/Icon Composer.app/Contents/Executables/ictool"
        if [ -x "$candidate" ]; then
            echo "$candidate"
            return
        fi
    fi
}

run_test() {
    # Usage: run_test "description" command [args...]
    local desc="$1"
    shift
    echo -n "  $desc... "
    if "$@" > /tmp/test_icedit_out.txt 2>&1; then
        echo "ok"
        PASS=$((PASS + 1))
    else
        echo "FAIL"
        cat /tmp/test_icedit_out.txt
        FAIL=$((FAIL + 1))
    fi
}

assert_eqaul() {
    # Usage: assert_eqaul "description" "actual" "expected"
    local desc="$1"
    local actual="$2"
    local expected="$3"
    echo -n "  $desc... "
    if [ "$actual" = "$expected" ]; then
        echo "ok"
        PASS=$((PASS + 1))
    else
        echo "FAIL"
        echo "    expected: $expected"
        echo "    actual:   $actual"
        FAIL=$((FAIL + 1))
    fi
}

assert_file_exists() {
    # Usage: assert_file_exists "description" path
    local desc="$1"
    local path="$2"
    echo -n "  $desc... "
    if [ -f "$path" ] || [ -d "$path" ]; then
        echo "ok"
        PASS=$((PASS + 1))
    else
        echo "FAIL (not found: $path)"
        FAIL=$((FAIL + 1))
    fi
}

layer_names() {
    # Usage: layer_names [group]
    # Prints layer names from icon.json, one per line, in array order
    local group="${1:-0}"
    python3 -c "
import json, sys
with open('$ICON/icon.json') as f:
    data = json.load(f)
groups = data.get('groups', [])
if $group < len(groups):
    for l in groups[$group].get('layers', []):
        print(l.get('name', ''))
"
}

reset_icon() {
    # Create a fresh icon with 3 layers: triangle(1), square(2), circle(3)
    rm -rf "$ICON"
    python3 icedit create "$ICON" blue 2>/dev/null
    python3 icedit add_svg "$ICON" "$SVG" circle 2>/dev/null
    python3 icedit add_svg "$ICON" "$SVG" square 2>/dev/null
    python3 icedit add_svg "$ICON" "$SVG" triangle 2>/dev/null
}

# --- Setup ---

echo "Starting icedit tests..."

rm -rf "$ICON"

if [ ! -f "$SVG" ]; then
    cat > "$SVG" << 'SVGEOF'
<svg xmlns="http://www.w3.org/2000/svg"><path d="M50 10 A40 40 0 1 1 50 90 A40 40 0 1 1 50 10"/></svg>
SVGEOF
fi

# --- Basic commands ---

echo ""
echo "Basic commands:"

run_test "create icon" python3 icedit create "$ICON" blue
assert_file_exists "icon directory exists" "$ICON"
assert_file_exists "icon.json exists" "$ICON/icon.json"

run_test "add SVG layer" python3 icedit add_svg "$ICON" "$SVG" circle --color red
assert_file_exists "SVG asset copied" "$ICON/Assets/circle.svg"

run_test "scale and shift layer" python3 icedit scale_shift "$ICON" circle 0.8 20 30
run_test "change fill to solid" python3 icedit change_fill "$ICON" circle solid green
run_test "change fill to auto-gradient" python3 icedit change_fill "$ICON" circle auto-gradient orange
run_test "change translucency" python3 icedit change_translucency "$ICON" "" 0.5

# --- Reorder ---

echo ""
echo "Reorder:"

reset_icon
names="$(layer_names)"
assert_eqaul "initial order" "$names" "$(printf 'triangle\nsquare\ncircle')"

run_test "move position 1 to position 2" python3 icedit reorder "$ICON" 1 2
names="$(layer_names)"
assert_eqaul "after move down" "$names" "$(printf 'square\ntriangle\ncircle')"

reset_icon
run_test "move position 3 to position 1" python3 icedit reorder "$ICON" 3 1
names="$(layer_names)"
assert_eqaul "after move up" "$names" "$(printf 'circle\ntriangle\nsquare')"

reset_icon
run_test "move by name" python3 icedit reorder "$ICON" circle 1
names="$(layer_names)"
assert_eqaul "after move by name" "$names" "$(printf 'circle\ntriangle\nsquare')"

reset_icon
run_test "move to same position (no-op)" python3 icedit reorder "$ICON" 2 2
names="$(layer_names)"
assert_eqaul "after no-op" "$names" "$(printf 'triangle\nsquare\ncircle')"

reset_icon
run_test "move first to last" python3 icedit reorder "$ICON" 1 3
names="$(layer_names)"
assert_eqaul "after move to last" "$names" "$(printf 'square\ncircle\ntriangle')"

# Reorder in second group
reset_icon
python3 -c "
import json
with open('$ICON/icon.json') as f:
    data = json.load(f)
data['groups'].append({'name': 'Second', 'layers': []})
with open('$ICON/icon.json', 'w') as f:
    json.dump(data, f)
" 2>/dev/null
python3 icedit add_svg "$ICON" "$SVG" alpha --group 2 2>/dev/null
python3 icedit add_svg "$ICON" "$SVG" beta --group 2 2>/dev/null
run_test "reorder in second group" python3 icedit reorder "$ICON" 2 1 --group 2
names="$(layer_names 1)"
assert_eqaul "second group order" "$names" "$(printf 'alpha\nbeta')"

# --- Export (if ictool available) ---

echo ""
echo "Export:"
ICTOOL="$(find_ictool)"
if [ -n "$ICTOOL" ]; then
    reset_icon
    rm -f /tmp/test_cli_icon.png
    run_test "export with ictool" "$ICTOOL" "$ICON" --export-image --output-file /tmp/test_cli_icon.png --platform macOS --rendition Default --width 1024 --height 1024 --scale 1
    assert_file_exists "exported PNG" /tmp/test_cli_icon.png
    rm -f /tmp/test_cli_icon.png
else
    echo "  (Icon Composer not available, skipping)"
fi

# --- Cleanup & Summary ---

rm -rf "$ICON"
rm -f /tmp/test_icedit_out.txt

echo ""
echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
echo "All icedit tests passed!"

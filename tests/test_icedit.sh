#!/bin/bash

set -e  # Exit on any error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "Starting icedit tests..."

# Clean up from previous runs
if [ -d "/tmp/test_cli_icon.icon" ]; then
    rm -rf "/tmp/test_cli_icon.icon"
    echo "Cleaned up previous test icon"
fi

# Ensure simple.svg exists
if [ ! -f "/tmp/simple.svg" ]; then
    cat > /tmp/simple.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg"><path d="M50 10 A40 40 0 1 1 50 90 A40 40 0 1 1 50 10"/></svg>
EOF
    echo "Created /tmp/simple.svg"
fi

# Test 1: Create icon
echo "Test 1: Creating icon with blue background"
python3 icedit create "/tmp/test_cli_icon.icon" blue
if [ ! -d "/tmp/test_cli_icon.icon" ]; then
    echo "ERROR: Icon directory not created"
    exit 1
fi
echo "✓ Icon created"

# Test 2: Add SVG layer
echo "Test 2: Adding SVG layer"
python3 icedit add_svg "/tmp/test_cli_icon.icon" "/tmp/simple.svg" circle --color red
if [ ! -f "/tmp/test_cli_icon.icon/Assets/circle.svg" ]; then
    echo "ERROR: SVG asset not added"
    exit 1
fi
echo "✓ SVG layer added"

# Test 3: Scale and shift
echo "Test 3: Scaling and shifting layer"
python3 icedit scale_shift "/tmp/test_cli_icon.icon" circle 0.8 20 30
echo "✓ Layer scaled and shifted"

# Test 4: Change gradient to solid
echo "Test 4: Changing gradient to solid"
python3 icedit change_gradient "/tmp/test_cli_icon.icon" circle solid green
echo "✓ Gradient changed to solid"

# Test 5: Change gradient to auto
echo "Test 5: Changing gradient to auto"
python3 icedit change_gradient "/tmp/test_cli_icon.icon" circle auto orange
echo "✓ Gradient changed to auto"

# Test 6: Change translucency
echo "Test 6: Changing translucency"
python3 icedit change_translucency "/tmp/test_cli_icon.icon" "" 0.5
echo "✓ Translucency set"

# Test 7: Export with ictool (if available)
echo "Test 7: Exporting icon"
if command -v /Applications/Icon\ Composer.app/Contents/Executables/ictool >/dev/null 2>&1; then
    rm -f "/tmp/test_cli_icon.png"
    /Applications/Icon\ Composer.app/Contents/Executables/ictool "/tmp/test_cli_icon.icon" --export-image --output-file "/tmp/test_cli_icon.png" --platform macOS --rendition Default --width 1024 --height 1024 --scale 1
    if [ -f "/tmp/test_cli_icon.png" ]; then
        echo "✓ Icon exported successfully"
        rm -f "/tmp/test_cli_icon.png"
    else
        echo "ERROR: Export failed"
        exit 1
    fi
else
    echo "⚠ Icon Composer not available, skipping export test"
fi

# Clean up
echo "Cleaning up..."
rm -rf "/tmp/test_cli_icon.icon"

echo "All icedit tests passed!"

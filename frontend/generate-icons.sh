#!/bin/bash

# Script to generate app icons from a base image
# Usage: ./generate-icons.sh <input-image.png>

INPUT_IMAGE=${1:-"icon-1024x1024.png"}
BUILD_DIR="build"

echo "🎨 Generating app icons from $INPUT_IMAGE..."

# Create build directory if it doesn't exist
mkdir -p "$BUILD_DIR"

# Check if input image exists
if [ ! -f "$INPUT_IMAGE" ]; then
    echo "❌ Error: Input image '$INPUT_IMAGE' not found!"
    echo "Please provide a 1024x1024 PNG image or create one first."
    exit 1
fi

# Generate Linux icon (512x512 PNG)
echo "📱 Generating Linux icon (icon.png)..."
sips -z 512 512 "$INPUT_IMAGE" --out "$BUILD_DIR/icon.png" 2>/dev/null || \
convert "$INPUT_IMAGE" -resize 512x512 "$BUILD_DIR/icon.png" 2>/dev/null || \
echo "⚠️  Warning: Could not generate icon.png. Install ImageMagick or use sips (macOS)."

# Generate macOS icon (.icns)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🍎 Generating macOS icon (icon.icns)..."
    
    # Create iconset directory
    ICONSET_DIR="$BUILD_DIR/icon.iconset"
    rm -rf "$ICONSET_DIR"
    mkdir -p "$ICONSET_DIR"
    
    # Generate all required sizes
    sips -z 16 16     "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_16x16.png" > /dev/null 2>&1
    sips -z 32 32     "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_16x16@2x.png" > /dev/null 2>&1
    sips -z 32 32     "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_32x32.png" > /dev/null 2>&1
    sips -z 64 64     "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_32x32@2x.png" > /dev/null 2>&1
    sips -z 128 128   "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_128x128.png" > /dev/null 2>&1
    sips -z 256 256   "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_128x128@2x.png" > /dev/null 2>&1
    sips -z 256 256   "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_256x256.png" > /dev/null 2>&1
    sips -z 512 512   "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_256x256@2x.png" > /dev/null 2>&1
    sips -z 512 512   "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_512x512.png" > /dev/null 2>&1
    sips -z 1024 1024 "$INPUT_IMAGE" --out "$ICONSET_DIR/icon_512x512@2x.png" > /dev/null 2>&1
    
    # Create .icns file
    iconutil -c icns "$ICONSET_DIR" -o "$BUILD_DIR/icon.icns" 2>/dev/null
    rm -rf "$ICONSET_DIR"
    
    if [ -f "$BUILD_DIR/icon.icns" ]; then
        echo "✅ macOS icon created successfully!"
    else
        echo "⚠️  Warning: Could not create .icns file"
    fi
else
    echo "⚠️  macOS icon generation skipped (not on macOS)"
fi

# Generate Windows icon (.ico) - requires ImageMagick
echo "🪟 Generating Windows icon (icon.ico)..."
if command -v convert &> /dev/null; then
    convert "$INPUT_IMAGE" -define icon:auto-resize=256,128,64,48,32,16 "$BUILD_DIR/icon.ico"
    if [ -f "$BUILD_DIR/icon.ico" ]; then
        echo "✅ Windows icon created successfully!"
    fi
else
    echo "⚠️  Warning: ImageMagick not found. Install it to generate .ico files."
    echo "   Or use an online converter: https://convertio.co/png-ico/"
fi

echo ""
echo "✨ Icon generation complete!"
echo "📁 Icons saved to: $BUILD_DIR/"
ls -lh "$BUILD_DIR"/icon.* 2>/dev/null || echo "⚠️  Some icons may not have been generated."


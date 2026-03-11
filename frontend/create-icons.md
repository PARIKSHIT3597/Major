# Creating App Icons for Desktop Application

## Quick Setup

### Option 1: Use Online Icon Generator (Recommended)

1. **Create a base icon** (1024x1024 PNG):
   - Use any image editor or online tool
   - Recommended: A chart/trend icon or dashboard symbol
   - Save as `icon-1024x1024.png`

2. **Generate icons using electron-icon-maker or online tools**:
   
   **Using electron-icon-maker (if installed):**
   ```bash
   npm install -g electron-icon-maker
   electron-icon-maker --input=icon-1024x1024.png --output=./build
   ```
   
   **Or use online tools:**
   - https://www.electronforge.io/tools/icons
   - https://iconverticons.com/online/
   - Upload your 1024x1024 PNG and download all formats

### Option 2: Manual Icon Creation

#### For macOS (.icns):
```bash
# Install iconutil (comes with macOS)
# Create iconset directory
mkdir build/icon.iconset

# Generate required sizes
sips -z 16 16     icon-1024x1024.png --out build/icon.iconset/icon_16x16.png
sips -z 32 32     icon-1024x1024.png --out build/icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon-1024x1024.png --out build/icon.iconset/icon_32x32.png
sips -z 64 64     icon-1024x1024.png --out build/icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon-1024x1024.png --out build/icon.iconset/icon_128x128.png
sips -z 256 256   icon-1024x1024.png --out build/icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon-1024x1024.png --out build/icon.iconset/icon_256x256.png
sips -z 512 512   icon-1024x1024.png --out build/icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon-1024x1024.png --out build/icon.iconset/icon_512x512.png
sips -z 1024 1024 icon-1024x1024.png --out build/icon.iconset/icon_512x512@2x.png

# Create .icns file
iconutil -c icns build/icon.iconset -o build/icon.icns
```

#### For Windows (.ico):
Use online converter or ImageMagick:
```bash
convert icon-1024x1024.png -define icon:auto-resize=256,128,64,48,32,16 build/icon.ico
```

#### For Linux (.png):
Use the 512x512 or 256x256 version:
```bash
sips -z 512 512 icon-1024x1024.png --out build/icon.png
```

### Option 3: Simple Setup (Using existing favicon)

If you have a favicon in `public/` folder:
```bash
# Copy and resize for app icon
cd frontend
cp public/vite.svg build/icon.png

# For macOS (requires iconutil)
# ... (follow Option 2 macOS steps)
```

## File Structure

After creating icons, your `frontend/build/` directory should contain:
```
build/
├── icon.icns    # macOS icon (required for macOS builds)
├── icon.ico     # Windows icon (required for Windows builds)
└── icon.png     # Linux icon (required for Linux builds, 512x512 recommended)
```

## Testing

After adding icons:
1. Rebuild the app: `npm run electron:build`
2. Check the app icon in the built application
3. The icon will appear in:
   - Dock/taskbar (macOS/Windows)
   - Application menu
   - Window title bar
   - About dialog

## Notes

- Minimum icon size: 512x512 pixels
- Recommended: 1024x1024 pixels for high-DPI displays
- Format: PNG for Linux/development, .icns for macOS, .ico for Windows
- Icons should be square and have transparent backgrounds (if needed)


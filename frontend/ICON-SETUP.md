# App Icon Setup Guide

## Quick Start: Generate Icons

### Step 1: Create or Download a Base Icon

You need a **1024x1024 PNG** image. Options:

1. **Create one online**: Use [Canva](https://www.canva.com), [Figma](https://www.figma.com), or similar
2. **Use an icon library**: Download from [Flaticon](https://www.flaticon.com) or [Icons8](https://icons8.com)
3. **Convert existing logo**: Use any image editor to resize to 1024x1024

**Icon suggestions for Market Dashboard:**
- 📈 Chart/Graph icon
- 💹 Stock market symbol
- 📊 Dashboard icon
- 💰 Money/Finance icon

### Step 2: Generate Icons Using the Script

**On macOS:**
```bash
cd frontend

# If you have a 1024x1024 PNG file:
./generate-icons.sh your-icon-1024x1024.png

# The script will create:
# - build/icon.icns (macOS)
# - build/icon.ico (Windows - if ImageMagick installed)
# - build/icon.png (Linux)
```

**On Windows/Linux:**
- Use an online icon generator (see below)

### Step 3: Use Online Icon Generator (Easiest)

1. Go to: https://www.electronforge.io/tools/icons
   OR
   https://iconverticons.com/online/

2. Upload your 1024x1024 PNG image

3. Download all formats:
   - `icon.icns` (macOS)
   - `icon.ico` (Windows)
   - `icon.png` (512x512 for Linux)

4. Place all three files in `frontend/build/` directory

## Manual Setup

### For macOS (.icns file)

1. Create a folder: `build/icon.iconset`
2. Generate these sizes from your base 1024x1024 image:
   - icon_16x16.png
   - icon_16x16@2x.png (32x32)
   - icon_32x32.png
   - icon_32x32@2x.png (64x64)
   - icon_128x128.png
   - icon_128x128@2x.png (256x256)
   - icon_256x256.png
   - icon_256x256@2x.png (512x512)
   - icon_512x512.png
   - icon_512x512@2x.png (1024x1024)

3. Run:
   ```bash
   iconutil -c icns build/icon.iconset -o build/icon.icns
   ```

### For Windows (.ico file)

Use ImageMagick or online converter:
```bash
convert icon-1024x1024.png -define icon:auto-resize=256,128,64,48,32,16 build/icon.ico
```

Or use: https://convertio.co/png-ico/

### For Linux (.png file)

Just resize your base image to 512x512:
```bash
sips -z 512 512 icon-1024x1024.png --out build/icon.png
```

## Verify Icons Are Set Up

After creating icons, check:

```bash
cd frontend
ls -lh build/icon.*
```

You should see:
- `icon.icns` (macOS)
- `icon.ico` (Windows)
- `icon.png` (Linux - 512x512)

## Testing the Icon

1. Rebuild the app:
   ```bash
   cd frontend
   npm run build
   npm run electron:build
   ```

2. The icon will appear in:
   - App dock/taskbar
   - Window title bar
   - About dialog
   - App switcher

## Current Status

✅ Electron main.js updated to use icons  
✅ Package.json configured for icon paths  
⚠️ You need to create the actual icon files in `frontend/build/`

## Quick Test Without Custom Icons

The app will work without custom icons, but will use the default Electron icon. To test the desktop app immediately:

```bash
./start-desktop.sh
```

Then add custom icons later when ready!


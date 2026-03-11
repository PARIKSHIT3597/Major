# Market Dashboard - Desktop Application Guide

## 🖥️ Desktop App Setup Complete!

Your Market Dashboard project is now configured as a desktop application using Electron.

## Quick Start

### Option 1: Using the Start Script (Recommended)

**macOS/Linux:**
```bash
./start-desktop.sh
```

**Windows:**
```bash
start-desktop.bat
```

This script will:
- Start the backend server automatically
- Launch the Electron desktop app
- Open DevTools in development mode

### Option 2: Manual Start

1. **Start Backend** (Terminal 1):
   ```bash
   cd backend
   python3 app.py
   ```

2. **Start Desktop App** (Terminal 2):
   ```bash
   cd frontend
   npm run electron:dev
   ```

## Building the Desktop App

### Development Build
The app runs in development mode with hot-reload and DevTools.

### Production Build

Build for your current platform:
```bash
cd frontend
npm run electron:build
```

Build for specific platforms:
```bash
# macOS
npm run electron:build:mac

# Windows
npm run electron:build:win

# Linux
npm run electron:build:linux
```

Built applications will be in `frontend/release/` directory.

## Project Structure

```
Major_Project/
├── backend/              # Python Flask backend
│   └── app.py           # Main server (runs on port 5001)
│
├── frontend/             # React + Electron frontend
│   ├── electron/        # Electron configuration
│   │   ├── main.js     # Electron main process
│   │   └── preload.js  # Preload script
│   ├── src/            # React application
│   └── dist/           # Built React app (generated)
│
├── start-desktop.sh     # macOS/Linux start script
└── start-desktop.bat    # Windows start script
```

## Features

✅ **Native Desktop Application**
- Runs as a standalone desktop app
- No browser required
- Native OS integration

✅ **Real-time Market Data**
- Live price updates via WebSocket
- Interactive charts
- News sentiment analysis

✅ **Cross-Platform**
- macOS (DMG, ZIP)
- Windows (NSIS installer, Portable)
- Linux (AppImage, DEB)

## Development vs Production

### Development Mode
- Connects to Vite dev server (`http://localhost:5173`)
- DevTools automatically open
- Hot module replacement enabled
- Backend must be running separately

### Production Mode
- Bundled React app loaded from `dist/`
- No DevTools
- Optimized build
- Backend still needs to run separately (or bundle it separately)

## Configuration

### Backend URL
The app connects to `http://localhost:5001` by default. To change this:

1. Update `frontend/src/socket.js`:
   ```javascript
   export const socket = io("http://your-backend-url:5001");
   ```

2. Update API calls in `frontend/src/components/Dashboard.jsx` and `NewsSentiment.jsx`

### Window Settings
Edit `frontend/electron/main.js` to customize:
- Window size
- Minimum window size
- Window title
- Icon

## Troubleshooting

### App won't start
- Ensure Node.js is installed: `node --version`
- Install dependencies: `cd frontend && npm install`
- Check that port 5173 is available

### Can't connect to backend
- Verify backend is running: `lsof -ti:5001` (macOS/Linux) or check Task Manager (Windows)
- Check connection status indicator in the app
- Verify backend URL in socket.js

### Build fails
- Run `npm run build` first to create the dist folder
- Check that all dependencies are installed
- Review error messages in the terminal

### Port conflicts
- Frontend dev server: 5173
- Backend server: 5001
- Make sure these ports are not in use

## Next Steps

### For Standalone Distribution
To create a fully standalone app (including backend):

1. **Bundle Python Backend** (using PyInstaller):
   ```bash
   pip install pyinstaller
   cd backend
   pyinstaller --onefile app.py
   ```

2. **Include in Electron Build**
   - Copy bundled backend to Electron resources
   - Update main.js to start backend automatically
   - Configure electron-builder to include backend

### Auto-Updater
Electron supports auto-updates. Configure in `package.json`:
- Add `electron-updater` package
- Configure update server
- Add update logic in main.js

## Available Scripts

| Script | Description |
|--------|-------------|
| `npm run dev` | Start Vite dev server only |
| `npm run build` | Build React app for production |
| `npm run electron` | Run Electron (requires built app) |
| `npm run electron:dev` | Run Electron with dev server |
| `npm run electron:build` | Build desktop app for current platform |
| `npm run electron:build:mac` | Build for macOS |
| `npm run electron:build:win` | Build for Windows |
| `npm run electron:build:linux` | Build for Linux |

## Notes

- The desktop app requires the backend server to be running
- For production, consider bundling the backend or using a cloud service
- The app uses WebSocket for real-time updates
- All API calls go to `http://localhost:5001`

## Support

For issues or questions:
1. Check the browser console (DevTools) for errors
2. Check backend server logs
3. Verify all dependencies are installed
4. Ensure ports 5001 and 5173 are available

---

**Enjoy your desktop Market Dashboard! 📈**


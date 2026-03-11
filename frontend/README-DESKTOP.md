# Market Dashboard - Desktop Application

This is the desktop version of the Market Dashboard application, built with Electron.

## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Backend server running on port 5001 (see main project README)

## Development

### Running the Desktop App in Development Mode

1. **Start the backend server** (in a separate terminal):
   ```bash
   cd ../backend
   python3 app.py
   ```

2. **Start the Electron app** (in the frontend directory):
   ```bash
   npm run electron:dev
   ```

   This will:
   - Start the Vite dev server on port 5173
   - Launch the Electron app
   - Open DevTools automatically

### Building the Desktop App

#### For macOS:
```bash
npm run electron:build:mac
```

#### For Windows:
```bash
npm run electron:build:win
```

#### For Linux:
```bash
npm run electron:build:linux
```

#### For all platforms:
```bash
npm run electron:build
```

Built applications will be in the `release/` directory.

## Production Build

The desktop app expects the backend server to be running. For a fully standalone app, you would need to bundle the Python backend as well (using tools like PyInstaller).

### Current Setup:
- Frontend: Bundled in Electron
- Backend: Must be run separately (Python server on port 5001)

## Project Structure

```
frontend/
├── electron/
│   ├── main.js          # Electron main process
│   ├── preload.js       # Preload script for security
│   └── package.json     # Electron package config
├── src/                 # React application
├── dist/                # Built React app (generated)
└── release/             # Built Electron apps (generated)
```

## Features

- ✅ Native desktop application
- ✅ Real-time market data visualization
- ✅ News sentiment analysis
- ✅ Cross-platform support (macOS, Windows, Linux)
- ✅ Auto-updater ready (can be configured)

## Troubleshooting

### App won't connect to backend
- Ensure the backend server is running on `http://localhost:5001`
- Check the connection status indicator in the app

### Build fails
- Make sure you've run `npm run build` first
- Check that all dependencies are installed: `npm install`

### Port conflicts
- The app uses port 5173 for the dev server
- Backend uses port 5001
- Make sure these ports are available

## Notes

- The app connects to `http://localhost:5001` for the backend API
- In production, you may want to configure a different backend URL
- The app includes DevTools in development mode only


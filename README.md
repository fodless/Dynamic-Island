# Dynamic Island for macOS

A macOS implementation of iPhone 14 Pro's Dynamic Island - an interactive widget that sits at the top of your screen displaying music controls, system information, and quick access to applications.

## Features

### Media Controls
- Real-time music playback information (song, artist, album)
- Album artwork display
- Interactive playback controls (play/pause, skip, volume)
- Waveform-style progress bar with scrubbing
- Supports Apple Music and Spotify

### Quick Access
- Launch up to 4 favorite applications directly from the island
- Right-click icon to change application
- Persistent settings across sessions

### Preset Workspaces
- 4 customizable workspace presets:
  - 💼 Programming
  - 🎧 Chilling
  - 🐛 Debugging
  - 🎯 Focus Mode
- Each preset can launch multiple applications at once
- Beautiful gradient-themed UI

### Visual Design
- Sleek pill-shaped widget at top of screen
- Smooth animations and transitions
- Modern dark theme with rounded corners
- Always-on-top floating window

## Requirements

- macOS 10.14 or later
- Python 3.13+
- PyObjC framework

## Installation

### Option 1: Use the pre-built app
1. Copy `Dynamic Island.app` to your Applications folder
2. Double-click to launch
3. Grant accessibility permissions if prompted

### Option 2: Run from source
```bash
python3 dynamic_island.py
```

## Usage

### Opening Settings
Click the gear icon (⚙️) in the Dynamic Island to open settings where you can:
- Configure Quick Access applications
- Set up Preset workspaces
- Customize your experience

### Media Controls
When music is playing:
- Click play/pause button to control playback
- Click skip buttons to navigate tracks
- Drag the waveform progress bar to scrub through the song
- Adjust volume with the volume slider

### Quick Access
- Click any of the 4 quick access slots to launch an application
- Right-click a slot to change the application

### Presets
- Click any preset card to launch all configured applications
- Click "Add App..." to add applications to a preset
- Apps are displayed in a scrollable list

## Tech Stack

- **Python 3**: Core application logic
- **PyObjC**: Objective-C bridge for macOS APIs
- **AppKit**: Native macOS UI framework
- **Foundation**: macOS system frameworks
- **ScriptingBridge**: Media player integration

## Project Structure

```
DynamicIsland/
├── Dynamic Island.app/     # macOS application bundle
│   ├── Contents/
│   │   ├── Info.plist     # App metadata
│   │   ├── MacOS/         # Executable launcher
│   │   └── Resources/     # App resources
│   │       ├── dynamic_island_main.py  # Main script
│   │       └── AppIcon.icns           # App icon
├── dynamic_island.py      # Source code
├── README.md             # This file
└── .gitignore           # Git ignore rules
```

## Settings Storage

Settings are stored in:
`~/Library/Preferences/com.dynamic_island.settings.plist`

This includes:
- Quick Access application paths
- Preset application configurations
- Window position and preferences

## Development

To modify the application:

1. Edit `dynamic_island.py`
2. Test your changes:
   ```bash
   python3 dynamic_island.py
   ```
3. Update the app bundle:
   ```bash
   cp dynamic_island.py "Dynamic Island.app/Contents/Resources/dynamic_island_main.py"
   ```

## Known Issues

- First launch may require granting accessibility permissions
- Some media players may not be fully supported

## Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

## License

This project is open source and available for personal and educational use.

## Credits

Inspired by Apple's Dynamic Island feature on iPhone 14 Pro.
# Dynamic-Island

# PigSpy - Police Scanner Monitor

A real-time police scanner monitoring application with speech recognition and keyword detection.

## Features

- Real-time audio stream monitoring
- Speech-to-text transcription using Whisper
- Keyword detection with notifications
- Textual-based TUI (Terminal User Interface)
- Cross-platform support (Windows/Linux/macOS)

## Installation

### Prerequisites

- Python 3.8 or higher
- FFmpeg (for audio processing)
- VLC Media Player (optional, for MP3 playback)

### Quick Install

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pigspy.git
cd pigspy
```

2. Install dependencies:
   - **Windows**: Double-click `install.bat`
   - **Linux/macOS**: Run `chmod +x install.sh && ./install.sh`

3. Configure your stream URL in `config.py`:
```python
STREAM_URL = "https://your-stream-url-here"
```

## Usage

Run the application:
```bash
python main.py
```

### Controls

- `1` - Start monitoring
- `2` - Stop monitoring
- `3` - Toggle audio passthrough
- `S` - Toggle silence mode
- `N` - Toggle notifications
- `C` - Clear logs

## Configuration

Edit `config.py` to customize:

- Stream URL
- Keywords to detect
- Audio settings
- Notification preferences

## License

MIT License - see LICENSE file for details.

## Disclaimer

This tool is for educational and research purposes only. Ensure you comply with all local laws and regulations regarding scanner monitoring.

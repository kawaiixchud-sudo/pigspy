# PigSpy GitHub Repository Setup Guide

## Quick Setup (3 Steps)

### Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Enter repository name: **pigspy**
3. Select **Public**
4. Do NOT check "Initialize this repository with a README"
5. Click **Create repository**

### Step 2: Copy Your Repository URL
After creating the repository, copy the HTTPS URL (looks like: `https://github.com/YOUR_USERNAME/pigspy.git`)

### Step 3: Push to GitHub
Run this command in the PigSpy_Portable folder:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/pigspy.git
git push -u origin master
```

Replace `YOUR_USERNAME` with your GitHub username.

---

## Automated Push (One Command)

If you already have your repository URL, run:
```powershell
python push_to_github.py
```

Then paste your repository URL when prompted.

---

## Full Project Structure

```
pigspy/
├── README.md              # Project documentation
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── main.py               # Main application
├── tui.py                # Terminal UI
├── stream_handler.py     # Audio stream handling
├── speech_recognizer.py  # Speech-to-text
├── keyword_detector.py   # Keyword detection
├── notifier.py           # Notifications
├── logger.py             # Logging
├── mp3_player.py         # Audio playback
├── police_codes.py       # Police code reference
├── install.bat           # Windows dependency installer
├── install.sh            # Linux/macOS installer
└── .gitignore            # Git ignore rules
```

---

## What's Been Done

✅ Removed all identifying computer information
✅ Cleaned up logs and build artifacts  
✅ Replaced specific URLs with placeholders
✅ Created professional README.md
✅ Added cross-platform install scripts (install.bat and install.sh)
✅ Initialized git repository with 2 commits
✅ Created .gitignore for Python and build files

---

## Next Steps After Pushing

1. **Update README**: Replace `yourusername` placeholder with your actual GitHub username
2. **Add Topics**: Go to repository settings and add topics like: python, police-scanner, speech-recognition, real-time-monitoring
3. **Enable Discussions**: Settings → Features → Enable Discussions
4. **Add License**: If not already present, consider adding a LICENSE file (MIT or Apache 2.0)

---

## Installation for Users

Users can now install PigSpy with:

```bash
git clone https://github.com/YOUR_USERNAME/pigspy.git
cd pigspy

# Windows
.\install.bat

# Linux/macOS
chmod +x install.sh
./install.sh

# Configure stream URL in config.py, then run:
python main.py
```

---

## Support

For issues or questions, please open an issue on the GitHub repository.

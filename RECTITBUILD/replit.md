# ReckITBuild (Discord Auto Messenger)

## Overview
A Python command-line script that sends automated messages to a Discord channel. It mimics human-like behavior by using configurable delays and random offsets between messages. Managed via a web-based UI.

## Project Structure
- `auto.py` - Main Python script
- `info.txt` - Stores user configuration (User ID, Discord token, channel URL, channel ID)
- `messages.txt` - Contains messages to be sent (one per line)
- `LICENSE` - MIT License
- `README.md` - Original project documentation

## How to Use
1. Run the workflow - it will start `python auto.py`
2. On first run, you'll be prompted to configure:
   - User ID
   - Discord token
   - Discord channel URL
   - Discord channel ID
3. After configuration, rerun to start sending messages
4. Customize messages by editing `messages.txt`

## Command Line Options
- `python auto.py` - Run the auto messenger
- `python auto.py --config` - Reconfigure user settings
- `python auto.py --setC` - Set channel URL and ID
- `python auto.py --help` - Show help

## Requirements
- Python 3.11 (installed via Replit modules)
- No external dependencies (uses only standard library)

## Notes
- This is a console/CLI application, not a web application
- Requires valid Discord credentials to function
- The script includes random sleep offsets to appear more human-like

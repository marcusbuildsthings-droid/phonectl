# phonectl - iOS Device Control CLI

## For AI Agents / LLMs

This document helps AI agents understand and use phonectl effectively.

## What It Does

phonectl is a Python CLI that controls iOS devices via USB using pymobiledevice3. It's a wrapper that makes common device operations simple one-liners.

## Prerequisites

- macOS with Python 3.9+
- iOS device connected via USB
- Device must be paired/trusted (run `pymobiledevice3 usbmux pair` first if needed)

## Installation

```bash
pip install pymobiledevice3
pip install -e /path/to/phonectl
```

## Commands Quick Reference

| Command | Description | Example |
|---------|-------------|---------|
| `phonectl devices` | List connected devices | `phonectl devices` |
| `phonectl apps` | List installed apps | `phonectl apps --user` |
| `phonectl screenshot` | Capture screen | `phonectl screenshot -o screen.png` |
| `phonectl launch` | Launch an app | `phonectl launch com.apple.mobilesafari` |
| `phonectl kill` | Kill an app | `phonectl kill com.apple.mobilesafari` |
| `phonectl ls` | List files | `phonectl ls /var/mobile/` |
| `phonectl pull` | Download file | `phonectl pull /path/to/file ./local` |
| `phonectl info` | Device info | `phonectl info` |

## Common Agent Tasks

### Check if device is connected
```bash
phonectl devices
# Returns JSON list of devices with UDID, name, model
```

### Take a screenshot and save it
```bash
phonectl screenshot -o /tmp/screen.png
# Creates PNG at specified path
```

### Find an app's bundle ID
```bash
phonectl apps --user | grep -i "app name"
# Output includes CFBundleIdentifier
```

### Launch Safari to a URL
```bash
phonectl launch com.apple.mobilesafari --url "https://example.com"
```

### Check device battery/status
```bash
phonectl info
# Returns device model, iOS version, battery level, etc.
```

## Error Handling

- **No devices**: Returns empty list, exit code 0
- **Device not paired**: Raises exception with instructions
- **App not found**: Returns error message, exit code 1
- **Permission denied**: Some paths require jailbreak

## Output Format

All commands output JSON by default for easy parsing:

```bash
phonectl devices
# [{"udid": "00008...", "name": "iPhone", "model": "iPhone14,2"}]
```

## Extending

The codebase is simple:
- `phonectl/cli.py` - Click CLI definitions
- `phonectl/device.py` - Device operations using pymobiledevice3

To add a new command, add to cli.py and implement in device.py.

## Security Notes

- Requires physical USB connection (no remote access)
- Device must be manually trusted by user
- No network exposure
- All operations are local

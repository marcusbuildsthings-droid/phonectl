# phonectl 📱

Simple CLI for iOS device control. Take screenshots, manage apps, browse files, and more.

```bash
pip install phonectl
```

## Why?

[pymobiledevice3](https://github.com/doronz88/pymobiledevice3) is incredibly powerful but has a complex CLI with dozens of subcommands. **phonectl** wraps the most common operations into simple, memorable commands.

## Quick Start

```bash
# List connected devices
phonectl list

# Take a screenshot
phonectl screenshot -o screen.png

# List installed apps
phonectl apps

# Launch an app
phonectl launch com.apple.mobilesafari

# Kill an app  
phonectl kill com.apple.mobilesafari

# Show device info
phonectl info
```

## File Operations

```bash
# List files
phonectl files ls /DCIM

# Pull file from device
phonectl files pull /DCIM/photo.jpg ./photo.jpg

# Push file to device
phonectl files push ./data.txt /Documents/data.txt
```

## iOS 17+ Support

iOS 17 changed how USB communication works. You need to start a tunnel daemon first:

```bash
# Start tunnel (requires sudo, run in separate terminal)
phonectl tunnel

# Then use other commands normally
phonectl screenshot
```

## All Commands

| Command | Description |
|---------|-------------|
| `phonectl list` | List connected devices |
| `phonectl info` | Show device information |
| `phonectl screenshot` | Take a screenshot |
| `phonectl apps` | List installed apps |
| `phonectl launch <bundle_id>` | Launch an app |
| `phonectl kill <bundle_id>` | Kill an app |
| `phonectl files ls <path>` | List files |
| `phonectl files pull <src> <dst>` | Pull file from device |
| `phonectl files push <src> <dst>` | Push file to device |
| `phonectl tunnel` | Start tunnel for iOS 17+ |

## Options

All commands support:
- `--udid, -u` — Specify device UDID (auto-selects first device if not provided)
- `--help` — Show help for any command

## Requirements

- macOS or Linux
- Python 3.9+
- iOS device connected via USB
- Device must be trusted (tap "Trust" when prompted)
- For iOS 17+: tunnel daemon must be running

## Installation

```bash
# From PyPI
pip install phonectl

# From source
git clone https://github.com/marcusbuildsthings-droid/phonectl
cd phonectl
pip install -e .
```

## Examples

### Automation Script

```bash
#!/bin/bash
# Take screenshots every 5 seconds

while true; do
    phonectl screenshot -o "screen_$(date +%s).png"
    sleep 5
done
```

### App Testing

```bash
# Kill app, relaunch, screenshot
phonectl kill com.myapp.test
phonectl launch com.myapp.test
sleep 2
phonectl screenshot -o test_result.png
```

### Backup Photos

```bash
# Pull all photos from DCIM
for file in $(phonectl files ls /DCIM/100APPLE); do
    phonectl files pull "/DCIM/100APPLE/$file" "./backup/$file"
done
```

## Troubleshooting

### "No devices found"
- Make sure device is connected via USB
- Check that you've tapped "Trust" on the device
- Try unplugging and reconnecting

### "Developer mode required" 
- Enable Developer Mode on device: Settings → Privacy & Security → Developer Mode

### "Permission denied" on iOS 17+
- Run `phonectl tunnel` in a separate terminal first (requires sudo)

### Screenshot fails
- Make sure Developer Mode is enabled
- For iOS 17+, ensure tunnel is running

## License

MIT

## Credits

Built on top of the excellent [pymobiledevice3](https://github.com/doronz88/pymobiledevice3) by doronz88.

# openclaw-pokemon-emulator

OpenClaw skill for playing Pokemon games via Game Boy and GBA emulation.

## Overview

This skill lets you control Pokemon game emulation on your machine through OpenClaw. Manage ROMs, save states, screenshots, and emulator settings using natural language commands.

## Supported Games

- Pokemon Red / Blue / Yellow (Game Boy)
- Pokemon Gold / Silver / Crystal (Game Boy Color)
- Pokemon Ruby / Sapphire / Emerald (Game Boy Advance)

## Supported Emulators

- **mGBA** - Great for GB/GBC/GBA
- **VBA-M** - Good GBA support
- **RetroArch** - Multi-system with libretro cores

## Installation

### Automatic (via OpenClaw)

```bash
openclaw skill install pokemon-emulator
```

### Manual

1. Clone this repository:
   ```bash
   git clone https://github.com/DevvGwardo/openclaw-pokemon-emulator.git
   ```

2. Copy the `pokemon-emulator` skill folder into your OpenClaw skills directory:
   ```bash
   # Windows
   copy pokemon-emulator %APPDATA%\npm\node_modules\openclaw\skills\

   # macOS / Linux
   cp -r pokemon-emulator ~/.openclaw/skills/
   ```

3. (Optional) Install an emulator if you don't have one:
   - **mGBA**: https://mgba.io/downloads.html
   - **VBA-M**: https://github.com/visualboyadvance-m/visualboyadvance-m/releases
   - **RetroArch**: https://www.retroarch.com/

## Usage

Once installed, OpenClaw will automatically use this skill when you want to play Pokemon games. Example commands:

```
"Launch Pokemon Emerald"
"Create a save state for me"
"Load my last save state"
"Take a screenshot"
"Configure emulator settings for Pokemon Ruby"
```

## Skill Structure

```
pokemon-emulator/
├── SKILL.md         # Skill definition and instructions
├── assets/          # Screenshots, box art, etc.
├── references/      # Game data, cheat databases
└── scripts/         # Helper scripts for emulator control
```

## Configuration

See `SKILL.md` for full configuration options including:
- Emulator executable paths
- ROM library location
- Save state directory
- Screenshot output path

## License

MIT License - see LICENSE file.

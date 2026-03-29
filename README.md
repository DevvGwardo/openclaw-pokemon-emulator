# 🎮 OpenClaw Pokemon Emulator Skill

> Play Pokemon, Game Boy, Game Boy Color, and Game Boy Advance games through OpenClaw!

```
    .---.     .---.     .---.     .---.     .---.
   /     \   /     \   /     \   /     \   /     \
  | () () | | () () | | () () | | () () | | () () |
   \  ^  /   \  ^  /   \  ^  /   \  ^  /   \  ^  /
    |||||     |||||     |||||     |||||     |||||
    |||||     |||||     |||||     |||||     |||||
   Pokemon   Pokemon   Pokemon   Pokemon   Pokemon
    Red       Blue     Yellow     Gold     Emerald
```

## What Is This?

The **Pokemon Emulator Skill** lets you play classic handheld Pokemon games directly through OpenClaw. It wraps two emulation backends:

- **PyBoy** — A pure-Python Game Boy (GB) and Game Boy Color (GBC) emulator. Great for scripting, automation, and lightweight play.
- **GBA Emulators** — Game Boy Advance games via subprocess launchers that work with mGBA, VBA-M, or any CLI-capable GBA emulator.

Beyond just launching games, this skill gives you:
- �save Save state management (multiple slots per game)
- 📸 Screenshot capture at any time
- ⌨️ Keyboard-driven gameplay control
- 🔧 Per-game configuration and hotkey maps

---

## 📋 Prerequisites

Before installing and using this skill, make sure you have the following:

### Required for GB/GBC Games (PyBoy)

| Requirement | Version/Details |
|---|---|
| **Python** | 3.8 or higher |
| **PyBoy** | Install via `pip install pyboy` |
| **ROM Files** | `.gb` or `.gbc` files you legally own |

### Required for GBA Games

| Requirement | Version/Details |
|---|---|
| **A GBA Emulator** | One of: **mGBA** (recommended), **VBA-M**, or any emulator with CLI support |
| **ROM Files** | `.gba` files you legally own |

### Optional but Recommended

| Requirement | Why |
|---|---|
| **SDL2** (for PyBoy) | Provides better performance; install via your system package manager |
| **qtpynput** or **pynput** | For advanced keyboard automation features |

---

## 🔧 Installing the Emulators

### Installing PyBoy

```bash
# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
# OR
.venv\Scripts\activate        # Windows

# Install PyBoy
pip install pyboy
```

> **Note:** PyBoy runs entirely in Python — no additional emulator binary needed!

### Installing mGBA (Recommended for GBA)

**Windows:**
1. Download mGBA from [https://mgba.io/downloads.html](https://mgba.io/downloads.html)
2. Extract the ZIP to a folder (e.g., `C:\Emulators\mGBA`)
3. Add that folder to your system `PATH`, or note the full path to `mgba.exe`

**Linux (Ubuntu/Debian):**
```bash
sudo add-apt-repository ppa:felis/linux-mgba
sudo apt update
sudo apt install mgba
```

**macOS:**
```bash
brew install mgba
```

### Installing VBA-M (Alternative GBA Emulator)

**Windows:**
1. Download VBA-M from [https://github.com/visualboyadvance-m/visualboyadvance-m/releases](https://github.com/visualboyadvance-m/visualboyadvance-m/releases)
2. Extract and place the executable somewhere convenient
3. Note the path to `visualboyadvance-m.exe`

**Linux:**
```bash
sudo apt install visualboyadvance-m
```

---

## 📦 Installing the Skill into OpenClaw

### Method 1: Via OpenClaw CLI (Recommended)

```bash
openclaw skill install pokemon-emulator
```

### Method 2: Manual Installation

If you need to install from a local path:

```bash
openclaw skill install --source C:\path\to\pokemon-emulator
```

### Method 3: Symlink for Development

If you're working on the skill itself:

```bash
# On Windows (PowerShell)
New-Item -ItemType SymbolicLink -Path "openclaw\skills\pokemon-emulator" -Target "C:\path\to\pokemon-emulator"

# On Linux/macOS
ln -s /path/to/pokemon-emulator ~/AppData/Roaming/openclaw/skills/pokemon-emulator
```

### Verify Installation

```bash
openclaw skill list | Select-String pokemon
# or
openclaw skill list | grep pokemon
```

---

## 🎮 Usage Examples

### Launch a Game

**Game Boy / Game Boy Color:**
```bash
python scripts/pyboy/launch.py "C:\ROMs\Pokemon\Pokemon - Red Version.gb"
```

**Game Boy Advance:**
```bash
python scripts/gba/launch.py "C:\ROMs\Pokemon\Pokemon - Emerald Version.gba"
```

### Or just ask OpenClaw naturally:

- *"Play Pokemon Yellow"*
- *"Start Pokemon Gold"*
- *"Launch Pokemon Emerald"*

### Save Your Game

```bash
# Save to slot 1
python scripts/pyboy/save_state.py "PokemonRed.gb" 1

# Save to slot 2
python scripts/pyboy/save_state.py "PokemonRed.gb" 2
```

### Load a Save State

```bash
# Load from slot 1
python scripts/pyboy/load_state.py "PokemonRed.gb" 1

# Load from slot 2
python scripts/pyboy/load_state.py "PokemonRed.gb" 2
```

### List Available Save Slots

```bash
python scripts/pyboy/list_states.py "PokemonRed.gb"
```

### Take a Screenshot

**PyBoy (GB/GBC):**
```bash
python scripts/pyboy/screenshot.py "PokemonRed.gb" "screenshots/pokedex.png"
```

**GBA:**
```bash
python scripts/gba/screenshot.py "PokemonEmerald.gba" "screenshots/battle.png"
```

### Or just ask OpenClaw:

- *"Take a screenshot of my Pokemon game"*
- *"Save my game in slot 3"*
- *"Show me my save states for Pokemon Blue"*

---

## 🎯 Gameplay Screenshot (PyBoy in Action)

```
┌─────────────────────────────────────────┐
│  ┌───────────────────────────────────┐  │
│  │                                   │  │
│  │   POKéMON RED                     │  │
│  │   ─────────────                   │  │
│  │                                   │  │
│  │   ┌─────┐                         │  │
│  │   │ ASH │  ♥♥♥♥♥♥♥♥  HP           │  │
│  │   └─────┘                         │  │
│  │                                   │  │
│  │        ┌────┐                     │  │
│  │        │BULB│                     │  │
│  │        │BASA│  Lv.5               │  │
│  │        └────┘                     │  │
│  │                                   │  │
│  │   ┌──────┐   ┌──────┐             │  │
│  │   │ POKE │   │ BAG  │             │  │
│  │   └──────┘   └──────┘             │  │
│  │                                   │  │
│  │   ┌──────┐   ┌──────┐             │  │
│  │   │ RUN  │   │FIGHT│             │  │
│  │   └──────┘   └──────┘             │  │
│  │                                   │  │
│  └───────────────────────────────────┘  │
│                                         │
│  [Arrow Keys] Move   [Z] A   [X] B      │
│  [Enter] Start       [Backspace] Select │
└─────────────────────────────────────────┘
```

---

## 📜 Supported Games

### Game Boy (GB) — via PyBoy

| Game | File Extension | Status |
|------|---------------|--------|
| Pokemon Red | `.gb` | ✅ Fully Supported |
| Pokemon Blue | `.gb` | ✅ Fully Supported |
| Pokemon Yellow | `.gb` | ✅ Fully Supported |
| Pokemon Green (JP) | `.gb` | ✅ Fully Supported |
| Tetris | `.gb` | ✅ Fully Supported |
| The Legend of Zelda: Link's Awakening | `.gb` | ✅ Fully Supported |
| Super Mario Land | `.gb` | ✅ Fully Supported |

### Game Boy Color (GBC) — via PyBoy

| Game | File Extension | Status |
|------|---------------|--------|
| Pokemon Gold | `.gbc` | ✅ Fully Supported |
| Pokemon Silver | `.gbc` | ✅ Fully Supported |
| Pokemon Crystal | `.gbc` | ✅ Fully Supported |
| The Legend of Zelda: Oracle of Ages | `.gbc` | ✅ Fully Supported |
| The Legend of Zelda: Oracle of Seasons | `.gbc` | ✅ Fully Supported |
| Pokemon Pinball (GBC) | `.gbc` | ✅ Fully Supported |

### Game Boy Advance (GBA) — via mGBA / VBA-M

| Game | File Extension | Status |
|------|---------------|--------|
| Pokemon Ruby | `.gba` | ✅ Fully Supported |
| Pokemon Sapphire | `.gba` | ✅ Fully Supported |
| Pokemon Emerald | `.gba` | ✅ Fully Supported |
| Pokemon FireRed | `.gba` | ✅ Fully Supported |
| Pokemon LeafGreen | `.gba` | ✅ Fully Supported |
| Pokemon Mystery Dungeon (Red/Blue) | `.gba` | ✅ Fully Supported |

> ⚠️ **Important:** ROM files are **not included** with this skill. You must own and provide your own legally-obtained ROM files. This skill does not distribute or encourage piracy.

---

## 📁 Directory Structure

```
pokemon-emulator/
├── README.md                 # This file!
├── SKILL.md                  # Skill metadata & internal docs
├── scripts/
│   ├── pyboy/               # GB/GBC emulation scripts
│   │   ├── launch.py        # Launch a GB/GBC game
│   │   ├── save_state.py    # Save to a slot
│   │   ├── load_state.py    # Load from a slot
│   │   ├── list_states.py   # List all save slots
│   │   └── screenshot.py    # Capture a screenshot
│   └── gba/                 # GBA emulation scripts
│       ├── launch.py        # Launch a GBA game
│       ├── save_state.py    # Save (via emulator hotkey)
│       ├── load_state.py    # Load (via emulator hotkey)
│       └── screenshot.py    # Capture a screenshot
├── references/
│   ├── hotkeys.md           # Default keyboard mappings
│   └── game-configs/        # Per-game settings
│       └── pokemon-emerald.md
└── assets/
    ├── saves/               # Save state files (*.state0, *.state1, etc.)
    └── screenshots/         # Captured screenshots
```

---

## 🔑 Default Hotkeys

### PyBoy (GB/GBC)

| Key | Action |
|-----|--------|
| Arrow Keys | D-Pad / Movement |
| Z | A Button |
| X | B Button |
| Enter | Start |
| Backspace | Select |

### GBA Emulators (mGBA / VBA-M)

Hotkeys depend on your emulator configuration. By default:

| Key | Action |
|-----|--------|
| Arrow Keys | D-Pad / Movement |
| Z | A Button |
| X | B Button |
| Enter | Start |
| Backspace | Select |
| Escape | Exit / Menu |

> 💡 Check `references/hotkeys.md` for customizable hotkey profiles.

---

## ❓ Troubleshooting

### "PyBoy not found" / ImportError

```bash
pip install pyboy
```

If you're using a virtual environment, make sure it's activated before running any scripts.

### "mGBA not found" when launching GBA games

Make sure mGBA is installed and the executable is in your system `PATH`.

```bash
# Verify on Windows
where mgba

# Verify on Linux/macOS
which mgba
```

If it's not in your PATH, you can set the `MGBA_PATH` environment variable:

```bash
$env:MGBA_PATH = "C:\Emulators\mGBA\mgba.exe"  # Windows
export MGBA_PATH="/usr/local/bin/mgba"          # Linux/macOS
```

### "ROM file not found"

- Double-check the path to your ROM file — use the full absolute path
- Make sure the file extension is correct (`.gb`, `.gbc`, or `.gba`)
- On Windows, use backslashes in quotes: `scripts\pyboy\launch.py "C:\ROMs\Pokemon\red.gb"`

### Save states not loading

- Save states are game-specific. A save state made in Pokemon Red won't work for Pokemon Blue.
- Check that the ROM filename matches exactly when loading a state.
- Make sure you have write permissions in the `assets/saves/` directory.

### PyBoy window not responding / frozen

- Press `Escape` to attempt to close the window.
- If that doesn't work, force-close the terminal running the script.
- Save states are preserved in `assets/saves/` and can be loaded on the next run.

### GBA game runs but no sound

- mGBA: Go to `Options > Audio` and enable audio output.
- VBA-M: Go to `Config > Audio > Sound Output` and enable it.
- Check your system volume settings.

### Game runs too fast / too slow

- PyBoy: Set an FPS cap via environment variable:
  ```bash
  $env:PYBOY_FPS = "60"
  ```
- mGBA: `Config > Frame Rate` — set to "Original" for authentic speed.

### "Permission denied" errors

On Linux/macOS, make sure the scripts are executable:
```bash
chmod +x scripts/pyboy/*.py
chmod +x scripts/gba/*.py
```

---

## 🤝 Contributing

Contributions are welcome! Here's how to get involved:

### Ways to Contribute

- 🐛 **Report bugs** — Open an issue with the game name, emulator, and steps to reproduce
- 💡 **Suggest features** — Have an idea? Open an issue or PR!
- 📖 **Improve docs** — Spelling fixes, clearer instructions, better examples
- 🔧 **Add new emulator support** — e.g., NO$GBA, Mednafen, RetroArch
- 🎮 **Add game configs** — New per-game hotkey profiles in `references/game-configs/`

### Development Setup

```bash
# Clone the skill repo
git clone https://github.com/your-username/openclaw-pokemon-emulator.git
cd openclaw-pokemon-emulator

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install PyBoy for local testing
pip install pyboy

# Test a script
python scripts/pyboy/launch.py "path/to/your/rom.gb"
```

### Code Style

- Follow [PEP 8](https://pep8.org/) for Python code
- Use meaningful variable and function names
- Add docstrings to all public functions
- Keep scripts focused — one responsibility per file

### Pull Request Process

1. **Fork** the repository
2. **Create a branch** for your feature or fix: `git checkout -b my-feature`
3. **Make your changes** and test them
4. **Update docs** if you're adding new functionality
5. **Open a PR** with a clear description of what changed and why

---

## ⚖️ Legal Disclaimer

This skill is a **framework for running legally-owned game ROMs**. It does not:

- Include any ROM files
- Download or distribute copyrighted game data
- Encourage or facilitate piracy

You must **own** the games you emulate. In many countries, owning a ROM backup of a game you physically own is legal; however, laws vary by jurisdiction. **Use responsibly.**

---

## 🙏 Credits

- **PyBoy** — [https://github.com/Baekalfen/PyBoy](https://github.com/Baekalfen/PyBoy) — Pure Python Game Boy emulator
- **mGBA** — [https://mgba.io/](https://mgba.io/) — Game Boy Advance emulator
- **VBA-M** — [https://github.com/visualboyadvance-m/visualboyadvance-m](https://github.com/visualboyadvance-m/visualboyadvance-m) — Enhanced Visual Boy Advance

---

## 📞 Support

Need help? Open an issue at the [OpenClaw issues page](https://github.com/openclaw/openclaw/issues) with:
- Your operating system
- The emulator and version
- The ROM file name
- Steps to reproduce the problem

---

*Happy gaming! 🎮 Let's catch 'em all!*

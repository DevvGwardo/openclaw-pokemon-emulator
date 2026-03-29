---
name: pokemon-emulator
description: Play Pokemon, Game Boy (GB), Game Boy Color (GBC), and Game Boy Advance (GBA) games via emulation. Provides scripts to launch games, manage save states, capture screenshots, and control gameplay through PyBoy (GB/GBC) and subprocess-based GBA emulators.
---

# Pokemon Emulator Skill

Play Pokemon and similar retro handheld games through Python-based and subprocess-based emulation on your machine.

## When to Use

Activate this skill when the user wants to:

- Play Pokemon games (any generation on GB/GBC/GBA)
- Play other Game Boy or Game Boy Color games
- Play Game Boy Advance games
- Manage save states during gameplay
- Capture screenshots or clips from games
- Configure emulator settings per game

## Available Emulators

### PyBoy (GB/GBC)

Python library for Game Boy emulation. Lightweight, scriptable, good for automation.

**Requirements:** `pip install pyboy`

**Location:** `scripts/pyboy/` — contains launch and control scripts

### GBA via Subprocess

Game Boy Advance games run via external emulator invoked as subprocess.

**Requirements:** mGBA, VBA-M, or similar CLI-capable emulator installed

**Location:** `scripts/gba/` — contains launch and control scripts

## Directory Structure

```
pokemon-emulator/
├── SKILL.md           # This file
├── scripts/
│   ├── pyboy/         # GB/GBC emulation scripts (PyBoy)
│   └── gba/           # GBA emulation scripts (subprocess)
├── references/        # Game-specific configs, hotkey maps, ROM notes
└── assets/            # Screenshots, save states generated during play
```

## Usage

### Launch a Game

```
python scripts/pyboy/launch.py <rom_path>
python scripts/gba/launch.py <rom_path>
```

### Save/Load State

```
python scripts/pyboy/save_state.py <rom_path> <slot>
python scripts/pyboy/load_state.py <rom_path> <slot>
```

### Screenshot

```
python scripts/pyboy/screenshot.py <rom_path> <output_path>
python scripts/gba/screenshot.py <rom_path> <output_path>
```

### List Save Slots

```
python scripts/pyboy/list_states.py <rom_path>
```

## Example Prompts

- "Play Pokemon Yellow"
- "Start Pokemon Gold and save my game"
- "Launch Pokemon Emerald and take a screenshot"
- "Load my Pokemon Red save state"
- "Play Tetris on Game Boy"
- "Start a GBA game — Pokemon FireRed"
- "Capture a screenshot from my Pokemon save state"

## Notes

- ROM files are not included — user must provide their own legally-owned ROMs
- Save states are stored in `assets/` with the ROM name as prefix
- Default hotkeys for GBA emulators depend on the emulator used; see `references/hotkeys.md`

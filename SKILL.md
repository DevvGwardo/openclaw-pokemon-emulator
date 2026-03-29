---
name: pokemon-emulator
description: "Play Pokemon and similar retro handheld games through Python-based and subprocess-based emulation on your machine. Provides scripts to launch games, manage save states, capture screenshots, and control gameplay through PyBoy (GB/GBC) and mGBA/VBA-M (GBA). Triggers when user wants to: play Pokemon games, play Game Boy/Color/Advance games, automate gameplay, capture screenshots, manage save states."
---

# Pokemon Emulator Skill

Play Pokemon and similar retro handheld games through Python-based and subprocess-based emulation.

## When to Use

Activate this skill when the user wants to:
- Play Pokemon games (any generation: GB/GBC/GBA)
- Play other Game Boy or Game Boy Color games via PyBoy
- Play Game Boy Advance games via mGBA or VBA-M
- Automate gameplay (AI-driven button presses)
- Capture screenshots or clips from games
- Manage save states during gameplay

## Available Emulators

### PyBoy (GB/GBC) — Python-native

Python library for Game Boy / Game Boy Color emulation. Scriptable, no external binary.

**Install:** `pip install pyboy pysdl2-dll numpy`
**Script:** `scripts/pyboy_interface.py`

```python
from pyboy_interface import PyBoyGame, A, B, UP, DOWN

game = PyBoyGame("pokemon_red.gb")
game.press_button(A)
x, y = game.get_position()
screen = game.get_screen()  # np.array (144, 160, 3)
```

### mGBA (GBA) — Recommended

Controls mGBA via PyAutoGUI (window focus + keypresses). HLE BIOS — no BIOS file needed.

**Install:** Download from https://mgba.io (portable .7z, no install needed)
**Script:** `scripts/mgba_control.py`

```python
from mgba_control import GBAEmulator, BUTTONS

gba = GBAEmulator("pokemon_ruby.gba", mgba_path="C:/mgba/mGBA.exe")
gba.press_button("A", frames=5)
gba.press_button("START", frames=3)
screen = gba.get_screen()  # PIL Image
gba.stop()
```

### PyBoyAdvance (GBA) — Pure Python fallback

Pure Python GBA emulator. Requires GBA BIOS file.

**Install:** `pip install pyboy-advance numpy pillow`
**Script:** `scripts/gba_interface.py`

## Key Scripts

| Script | Platform | Notes |
|--------|----------|-------|
| `scripts/pyboy_interface.py` | GB/GBC | Full API: RAM read/write, position, party, battle state |
| `scripts/mgba_control.py` | GBA | PyAutoGUI control of mGBA window |
| `scripts/gba_interface.py` | GBA | PyBoyAdvance wrapper (needs BIOS) |

## Common RAM Addresses (Pokemon Red/Blue)

| Data | Address |
|------|---------|
| Player X | 0xD362 |
| Player Y | 0xD361 |
| Map Number | 0xD35E |
| Money | 0xD47F |
| Party Count | 0xD163 |
| Badges | 0xD2F7 |
| First Pokemon HP | 0xD16C |
| Game State | 0xD057 (0=overworld, 1-6=battle) |

## Example Prompts

- "Play Pokemon Yellow on Game Boy"
- "Start Pokemon Ruby and navigate the intro"
- "Play Pokemon FireRed on GBA and show me the screen"
- "Run Pokemon Gold, get my party info"
- "Automate playing Tetris on Game Boy"
- "Save my Pokemon Red game state"

## Notes

- **ROM files not included** — user must provide their own legally-owned ROMs
- mGBA is the recommended GBA emulator (HLE, no BIOS required, fast)
- PyBoy is the recommended GB/GBC emulator (pure Python, scriptable)
- Save states stored in `assets/` directory
- Screenshots saved as PNG in working directory

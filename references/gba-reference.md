# GBA Emulator Reference

## Overview

Two supported approaches for OpenClaw:

1. **PyBoyAdvance** — Pure Python, pip-installable, no external binary (recommended for portability)
2. **mGBA / RetroArch** — Production-grade, cycle-accurate, requires external binary (recommended for performance)

---

## Option 1: PyBoyAdvance (Pure Python)

### Installation

```bash
pip install pyboy-advance numpy pillow
```

**Requires:** GBA BIOS file (Normatt's open-source BIOS: https://github.com/Normmatt/PowerStone/releases or search for "gba_bios.bin")

```python
from pyboy_advance import PyBoyAdvance

emulator = PyBoyAdvance(rom="game.gba", bios="/path/to/gba_bios.bin")
emulator.run()
```

### CLI

```bash
pyboy_advance --bios /path/to/bios.bin game_rom.gba
```

### API

```python
from pyboy_advance import PyBoyAdvance

emu = PyBoyAdvance(rom="pokemon.gba", bios="gba_bios.bin")

# Advance one frame
emu.tick()

# Press a button
emu.button('A')
emu.button('B')
emu.button('START')
emu.button('SELECT')
emu.button('UP', frames=60)  # hold for N frames

# Read screen
screen = emu.screen()  # np.ndarray shape (160, 240, 3)
```

### Limitations
- **Slow on CPython** — even with Cython compilation, ~10-30% of native speed
- Many GBA hardware features unimplemented
- Not suitable for real-time gameplay

---

## Option 2: mGBA + Python (Production)

### Installation

1. Download mGBA: https://mgba.io/downloads.html
2. Add to PATH or note install location

### Python Integration (via subprocess + socket)

Use **mGBA-http** project (https://github.com/nikouu/mGBA-http) to remote-control a running mGBA instance:

```python
import requests

# mGBA must be running with Lua scripting enabled
# mGBA-http server running on localhost:5000

requests.post("http://localhost:5000/input", json={"button": "A"})
requests.post("http://localhost:5000/screenshot")
```

### RetroArch + VBA-M Core (CLI approach)

```bash
# Install RetroArch: https://retroarch.com/
# Download VBA-M libretro core (.dll/.so)
```

```python
import subprocess

retroarch = r"C:\RetroArch\retroarch.exe"
core = r"C:\RetroArch\cores\vbam_libretro.dll"
rom = r"C:\Roms\GBA\Pokemon.gba"

process = subprocess.Popen([retroarch, "-L", core, rom])
```

### Keyboard Shortcuts for Both

| Button | PyBoyAdvance | mGBA / RetroArch |
|--------|-------------|-----------------|
| A      | `button('A')` | `A` key |
| B      | `button('B')` | `S` key |
| Start  | `button('START')` | `Enter` |
| Select | `button('SELECT')` | `Backspace` |
| Up     | `button('UP')` | `Arrow Up` |
| Down   | `button('DOWN')` | `Arrow Down` |
| Left   | `button('LEFT')` | `Arrow Left` |
| Right  | `button('RIGHT')` | `Arrow Right` |
| L      | `button('L')` | `Q` |
| R      | `button('R')` | `E` |

---

## Screen Dimensions

- GBA screen: **240×160 pixels** (3:4 portrait ratio)
- Color depth: 16-bit (5 bits per channel RGB)

---

## GBA Pokemon Games RAM Addresses

Known addresses for Pokemon Emerald (GBA):

| Data         | Address (approx) |
|--------------|-----------------|
| Player X     | 0x022FF808 |
| Player Y     | 0x022FF80C |
| Party Count  | 0x0222D000 |
| Money        | 0x0222CF48 |
| Badges       | 0x0222CD38 |

> GBA RAM addresses vary significantly between games and versions. Memory scanning (like PyBoy's `memory_scanner`) is the best approach to find dynamic addresses.

---

## Save States

Both mGBA and VBA-M support save states:

```python
# mGBA - via Lua scripting
# Use Tools > Lua > run mGBASocketServer.lua

# Save
requests.post("http://localhost:5000/savestate", json={"slot": 1})

# Load
requests.post("http://localhost:5000/loadstate", json={"slot": 1})
```

```bash
# RetroArch command-line
retroarch -L vbam_libretro.dll rom.gba --save-subtitle "slot1"
```

---

## Recommended Setup for OpenClaw

For maximum compatibility:

1. **Development / scripting:** PyBoyAdvance (pure Python, no external deps)
2. **Production automation:** mGBA + mGBA-http (native speed, HTTP API)

To switch between them, update `TOOLS.md` in the workspace with the emulator path.

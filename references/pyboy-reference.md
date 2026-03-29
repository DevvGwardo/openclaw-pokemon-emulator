# PyBoy API Reference

PyBoy Docs: https://docs.pyboy.dk/

## Installation

```bash
pip install pyboy
# For GUI rendering (Windows):
pip install pysdl2-dll
# Linux: libsdl2-dev
# macOS: brew install sdl2
```

---

## Core API

### PyBoy Class

```python
from pyboy import PyBoy

pyboy = PyBoy('rom.gb', sound=False, window='SDL2', bios=None)
while pyboy.tick():
    pass
pyboy.stop()
```

**Constructor args:**
- `rom` — path to ROM file or file-like object
- `sound` — enable sound (default False)
- `window` — `'SDL2'` for GUI, `None` for headless
- `bios` — path to BIOS file (optional)
- `rewind` — enable rewind feature (default False)
- `game_wrapper` — pre-built game wrapper (e.g. `pyboy.plugins.MarioPlugin`)

---

### Button Input

```python
pyboy.button('a')              # Press + auto-release (1 frame)
pyboy.button('down')            # Press down for 1 frame
pyboy.button_press('right')     # Hold
pyboy.button_release('right')   # Release
```

**Buttons:** `'a'`, `'b'`, `'start'`, `'select'`, `'left'`, `'right'`, `'up'`, `'down'`

---

### Screen

```python
pyboy.screen.image        # PIL Image
pyboy.screen.ndarray      # np.ndarray (144, 160, 4) RGBA
pyboy.screen.raw_buffer   # raw bytes
pyboy.screen.raw_buffer_dims  # (rows, cols)
```

> ⚠️ For AI/bots: use `tilemap_background`, `tilemap_window`, and `get_sprite()` instead of screen captures — much more efficient.

---

### Tilemap Access (efficient game state)

```python
pyboy.tilemap_background[7:12, 8:11]  # slice tilemap
pyboy.tilemap_window[8, 8]
```

### Sprites

```python
for sprite in pyboy.get_sprite(0):  # iterate sprites
    print(sprite)
```

---

### Memory / RAM

```python
value = pyboy.memory[0xC345]                  # read byte
pyboy.memory[0xC000] = 1                       # write byte
data = pyboy.memory[0xC000:0xC010]            # read slice
pyboy.memory[2, 0xA000]                       # external RAM bank 2
pyboy.memory[0, 0x2000]                       # ROM bank 0
```

**Key memory ranges:**
- `0x0000–0x7FFF` — ROM (banked)
- `0x8000–0x9FFF` — Video RAM
- `0xC000–0xCFFF` — Work RAM (WRAM)
- `0xFF00–0xFF7F` — I/O registers
- `0xFF80–0xFFFF` — High RAM (HRAM)

---

### Memory Scanner

```python
pyboy.memory_scanner.scan_memory(4, start_addr=0xC000, end_addr=0xDFFF)
```

---

### Save / Load State

```python
import io

# Save
with io.BytesIO() as f:
    pyboy.save_state(f)
    saved = f.getvalue()

# Load
with io.BytesIO(saved) as f:
    pyboy.load_state(f)

# File-based
with open('state.state', 'wb') as f:
    pyboy.save_state(f)
```

---

### GameShark / Cheats

```python
pyboy.gameshark.add("01FF16D0")       # add cheat
pyboy.gameshark.remove("01FF16D0")    # remove cheat
pyboy.gameshark.clear_all()           # clear all
```

Code format: `ttvvaaaa` — type (01), value (vv), address low-byte-first (aaaa)

---

### Speed Control

```python
pyboy.tick()           # normal: ~60fps
pyboy.tick(15)         # frame-skip 15: ~344x realtime
pyboy.set_emulation_speed(0)  # unlimited
```

---

## Game Wrappers (Plugins)

Pre-built wrappers for specific games:

```python
from pyboy.plugins.manager import PluginManager
MarioPlugin = pyboy.get_plugin("pyboy.plugins.mario.MarioPlugin")
```

Available plugins (check `pyboy.plugins` for full list):
- Mario
- Tetris
- Kirby
- Pokemon Red/Blue (partial)

---

## Pokemon Red/Blue Known RAM Addresses

| Data         | Address |
|--------------|---------|
| Player X     | 0xD362  |
| Player Y     | 0xD361  |
| Map Number   | 0xD35E  |
| Money        | 0xD47F  |
| Party Count  | 0xD163  |
| Badges       | 0xD2F7  |
| First Pokemon HP | 0xD16C (low), 0xD16D (high) |
| Game State   | 0xD057  |

**Game state detection:**
- 0x00 = overworld
- 0x01–0x06 = battle
- 0x11 = menu
- 0x02 = text/dialog

> Addresses may vary by ROM version. Validate against your specific dump.

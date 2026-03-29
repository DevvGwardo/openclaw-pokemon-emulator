"""
gba_interface.py - Clean Python interface for GBA Pokemon game automation.

IMPLEMENTATION: Uses PyBoyAdvance (Python-native GBA emulator).
  pip install pyboy-advance

ALTERNATIVE: mGBA with mgba-mcp (see "Alternative: mGBA" section below).

Dependencies:
    pip install pyboy-advance numpy pillow

You also need a GBA BIOS file (e.g. gba_bios.bin). Normatt's open-source BIOS:
    https://github.com/Nebuleon/ReGBA/raw/master/bios/gba_bios.bin

External dependencies (must be installed):
    1. Python 3.8+
    2. pip install pyboy-advance numpy pillow
    3. A GBA BIOS file (gba_bios.bin)
    4. GBA ROM files (.gba)

Usage:
    from gba_interface import GBAEmulator, Button

    emulator = GBAEmulator(bios_path="path/to/gba_bios.bin")
    emulator.load_rom("path/to/pokemon.gba")
    emulator.press_button(Button.A)
    screen = emulator.get_screen()   # numpy array (H, W, 3), uint8
    print(emulator.is_running())
    emulator.close()
"""

from __future__ import annotations

import subprocess
import os
import sys
import time
import tempfile
import shutil
from pathlib import Path
from typing import Optional

import numpy as np

# Try to import PyBoyAdvance; provide clear error if not available
try:
    from pyboy_advance import PyBoyAdvance
except ImportError:
    PyBoyAdvance = None


# ---------------------------------------------------------------------------
# Button constants
# ---------------------------------------------------------------------------
class Button:
    """GBA button constants for use with GBAEmulator.press_button()."""
    A      = "a"
    B      = "b"
    START  = "start"
    SELECT = "select"
    UP     = "up"
    DOWN   = "down"
    LEFT   = "left"
    RIGHT  = "right"
    L      = "l"
    R      = "r"

    @classmethod
    def all(cls) -> list[str]:
        return [cls.A, cls.B, cls.START, cls.SELECT,
                cls.UP, cls.DOWN, cls.LEFT, cls.RIGHT,
                cls.L, cls.R]


# ---------------------------------------------------------------------------
# Primary implementation: PyBoyAdvance
# ---------------------------------------------------------------------------

class GBAEmulator:
    """
    Clean interface for playing/automating GBA Pokemon games using
    PyBoyAdvance (a Python-native GBA emulator).

    Parameters
    ----------
    bios_path : str
        Path to the GBA BIOS file (e.g. gba_bios.bin).
        Required. Normatt's open-source BIOS:
        https://github.com/Nebuleon/ReGBA/raw/master/bios/gba_bios.bin

    speed : int, default 1
        Emulation speed multiplier. Use > 1 for faster automation.
        Note: PyBoyAdvance is slow on CPython; speed > 1 helps.

    headless : bool, default False
        If True, disables the SDL window. Useful for server/automation
        contexts where you only need screen frames.
    """

    # Screen dimensions for GBA
    WIDTH  = 240
    HEIGHT = 160
    SCREEN_SHAPE = (HEIGHT, WIDTH, 3)   # RGB

    def __init__(
        self,
        bios_path: str,
        speed: int = 1,
        headless: bool = False,
    ):
        if PyBoyAdvance is None:
            raise ImportError(
                "PyBoyAdvance is not installed.\n"
                "Run: pip install pyboy-advance\n"
                "Also install dependencies: pip install numpy pillow"
            )
        if not os.path.isfile(bios_path):
            raise FileNotFoundError(
                f"GBA BIOS not found at: {bios_path}\n"
                "Download Normatt's open-source BIOS from:\n"
                "  https://github.com/Nebuleon/ReGBA/raw/master/bios/gba_bios.bin"
            )

        self._bios_path = os.path.abspath(bios_path)
        self._speed = speed
        self._headless = headless
        self._pyboy: Optional[PyBoyAdvance] = None
        self._rom_path: Optional[str] = None
        self._running = False
        self._screen_buffer: Optional[np.ndarray] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_rom(self, path: str) -> None:
        """
        Load a GBA ROM file and start emulation.

        Parameters
        ----------
        path : str
            Absolute or relative path to a .gba ROM file.
        """
        if not os.path.isfile(path):
            raise FileNotFoundError(f"ROM not found: {path}")

        # Close any existing session
        self._close_pyboy()

        abs_path = os.path.abspath(path)
        self._pyboy = PyBoyAdvance(
            rom=abs_path,
            bios=self._bios_path,
        )
        self._rom_path = abs_path
        self._running = True

        # Set emulation speed if supported
        try:
            if hasattr(self._pyboy, 'set_emulation_speed'):
                self._pyboy.set_emulation_speed(self._speed)
        except Exception:
            pass

        # If headless, try to disable video output
        if self._headless:
            try:
                if hasattr(self._pyboy, 'disable_video'):
                    self._pyboy.disable_video()
            except Exception:
                pass

    def press_button(self, button: str, frames: int = 1) -> None:
        """
        Press and hold a GBA button for a number of frames.

        Parameters
        ----------
        button : str
            One of the Button constants (A, B, START, SELECT,
            UP, DOWN, LEFT, RIGHT, L, R).
        frames : int, default 1
            Number of frames to hold the button. The emulator
            will advance by this many frames while the button
            is held down.
        """
        if not self._running or self._pyboy is None:
            raise RuntimeError("No ROM loaded. Call load_rom() first.")

        if button not in Button.all():
            raise ValueError(
                f"Unknown button: {button!r}. "
                f"Valid buttons: {Button.all()}"
            )

        # Press the button
        self._pyboy.button(button)
        # Advance the requested number of frames
        for _ in range(frames):
            self._pyboy.tick()
        # Release the button
        self._pyboy.release(button)

    def get_screen(self) -> np.ndarray:
        """
        Capture the current GBA screen as a numpy array.

        Returns
        -------
        numpy.ndarray
            Shape (160, 240, 3), dtype uint8.
            RGB pixel data at the moment of the call.
            Returns a blank (zero) array if the emulator is not running.
        """
        if not self._running or self._pyboy is None:
            return np.zeros(self.SCREEN_SHAPE, dtype=np.uint8)

        try:
            # PyBoyAdvance provides screen as a flat list of 16-bit values
            screen_data = self._pyboy.screen()  # e.g. [(r,g,b), ...] or flat list
            return self._convert_screen_to_array(screen_data)
        except Exception:
            return np.zeros(self.SCREEN_SHAPE, dtype=np.uint8)

    def is_running(self) -> bool:
        """Return True if a ROM is loaded and emulation is active."""
        if self._pyboy is None:
            return False
        try:
            # PyBoyAdvance sets a quit flag when emulation ends
            return not self._pyboy.poll()
        except Exception:
            return self._running

    def advance_frames(self, n: int = 1) -> None:
        """Advance the emulator by n frames without pressing any button."""
        if not self._running or self._pyboy is None:
            raise RuntimeError("No ROM loaded.")
        for _ in range(n):
            self._pyboy.tick()

    def close(self) -> None:
        """Stop emulation and release resources."""
        self._close_pyboy()
        self._running = False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _close_pyboy(self) -> None:
        """Safely close the PyBoyAdvance instance."""
        if self._pyboy is not None:
            try:
                self._pyboy.stop()
            except Exception:
                pass
            self._pyboy = None

    def _convert_screen_to_array(self, screen_data) -> np.ndarray:
        """
        Convert PyBoyAdvance screen output to a (H, W, 3) numpy uint8 array.

        Parameters
        ----------
        screen_data :
            PyBoyAdvance screen data. Format may vary; handle common cases.

        Returns
        -------
        numpy.ndarray
            Shape (160, 240, 3), uint8, RGB pixel values.
        """
        arr = np.zeros(self.SCREEN_SHAPE, dtype=np.uint8)

        if screen_data is None:
            return arr

        # Handle flat list / byte array of RGB tuples or integers
        flat = np.asarray(screen_data, dtype=np.int32).flatten()

        # PyBoyAdvance screen format: list of (r, g, b) tuples or
        # a flat array of 16-bit BGR values depending on version
        n_pixels = self.WIDTH * self.HEIGHT

        if len(flat) == n_pixels:
            # 1 value per pixel — could be 16-bit BGR565 or 8-bit index
            # Treat as 16-bit BGR565 (common GBA framebuffer format)
            try:
                b = ((flat >> 0)  & 0x1F) * 255 // 31
                g = ((flat >> 5)  & 0x3F) * 255 // 63
                r = ((flat >> 11) & 0x1F) * 255 // 31
                arr[:, :, 0] = r.reshape((self.HEIGHT, self.WIDTH))
                arr[:, :, 1] = g.reshape((self.HEIGHT, self.WIDTH))
                arr[:, :, 2] = b.reshape((self.HEIGHT, self.WIDTH))
            except Exception:
                pass
        elif len(flat) == n_pixels * 3:
            # 3 values per pixel (R, G, B)
            try:
                arr = flat.reshape((self.HEIGHT, self.WIDTH, 3)).astype(np.uint8)
            except Exception:
                pass

        return arr

    def __enter__(self) -> "GBAEmulator":
        return self

    def __exit__(self, *args) -> None:
        self.close()

    def __repr__(self) -> str:
        status = "running" if self.is_running() else "stopped"
        rom = os.path.basename(self._rom_path) if self._rom_path else "none"
        return f"<GBAEmulator rom={rom!r} status={status}>"


# ---------------------------------------------------------------------------
# Alternative: mGBA via mgba-mcp subprocess
# (Documented for reference — not imported/used by default)
# ---------------------------------------------------------------------------
#
# mGBA is the most accurate GBA emulator and supports headless operation.
# Use mgba-mcp to control it from Python.
#
# Installation:
#   1. Download mGBA for Windows: https://mgba.io/downloads.html
#      (get the Qt version — mgba-qt.exe)
#   2. Add the mGBA directory to your system PATH
#   3. pip install mgba-mcp  (or: uv pip install -e <mgba-mcp-repo>)
#
# mgba-mcp runs mgba-qt as a subprocess and communicates via its scripting
# API (Lua hooks + screenshot/memory endpoints). This is the recommended
# approach for production/headless use as mGBA is cycle-accurate and fast.
#
# Example with mgba-mcp:
#   from mgba.mgba import MBEmulator
#   emu = MBEmulator(rom_path="game.gba")
#   emu.run_frames(60)
#   screenshot = emu.screenshot()  # returns PIL Image or numpy array
#   emu.button("a")
#   emu.close()
#
# See: https://github.com/struktured-labs/mgba-mcp
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Simple example
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="GBA Interface — demonstrate loading a ROM and capturing a screen."
    )
    parser.add_argument(
        "--bios", "-b",
        required=True,
        help="Path to GBA BIOS file (e.g. gba_bios.bin)",
    )
    parser.add_argument(
        "--rom", "-r",
        required=True,
        help="Path to GBA ROM file (e.g. pokemon.gba)",
    )
    parser.add_argument(
        "--frames", "-f",
        type=int, default=60,
        help="Number of frames to advance before taking screenshot (default: 60)",
    )
    parser.add_argument(
        "--output", "-o",
        default="screenshot.png",
        help="Output path for the screenshot (default: screenshot.png)",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("GBA Interface Demo")
    print("=" * 60)

    # Initialize emulator
    print(f"\n[1] Loading BIOS: {args.bios}")
    emulator = GBAEmulator(bios_path=args.bios, speed=2)

    print(f"[2] Loading ROM:  {args.rom}")
    emulator.load_rom(args.rom)

    print(f"[3] Advancing {args.frames} frames...")
    emulator.advance_frames(args.frames)

    print("[4] Capturing screen...")
    screen = emulator.get_screen()
    print(f"    Screen shape: {screen.shape}, dtype: {screen.dtype}")
    print(f"    Pixel value range: [{screen.min()}, {screen.max()}]")

    # Save screenshot using PIL
    try:
        from PIL import Image
        img = Image.fromarray(screen, mode="RGB")
        img.save(args.output)
        print(f"[5] Screenshot saved to: {args.output}")
    except Exception as e:
        print(f"[5] Could not save screenshot (PIL not available): {e}")

    print(f"\n[6] Emulator status: {emulator}")
    print(f"    is_running: {emulator.is_running()}")

    print("\n[7] Closing emulator.")
    emulator.close()
    print("Done.")

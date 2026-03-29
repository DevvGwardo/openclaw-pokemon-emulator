"""
mGBA GBA Emulator Interface for OpenClaw Pokemon Emulator Skill.

Controls mGBA (https://mgba.io/) via window focus + PyAutoGUI keypresses
and screenshots via MSS/PIL. mGBA must be installed (see install below).

Install mGBA:
    Download: https://mgba.io/downloads.html
    - Windows portable: mGBA-0.10.5-win64.7z (no install needed)
    - Extract with 7-Zip to e.g. C:\mgba\

Usage:
    python mgba_control.py --rom "Pokemon - Ruby.gba"

Controls mGBA in windowed mode. mGBA must be in windowed mode (not fullscreen).
"""

import subprocess
import time
import sys
import os
import signal
from pathlib import Path
from PIL import Image
import pyautogui

try:
    import mss
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False
    print("mss not installed: screenshots will be slower. Run: pip install mss")

try:
    import numpy as np
    NP_AVAILABLE = True
except ImportError:
    NP_AVAILABLE = False


# GBA button mappings for PyAutoGUI (keyboard shortcuts in mGBA)
# mGBA default keybindings: https://mgba.io/docs.html
# These are the hotkeys mGBA uses (can be customized in mGBA settings)
BUTTON_MAP = {
    "A": "s",      # A button
    "B": "a",      # B button
    "START": "Return",   # Start
    "SELECT": "BackSpace",  # Select
    "UP": "Up",
    "DOWN": "Down",
    "LEFT": "Left",
    "RIGHT": "Right",
    "L": "q",      # Left shoulder
    "R": "e",      # Right shoulder
}

BUTTONS = list(BUTTON_MAP.keys())

# mGBA window title patterns to look for
GBA_WINDOW_TITLES = ["mGBA", "Pokemon"]


class GBAEmulator:
    """
    Controls mGBA running a GBA ROM via window focus + PyAutoGUI.
    
    Args:
        rom_path: Path to the GBA ROM file
        mgba_path: Path to mGBA.exe (auto-detected if not provided)
        window_title: Window title or partial match for the mGBA window
        headless: Not supported for mGBA (requires display)
    """

    def __init__(
        self,
        rom_path: str,
        mgba_path: str = None,
        window_title: str = None,
        headless: bool = False,
    ):
        if headless:
            raise NotImplementedError(
                "mGBA does not support headless mode. "
                "Use a windowed launch or consider RetroArch + VBA-M core."
            )

        self.rom_path = os.path.abspath(rom_path)
        if not os.path.exists(self.rom_path):
            raise FileNotFoundError(f"ROM not found: {self.rom_path}")

        # Auto-detect mGBA if not provided
        if mgba_path is None:
            mgba_path = self._find_mgba()
            if mgba_path is None:
                raise FileNotFoundError(
                    "mGBA not found. Please provide mgba_path or install mGBA from https://mgba.io"
                )
        self.mgba_path = os.path.abspath(mgba_path)

        self.window_title = window_title or "mGBA"
        self.process = None
        self.window = None

        # Load ROM
        self.load_rom(self.rom_path)

    def _find_mgba(self) -> str:
        """Search common locations for mGBA.exe"""
        search_paths = [
            # Portable installs
            r"C:\mgba\mGBA.exe",
            r"C:\mgba\mGBA-*-win64\mGBA.exe",
            r"C:\Program Files\mGBA\mGBA.exe",
            r"C:\Program Files (x86)\mGBA\mGBA.exe",
            # User directories
            os.path.expanduser(r"~\mgba\mGBA.exe"),
            os.path.expanduser(r"~\Downloads\mGBA.exe"),
        ]

        for pattern in search_paths:
            if '*' in pattern:
                import glob
                matches = glob.glob(pattern)
                if matches:
                    return matches[0]
            elif os.path.exists(pattern):
                return pattern

        # Scan desktop
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(desktop):
            for f in os.listdir(desktop):
                if "mgba" in f.lower() and f.endswith(".exe"):
                    return os.path.join(desktop, f)

        return None

    def load_rom(self, rom_path: str):
        """Load a ROM file and start mGBA."""
        if self.process:
            self.stop()

        self.rom_path = os.path.abspath(rom_path)

        # Start mGBA with the ROM
        self.process = subprocess.Popen(
            [self.mgba_path, self.rom_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Wait for window to open
        time.sleep(2)
        self._find_window()

    def _find_window(self):
        """Find the mGBA window using PyGetWindow."""
        try:
            import pygetwindow
            windows = pygetwindow.getWindowsWithTitle(self.window_title)
            if windows:
                self.window = windows[0]
                return
            # Try partial match
            for w in pygetwindow.getAllWindows():
                if self.window_title.lower() in w.title.lower():
                    self.window = w
                    return
        except Exception as e:
            print(f"Window search error: {e}")

        # Try focusing by title
        try:
            import pygetwindow
            all_wins = pygetwindow.getAllWindows()
            for w in all_wins:
                if any(t.lower() in w.title.lower() for t in GBA_WINDOW_TITLES):
                    self.window = w
                    return
        except:
            pass

    def _focus_window(self):
        """Bring mGBA window to foreground."""
        if self.window:
            try:
                self.window.activate()
                time.sleep(0.1)
            except Exception:
                pass

    def press_button(self, button: str, frames: int = 1):
        """
        Press a GBA button for a number of frames.
        
        Args:
            button: One of A, B, START, SELECT, UP, DOWN, LEFT, RIGHT, L, R
            frames: Number of frames to hold (default 1)
        """
        if button not in BUTTON_MAP:
            raise ValueError(f"Unknown button: {button}. Valid: {BUTTONS}")

        key = BUTTON_MAP[button]
        self._focus_window()

        for _ in range(frames):
            pyautogui.press(key)

    def hold_button(self, button: str, frames: int = 30):
        """Hold a button for N frames."""
        if button not in BUTTON_MAP:
            raise ValueError(f"Unknown button: {button}")

        key = BUTTON_MAP[button]
        self._focus_window()
        pyautogui.keyDown(key)
        time.sleep(frames / 60.0)  # ~60fps
        pyautogui.keyUp(key)

    def get_screen(self) -> Image.Image:
        """
        Capture the mGBA window screen as a PIL Image.
        Returns a 240x160 image (GBA resolution).
        """
        if not self.window:
            self._find_window()

        if self.window:
            try:
                # Capture just the mGBA window
                x = self.window.left
                y = self.window.top
                width = self.window.width
                height = self.window.height

                if MSS_AVAILABLE:
                    with mss.mss() as sct:
                        monitor = {"left": x, "top": y, "width": width, "height": height}
                        screenshot = sct.grab(monitor)
                        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                else:
                    img = pyautogui.screenshot(region=(x, y, width, height))

                return img
            except Exception as e:
                print(f"Screenshot error: {e}")

        return None

    def get_screen_array(self):
        """Get screen as numpy array (H, W, 3) BGR."""
        img = self.get_screen()
        if img is None:
            return None
        # Resize to GBA resolution if larger
        if img.width != 240 or img.height != 160:
            img = img.resize((240, 160), Image.LANCZOS)
        arr = np.array(img) if NP_AVAILABLE else None
        return arr

    def is_running(self) -> bool:
        """Check if mGBA process is still running."""
        if self.process is None:
            return False
        return self.process.poll() is None

    def stop(self):
        """Stop the mGBA process."""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
            self.process = None

    def advance_frames(self, n: int = 1):
        """Advance n frames without pressing any buttons."""
        # mGBA runs autonomously; just wait
        time.sleep(n / 60.0)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.stop()


def find_mgba_windows():
    """List all open windows with mGBA or game ROM titles."""
    try:
        import pygetwindow
        results = []
        for w in pygetwindow.getAllWindows():
            if any(t.lower() in w.title.lower() for t in ["mgba", "pokemon", "gba"]):
                results.append({"title": w.title, "left": w.left, "top": w.top,
                               "width": w.width, "height": w.height})
        return results
    except Exception as e:
        return [{"error": str(e)}]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="mGBA GBA Emulator Controller")
    parser.add_argument("--rom", required=True, help="Path to GBA ROM")
    parser.add_argument("--mgba", help="Path to mGBA.exe")
    parser.add_argument("--frames", type=int, default=60, help="Frames to run")
    parser.add_argument("--buttons", nargs="+", default=[], help="Buttons to press")
    args = parser.parse_args()

    print(f"Starting mGBA with: {args.rom}")
    print(f"mGBA path: {args.mgba or 'auto-detect'}")

    with GBAEmulator(args.rom, mgba_path=args.mgba) as gba:
        print(f"Running {args.frames} frames...")
        gba.advance_frames(args.frames)

        for btn in args.buttons:
            print(f"Pressing {btn}...")
            gba.press_button(btn.upper(), frames=10)
            gba.advance_frames(10)

        print("Capturing screen...")
        img = gba.get_screen()
        if img:
            img.save("gba_screenshot.png")
            print(f"Screenshot saved! Size: {img.size}")

        print(f"mGBA running: {gba.is_running()}")

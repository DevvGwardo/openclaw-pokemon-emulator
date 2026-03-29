"""
pyboy_interface.py - Clean interface for playing Game Boy Pokemon games using PyBoy

This module provides a PyBoyGame class that wraps the PyBoy emulator with helpful
methods for interacting with Game Boy games, particularly Pokemon Red/Blue.

Usage:
    from pyboy_interface import PyBoyGame, A, B, UP
    
    game = PyBoyGame()
    game.load_rom("pokemon_red.gb")
    
    while game.is_running():
        game.press_button(A)
        screen = game.get_screen()
        x, y = game.get_position()
        print(f"Position: ({x}, {y})")
        
    game.stop()

Requirements:
    pip install pyboy numpy opencv-python
"""

from pyboy import PyBoy
import numpy as np
from typing import Optional, Tuple, List, Dict, Any
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# =============================================================================
# Button Constants
# =============================================================================

class Buttons:
    """Game Boy button constants."""
    A = "a"
    B = "b"
    START = "start"
    SELECT = "select"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


# Alias for convenience
A = Buttons.A
B = Buttons.B
START = Buttons.START
SELECT = Buttons.SELECT
UP = Buttons.UP
DOWN = Buttons.DOWN
LEFT = Buttons.LEFT
RIGHT = Buttons.RIGHT


# =============================================================================
# Pokemon RAM Addresses (Pokemon Red/Blue - DMG CPU)
# =============================================================================

class PokemonAddresses:
    """
    Known RAM addresses for Pokemon Red/Blue (and similar Generation I games).
    Addresses are for the DMG (original Game Boy) version.
    
    Note: These addresses may vary slightly between game versions and
    may change during RAM bank switching. Use with caution.
    """
    
    # Player Position
    PLAYER_X = 0xD362      # Player's X coordinate on the map
    PLAYER_Y = 0xD361      # Player's Y coordinate on the map
    
    # Map Info
    MAP_NUMBER = 0xD35E    # Current map number
    MAP_WIDTH = 0xD35E    # Map width (sometimes)
    
    # Player Info
    MONEY = 0xD47F         # Player's money (3 bytes, BCD encoded)
    COINS = 0xD47C        # Game Corner coins
    PLAYER_ID = 0xD356    # Player's ID number
    
    # Party Pokemon
    PARTY_COUNT = 0xD163  # Number of Pokemon in party (0-6)
    PARTY_SIZE_MAX = 6    # Maximum party size
    
    # PC Box Pokemon data starts at 0xD98A (or 0xD58A in SGB)
    
    # Badge Count
    BADGES = 0xD2F7       # Earned badges (bitfield)
    
    # Player Stats
    PLAYER_MAX_HP_CURRENT = 0xD16C  # Current HP of first party Pokemon
    PLAYER_MAX_HP_CURRENT_PARTY = 0xD16C  # First party Pokemon current HP
    PLAYER_MAX_HP_PARTY = 0xD18D    # First party Pokemon max HP
    
    # Game State
    GAME_STATE = 0xD057   # Current game state (0=overworld, 1=battle, etc.)
    OVERWORLD = 0x01      # Overworld state value
    BATTLE = 0x02         # Battle state value
    MENU = 0x03           # Menu state value
    
    # In-Battle Addresses
    BATTLE_TYPE = 0xD057  # Type of battle (wild, trainer, etc.)
    ENEMY_HP = 0xD06B     # Enemy current HP
    ENEMY_MAX_HP = 0xD06C # Enemy max HP
    PLAYER_HP = 0xD016    # Player current HP
    PLAYER_MAX_HP = 0xD037  # Player max HP
    
    # Text/Message State
    TEXT_STATE = 0xD057   # Text display state
    DIALOG_ACTIVE = 0xD057  # Dialog box active
    
    # Save/Options
    OPTIONS = 0xD72C      # Text speed, sound options


# =============================================================================
# PyBoyGame Class
# =============================================================================

class PyBoyGame:
    """
    A clean interface for interacting with Game Boy ROMs using PyBoy.
    
    This class wraps PyBoy to provide convenient methods for game interaction,
    with special support for Pokemon games via known RAM addresses.
    
    Attributes:
        path (str): Path to the ROM file
        pyboy (PyBoy): The underlying PyBoy instance
        headless (bool): Whether to run in headless mode
        
    Example:
        >>> game = PyBoyGame()
        >>> game.load_rom("pokemon_red.gb")
        >>> game.press_button(A, duration=2)  # Press A twice
        >>> screen = game.get_screen()  # Get screen as numpy array
        >>> print(game.get_position())  # Get player (x, y)
        >>> game.stop()
    """
    
    def __init__(self, headless: bool = False, scale: int = 1):
        """
        Initialize the PyBoyGame interface.
        
        Args:
            headless: If True, run without rendering (faster, no display)
            scale: Display scale factor (1-6)
        """
        self._pyboy: Optional[PyBoy] = None
        self._path: Optional[str] = None
        self._headless = headless
        self._scale = scale
        self._running = False
        logger.info("PyBoyGame initialized")
    
    def load_rom(self, path: str) -> bool:
        """
        Load a Game Boy ROM file.
        
        Args:
            path: Path to the ROM file (.gb, .gbc, or .rom)
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            logger.info(f"Loading ROM: {path}")
            self._path = path
            
            # PyBoy expects disable_input to be False for normal operation
            self._pyboy = PyBoy(
                path,
                window="none" if self._headless else "SDL2",
                scale=self._scale,
                disable_input=False
            )
            
            self._running = True
            logger.info("ROM loaded successfully")
            return True
            
        except FileNotFoundError:
            logger.error(f"ROM file not found: {path}")
            return False
        except Exception as e:
            logger.error(f"Failed to load ROM: {e}")
            return False
    
    def is_running(self) -> bool:
        """
        Check if the game is still running.
        
        Returns:
            True if game is running, False otherwise
        """
        if self._pyboy is None:
            return False
        
        # Check if PyBoy's tick loop is still active
        return not self._pyboy.tick() == False and self._running
    
    def tick(self) -> bool:
        """
        Advance the emulator by one frame.
        
        Returns:
            True if successful, False if emulation stopped
        """
        if self._pyboy is None:
            return False
        return self._pyboy.tick()
    
    def press_button(self, button: str, duration: int = 1) -> None:
        """
        Press and release a Game Boy button.
        
        Args:
            button: One of A, B, START, SELECT, UP, DOWN, LEFT, RIGHT
            duration: Number of frames to hold the button (default: 1)
        """
        if self._pyboy is None:
            logger.warning("No ROM loaded, cannot press button")
            return
        
        button = button.lower()
        
        # Press the button
        self._pyboy.button(button)
        
        # Hold for specified duration
        for _ in range(duration):
            self._pyboy.tick()
        
        # Release the button
        self._pyboy.button_release(button)
        
        logger.debug(f"Pressed button: {button} for {duration} frames")
    
    def hold_button(self, button: str, frames: int = 60) -> None:
        """
        Hold a button down for a specified number of frames.
        
        Args:
            button: One of A, B, START, SELECT, UP, DOWN, LEFT, RIGHT
            frames: Number of frames to hold (default: 60 ≈ 1 second)
        """
        if self._pyboy is None:
            return
        
        button = button.lower()
        self._pyboy.button(button)
        
        for _ in range(frames):
            self._pyboy.tick()
        
        self._pyboy.button_release(button)
    
    def get_screen(self) -> Optional[np.ndarray]:
        """
        Get the current screen state as a numpy array.
        
        Returns:
            A numpy array of shape (144, 160, 3) containing RGB pixel data,
            or None if the game is not running.
            
        Note:
            For Pokemon Red/Blue, the screen is 160x144 pixels.
            The original Game Boy had a 2-bit color palette, so this
            returns the colorized version from PyBoy's LCD frame buffer.
        """
        if self._pyboy is None or not self._running:
            return None
        
        try:
            # Get the screen from PyBoy's frame buffer
            screen = self._pyboy.screen()
            
            # Convert to numpy array if needed
            if not isinstance(screen, np.ndarray):
                screen = np.array(screen)
            
            # Ensure RGB format (PyBoy returns RGB tuples)
            if len(screen.shape) == 2:
                # Grayscale image, convert to RGB
                screen = np.stack([screen] * 3, axis=-1)
            elif screen.shape[-1] == 4:
                # RGBA, convert to RGB
                screen = screen[:, :, :3]
            
            return screen.astype(np.uint8)
            
        except Exception as e:
            logger.error(f"Failed to get screen: {e}")
            return None
    
    def read_memory(self, address: int, length: int = 1) -> int:
        """
        Read data from the Game Boy's RAM at a specified address.
        
        Args:
            address: Memory address to read (0x0000 - 0xFFFF)
            length: Number of bytes to read (default: 1)
            
        Returns:
            The byte value(s) at the specified address, or 0 if failed.
        """
        if self._pyboy is None:
            return 0
        
        try:
            if length == 1:
                return self._pyboy.memory[address]
            else:
                return [self._pyboy.memory[address + i] for i in range(length)]
        except Exception as e:
            logger.error(f"Failed to read memory at 0x{address:04X}: {e}")
            return 0
    
    def write_memory(self, address: int, value: int) -> bool:
        """
        Write a value to the Game Boy's RAM at a specified address.
        
        Args:
            address: Memory address to write to (0x0000 - 0xFFFF)
            value: Byte value to write (0-255)
            
        Returns:
            True if successful, False otherwise.
        """
        if self._pyboy is None:
            return False
        
        try:
            self._pyboy.memory[address] = value
            return True
        except Exception as e:
            logger.error(f"Failed to write to memory at 0x{address:04X}: {e}")
            return False
    
    def get_position(self) -> Tuple[int, int]:
        """
        Get the player's current position (if Pokemon ROM is loaded).
        
        Returns:
            A tuple (x, y) with the player's coordinates.
            Returns (0, 0) if memory cannot be read.
            
        Note:
            This uses Pokemon Red/Blue RAM addresses. These may differ
            in other Pokemon versions or other Game Boy games.
        """
        x = self.read_memory(PokemonAddresses.PLAYER_X)
        y = self.read_memory(PokemonAddresses.PLAYER_Y)
        return (x, y)
    
    def get_game_state(self) -> int:
        """
        Get the current game state.
        
        Returns:
            Game state value (0=overworld, 1=battle, 2=menu, etc.)
            See PokemonAddresses.GAME_STATE and related constants.
        """
        return self.read_memory(PokemonAddresses.GAME_STATE)
    
    def is_on_overworld(self) -> bool:
        """
        Check if the player is currently on the overworld map.
        
        Returns:
            True if on overworld, False otherwise.
        """
        return self.get_game_state() == PokemonAddresses.OVERWORLD
    
    def is_in_battle(self) -> bool:
        """
        Check if a battle is currently active.
        
        Returns:
            True if in battle, False otherwise.
        """
        state = self.get_game_state()
        return state in (PokemonAddresses.BATTLE, 0x02)
    
    def get_party_count(self) -> int:
        """
        Get the number of Pokemon in the player's party.
        
        Returns:
            Number of Pokemon in party (0-6).
        """
        return self.read_memory(PokemonAddresses.PARTY_COUNT)
    
    def get_player_money(self) -> int:
        """
        Get the player's current money.
        
        Returns:
            Money in the player's possession.
            
        Note:
            Pokemon stores money as BCD (Binary-Coded Decimal), so this
            reads and converts it properly.
        """
        # Money is stored as 3 BCD bytes at D47F-D481
        money_bytes = self.read_memory(PokemonAddresses.MONEY, length=3)
        if isinstance(money_bytes, list):
            # BCD conversion: each nibble is a decimal digit
            return money_bytes[0] * 10000 + money_bytes[1] * 100 + money_bytes[2]
        return money_bytes
    
    def get_first_pokemon_hp(self) -> Tuple[int, int]:
        """
        Get the first party Pokemon's current and max HP.
        
        Returns:
            A tuple (current_hp, max_hp).
        """
        current = self.read_memory(PokemonAddresses.PLAYER_MAX_HP_CURRENT_PARTY)
        max_hp = self.read_memory(PokemonAddresses.PLAYER_MAX_HP_PARTY)
        
        # These are stored as little-endian
        if isinstance(current, list) and len(current) == 2:
            current = current[0] | (current[1] << 8)
        if isinstance(max_hp, list) and len(max_hp) == 2:
            max_hp = max_hp[0] | (max_hp[1] << 8)
            
        return (current, max_hp)
    
    def get_map_number(self) -> int:
        """
        Get the current map number.
        
        Returns:
            The current map/area number.
        """
        return self.read_memory(PokemonAddresses.MAP_NUMBER)
    
    def get_badges(self) -> int:
        """
        Get the earned badges as a bitfield.
        
        Returns:
            A bitfield where each bit represents a badge:
            - Bit 0: Boulder Badge
            - Bit 1: Cascade Badge
            - Bit 2: Thunder Badge
            - Bit 3: Rainbow Badge
            - Bit 4: Soul Badge
            - Bit 5: Marsh Badge
            - Bit 6: Volcano Badge
            - Bit 7: Earth Badge
        """
        return self.read_memory(PokemonAddresses.BADGES)
    
    def count_badges(self) -> int:
        """
        Count the number of badges the player has earned.
        
        Returns:
            Number of badges (0-8).
        """
        badges = self.get_badges()
        return bin(badges).count('1') if badges else 0
    
    def stop(self) -> None:
        """
        Stop the emulator and clean up resources.
        """
        logger.info("Stopping PyBoyGame")
        self._running = False
        if self._pyboy is not None:
            self._pyboy.stop()
            self._pyboy = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures cleanup."""
        self.stop()
        return False
    
    def __del__(self):
        """Destructor - ensures cleanup."""
        self.stop()


# =============================================================================
# Helper Functions
# =============================================================================

def find_rom_paths(directory: str, extensions: tuple = ('.gb', '.gbc', '.rom')) -> List[str]:
    """
    Find all Game Boy ROM files in a directory.
    
    Args:
        directory: Directory path to search
        extensions: Tuple of valid ROM extensions
        
    Returns:
        List of paths to found ROM files
    """
    import os
    rom_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(extensions):
                rom_files.append(os.path.join(root, file))
    return rom_files


def screenshot_to_file(screen: np.ndarray, filename: str) -> bool:
    """
    Save a screen numpy array to an image file.
    
    Args:
        screen: Screen array from get_screen()
        filename: Output filename (should end in .png or .jpg)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import cv2
        cv2.imwrite(filename, screen)
        return True
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")
        return False


# =============================================================================
# Demo / Example Game Loop
# =============================================================================

def example_game_loop(rom_path: str, duration_seconds: int = 30):
    """
    An example demonstrating how to use PyBoyGame to play a Pokemon ROM.
    
    This creates a PyBoyGame instance, loads a ROM, and runs a simple
    demonstration loop that presses buttons and captures screen data.
    
    Args:
        rom_path: Path to the Game Boy ROM file
        duration_seconds: How long to run the demo (approximate)
    """
    print(f"Starting demo with ROM: {rom_path}")
    print("=" * 50)
    
    # Create game instance (headless=False for display)
    game = PyBoyGame(headless=True, scale=3)
    
    if not game.load_rom(rom_path):
        print("Failed to load ROM!")
        return
    
    print("ROM loaded successfully!")
    print(f"Game running: {game.is_running()}")
    
    # Example: Press START to begin game
    print("\nPressing START to begin...")
    game.press_button(START, duration=5)
    
    # Run for specified duration
    start_time = time.time()
    frame_count = 0
    
    print(f"\nRunning game loop for ~{duration_seconds} seconds...")
    print("Press Ctrl+C to stop early\n")
    
    try:
        while game.is_running() and (time.time() - start_time) < duration_seconds:
            # Advance a few frames
            for _ in range(10):
                game.tick()
            
            # Every 60 frames (~1 second), get some info
            if frame_count % 60 == 0:
                state = game.get_game_state()
                state_name = {0: "Overworld", 1: "Battle", 2: "Menu"}.get(state, f"Unknown({state})")
                pos = game.get_position()
                party = game.get_party_count()
                money = game.get_player_money()
                badges = game.count_badges()
                
                print(f"[{int(time.time() - start_time):3d}s] State: {state_name:12s} | "
                      f"Pos: ({pos[0]:3d}, {pos[1]:3d}) | "
                      f"Party: {party} | "
                      f"Badges: {badges} | "
                      f"$: {money}")
                
                # Show HP if in battle
                if game.is_in_battle():
                    hp = game.get_first_pokemon_hp()
                    print(f"         YOUR POKEMON HP: {hp[0]}/{hp[1]}")
            
            frame_count += 1
            
            # Small delay to prevent maxing out CPU
            # Remove this in actual training/automation
            # time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    
    print("\n" + "=" * 50)
    print("Demo complete!")
    print(f"Total frames: {frame_count}")
    
    # Clean up
    game.stop()
    print("Game stopped")


def simple_navigation_demo(rom_path: str):
    """
    A simpler demo that just navigates around.
    
    Args:
        rom_path: Path to the ROM file
    """
    game = PyBoyGame(headless=True)
    
    if not game.load_rom(rom_path):
        print("Failed to load ROM!")
        return
    
    print("Navigating: Walk around for 5 seconds...")
    
    # Simple navigation pattern
    directions = [UP, RIGHT, DOWN, LEFT]
    
    start = time.time()
    idx = 0
    
    while game.is_running() and (time.time() - start) < 5:
        game.press_button(directions[idx % 4], duration=3)
        idx += 1
        
        if idx % 20 == 0:
            pos = game.get_position()
            print(f"Position: {pos}")
    
    game.stop()
    print("Done!")


# =============================================================================
# Main Entry Point
# =============================================================================

if __name__ == "__main__":
    import sys
    import os
    
    print("PyBoy Interface - Pokemon Game Helper")
    print("=" * 50)
    
    # Check if a ROM path was provided as argument
    if len(sys.argv) > 1:
        rom_path = sys.argv[1]
        if os.path.exists(rom_path):
            example_game_loop(rom_path, duration_seconds=30)
        else:
            print(f"Error: ROM file not found: {rom_path}")
            print("\nUsage: python pyboy_interface.py [rom_path]")
            print("  rom_path: Path to a Game Boy ROM file (.gb, .gbc, .rom)")
    else:
        print("No ROM path provided.")
        print("\nUsage: python pyboy_interface.py [rom_path]")
        print("\nThis module can also be imported:")
        print("  from pyboy_interface import PyBoyGame, A, B, UP, DOWN")
        print("")
        print("  game = PyBoyGame()")
        print("  game.load_rom('pokemon_red.gb')")
        print("  game.press_button(A)")
        print("  screen = game.get_screen()")
        print("  game.stop()")

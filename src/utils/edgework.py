"""
Edgework generation utilities.
Generates random serial numbers, batteries, indicators, etc.
"""
import random
from typing import Dict
from src.core.game_state import Edgework


def generate_serial_number() -> str:
    """
    Generate a random serial number.
    Format: 2 letters, 1 digit, 2 letters, 1 digit (e.g., AB3CD5)
    Excludes 'I' and '1' to avoid confusion.
    """
    letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"  # Exclude 'I'
    digits = "023456789"  # Exclude '1'
    
    return (
        random.choice(letters) +
        random.choice(letters) +
        random.choice(digits) +
        random.choice(letters) +
        random.choice(letters) +
        random.choice(digits)
    )


def generate_batteries() -> int:
    """Generate random battery count (0-4)."""
    return random.randint(0, 4)


def generate_indicators() -> Dict[str, bool]:
    """
    Generate random indicator states.
    Each indicator has a chance to be present (lit or unlit).
    """
    possible_indicators = ["CAR", "FRK", "SIG", "BOB", "CLR", "IND", "MSA", "NSA"]
    indicators = {}
    
    # Randomly select 2-4 indicators to be present
    num_indicators = random.randint(2, 4)
    selected = random.sample(possible_indicators, num_indicators)
    
    for ind in selected:
        # 50% chance of being lit
        indicators[ind] = random.choice([True, False])
    
    return indicators


def generate_parallel_port() -> bool:
    """Generate random parallel port presence."""
    return random.choice([True, False])


def generate_edgework() -> Edgework:
    """Generate complete edgework for a new game."""
    return Edgework(
        serial_number=generate_serial_number(),
        batteries=generate_batteries(),
        has_parallel=generate_parallel_port(),
        indicators=generate_indicators()
    )

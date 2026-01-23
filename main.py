#!/usr/bin/env python3
"""
Fission Impossible - Nüclear Solutions Maintenance Terminal
Main entry point.

"We're Glad You're Expendable."
"""
import sys
from src.core.game import Game


def main():
    """Main entry point."""
    game = Game()
    game.run()
    sys.exit(0)


if __name__ == "__main__":
    main()

from config import SCREEN_WIDTH, SCREEN_HEIGHT
from controllers.game_manager import GameManager


def main():
    """Main entry point for the simulation."""
    game = GameManager(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.initialize()
    game.run()


if __name__ == "__main__":
    main()
from settings import FPS
from game import Game


def main():
    game = Game()
    game.run(FPS)


if __name__ == "__main__":
    main()
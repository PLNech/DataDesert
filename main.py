from random import randint
from typing import List, Optional

import numpy as np
import pygame as pg


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY = (50, 50, 50)


class Tile:
    color: tuple[int, int, int]
    rect: Optional[list[int]]

    def __init__(self, color=BLACK, rect=None) -> None:
        self.color = color
        self.rect = rect


class Game:

    def __init__(self, screen_height, screen_width) -> None:
        self.width = 10
        self.height = 10
        self.margin = 1

        self.rows = screen_height // (self.height + self.margin)
        self.columns = screen_width // (self.width + self.margin)
        print(f"Game setup with {self.rows} rows & {self.columns} columns.")

        self.reset()

        self.decay_rate = 0.015

    def evolve(self, grid=None):
        grid = grid or self.grid
        cols = self.columns
        rows = self.rows

        new_grid = grid.copy()

        for x in range(0, cols):
            for y in range(0, rows):
                state = grid[x, y]
                neighbors = (grid[x, (y - 1) % rows] + grid[x, (y + 1) % rows] +
                             grid[(x - 1) % cols, y] + grid[(x + 1) % cols, y] +
                             grid[(x - 1) % cols, (y - 1) % rows] + grid[(x + 1) % cols, (y - 1) % rows] +
                             grid[(x - 1) % cols, (y + 1) % rows] + grid[(x + 1) % cols, (y + 1) % rows])

                # Évolution
                new_state = Game.conway(neighbors, state)
                new_grid[x, y] = new_state

        # Décomposition
        nb_decompose = int(self.columns * self.rows * self.decay_rate)
        indices_x = np.random.randint(0, self.grid.shape[0], nb_decompose)
        indices_y = np.random.randint(0, self.grid.shape[1], nb_decompose)
        new_grid[indices_x, indices_y] = 0

        self.grid = new_grid

    @staticmethod
    def conway(neighbors, state):
        if state == 0 and neighbors == 3:
            new_state = 1
        elif state == 1 and (neighbors < 2):
            new_state = 0
        elif state == 1 and (neighbors > 5):
            new_state = 0
        else:
            new_state = state
        return new_state

    def render_tiles(self) -> List[Tile]:
        tiles = []
        for row in range(self.rows):
            for column in range(self.columns):
                color = BLACK
                if self.grid[column, row] == 1:
                    color = WHITE
                rect = [(self.margin + self.width) * column + self.margin,
                        (self.margin + self.height) * row + self.margin,
                        self.width, self.height]
                tiles.append(Tile(color, rect))
        return tiles

    def on_mouse(self, event):
        pressed = pg.mouse.get_pressed()
        is_left = pressed[0]
        is_right = pressed[2]
        print(f"Game click: left={is_left},right={is_right}")

        pos = pg.mouse.get_pos()
        column = pos[0] // (self.width + self.margin)
        row = pos[1] // (self.height + self.margin)

        if is_left or is_right:
            val = 1 if is_left else 0
            self.grid[column, row] = val
            print(f"Grid{column}x{row}={val}")

    def random_seed(self):
        for i in range(self.columns):
            for j in range(self.width):
                self.grid[i, j] = randint(0, 1)

    def reset(self):
        self.grid = np.zeros((self.columns, self.rows))
        self.random_seed()


class App:

    def __init__(self, width=1024, height=1024):
        self.clock: pg.time.Clock = pg.time.Clock()
        self.game = Game(width, height)
        self.display: pg.Surface = None
        self.background: pg.Surface = None
        self.running = True
        self.size = self.width, self.height = width, height  # FIXME Accessors

    def on_init(self):
        pg.init()
        pg.display.set_caption("Data D3s3rt <3")

        self.display = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)
        self.background = pg.Surface(self.display.get_size())
        self.background = self.background.convert()
        self.background.fill((170, 238, 187))

        self.running = True

    def on_event(self, event):
        if event.type == pg.QUIT \
                or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.running = False
            print("Quitting!")
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.game.on_mouse(event)
        elif event.type == pg.MOUSEBUTTONUP:
            pass
        elif event.type == pg.KEYDOWN and event.key == pg.K_r:
            self.on_reset()

    def on_loop(self):
        self.game.evolve()

    def on_render(self):
        # self.display.blit(self.background, (0, 0))
        self.display.fill(GREY)

        tiles = self.game.render_tiles()
        for tile in tiles:
            pg.draw.rect(self.display, tile.color, tile.rect)
        del tiles
        pg.display.flip()

    def on_cleanup(self):
        pg.quit()

    def on_execute(self):
        self.on_init()

        while self.running:
            self.clock.tick(10)
            for event in pg.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def on_reset(self):
        self.game.reset()


if __name__ == '__main__':
    app = App(256, 256)
    app.on_execute()
    print("DONE")

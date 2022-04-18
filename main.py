#! /usr/bin/env python3

from random import randint
from typing import List, Optional

import numpy as np
import pygame as pg

MAX_FPS = 60
MIN_FPS = 1

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
        self.margin = 4

        self.rows = screen_height // (self.height + self.margin)
        self.columns = screen_width // (self.width + self.margin)
        print(f"Game setup with {self.rows} rows & {self.columns} columns.")

        self.reset()

        self.decay_rate = 0.015
        self.growth_rate = 0.005

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
        nb_grow = int(self.columns * self.rows * self.growth_rate)
        decompose_x = np.random.randint(0, self.grid.shape[0], nb_decompose)
        decompose_y = np.random.randint(0, self.grid.shape[1], nb_decompose)
        new_grid[decompose_x, decompose_y] = 0

        grow_x = np.random.randint(0, self.grid.shape[0], nb_grow)
        grow_y = np.random.randint(0, self.grid.shape[1], nb_grow)
        self.grow(new_grid, grow_x, grow_y)

        self.grid = new_grid

    @staticmethod
    def conway(neighbors, state):
        new_state = state
        if state == 0:
            if neighbors == 3:
                new_state = 1
        else:
            if neighbors < 2:
                new_state = 0
            elif neighbors > 3:
                new_state = 0
        return new_state

    def render_tiles(self) -> List[Tile]:
        tiles = []
        for row in range(self.rows):
            for column in range(self.columns):
                color = BLACK
                cell = self.grid[column, row]
                if cell > 0:
                    r, g, b = WHITE
                    color = r, (g - cell), b
                    # if cell > 0:
                    # print(f"{cell} => {color}")

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
            self.grow(self.grid, column, row)
            print(f"Growth at {column}x{row} (->{val})")

    def random_seed(self):
        for i in range(self.columns):
            for j in range(self.width):
                self.grid[i, j] = randint(0, 1)

    def reset(self):
        self.grid = np.zeros((self.columns, self.rows))
        self.random_seed()

    def grow(self, new_grid, grow_x, grow_y, val=1):
        relative_coords = [[grow_x, grow_y],
                           [grow_x + 1, grow_y],
                           [grow_x, grow_y + 1],
                           [grow_x + 1, grow_y + 1]]
        for x, y in relative_coords:
            try:
                new_grid[x, y] = val
            except IndexError:
                pass


class App:
    running: bool = True
    paused: bool = False

    def __init__(self, width=300, height=None):
        self.tick: int = 60
        height = height or width
        self.clock: pg.time.Clock = pg.time.Clock()
        self.game = Game(width, height)
        self.display: pg.Surface = None
        self.background: pg.Surface = None
        self.size = self.width, self.height = width, height  # FIXME Accessors

    def on_init(self, tick: int = None):
        pg.init()
        pg.display.set_caption("Data D3s3rt <3")

        self.display = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)
        self.background = pg.Surface(self.display.get_size())
        self.background = self.background.convert()
        self.background.fill((170, 238, 187))

        if tick:
            self.tick = tick

    def on_event(self, event):
        if event.type == pg.QUIT \
                or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.running = False
            print("Quitting!")
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.game.on_mouse(event)
        elif event.type == pg.MOUSEBUTTONUP:
            pass
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_r:
                self.on_reset()
            if event.key == pg.K_p:
                self.paused = not self.paused
            elif event.key == pg.K_q:
                self.game.growth_rate += 0.01
                print(f"GROWTH+[{self.game.growth_rate}]")
            elif event.key == pg.K_w:
                self.game.growth_rate = max(0, self.game.growth_rate - 0.01)
                print(f"GROWTH-[{self.game.growth_rate}]")
            elif event.key == pg.K_a:
                self.game.decay_rate += 0.01
                print(f"DECAY+[{self.game.decay_rate}]")
            elif event.key == pg.K_s:
                self.game.decay_rate = max(0, self.game.decay_rate - 0.01)
                print(f"DECAY-[{self.game.growth_rate}]")
            elif event.key in [pg.K_EQUALS, pg.K_KP_EQUALS, pg.K_PLUS, pg.K_KP_PLUS]:
                self.tick = min(MAX_FPS, self.tick + 1)
            elif event.key in [pg.K_MINUS, pg.K_KP_MINUS, pg.K_UNKNOWN]:
                self.tick = max(MIN_FPS, self.tick - 1)
            else:
                print(f"Unhandled key: {event.key}")

    def on_loop(self):
        if not self.paused:
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

    def on_execute(self, tick=10):
        self.on_init(tick)

        while self.running:
            self.clock.tick(self.tick)
            for event in pg.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()

    def on_reset(self):
        self.game.reset()


if __name__ == '__main__':
    app = App(512)
    app.on_execute(3)
    print("DONE")

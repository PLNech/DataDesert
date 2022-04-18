# ! /usr/bin/env python3

from typing import List, Optional, Dict

import numpy as np
import pygame as pg
import pygame_widgets
from pygame_widgets.textbox import TextBox

INCREMENT_GROWTH = 0.0001
INCREMENT_DECAY = 0.001

MAX_FPS = 60
MIN_FPS = 1

# MAIN THEME
BLACK = (8, 8, 8)
WHITE = (255, 255, 255)
GREY = (50, 50, 50)

# Desert Theme
BLACK = (255, 213, 0)
WHITE = (255, 255, 255)
GREY = (150, 150, 150)


class Tile:
    color: tuple[int, int, int]
    rect: Optional[list[int]]

    def __init__(self, color=BLACK, rect=None) -> None:
        self.color = color
        self.rect = rect


class Game:
    must_seed: bool
    seed_rate: float
    decay_rate: float
    growth_rate: float

    print_stats: bool = False
    is_classic: bool = False

    grid: np.ndarray

    def __init__(self, screen_height, screen_width) -> None:
        self.width = 10
        self.height = 10
        self.margin = 2

        self.rows = screen_height // (self.height + self.margin)
        self.columns = screen_width // (self.width + self.margin)
        print(f"Game setup with {self.rows} rows & {self.columns} columns.")

        self.must_seed = True

        self.seed_rate = 0.15
        self.decay_rate = 0.015
        self.growth_rate = 0.0005

    def evolve(self, grid=None):
        grid = grid or self.grid
        cols = self.columns
        rows = self.rows

        new_grid = grid.copy()

        if self.must_seed:
            print("Seeding...")
            self.reset()
            self.must_seed = False

        for x in range(0, cols):
            for y in range(0, rows):
                state = grid[x, y]
                neighborhood = [grid[x, (y - 1) % rows] + grid[x, (y + 1) % rows],
                                grid[(x - 1) % cols, y], grid[(x + 1) % cols, y],
                                grid[(x - 1) % cols, (y - 1) % rows], grid[(x + 1) % cols, (y - 1) % rows],
                                grid[(x - 1) % cols, (y + 1) % rows], grid[(x + 1) % cols, (y + 1) % rows]]
                neighbor_sum = sum([(0 if n < 1 else 1) for n in neighborhood])
                neighbor_old_sum = sum([int(bool(n)) for n in neighborhood])

                # Évolution
                new_state = self.conway(neighbor_sum, state)
                new_grid[x, y] = new_state

        if self.print_stats:
            print(
                f"States stats: Alive={np.count_nonzero(self.grid):5}/{np.size(self.grid):5}, Max={int(np.max(self.grid)):3}")

        self.decompose(new_grid)
        self.growth(new_grid)

        self.grid = new_grid

    def growth(self, grid):
        nb_grow = int(self.columns * self.rows * self.growth_rate)
        grow_x = np.random.randint(0, self.grid.shape[0], nb_grow)
        grow_y = np.random.randint(0, self.grid.shape[1], nb_grow)
        self.grow_at(grid, grow_x, grow_y, size=1)

    def decompose(self, grid):
        nb_decompose = int(self.columns * self.rows * self.decay_rate)
        decompose_x = np.random.randint(0, self.grid.shape[0], nb_decompose)
        decompose_y = np.random.randint(0, self.grid.shape[1], nb_decompose)
        grid[decompose_x, decompose_y] = 0

    def conway(self, neighbor_sum, state):
        new_state = state
        # TODO: Stateful conway
        # for rule in self.rules:
        #     rule.apply(state, neighbors)
        if state <= 0:
            if neighbor_sum == 3:
                new_state = 1
            else:
                new_state -= 1
        else:
            if neighbor_sum < 2:
                new_state = 0
            elif neighbor_sum == 3:
                new_state = 0 if self.is_classic else 1
            elif neighbor_sum > 4:
                new_state = 0
            else:
                new_state += 1
        return new_state

    def render_tiles(self) -> List[Tile]:
        tiles = []
        for row in range(self.rows):
            for column in range(self.columns):
                color = BLACK
                cell = self.grid[column, row]
                if cell > 0:
                    r = int((0 + cell / 25) % 255)
                    b = int((25 + cell / 10) % 255)
                    g = int(max(200 - cell * 10, 85) % 255)
                    color = r, g, b
                else:
                    r = (255 + cell)
                    g = 0
                    b = 0
                rect = [(self.margin + self.width) * column + self.margin,
                        (self.margin + self.height) * row + self.margin,
                        self.width, self.height]
                tiles.append(Tile(color, rect))
        return tiles

    def on_mouse(self, event):
        pressed = pg.mouse.get_pressed()
        is_left = pressed[0]
        is_right = pressed[2]

        pos = pg.mouse.get_pos()
        column = pos[0] // (self.width + self.margin)
        row = pos[1] // (self.height + self.margin)
        if column > self.columns or row > self.rows:
            pass  # print("Out of game bounds.")
        else:
            print(f"Game click: left={is_left},right={is_right}")

            if is_left or is_right:
                val = 1 if is_left else 0
                self.grow_at(self.grid, column, row)
                print(f"Growth at {column}x{row} (->{val})")

    def random_seed(self):
        nb_seed = int(self.columns * self.rows * self.seed_rate)
        seed_x = np.random.randint(0, self.grid.shape[0], nb_seed)
        seed_y = np.random.randint(0, self.grid.shape[1], nb_seed)
        self.grid[seed_x, seed_y] = 1

    def reset(self):
        self.init_grid()
        self.random_seed()

        if self.is_classic:
            self.growth_rate = 0
            self.decay_rate = 0


    def init_grid(self):
        self.grid = np.zeros((self.columns, self.rows))

    def grow_at(self, new_grid, grow_x, grow_y, val=1, size=4):
        relative_coords = [[grow_x, grow_y],
                           [grow_x + 1, grow_y],
                           [grow_x, grow_y + 1],
                           [grow_x + 1, grow_y + 1]]
        for i, (x, y) in enumerate(relative_coords, 1):
            if i > size:
                break
            try:
                new_grid[x, y] = val
            except IndexError:
                pass  # Out of grid bounds - TODO Wrap? Or display "walls"?


class App:
    running: bool = True
    paused: bool = False

    display: pg.Surface
    background: pg.Surface

    def __init__(self, width=300, height=None):
        self.tick: int = 60
        height = height or width
        self.clock: pg.time.Clock = pg.time.Clock()
        self.size = self.width, self.height = width, height  # FIXME Accessors

        self.game = Game(width, height)
        self.game.init_grid()

    def on_init(self, tick: int = None):
        pg.init()
        pg.display.set_caption("Data D3s3rt <3")

        self.display = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)
        self.background = pg.Surface(self.display.get_size())
        self.background = self.background.convert()
        self.background.fill((170, 238, 187))

        # UI
        fontSize = 30
        uiBaseX = self.pwidth(0.835)
        uiBaseY = self.pheight(0.006)
        uiWidth = 190
        uiHeight = 45
        self.ui: Dict[str, TextBox] = {
            "tick": TextBox(self.display, uiBaseX, self.uiheight(uiBaseY, 0), uiWidth, uiHeight, fontSize=fontSize),
            "alive": TextBox(self.display, uiBaseX, self.uiheight(uiBaseY, 1), uiWidth, uiHeight, fontSize=fontSize),
            "growth": TextBox(self.display, uiBaseX, self.uiheight(uiBaseY, 2), uiWidth, uiHeight, fontSize=fontSize),
            "decay": TextBox(self.display, uiBaseX, self.uiheight(uiBaseY, 3), uiWidth, uiHeight, fontSize=fontSize),
            "oldest": TextBox(self.display, uiBaseX, self.uiheight(uiBaseY, 4), uiWidth, uiHeight, fontSize=fontSize),
            "average": TextBox(self.display, uiBaseX, self.uiheight(uiBaseY, 5), uiWidth, uiHeight, fontSize=fontSize),
            "fourth": TextBox(self.display, uiBaseX, self.uiheight(uiBaseY, 6), uiWidth, uiHeight, fontSize=fontSize),
        }
        for box in self.ui.values():
            box.disable()

        if tick:
            self.tick = tick

    def pwidth(self, percentage: float):
        return int(self.width * percentage)

    def pheight(self, percentage: float):
        return int(self.height * percentage)

    def uiheight(self, base: int, i: int = 0):
        return int(base + i * 50)

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
            if event.key == pg.K_f:
                self.game.is_classic = not self.game.is_classic
            if event.key == pg.K_o:
                self.game.print_stats = not self.game.print_stats
            elif event.key == pg.K_q:
                self.game.growth_rate += INCREMENT_GROWTH
                print(f"Growth ↗ [{self.game.growth_rate}]")
            elif event.key == pg.K_w:
                self.game.growth_rate = max(0.0, self.game.growth_rate - INCREMENT_GROWTH)
                print(f"Growth ↘ [{self.game.growth_rate}]")
            elif event.key == pg.K_a:
                self.game.decay_rate += INCREMENT_DECAY
                print(f"Decay ↗ [{self.game.decay_rate}]")
            elif event.key == pg.K_s:
                self.game.decay_rate = max(0.0, self.game.decay_rate - INCREMENT_DECAY)
                print(f"Decay ↘ [{self.game.decay_rate}]")
            elif event.key in [pg.K_EQUALS, pg.K_KP_EQUALS, pg.K_PLUS, pg.K_KP_PLUS]:
                self.tick = min(MAX_FPS, self.tick + 1)
                print(f"Tick ↗ [{self.tick}]")
            elif event.key in [pg.K_MINUS, pg.K_KP_MINUS, pg.K_UNKNOWN]:
                self.tick = max(MIN_FPS, self.tick - 1)
                print(f"Tick ↘ [{self.tick}]")
            else:
                print(f"Unhandled key: {event.key}")

    def on_loop(self):
        if not self.paused:
            self.game.evolve()

    def on_render(self, events):
        # self.display.blit(self.background, (0, 0))
        self.display.fill(GREY)

        tiles = self.game.render_tiles()
        for tile in tiles:
            pg.draw.rect(self.display, tile.color, tile.rect)
        del tiles

        texts = {
            "tick": f"Tick rate: {self.tick if not self.paused else 'PAUSED':7}",
            "alive": f"Alive : {np.count_nonzero(self.game.grid):5}/{np.size(self.game.grid):5}",
            "growth": f"Growth: {self.game.growth_rate:5.4f}",
            "decay": f"Decay : {self.game.decay_rate:5.4f}",
            "oldest": f"Oldest: {int(np.max(self.game.grid)):5}",
            "average": f"Average:{np.average(np.nonzero(self.game.grid)):5.2f}",
            "fourth": f"4th? :{not self.game.is_classic}",
        }
        for stat, text in texts.items():
            self.ui[stat].setText(text)

        pygame_widgets.update(events)
        pg.display.update()
        pg.display.flip()

    def on_cleanup(self):
        pg.quit()

    def on_execute(self, tick: int = None):
        self.on_init(tick)

        while self.running:
            self.clock.tick(self.tick)
            events = pg.event.get()
            for event in events:
                self.on_event(event)
            self.on_loop()
            self.on_render(events)
        self.on_cleanup()

    def on_reset(self):
        self.game.reset()


if __name__ == '__main__':
    app = App(1200, 1000)
    app.tick = 12

    print(f"Created app: {app.tick}")
    app.game.is_classic = False
    app.game.reset()
    # app.paused = True
    app.on_execute()
    print("DONE")

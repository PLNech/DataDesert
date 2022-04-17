import pygame as pg


class App:

    def __init__(self, width=640, height=400):
        self.display: pg.Surface = None
        self.background: pg.Surface = None
        self.running = True
        self.size = self.width, self.height = width, height  # FIXME Accessors

    def on_init(self):
        pg.init()
        self.display = pg.display.set_mode(self.size, pg.HWSURFACE | pg.DOUBLEBUF)
        self.background = pg.Surface(self.display.get_size())
        self.background = self.background.convert()
        self.background.fill((170, 238, 187))

        self.clock = pg.time.Clock()

        self.running = True

    def on_event(self, event):
        if event.type == pg.QUIT \
                or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            self.running = False
            print("Quitting!")
        elif event.type == pg.MOUSEBUTTONDOWN:
            pass
        elif event.type == pg.MOUSEBUTTONUP:
            pass

    def on_loop(self):
        print("LOOP")

    def on_render(self):
        self.display.blit(self.background, (0, 0))
        pg.display.flip()

    def on_cleanup(self):
        pg.quit()

    def on_execute(self):
        self.on_init()

        while self.running:
            self.clock.tick(60)
            for event in pg.event.get():
                self.on_event(event)
            self.on_loop()
            self.on_render()
        self.on_cleanup()


if __name__ == '__main__':
    app = App()
    app.on_execute()
    print("DONE")

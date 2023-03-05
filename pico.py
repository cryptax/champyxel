import pyxel
import logging
import random

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 200

logging.basicConfig(level=logging.DEBUG)


class Pico:
    def __init__(self):
        self.x = 0  # position of Pico

    def draw(self):
        pyxel.blt(self.x, y=SCREEN_HEIGHT-16, img=0, u=16, v=0, w=24, h=16)

    def update(self):
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x = (self.x + 1) % pyxel.width
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x = (self.x - 1) % pyxel.width


class Champagne:
    def __init__(self):
        self.x = random.randint(21, SCREEN_WIDTH-4)
        self.y = 11
        self.frame_count = 0
        logging.debug(f'[+] Bottle created at ({self.x}, {self.y})')

    def draw(self):
        pyxel.blt(self.x, y=self.y, img=0, u=0, v=16, w=3, h=8)

    def update(self):
        self.frame_count = self.frame_count + 1
        if self.frame_count % 1 == 0:
            self.y = (self.y + 1) % pyxel.height


class Game:
    def __init__(self):
        self.pico = Pico()
        self.bottles = []
        self.in_box = 0
        self.broken = 0

        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pico et le champagne")
        pyxel.load("pico.pyxres", True, False, True, True)
        logging.debug('[+] init done')
        # pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def draw(self):
        pyxel.cls(0)
        pyxel.text(10, 20,
                   f'CHAMPAGNE={self.in_box} BROKEN={self.broken}',
                   pyxel.frame_count % 16)

        self.pico.draw()
        for b in self.bottles:
            b.draw()

    def update(self):
        if pyxel.btn(pyxel.KEY_Q) or self.broken >= 3:
            logging.warning('Bye bye')
            pyxel.quit()
        self.pico.update()

        # generate bottles
        if pyxel.frame_count > 5:
            if pyxel.frame_count % 1000 == 0 or len(self.bottles) == 0:
                logging.debug(f'frame_count={pyxel.frame_count}'
                              f' bottles={len(self.bottles)}')
                self.bottles.append(Champagne())

        for b in self.bottles:
            if b.y >= (SCREEN_HEIGHT - 16):
                logging.debug(f'CATCH ZONE: bottle=({b.x}, {b.y})'
                              f' pico={self.pico.x} '
                              f'[ {self.pico.x+14}, {self.pico.x+21}]')
                # catch / brake bottles
                if b.x >= (self.pico.x + 14) and \
                   b.x <= (self.pico.x + 21):
                    logging.debug('Gotcha!')
                    self.in_box = self.in_box + 1
                else:
                    logging.debug('Broken')
                    self.broken = self.broken + 1
                logging.debug(f'in_box={self.in_box} broken={self.broken}')
                self.bottles.remove(b)
            else:
                # drop bottle
                b.update()



Game()

import pyxel
import logging
import random

SCREEN_WIDTH = 160
SCREEN_HEIGHT = 200
HEADER_HEIGHT = 10

logging.basicConfig(level=logging.DEBUG)


class Pico:
    Y = SCREEN_HEIGHT - 30

    def __init__(self):
        self.x = 0  # position of Pico

    def draw(self):
        pyxel.blt(self.x, y=Pico.Y, img=0, u=16, v=0, w=24, h=16)

    def update(self):
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x = (self.x + 2) % pyxel.width
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x = (self.x - 2) % pyxel.width


class Champagne:
    def __init__(self, speed=1):
        self.x = random.randint(21, SCREEN_WIDTH-4)
        self.y = HEADER_HEIGHT + 1
        self.speed = speed
        logging.debug(f'[+] Bottle created at ({self.x}, {self.y})')

    def draw(self):
        pyxel.blt(self.x, y=self.y, img=0, u=0, v=16, w=3, h=8)

    def update(self):
        self.y = (self.y + self.speed) % pyxel.height


class Game:
    def __init__(self):
        self.pico = Pico()
        # current array of dropping bottles
        self.bottles = []
        # nb of bottles Pico has successfully caught
        self.in_box = 0
        # nb of bottles Pico missed
        self.broken = 0
        # how fast bottles drop
        self.speed = 1
        # maximum number of simultaneous dropping bottles
        self.simultaneous_bottles = 1
        # frame count value last time a bottle was generated
        self.last_generation = 0

        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pico et le champagne")
        pyxel.load("pico.pyxres", True, False, True, True)
        logging.debug('[+] init done')
        # pyxel.playm(0, loop=True)
        pyxel.run(self.update, self.draw)

    def draw(self):
        pyxel.cls(0)
        pyxel.text(10, HEADER_HEIGHT,
                   f'CHAMPAGNE={self.in_box} '
                   f'BROKEN={self.broken} ',
                   pyxel.frame_count % 16)

        self.pico.draw()
        for b in self.bottles:
            b.draw()

        if self.broken >= 3:
            pyxel.text(30, SCREEN_HEIGHT//2,
                       'Game Over', pyxel.frame_count % 16)
            if pyxel.btn(pyxel.KEY_RETURN):
                pyxel.quit()

    def level(self):
        if self.in_box > 0:
            self.simultaneous_bottles = (self.in_box // 3) + 1
            if self.simultaneous_bottles % 5 == 0:
                self.speed = self.speed + 1
                logging.debug(f'level up: in box={self.in_box} '
                              f' speed={self.speed} '
                              f' nb_bottles={self.simultaneous_bottles}')

    def update(self):
        if pyxel.btn(pyxel.KEY_Q):
            logging.warning('Bye bye')
            pyxel.quit()

        if self.broken >= 3:
            # stop updating if game over
            return

        # update position of Pico
        self.pico.update()

        # generate bottles
        if len(self.bottles) < self.simultaneous_bottles and \
           (pyxel.frame_count - self.last_generation) > 50:
            logging.debug(f'bottles={len(self.bottles)} '
                          f'target={self.simultaneous_bottles}')
            self.bottles.append(Champagne(self.speed))
            self.last_generation = pyxel.frame_count

        for b in self.bottles:
            if b.y >= Pico.Y:
                logging.debug(f'CATCH ZONE: bottle=({b.x}, {b.y})'
                              f' pico={self.pico.x}'
                              f' frame_count={pyxel.frame_count}')
                # catch / brake bottles
                if b.x >= (self.pico.x + 14) and \
                   b.x <= (self.pico.x + 21):
                    self.in_box = self.in_box + 1
                else:
                    self.broken = self.broken + 1
                self.bottles.remove(b)
            else:
                # drop bottle
                b.update()

        self.level()


Game()

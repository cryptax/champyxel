import pyxel
import logging
import random

SCREEN_WIDTH = 180
SCREEN_HEIGHT = 180
HEADER_HEIGHT = 10

logging.basicConfig(level=logging.DEBUG)


class Pico:
    Y = SCREEN_HEIGHT - 30
    NORMAL_FACE = 0
    SMILING_FACE = 1
    SPRITE_WIDTH = 49
    SPRITE_HEIGHT = 27

    def __init__(self):
        self.x = 0  # position of Pico
        self.face = Pico.NORMAL_FACE

    def draw(self):
        if self.face == Pico.NORMAL_FACE:
            pyxel.blt(self.x, y=Pico.Y, img=0, u=0, v=0,
                      w=Pico.SPRITE_WIDTH, h=Pico.SPRITE_HEIGHT)
        else:
            pyxel.blt(self.x, y=Pico.Y, img=0, u=0, v=32,
                      w=Pico.SPRITE_WIDTH, h=Pico.SPRITE_HEIGHT)

    def update(self):
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.x = (self.x + 3) % pyxel.width
        if pyxel.btn(pyxel.KEY_LEFT):
            self.x = (self.x - 3) % pyxel.width


class Champagne:
    def __init__(self, speed=1):
        self.x = random.randint(Pico.SPRITE_WIDTH+1, SCREEN_WIDTH-4)
        self.y = HEADER_HEIGHT + 15
        self.speed = speed
        self.broken_framecount = 0
        logging.debug(f'[+] Bottle created at ({self.x}, {self.y})'
                      f' with speed={self.speed}')

    def draw(self):
        if self.broken_framecount > 0:
            pyxel.blt(self.x, y=self.y, img=0, u=8, v=66, w=8, h=14)
        else:
            pyxel.blt(self.x, y=self.y, img=0, u=0, v=63, w=5, h=17)

    def update(self):
        self.y = (self.y + self.speed) % pyxel.height

    def miss(self):
        # call this the first time a bottle is broken
        self.broken_framecount = pyxel.frame_count
        # bottles break on the floor, this is an adjustment
        self.y = self.y + 10


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
        # frame count when last bottle caught
        self.last_catch = 0
        # last nb of simultaneous bottles we increased level for
        self.level_up = 0
        # game is paused
        self.pause = False

        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Pico et le champagne")
        pyxel.load("pico.pyxres", True, False, True, True)
        logging.debug('[+] init done')
        pyxel.run(self.update, self.draw)

    def welcome(self):
        # welcome screen
        position = SCREEN_HEIGHT // 2
        # tete de Pico
        pyxel.blt(40, position-10, 1, 0, 0, 34, 24)
        # bouteille de champagne
        pyxel.blt(100, position, 1, 5, 30, 5, 18)
        # text
        pyxel.text(50, position+20, 'PICO', 3)
        pyxel.text(50, position+30, 'range son', 3)
        pyxel.text(50, position+40, 'Champagne', 3)

    def level(self):
        if self.in_box > 0:
            # every 3 boxes, we add a bottle
            self.simultaneous_bottles = (self.in_box // 3) + 1
            if self.simultaneous_bottles % 10 == 0 and \
               self.level_up < self.simultaneous_bottles:
                self.speed = self.speed + 1
                self.level_up = self.simultaneous_bottles
                logging.debug(f'level up: in box={self.in_box} '
                              f' level={self.level_up}'
                              f' speed={self.speed}'
                              f' nb_bottles={self.simultaneous_bottles}')

    def draw(self):
        pyxel.cls(0)
        if pyxel.frame_count < 100:
            self.welcome()
            return
        
        # brown background: pyxel.rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 4)
        pyxel.text(25, HEADER_HEIGHT,
                   f'CHAMPAGNE={self.in_box} '
                   f'BROKEN={self.broken} '
                   f'LEVEL={self.speed}',
                   7)

        self.pico.draw()
        for b in self.bottles:
            b.draw()

        if self.broken >= 3:
            position = SCREEN_HEIGHT // 2
            pyxel.text(40, position - 10, '3 broken bottles!!!', 7)
            pyxel.text(55, position, 'Game Over', 7)
            if pyxel.btn(pyxel.KEY_RETURN):
                pyxel.quit()

        if self.pause:
            position = SCREEN_HEIGHT // 2
            pyxel.text(50, position - 10, 'Game is paused', 7)
            pyxel.text(45, position, 'ENTER to un-pause', 7)
            if pyxel.btn(pyxel.KEY_RETURN):
                self.pause = False


    def update(self):
        if pyxel.btn(pyxel.KEY_Q):
            logging.warning('Bye bye')
            pyxel.quit()

        if pyxel.btn(pyxel.KEY_P) and not self.pause:
            logging.info('Game is paused')
            self.pause = True

        if self.broken >= 3 or self.pause or pyxel.frame_count < 100:
            # stop updating if game over
            return

        if pyxel.frame_count - self.last_catch > 10:
            # Pico has smiled for his success long enough
            self.pico.face = Pico.NORMAL_FACE

        # update position of Pico
        self.pico.update()

        # generate bottles
        if len(self.bottles) < self.simultaneous_bottles and \
           ((pyxel.frame_count -
             self.last_generation) > 50 or len(self.bottles) == 0):
            logging.debug(f'bottles={len(self.bottles)} '
                          f'target={self.simultaneous_bottles}')
            self.bottles.append(Champagne(self.speed))
            self.last_generation = pyxel.frame_count
            pyxel.play(0, 4)

        for b in self.bottles:
            if b.y >= Pico.Y:
                logging.debug(f'CATCH ZONE: bottle=({b.x}, {b.y})'
                              f' pico catch=[{self.pico.x+26}-{self.pico.x+42-5}]'
                              f' frame_count={pyxel.frame_count}')
                # catch / brake bottles
                # offset box: [ 26 - 42 ]
                # bottle width: 5
                if b.x >= (self.pico.x + 26) and \
                   b.x <= (self.pico.x + 42 - 5):
                    self.in_box = self.in_box + 1
                    self.pico.face = Pico.SMILING_FACE
                    self.last_catch = pyxel.frame_count
                    self.bottles.remove(b)  # remove the bottle Pico caught
                    # pyxel.play(0, 2)
                else:
                    if b.broken_framecount == 0:
                        self.broken = self.broken + 1
                        b.miss()
                        pyxel.play(0, 3)
                    # else: bottle is not yet removed but already broken
            else:
                # drop bottle
                b.update()

            # remove the broken bottles
            if b.broken_framecount > 0 and \
               (pyxel.frame_count - b.broken_framecount > 5):
                self.bottles.remove(b)

        self.level()


Game()

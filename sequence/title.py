import pygame as pg
from ext import evthandler as eh

import conf
from level import Level

class Title:
    def __init__ (self, game, event_handler, ID = 0):
        self.game = game
        self.event_handler = event_handler
        self.level_ID = ID
        self.frame = conf.FRAME
        event_handler.add_event_handlers({
            pg.MOUSEBUTTONDOWN: self.start
        })
        event_handler.add_key_handlers([
            (conf.KEYS_NEXT, self.start, eh.MODE_ONDOWN),
            (conf.KEYS_BACK, lambda *args: self.game.quit(), eh.MODE_ONDOWN)
        ])

    def start (self, *args):
        self.game.start_backend(Level, self.level_ID)

    def update (self):
        pass

    def draw (self, screen):
        if self.dirty:
            # BG
            screen.fill(conf.BG)
            # text
            w, h = self.game.res
            x = conf.TITLE_PADDING * w
            y = conf.TITLE_PADDING * h
            w -= 2 * x
            font = (conf.FONT, conf.FONT_SIZE * h, False)
            font_args = (font, conf.TITLE_TEXT, conf.FONT_COLOUR, None, w)
            sfc = self.game.img(font_args)[0]
            screen.blit(sfc, (x, y))
            self.dirty = False 
            return True
        else:
            return False
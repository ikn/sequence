from os import sep

import pygame as pg

# paths
DATA_DIR = ''
IMG_DIR = DATA_DIR + 'img' + sep
SOUND_DIR = DATA_DIR + 'sound' + sep
MUSIC_DIR = DATA_DIR + 'music' + sep
FONT_DIR = DATA_DIR + 'font' + sep

# display
WINDOW_ICON = IMG_DIR + 'icon.png'
WINDOW_TITLE = 'Sequence'
MOUSE_VISIBLE = True
FLAGS = 0
FULLSCREEN = False
RESIZABLE = False
RES_W = (960, 540)
RES_F = pg.display.list_modes()[0]
MIN_RES_W = (320, 180)
ASPECT_RATIO = None

# timing
FPS = 60
FRAME = 1. / FPS

# input
KEYS_NEXT = (pg.K_RETURN, pg.K_SPACE, pg.K_KP_ENTER)
KEYS_BACK = (pg.K_ESCAPE, pg.K_BACKSPACE)
KEYS_MINIMISE = (pg.K_F10,)
KEYS_FULLSCREEN = (pg.K_F11, (pg.K_RETURN, pg.KMOD_ALT, True),
                   (pg.K_KP_ENTER, pg.KMOD_ALT, True))
KEYS_FF = (pg.K_TAB, pg.K_LCTRL, pg.K_RCTRL)
KEYS_MOVE = [(k, 0, True) for k in (pg.K_LEFT, pg.K_UP, pg.K_RIGHT, pg.K_DOWN)]
KEYS_ROTATE = ((pg.K_LEFT, pg.KMOD_CTRL, False), (pg.K_RIGHT, pg.KMOD_CTRL, False))
MB_MOVE = 1
MB_ROTATE = 3
ROTATE_SPEED = .0015
KEY_MOVE_SPEED = 3
KEY_ROTATE_SPEED = .01

# audio
MUSIC_VOLUME = 50
SOUND_VOLUME = 50
EVENT_ENDMUSIC = pg.USEREVENT
SOUNDS = {}
SOUND_VOLUMES = {}

# levels
INITIAL_LINE = ((480, 270), 0) # (point, angle)
# (pos, angle, turn angle)
OBJS = [
    [((650, 0), -.2, 0)],
    [((0, 150), .4, 0), ((960, 390), -.6, 0), ((300, 540), .65, 0)],
    [((200, 540), .5, -.5), ((400, 540), .4, -.5)],
    [((300, 0), -.5, 1), ((700, 0), -.5, 1), ((0, 300), 0, .5)],
    [((0, 50), .2, -.05), ((0, 100), .1, -.05), ((0, 150), 0, -.05),
     ((0, 200), -.1, -.05), ((0, 250), -.2, -.05), ((960, 250), 1, .05),
     ((960, 300), 1.1, .05), ((960, 350), 1.2, .05), ((960, 400), 1.3, .05),
     ((960, 450), 1.4, .05)],
    [((20, 0), -.1, 0), ((0, 170), .07, 0), ((0, 180), -.45, 0),
     ((945, 0), -.5, .46)]
]

# gameplay
SPEED = 2
FF_ITERATIONS = 5
SMALL_THRESHOLD = 10 ** -5

# appearance
BG = (255, 255, 255)
LINE_COLOUR = (0, 0, 0)
OBJ_LINE_COLOUR = (255, 0, 0)
ARC_BG_COLOUR = (200, 200, 255)
ARC_COLOUR = (0, 0, 150)
ARROW_SIZE = 50
ARC_RADIUS = 20
OBJ_COLOUR = (0, 0, 200)
OBJ_RADIUS = 5

# title screen
TITLE_TEXT = '''Use the mouse to move and rotate the line so that all of the \
red lines around the border will cross your line when extended.

Press space  to start things moving along the red lines to find out if you've \
solved the puzzle.

Press space to begin.'''
FONT = 'Jura-Light.ttf'
FONT_SIZE = .09 # proportion of screen height
FONT_COLOUR = (0, 0, 0)
TITLE_PADDING = .05 # proportion of screen height
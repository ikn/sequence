from math import tan, atan, cos, sin, pi

import pygame as pg
from ext import evthandler as eh

import conf

ir = lambda x: int(round(x))
get_dx = lambda a: (-1 if pi / 2 < a <= 3 * pi / 2 else 1) * abs(cos(a))
get_dy = lambda a: (1 if a >= pi else -1) * abs(sin(a))
fix_angle = lambda a: (a * pi) % (2 * pi)

class Level:
    def __init__ (self, game, event_handler, ID = 0):
        self.game = game
        self.event_handler = event_handler
        self.frame = conf.FRAME
        event_handler.add_event_handlers({
            pg.MOUSEBUTTONDOWN: self.click,
            pg.MOUSEBUTTONUP: self.unclick,
            pg.MOUSEMOTION: self.drag
        })
        event_handler.add_key_handlers([
            (conf.KEYS_NEXT, self.start, eh.MODE_ONDOWN),
            (conf.KEYS_BACK, self.stop, eh.MODE_ONDOWN),
            (conf.KEYS_FF, self.ff, eh.MODE_ONPRESS),
            (conf.KEYS_MOVE, self.move_kb, eh.MODE_HELD),
            (conf.KEYS_ROTATE, self.rotate_kb, eh.MODE_HELD)
        ])
        self.pos, self.angle = conf.INITIAL_LINE
        self.pos = list(self.pos)
        self.speed = conf.SPEED
        self.iterations = 1
        self.rect = pg.Rect((0, 0), self.game.res).inflate(2, 2)
        self.init(ID)

    def init (self, ID):
        self.ID = ID
        self.update_line_pts()
        self.objs = conf.OBJS[ID]
        self.moving = self.rotating = False
        self.running = False

    def eqn (self, p = None, angle = None):
        if p is None:
            p = self.pos
        if angle is None:
            angle = self.angle
        x, y = p
        angle = fix_angle(angle)
        dx = get_dx(angle)
        if abs(dx) < conf.SMALL_THRESHOLD:
            # pretty much vertical
            m = None
            c = None
        else:
            m = get_dy(angle) / dx
            c = y - m * x
        return m, c

    def update_line_pts (self):
        m, c = self.eqn()
        # get border intercepts
        w, h = self.game.res
        if m is None:
            # vertical
            x = self.pos[0]
            self.pts = [(x, 0), (x, h)]
        else:
            pts = []
            for x in (0, w):
                y = m * x + c
                if 0 <= y <= h:
                    pts.append((x, y))
            for y in (0, h):
                try:
                    x = (y - c) / m
                except ZeroDivisionError:
                    pass
                else:
                    if 0 <= x <= w:
                        pts.append((x, y))
            self.pts = pts[:2]
        self.dirty = True

    def click (self, evt):
        if evt.button == conf.MB_MOVE:
            self.moving = True
        elif evt.button == conf.MB_ROTATE:
            self.rotating = True

    def unclick (self, evt):
        if evt.button == conf.MB_MOVE:
            self.moving = False
        elif evt.button == conf.MB_ROTATE:
            self.rotating = False

    def drag (self, evt):
        if self.moving:
            self.move(evt.rel)
        if self.rotating:
            self.rotate(evt.rel[0])

    def move_kb (self, key, evt, mods):
        d = conf.KEYS_MOVE.index(key)
        amount = [0, 0]
        amount[d % 2] = conf.KEY_MOVE_SPEED * (1 if d > 1 else -1)
        self.move(amount)

    def rotate_kb (self, key, evt, mods):
        d = conf.KEYS_ROTATE.index(key) or -1
        self.rotate(conf.KEY_MOVE_SPEED * d)

    def move (self, amount):
        if not self.running:
            self.pos[0] += amount[0]
            self.pos[1] += amount[1]
            self.update_line_pts()

    def rotate (self, amount):
        if not self.running:
            self.angle -= conf.ROTATE_SPEED * amount
            self.update_line_pts()

    def obj_info (self, m_l, c_l, o):
        p, angle, turn = o
        m, c = self.eqn(p, angle)
        # get intersect
        if m_l is None:
            # main line vertical: intersect at line's x-value
            i = (self.pos[0], None)
        elif m is None:
            # obj line vertical: intersect at line's y-value for this x
            i = (None, m_l * p[0] + c_l)
        else:
            try:
                i = (float(c_l - c) / (m - m_l), None)
            except ZeroDivisionError:
                # same gradient: only intersect if same intercept
                i = True if c_l == c else None
        return [p, list(p), i, angle, turn]

    def start (self, *args):
        if not self.running:
            self.moving = False
            self.rotating = False
            self.running = True
            self.t = 0
            m, c = self.eqn()
            # precalculate equation and intersect with line for each obj
            self._objs = [self.obj_info(m, c, o) for o in self.objs]

    def stop (self, *args):
        if self.running:
            self.running = False
            del self._objs
            self.dirty = True

    def ff (self, keys, evt, mods):
        if evt == 0:
            self.iterations = conf.FF_ITERATIONS
        else:
            self.iterations = 1

    def next_level (self):
        ID = self.ID + 1
        if len(conf.OBJS) <= ID:
            self.game.quit_backend()
        else:
            self.init(ID)

    def _update (self):
        os = self._objs
        d = self.speed * self.t
        dead = 0
        rm = []
        for o in os:
            p0, p, i, a, t = o
            a = fix_angle(a)
            x = p0[0] + d * get_dx(a)
            y = p0[1] + d * get_dy(a)
            p_new = o[1] = [x, y]
            if not self.rect.collidepoint(x, y):
                # lose
                self.stop()
                return
            # check if crossed main line
            this_dead = False
            if i is True:
                # same line
                this_dead = True
            elif i is None:
                # doesn't cross
                pass
            else:
                # crosses at one point (given in one of x or y)
                j = i[0] is None
                if p[j] <= i[j] <= p_new[j] or p_new[j] <= i[j] <= p[j]:
                    this_dead = True
            if this_dead:
                dead += 1
                rm.append(o)
        for o in rm:
            os.remove(o)
        if dead:
            m_l, c_l = self.eqn()
            for i, (p0, p, intersect, a, t) in enumerate(os):
                a += dead * t
                b = fix_angle(a)
                p0 = list(p)
                p0[0] -= d * get_dx(b)
                p0[1] -= d * get_dy(b)
                os[i] = self.obj_info(m_l, c_l, (p0, a, t))
                os[i][1] = p
        if len(os) == 0:
            # win
            self.stop()
            self.next_level()
        self.t += 1
        self.dirty = True

    def update (self):
        for i in xrange(self.iterations):
            if self.running:
                self._update()
            else:
                break

    def draw (self, screen):
        if self.dirty:
            self.dirty = False
        else:
            return False
        # BG
        screen.fill(conf.BG)
        # line
        if len(self.pts) == 2: # else off-screen
            pg.draw.aaline(screen, conf.LINE_COLOUR, *self.pts)
        # objs
        if self.running:
            # draw the objs themselves
            d = self.speed * self.t
            for p0, p, i, a, t in self._objs:
                pg.draw.circle(screen, conf.OBJ_COLOUR, [ir(x) for x in p], conf.OBJ_RADIUS)
        else:
            # draw arrows
            s = conf.ARROW_SIZE
            r = conf.ARC_RADIUS
            for (x, y), angle, turn in self.objs:
                angle = fix_angle(angle)
                turn *= pi
                # arrow
                dx = s * get_dx(angle)
                dy = s * get_dy(angle)
                end = (x + dx, y + dy)
                pg.draw.aaline(screen, conf.OBJ_LINE_COLOUR, (x, y), end)
                if turn != 0:
                    # arc
                    rect = pg.Rect(0, 0, 2 * r, 2 * r)
                    rect.center = end
                    angles = (angle, angle + turn)
                    pg.draw.arc(screen, conf.ARC_BG_COLOUR, rect, max(angles), min(angles))
                    pg.draw.arc(screen, conf.ARC_COLOUR, rect, min(angles), max(angles))
        return True

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
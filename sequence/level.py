from math import cos, sin, pi, acos

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

    def _get_line_ends (self):
        m, c = self.eqn()
        # get border intercepts
        w, h = self.game.res
        if m is None:
            # vertical
            x = self.pos[0]
            pts = [(x, 0), (x, h)]
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
            pts = pts[:2]
        return pts

    def _get_line_centre (self):
        (x1, y1), (x2, y2) = self._get_line_ends()
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def update_line_pts (self):
        self.pts = self._get_line_ends()
        self.dirty = True

    def click (self, evt):
        if evt.button == conf.MB_MOVE:
            # start moving
            self.moving = True
            # stop rotating
            if self.rotating:
                self.rotating = None
        elif evt.button == conf.MB_ROTATE:
            # start rotating
            self.rotating = True
            if self.moving:
                self.pos = list(self._get_line_centre())
                # stop moving
                self.moving = None

    def unclick (self, evt):
        if evt.button == conf.MB_MOVE:
            self.moving = False
            self.pos = list(self._get_line_centre())
            # if stopped rotating because started moving, start rotating again
            if self.rotating is None:
                self.rotating = True
        elif evt.button == conf.MB_ROTATE:
            self.rotating = False
            # if stopped moving because started rotating, start moving again
            if self.moving is None:
                self.moving = True

    def drag (self, evt):
        if self.moving:
            self.move(evt.rel)
        if self.rotating:
            x, y = self.pos
            x2, y2 = pg.mouse.get_pos()
            dx, dy = evt.rel
            x1, y1 = x2 - dx, y2 - dy
            a_x, a_y, b_x, b_y = x1 - x, y1 - y, x2 - x, y2 - y
            a_len = (a_x ** 2 + a_y ** 2) ** .5
            b_len = (b_x ** 2 + b_y ** 2) ** .5
            if a_len != 0 and b_len != 0: # else at the centre (don't rotate)
                angle = acos((a_x * b_x + a_y * b_y) / (a_len * b_len))
                # get line from (x, y) to centre of mouse movement's line
                c_x, c_y = ((x1 + x2) / 2 - x, (y1 + y2) / 2 - y)
                # sign of cross product with (dx, dy) gives rotation direction
                sign = 1 if dx * c_y - dy * c_x > 0 else -1
                self.rotate(sign * angle)

    def move_kb (self, key, evt, mods):
        d = conf.KEYS_MOVE.index(key)
        amount = [0, 0]
        amount[d % 2] = conf.KEY_MOVE_SPEED * (1 if d > 1 else -1)
        self.move(amount)

    def rotate_kb (self, key, evt, mods):
        d = conf.KEYS_ROTATE.index(key) or -1
        self.rotate(-conf.KEY_ROTATE_SPEED * d)

    def move (self, amount):
        if not self.running:
            self.pos[0] += amount[0]
            self.pos[1] += amount[1]
            self.update_line_pts()

    def rotate (self, amount):
        if not self.running:
            self.angle += amount / pi
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
                    # lines to mark arc
                    for a in angles:
                        a %= 2 * pi
                        x = end[0] + r * get_dx(a)
                        y = end[1] + r * get_dy(a)
                        pg.draw.aaline(screen, conf.ARC_COLOUR, end, (x, y))
        return True
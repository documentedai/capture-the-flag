"""Rendering `Ctf` board"""

import pyglet
from pyglet import gl

from ctf.pieces import Unit, Flag
from ctf import io


class Renderer(object):
    """`Renderer` class, handles the rendering of a `Ctf` game."""
    def __init__(self, width, height, x_pad, y_pad, box, unit_pad):
        """Initialization of `Renderer` object.

        Args:
            width (int): Width of window.
            height (int): Height of window.
            x_pad (float): Amount of padding to add to left / right of
                the window. The higher this number is, the more white
                space will exist to the left of the grid and right of
                the logs / scoreboard.
            y_pad (float): Amount of padding to add to top / bottom of
                the window. The higher this number is, the more white
                space will exist to the left of the grid and right of
                the logs / scoreboard.
            box (float): How large should a box in the grid be. This
                number corresponds to the length of the sides of the
                square.
            unit_pad (float): How much padding should exist between the
                sides of the box the unit is within, and the unit
                itself. if box is 30, and unit_pad is 5, the unit will
                be a 20x20 glyph within a 30x30 box. (A `Unit` side
                length is = box - unit_pad * 2, a `Flag` side length is
                = box - unit_pad * 2 * 2)

        """
        self.width = width
        self.height = height
        self.x_pad = x_pad
        self.y_pad = y_pad
        self.box = box
        self.unit_pad = unit_pad

        self.window = pyglet.window.Window(
            width=self.width,
            height=self.height,
            caption='Capture The Flag'
        )

        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

        font_path = io.resource_path('PressStart2P-Regular.ttf')
        pyglet.font.add_file(font_path)
        press_start_2p = pyglet.font.load('Press Start 2P')

    def draw_grid(self, dims):
        """Method for drawing a grid on the window.

        This method draws a gray and white grid on the left side of the
        window. This grid is where the pieces drawn by `draw_pieces`
        will go.

        Args:
            dims (tuple): Dimensions of the board being drawn.

        """
        gray = True
        for y in range(dims[0]):
            for x in range(dims[1]):
                coordinates = [
                    self.x_pad + x * self.box,
                    self.y_pad + y * self.box,
                    self.x_pad + x * self.box,
                    self.y_pad + (y + 1) * self.box,
                    self.x_pad + (x + 1) * self.box,
                    self.y_pad + (y + 1) * self.box,
                    self.x_pad + (x + 1) * self.box,
                    self.y_pad + y * self.box
                ]

                if gray:
                    colors = [150, 150, 150]*4
                    gray = False
                else:
                    colors = [255, 255, 255]*4
                    gray = True

                pyglet.graphics.draw(
                    4,
                    gl.GL_QUADS,
                    ('v2f', coordinates),
                    ('c3B', colors)
                )

    def draw_pieces(self, dims, key):
        """Method for drawing the pieces on the window.

        This method draws each of the games pieces within boxes on the
        grid drawn by `draw_grid`.

        Args:
            dims (tuple): Dimensions of the board being drawn.
            key (dict): Private `_key` key from `Ctf`.

        """
        for v in key.values():
            if v != 'EMPTY':
                unit_x = v.position[1]
                unit_y = dims[0] - (v.position[0] + 1)

            if isinstance(v, Unit):
                l = self.x_pad + unit_x * self.box + self.unit_pad
                r = self.x_pad + (unit_x + 1) * self.box - self.unit_pad
                b = self.y_pad + unit_y * self.box + self.unit_pad
                t = self.y_pad + (unit_y + 1) * self.box - self.unit_pad

                unit_coordinates = [
                    l, b,
                    l, t,
                    r, t,
                    r, b
                ]

                if v.team == 1:
                    if v.has_flag:
                        unit_colors = [255, 150, 0]*4
                    else:
                        unit_colors = [255, 0, 0]*4
                elif v.team == 2:
                    if v.has_flag:
                        unit_colors = [0, 150, 255]*4
                    else:
                        unit_colors = [0, 0, 255]*4

                pyglet.graphics.draw(
                    4,
                    gl.GL_QUADS,
                    ('v2f', unit_coordinates),
                    ('c3B', unit_colors)
                )

                unit_label = pyglet.text.Label(
                    str(v.idx),
                    font_name='Press Start 2P',
                    font_size=8,
                    x=(l + r) / 2.0,
                    y=(t + b) / 2.0,
                    anchor_x='center',
                    anchor_y='center',
                    color=(255, 255, 255, 255)
                )
                unit_label.draw()

            elif isinstance(v, Flag):
                flag_coordinates = [
                    self.x_pad + unit_x * self.box + self.unit_pad * 2,
                    self.y_pad + unit_y * self.box + self.unit_pad * 2,
                    self.x_pad + unit_x * self.box + self.unit_pad * 2,
                    self.y_pad + (unit_y + 1) * self.box - self.unit_pad * 2,
                    self.x_pad + (unit_x + 1) * self.box - self.unit_pad * 2,
                    self.y_pad + (unit_y + 1) * self.box - self.unit_pad * 2,
                    self.x_pad + (unit_x + 1) * self.box - self.unit_pad * 2,
                    self.y_pad + unit_y * self.box + self.unit_pad * 2
                ]

                if v.team == 1:
                    flag_colors = [255, 0, 0]*4
                elif v.team == 2:
                    flag_colors = [0, 0, 255]*4

                if v.grounded:
                    draw = True
                else:
                    draw = False

                if draw:
                    pyglet.graphics.draw(
                        4,
                        gl.GL_QUADS,
                        ('v2f', flag_coordinates),
                        ('c3B', flag_colors)
                    )

    def draw_scoreboard_logs(self, dims, score, logs, key):
        """Method for drawing the scoreboard and logs on the window.

        This method draws a pixelart inspired scoreboard in the top
        right of the window and then draws the games logs underneath
        it.

        Args:
            dims (tuple): The dimensions of the board being drawn.
            score (dict): The score of the game being drawn.
            logs (list): The logs of the game being drawn.
            key (dict): Private `_key` object from `Ctf`.

        """
        grid_limit = self.x_pad + dims[1] * self.box
        score_x = (self.width + grid_limit) / 2.0

        score_label = pyglet.text.Label(
            'Score',
            font_name='Press Start 2P',
            font_size=24,
            x=score_x,
            y=self.height - self.y_pad,
            anchor_x='center',
            anchor_y='top',
            color=(0, 0, 0, 255)
        )
        score_label.draw()

        bar_1_coordinates = [
            score_x - score_label.content_width / 2.0,
            self.height - self.y_pad - score_label.content_height - 10,
            score_x - score_label.content_width / 2.0,
            self.height - self.y_pad - score_label.content_height - 2,
            score_x + score_label.content_width / 2.0,
            self.height - self.y_pad - score_label.content_height - 2,
            score_x + score_label.content_width / 2.0,
            self.height - self.y_pad - score_label.content_height - 10
        ]
        bar_1_colors = [0, 0, 0]*4
        pyglet.graphics.draw(
            4,
            gl.GL_QUADS,
            ('v2f', bar_1_coordinates),
            ('c3B', bar_1_colors)
        )

        bar_2_top = self.height \
                    - self.y_pad \
                    - score_label.content_height - 18
        bar_2_bottom = self.height \
                       - self.y_pad \
                       - score_label.content_height * 2 - 18
        bar_2_coordinates = [
            score_x - 4,
            bar_2_bottom,
            score_x - 4,
            bar_2_top,
            score_x + 4,
            bar_2_top,
            score_x + 4,
            bar_2_bottom
        ]
        bar_2_colors = [0, 0, 0]*4
        pyglet.graphics.draw(
            4,
            gl.GL_QUADS,
            ('v2f', bar_2_coordinates),
            ('c3B', bar_2_colors)
        )

        score_1_label = pyglet.text.Label(
            str(score[1]),
            font_name='Press Start 2P',
            font_size=24,
            x=score_x - score_label.content_width / 4.0,
            y=bar_2_top,
            anchor_x='center',
            anchor_y='top',
            color=(255, 0, 0, 255)
        )
        score_1_label.draw()

        score_2_label = pyglet.text.Label(
            str(score[2]),
            font_name='Press Start 2P',
            font_size=24,
            x=score_x + score_label.content_width / 4.0,
            y=bar_2_top,
            anchor_x='center',
            anchor_y='top',
            color=(0, 0, 255, 255)
        )
        score_2_label.draw()

        if len(logs) > 0:
            for i, log in enumerate(reversed(logs)):
                if key[log['unit']].team == 1:
                    log_color = (255, 0, 0, 255 - i * 10)
                else:
                    log_color = (0, 0, 255, 255 - i * 10)

                if i == 0:
                    log_y = bar_2_bottom - 60
                else:
                    log_y = bar_2_bottom - 60 - (log_label.content_height + 10) * i

                log_label = pyglet.text.Label(
                    '{}: {}'.format(log['unit'], log['direction']),
                    font_name='Press Start 2P',
                    font_size=16,
                    x=score_x,
                    y=log_y,
                    anchor_x='center',
                    anchor_y='top',
                    color=log_color
                )
                log_label.draw()

    def init_window(self):
        """Method for initializing the window to be drawn on.

        This method clears the window, sets the background to white,
        sets the window as the current OpenGL context, and dispatches
        event handlers.

        """
        gl.glClearColor(1, 1, 1, 1)
        self.window.clear()
        self.window.switch_to()
        self.window.dispatch_events()

    def show(self):
        """Method for showing the window.

        This method swaps the OpenGL front and back buffers.

        """
        self.window.flip()

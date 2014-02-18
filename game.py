import random
import math
import pyglet
from bird import *
from pipe import *
from record import *
import resource

class Game:
    def __init__(self):
        # constants
        self.WINDOW_WIDTH = resource.bg_day.width
        self.WINDOW_HEIGHT = resource.bg_day.height
        self.PIPE_WIDTH = resource.pipe_up.width
        self.PIPE_HEIGHT = resource.pipe_up.height
        self.PIPE_WIDTH_INTERVAL = 150
        self.PIPE_HEIGHT_INTERVAL = self.PIPE_HEIGHT + 80
        self.LAND_HEIGHT = resource.land.height

        self.state = 'INIT'
        
        self.record = Record()

        # sprites
        self.logo = pyglet.sprite.Sprite(resource.title, 60, 320)
        self.button_play = pyglet.sprite.Sprite(resource.button_play, 20, 140)
        self.button_score = pyglet.sprite.Sprite(resource.button_score, 150, 140)
        self.text_ready = pyglet.sprite.Sprite(resource.text_ready, 50, 350)
        self.tutorial = pyglet.sprite.Sprite(resource.tutorial, 90, 200)
        self.game_over = pyglet.sprite.Sprite(resource.text_game_over, 45, 360)
        self.score_panel = pyglet.sprite.Sprite(resource.score_panel, 28, 220)

        # create land
        self.land = pyglet.sprite.Sprite(resource.land, 0, 0)
        self.__setup()

    def __setup(self):
        # create a bird
        self.bird = Bird(resource.bird_gif, 140, 270)
        # create pipes
        self.pipes = []
        y = self.__gen_pipe_pos_y()
        p = Pipe(resource.pipe_up, 500, y)
        self.pipes.append(p)
        p = Pipe(resource.pipe_down, 500, y + self.PIPE_HEIGHT_INTERVAL)
        self.pipes.append(p)
        self.record.reset()

    def reset(self):
        self.__setup()

    def draw(self):
        if self.state == 'INIT':
            # add logo
            self.logo.draw()
            self.button_play.draw()
            self.button_score.draw()
            self.bird.draw()
            self.land.draw()
        elif self.state == 'READY':
            self.text_ready.draw()
            self.tutorial.draw()
            self.bird.set_position(85, 250)
            self.bird.draw()
            self.land.draw()
        elif self.state == 'PLAY' or self.state == 'FAILING':
            self.__draw_pipes()
            self.land.draw()
            self.bird.draw()
            # show current score
            Record.draw_num(self.record.get(), resource.big_nums, 130, 400)
        elif self.state == 'FAILED':
            self.__draw_pipes()
            self.land.draw()
            # show game over
            self.game_over.draw()
            # show score panel
            self.score_panel.draw()
            # show score
            Record.draw_num(self.record.get(), resource.small_nums, 210, 290)
            Record.draw_num(self.record.best_score, resource.small_nums, 210, 250)
            # show buttons
            self.button_play.draw()
            self.button_score.draw()

    def __draw_pipes(self):
        i = 0
        while i < len(self.pipes):
            pipe = self.pipes[i]
            if pipe.x + pipe.width < 0:
                # this pipe has move out of the window, delete it
                self.pipes.pop(0)
                self.pipes.pop(0)
                continue
            elif pipe.x <= self.WINDOW_WIDTH:
                self.pipes[i].draw()
                self.pipes[i + 1].draw()
            i += 2
        # always keep 3 pair of pipes
        if len(self.pipes) < 6:
            x = self.pipes[-1].x + self.PIPE_WIDTH_INTERVAL
            y = self.__gen_pipe_pos_y()
            pipe = Pipe(resource.pipe_up, x, y)
            self.pipes.append(pipe)
            pipe = Pipe(resource.pipe_down, x, y + self.PIPE_HEIGHT_INTERVAL)
            self.pipes.append(pipe)

    def update(self, dt):
        if self.state == 'INIT' or self.state == 'READY':
            # move the land
            self.land.x = 0 if self.land.x else -10
        elif self.state == 'PLAY':
            if self.__is_collide():
                resource.hit_sound.play()
                self.state = 'FAILING'
                self.record.save()
                print 'FAIL!!!!!', self.bird.y, self.bird.height / 2
            else:
                self.bird.update(dt)
                # update pipes
                [pipe.update(dt) for pipe in self.pipes]
                # move the land
                self.land.x = 0 if self.land.x else -10
            self.__calc_score()
        elif self.state == 'FAILING':
            if self.bird.y > self.LAND_HEIGHT + 24:
                self.bird.update(dt)
            elif self.bird.rotation != 90:
                self.bird.rotate(dt)
            else:
                self.state = 'FAILED'

    def __calc_score(self):
        for i in range(1, 2, len(self.pipes)):
            p = self.pipes[i]
            if (not p.scored) and self.bird.x > p.x:
                self.record.inc()
                p.scored = True
                resource.point_sound.play()
                return


    def __is_collide(self):
        HALF_BIRD_SIZE = self.bird.height / 2
        # hit the land
        if self.bird.y < self.LAND_HEIGHT + HALF_BIRD_SIZE:
            return True
        # hit the pipe
        for i in range(1, 2, len(self.pipes)):
            p = self.pipes[i]
            if (self.bird.y + 10 >= p.y or \
                self.bird.y <= p.y - 80 + 10) and \
                self.bird.x - HALF_BIRD_SIZE <= p.x + self.PIPE_WIDTH and \
                self.bird.x + HALF_BIRD_SIZE >= p.x:
                return True
        return False

    def __gen_pipe_pos_y(self):
        return random.randint(-200, 100)
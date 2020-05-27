import math
import random
import pygame
import tkinter as tk
from tkinter import messagebox
import gym
import numpy as np
import time
from gym import spaces
from setuptools.command.dist_info import dist_info


class SkiingGame(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self):
        global width, window, rows, skier, gate, gateCountLimit, finish, isFinishing, score, scoreFont, gateWidth, observationArr, distanceToGate
        pygame.init()
        width = 500
        rows = 20
        gateWidth = 3
        gateCountLimit = 5
        window = pygame.display.set_mode((width, width))
        spawnX = 10
        spawnY = 1
        score = 0
        scoreFont = pygame.font.SysFont("monospace", 16)
        isFinishing = False
        observationArr = np.zeros((2, rows, rows), dtype=int) #pole matic s pozorovaniami
        skier = self.skier((255, 0, 0), (10, 1))  # zaciatocna pozicia
        observationArr[0][spawnY][spawnX] = 1   #hlbka 0 je matica s poziciou jazdca
        gate = self.gate((0, 255, 0), randomGatePosition())
        observationArr[1][gate.body[1]][gate.body[0]:gate.body[0] + gateWidth] = 1 #hlbka 1 je matica s poziciou branky
        finish = self.finishLine((0, 255, 0), (0, 19))
        self.action_space = spaces.Discrete(2)

        calculateDistanceToGate()



    def step(self, action):
        global width, rows, skier, gate, gateCountLimit, finish, isFinishing, score, scoreFont, gateWidth, observationArr, distanceToGate
        episode_over = False
        reward = 0

        previousDistance = distanceToGate

        if isFinishing == False:
            self.skier.move(self=skier,isFinishing=False, action=action)
        else:
            skier.move(True, action)

        calculateDistanceToGate()

        #ak sa hrac pohol smerom od branky
        if distanceToGate > 0 and distanceToGate >= previousDistance:
            reward = -1

        if gateCountLimit > 0:
            gate.move()
            if skier.body[1] == gate.body[1] and (skier.body[0] == gate.body[0] or skier.body[0] == gate.body[0]+1 or skier.body[0] == gate.body[0]+2):
                score += 1
                reward = 1 #odmena za prechod brankou
        else:
            isFinishing = True

        #ak je zjazd do cielovej rovinky, tak odmenu nepocitame
        if isFinishing == True:
           reward = 0

        if skier.body[1] == 20:
            episode_over = True

        ob = observationArr
        return ob, reward, episode_over, {}

    def reset(self):
        global observationArr, skier, gate, finish, gateCountLimit, score, isFinishing, distanceToGate
        isFinishing = False
        observationArr = np.zeros((2, rows, rows), dtype=int)
        skier = self.skier((255, 0, 0), (10, 1))  # spawn point
        gate = self.gate((0, 255, 0), randomGatePosition())
        finish = self.finishLine((0, 255, 0), (0, 19))
        gateCountLimit = 5
        score = 0
        calculateDistanceToGate()
        return observationArr

    def render(self, mode='human', close=False):
        global window
        redrawWindow(window)


    #GAME CODE*********************************
    class gate(object):
        def __init__(self, color, pos):
            self.color = color
            self.body = pos

        def move(self):
            global rows, gateCountLimit, observationArr
            observationArr[1][self.body[1]][self.body[0]:self.body[0] + gateWidth] = 0
            if self.body[1] == 0:
                self.body = (randomGatePosition())
                gateCountLimit -= 1
            else:
                self.body = (self.body[0], self.body[1] - 1)

            if gateCountLimit > 0:
                observationArr[1][self.body[1]][self.body[0]:self.body[0] + gateWidth] = 1

        def draw(self, surface):
            global width, rows, gateWidth
            if self.body[1] >= 0:
                distance = width // rows
                pygame.draw.rect(surface, self.color, (self.body[0] * distance, self.body[1]  * distance, gateWidth * distance, distance))

    class finishLine(object):
        def __init__(self, color, position):
            self.color = color
            self.body = position

        def move(self):
            self.body = (self.body[0], self.body[1] - 1)

        def draw(self, surface):
            global width, rows
            distance = width // rows
            pygame.draw.rect(surface, self.color,
                             (self.body[0] * distance, self.body[1] * distance, rows * distance, distance))

    class skier(object):

        def __init__(self, color, position):
            self.color = color
            self.body = position
            self.direction = 1  # inicializuje pohyb hned po spawne

        def move(self, isFinishing, action):
            global rows, observationArr

            if action == 0:
                self.direction = -1
            elif action == 1:
                self.direction = 1

            if self.body[1] < rows:
                observationArr[0][self.body[1]][self.body[0]] = 0

            if isFinishing:
                self.body = (self.body[0], self.body[1] + 1)

            # ombedzenia pre pohyb mimo zjazdovu plochu
            if self.direction == -1 and self.body[0] <= 0:
                self.body = (self.body[0], self.body[1])
                self.direction = self.direction * -1
            elif self.direction == 1 and self.body[0] >= rows - 1:
                self.body = (self.body[0], self.body[1])
                self.direction = self.direction * -1
            else:
                self.body = (self.body[0] + self.direction, self.body[1])

            if self.body[1] < rows:
                observationArr[0][self.body[1]][self.body[0]] = 1

        def reset(self, position):
            playerArr[self.body[1]][self.body[0]] = 0
            self.body = position
            self.direction = 1

        def draw(self, surface):
            global width, rows
            distance = width // rows
            pygame.draw.rect(surface, self.color,
                             (self.body[0] * distance, self.body[1] * distance, distance, distance))

def calculateDistanceToGate():
    global distanceToGate
    # ak je hrac v strede branky
    if abs(skier.body[0] - gate.body[0]) - abs(skier.body[0] - (gate.body[0] + 2)) == 0:
        distanceToGate = 0
    else:
        distanceToGate = min(abs(skier.body[0] - gate.body[0]), abs(skier.body[0] - (gate.body[0] + 2)))

def randomGatePosition():
    global rows, gateWidth
    x = random.randrange(rows - gateWidth)
    y = rows - 1
    return (x, y)

def redrawWindow(surface):
    global width, rows, skier, gate, isFinishing, score, myfont
    surface.fill((255, 255, 255))
    if isFinishing:
        finish.draw(surface)
    else:
        gate.draw(surface)
    skier.draw(surface)
    scoretext = scoreFont.render("Score {0}".format(score), 1, (0, 0, 0))
    surface.blit(scoretext, (5, 10))
    pygame.display.update()

from random import random, uniform
import math
import time
import csv

import numpy
import pygame
import os


class Lane:
    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.hasCar = False


class Street:
    def __init__(self, carProbability):
        self.carProbability = carProbability

    # initiate lanes: the (1, 3) and (5, 7) indicate the values on the x-axis that the lane spans too
    rightLane = Lane((1, 3))
    leftLane = Lane((5, 7))

    def spawnCar(self):
        self.rightLane.hasCar = False
        self.leftLane.hasCar = False

        if random() <= self.carProbability:
            self.rightLane.hasCar = True

        if random() <= self.carProbability:
            self.leftLane.hasCar = True


class Person:
    # position_x and position_y indicate the position of the person on the street
    position_x = 0.0
    position_y = 0.0
    # moving direction indicates the angel that the person is moving
    movingDirection = 0
    crossed = False
    alive = True

    def __init__(self, movingType, movingSpeed):
        self.movingType = movingType
        self.movingSpeed = movingSpeed
        # since the person starts in the right direction, then it makes sense for us to start the simulation where
        # the person is <movingSpeed> meters in the right direction
        # e.g.: if the movingSpeed is 2m/s and the person starts in the right direction, then the person's position
        # on the x-axis would be 2
        self.position_x = movingSpeed

    def move(self):
        alpha_degree = 0

        if self.movingType == 'A':
            # change of direction with 90 degree possibility
            number = random()

            if number <= 0.25:
                # Degree change of 90, left turn
                alpha_degree = 90
            elif number <= 0.5:
                # Degree change of -90, right turn
                alpha_degree = -90


        if self.movingType == 'B' or self.movingType == 'C':
            # new direction = old direction +α with α is uniformly distributed in [−2/3π, +2/3π]
            alpha = uniform(-2 / 3 * math.pi, 2 / 3 * math.pi)
            # convert from radian to degree
            alpha_degree = round(math.degrees(alpha), 2)
            # update the moving direction with the change of <alpha_degree> degrees

            # generate a random moving speed between 0 and 2
        if self.movingType == 'C':
            self.movingSpeed = numpy.random.exponential(scale=2, size=1)

        self.movingDirection += alpha_degree
        self.movingDirection %= 360
        # Add the cos of the alpha degree * the moving speed to the x position
        self.position_x += math.cos(math.radians(alpha_degree)) * self.movingSpeed
        # Add the sin of the alpha degree * the moving speed to the y position
        self.position_y += math.sin(math.radians(alpha_degree)) * self.movingSpeed


class Simulation:
    def __init__(self, movingType, movingSpeed, carProbability, simulationNumber):
        self.person = Person(movingType, movingSpeed)
        self.street = Street(carProbability)
        self.logger = Logger()
        self.id = simulationNumber
        self.t = 1

    def isInRange(self, number, range):
        return range[0] <= number <= range[1]

    def start(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 1000))
        clock = pygame.time.Clock()
        background = pygame.image.load('background2.png')
        # background = pygame.transform.scale(background, (800, 1000))
        personImage = pygame.image.load('person.png')
        personImage = pygame.transform.scale(personImage, (30, 80))
        laneSquare = pygame.Surface((200, 1000))
        laneSquare.fill('red')
        screen.blit(personImage, (100, self.person.position_y * 100))

        screen.blit(personImage, (0, 0))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()


            self.person.move()
            self.street.spawnCar()
            self.logger.writeLog([self.id, self.person.position_x, self.person.position_y, self.t])
            print('X: ' + str(self.person.position_x) + ' Y: ' + str(self.person.position_y))
            screen.blit(background, (0, 0))

            if self.person.position_y < 0:
                self.person.position_y = 3

            if self.person.position_y > 7:
                self.person.position_y = 5

            screen.blit(personImage, (self.person.position_x * 100, self.person.position_y * 100))

            if self.street.rightLane.hasCar:
                screen.blit(laneSquare, (100, 0))

            if self.street.leftLane.hasCar:
                screen.blit(laneSquare, (500, 0))

            pygame.display.update()
            clock.tick(60)

            if not self.person.alive or self.person.crossed:
                break

            # If the right lane has a car running, and the person is on the right lane
            if self.street.rightLane.hasCar and self.isInRange(self.person.position_x,
                                                               self.street.rightLane.coordinates):
                self.person.alive = False
                self.logger.writeResult([self.id, 0, self.person.position_x, 'no', 'dead: right lane', self.t])
                print('Person was ran over by the car!')
                totals['dead'] += 1
                break

            # If the left lane has a car running, and the person is on the right lane
            if self.street.leftLane.hasCar and self.isInRange(self.person.position_x,
                                                              self.street.leftLane.coordinates):
                self.person.alive = False
                logger.writeResult([self.id, 0, self.person.position_x, 'no', 'dead: left lane', self.t])
                totals['dead'] += 1
                print('Person was run over by the car!')
                break

            # if the person has crossed the street,
            if self.person.position_x >= 7:
                self.person.crossed = True
                logger.writeResult([self.id, 0, self.person.position_x, 'yes', 'Crossed', self.t])
                print('Person Crossed, time elapsed: ' + str(self.t) + ' seconds')
                totals['crossed'] += 1
                break

            # if the person went back on the initial sidewalk
            if self.person.position_x <= 0:
                self.person.crossed = True
                logger.writeResult([self.id, 0, self.person.position_x, 'yes', 'Went back to the sidewalk', self.t])
                print('Person went back to the sidewalk, time elapsed: ' + str(self.t) + ' seconds')
                totals['went_back'] += 1
                break

            time.sleep(1)
            self.t += 1

class Logger:
    resultsFilePath = 'WayHome_results.csv'
    logsFilePath = 'WayHome_logs.csv'
    resultsColumns = ['id', 'startPosition', 'endPosition', 'survived', 'epilogue', 'total_iterations']
    logsColumns = ['id', 'position_x', 'position_y', 'iteration_number']

    def __init__(self):
        if os.path.exists(self.logsFilePath):
            os.remove(self.logsFilePath)

        if os.path.exists(self.resultsFilePath):
            os.remove(self.resultsFilePath)

        open(self.resultsFilePath, 'a')
        self.writeResult(self.resultsColumns)
        open(self.logsFilePath, 'a')
        self.writeLog(self.logsColumns)

    def writeLog(self, row):
        self.writeRow(row, self.logsFilePath)

    def writeResult(self, row):
        self.writeRow(row, self.resultsFilePath)

    def writeRow(self, row, file):
        with open(file, 'a', newline='') as item:
            csv_writer = csv.writer(item)
            csv_writer.writerow(row)


movingType = 'B'
movingSpeed = 2
carProbability = 0.05
logger = Logger()
totals = {
    "crossed": 0,
    "dead": 0,
    "went_back": 0
}

# for i in range(1, 100):
simulation = Simulation(movingType, movingSpeed, carProbability, 1)
simulation.start()


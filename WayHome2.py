from random import random, seed, randrange, uniform
import math
import time
import csv
import pygame

class Lane:

    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.hasCar = False


class Street:
    def __init__(self, carProbability):
        self.carProbability = carProbability

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
    # we are only concerned about the horizontal position of the person
    # In this case, we assume the length of the road spans infinitely, whereas the length is 8 units
    # therefore, the position represents how far is the person from 0 to 8 in the street
    # if the person is on positions 0-1, 4-5, 7-8 they are in the sidewalk, which means they are safe
    # otherwise they are in danger to be run over by a car
    position_x = 0.0
    position_y = 5.0
    movingDirection = 0
    crossed = False
    alive = True

    def __init__(self, movingType, movingSpeed):
        self.movingType = movingType
        self.movingSpeed = movingSpeed

    def move(self):
        if self.movingType == 'A':
            # change of direction with 90 degree possibility
            number = random()

            if number <= 0.25:
                # In cases the person moves North or South, we don't advance the position on the street
                # because they moved vertically
                self.movingDirection = 90
                self.position_y -= self.movingSpeed
            elif number <= 0.5:
                self.movingDirection = 270
                self.position_y += self.movingSpeed
            else:
                self.movingDirection = 0
                # In cases when the person moves east, we advance the position by <movingSpeed> meters
                self.position_x += self.movingSpeed

        if self.movingType == 'B':
            # new direction = old direction +α with α is uniformly distributed in [−2/3π, +2/3π]
            alpha = uniform(-2 / 3 * math.pi, 2 / 3 * math.pi)
            # convert from radian to degree
            alpha_degree = round(math.degrees(alpha), 2)
            self.movingDirection += alpha_degree
            self.movingDirection %= 360
            self.position_x += math.cos(alpha_degree) * self.movingSpeed
            self.position_y += math.sin(alpha_degree) * self.movingSpeed

        if self.position_x < 0:
            self.position_x = 0

class Simulation:
    def __init__(self, movingType, movingSpeed, carProbability, simulationNumber):
        self.person = Person(movingType, movingSpeed)
        self.street = Street(carProbability)
        self.logger = Logger()
        # TODO: generate random id for the simulation
        self.id = str(time.time()) + '_' + str(simulationNumber)
        self.t = 0

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

            if self.street.rightLane.hasCar and self.isInRange(self.person.position_x,
                                                               self.street.rightLane.coordinates):
                self.person.alive = False
                self.logger.writeResult([self.id, 0, self.person.position_x, 'no', self.t])
                print('Person Dead!')
                break

            if self.street.leftLane.hasCar and self.isInRange(self.person.position_x, self.street.leftLane.coordinates):
                self.person.alive = False
                self.logger.writeResult([self.id, 0, self.person.position_x, 'no', self.t])
                print('Person Dead!')
                break

            if self.person.position_x >= 8:
                self.person.crossed = True
                self.logger.writeResult([self.id, 0, self.person.position_x, 'yes', self.t])
                print('Person Crossed, time elapsed: ' + str(self.t) + ' seconds')
                break
            time.sleep(1)
            self.t += 1

class Logger:
    resultsFilePath = 'WayHome_results.csv'
    logsFilePath = 'WayHome_logs.csv'
    resultsColumns = ['id', 'startPosition', 'endPosition', 'has_crossed?', 'total_iterations']
    logsColumns = ['id', 'position_x', 'position_y', 'iteration_number']

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

# for i in range(1, 100):
simulation = Simulation(movingType, movingSpeed, carProbability, 1)
simulation.start()


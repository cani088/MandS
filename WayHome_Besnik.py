from random import random, uniform, expovariate
import math
import csv

import os


class Lane:
    def __init__(self, coordinates, carProbability):
        self.coordinates = coordinates
        self.carProbability = carProbability
        self.carTimes = []
        self.generateCarTimes()

    def generateCarTimes(self):
        for i in range(0, 10000):
            if random() < self.carProbability:
                self.carTimes.append((i, i + 1))


class Street:
    def __init__(self, carProbability):
        # initiate lanes: the (1, 3) and (5, 7) indicate the values on the x-axis that the lane spans too
        self.rightLane = Lane((1, 3), carProbability)
        self.leftLane = Lane((5, 7), carProbability)


class Person:
    # position_x and position_y indicate the position of the person on the street
    position_x = 0.0
    position_y = 0.0
    # moving direction indicates the angel that the person is moving
    movingDirection = 0
    crossed = False
    alive = True

    def __init__(self, movingType, stepSize):
        self.movingType = movingType
        self.stepSize = stepSize
        self.stepSizeConstant = stepSize
        # since the person starts in the right direction, then it makes sense for us to start the simulation where
        # the person is <stepSize> meters in the right direction
        # e.g.: if the stepSize is 2m and the person starts in the right direction, then the person's position
        # on the x-axis would be 2
        self.position_x = stepSize

    def isInLaneWithCar(self, street, time):
        for lane in [street.rightLane, street.leftLane]:
            isInLane = lane.coordinates[0] <= self.position_x <= lane.coordinates[1]

            if not isInLane:
                continue

            laneHasCar = any(start <= time <= end for start, end in lane.carTimes)

            if laneHasCar:
                return True

        return False

    def move(self):
        alpha_degree = 0  # store the angle (in degrees) in which the direction is going to change
        if self.movingType == 'A':
            # change of direction with 90 degree possibility
            number = random()
            if number <= 0.25:
                alpha_degree = 90  # Degree change of 90, left turn
            elif number <= 0.5:
                alpha_degree = -90  # Degree change of -90, right turn

        if self.movingType == 'B' or self.movingType == 'C' or self.movingType == 'D':
            # generate a new alpha angle (in radians) which the person is expected to change the direction
            alpha = uniform(-2 / 3 * math.pi, 2 / 3 * math.pi)
            alpha_degree = round(math.degrees(alpha), 2)  # convert from radian to degree

        if self.movingType == 'D':
            self.stepSize = expovariate(1 / self.stepSizeConstant)

        self.movingDirection += alpha_degree  # change the moving direction with <alpha_degree> degrees
        self.movingDirection %= 360
        tempX = self.position_x

        # Add the cos of the movingDirection angle * the step size to the x position
        self.position_x += math.cos(math.radians(self.movingDirection)) * self.stepSize
        # Add the sin of the movingDirection angle * the step size to the y position
        self.position_y += math.sin(math.radians(self.movingDirection)) * self.stepSize

        if tempX <= self.position_x:
            totals_global['wrong_dir'] += 1


class Simulation:
    def __init__(self, movingType, stepSize, carProbability, logger, simulationNumber):
        self.person = Person(movingType, stepSize)
        self.street = Street(carProbability)
        self.logger = logger
        self.id = simulationNumber
        self.time = 1
        self.totalSteps = 1
        self.carProbability = carProbability

    def start(self):
        self.logger.writeLog([self.id, 0, 0, 0, 0])
        self.logger.writeLog([self.id, self.person.stepSize, 0, 1, 1])

        while self.person.alive and not self.person.crossed:
            self.person.move()
            timeToAdd = 1
            if self.person.movingType == 'C':
                timeToAdd = expovariate(1 / 1)
                print('TimeToAdd: ' + str(timeToAdd))

            self.time += timeToAdd
            totals_global['time'] += timeToAdd
            totals_global['steps'] += 1

            self.totalSteps += 1
            self.logger.writeLog([self.id, self.person.position_x, self.person.position_y, self.totalSteps, self.time])
            print('X: ' + str(self.person.position_x) + ' Y: ' + str(self.person.position_y))

            if self.person.isInLaneWithCar(self.street, self.time):
                self.person.alive = False
                self.logger.writeResult([self.id, 0, self.person.position_x, 'no', 'dead',
                                         self.totalSteps, self.time, self.person.stepSize,
                                         self.person.movingType, self.carProbability])
                print('Person was ran over by the car!')
                totals_global['dead'] += 1
                break

            # if the person has crossed the street,
            if self.person.position_x >= 7:
                self.person.crossed = True
                logger.writeResult([self.id, 0, self.person.position_x, 'yes', 'Crossed',
                                    self.totalSteps, self.time, self.person.stepSize,
                                    self.person.movingType, self.carProbability])
                print('Person Crossed, time elapsed: ' + str(self.time) + ' seconds')
                totals_global['crossed'] += 1
                break

            if self.person.position_x <= 0:
                self.person.position_x = 0
            # # if the person went back on the initial sidewalk
            # if self.person.position_x <= 0:
            #     self.person.crossed = True
            #     logger.writeResult([self.id, 0, self.person.position_x, 'yes', 'Went back to the sidewalk',
            #                         self.totalSteps, self.time, self.person.stepSize,
            #                         self.person.movingType, self.carProbability])
            #     print('Person went back to the sidewalk, time elapsed: ' + str(self.time) + ' seconds')
            #     totals_global['went_back'] += 1
            #     break


class Logger:
    resultsColumns = ['id', 'startPosition', 'endPosition', 'survived', 'epilogue', 'total_iterations',
                      'total_time', 'step_size', 'moving_type', 'car probability']
    logsColumns = ['id', 'position_x', 'position_y', 'iteration_number', 'time']
    logsFilePath = ''
    resultsFilePath = ''

    def __init__(self, movingType):
        self.resultsFilePath = 'WayHome_results_' + movingType + '.csv'
        self.logsFilePath = 'WayHome_logs_' + movingType + '.csv'

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


movingType = 'D'
stepSize = 2
carProbability = 0.05
logger = Logger(movingType)
totals_global = {
    "crossed": 0,
    "dead": 0,
    "went_back": 0,
    "steps": 0,
    "time": 0,
    "wrong_dir": 0
}

sim_res = {}

for cp in range(0, 101):
    carProbability = cp / 100

    for i in range(0, 100):
        simulation = Simulation(movingType, stepSize, carProbability, logger, i)
        simulation.start()

    sim_res[cp] = totals_global['crossed']
    totals_global['crossed'] = 0

print(sim_res)
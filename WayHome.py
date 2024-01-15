from random import random, seed, randrange, uniform
import math
import time


class Lane:

    def __init__(self, coordinates):
        self.coordinates = coordinates
        self.hasCar = False


class Street:
    def __init__(self, carProbability):
        self.carProbability = carProbability

    rightLane = Lane((1, 2))
    leftLane = Lane((6, 7))

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
    position_y = 0.0
    movingDirection = 'E'
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
                self.movingDirection = 'N'
                self.position_y -= self.movingSpeed
            elif number <= 0.5:
                self.movingDirection = 'S'
                self.position_y += self.movingSpeed
            else:
                self.movingDirection = 'E'
                # In cases when the person moves east, we advance the position by <movingSpeed> meters
                self.position_x += self.movingSpeed

        if self.movingType == 'B':
            # the new direction can change on the angle range of [−2/3π, +2/3π], that is -120 to 120 degrees
            # Translated on the x-axis, that range would fall from -0.5 to 1, because cos(120) is -0.5 and cos 0 is 1
            # therefore, when we update the new position, we get a random value from -0.5 to 1,
            # and multiply that by moving speed to get the new position on the x-axis
            stepSize = uniform(-0.5, 1) * self.movingSpeed
            self.position_x += stepSize
            self.position_y += self.movingSpeed - stepSize

class Simulation:
    def __init__(self, movingType, movingSpeed, carProbability):
        self.person = Person(movingType, movingSpeed)
        self.street = Street(carProbability)
        self.t = 0

    def isInRange(self, number, range):
        return range[0] <= number <= range[1]

    def start(self):
        while self.person.alive and not self.person.crossed:
            self.person.move()
            self.street.spawnCar()
            print('Person new Position: X: ' + str(self.person.position_x) + " Y: " + str(self.person.position_y))
            print('Time: ' + str(self.t))
            print("\n")

            if self.street.rightLane.hasCar and self.isInRange(self.person.position_x, self.street.rightLane.coordinates):
                self.person.alive = False
                print('Person Dead!')
                break

            if self.street.leftLane.hasCar and self.isInRange(self.person.position_x, self.street.leftLane.coordinates):
                self.person.alive = False
                print('Person Dead!')
                break

            if self.person.position_x >= 8:
                self.person.crossed = True
                print('Person Crossed, time elapsed: ' + str(self.t) + ' seconds')
                break

            self.t += 1
            time.sleep(1)


movingType = 'B'
movingSpeed = 2
carProbability = 0.05

simulation = Simulation(movingType, movingSpeed, carProbability)
simulation.start()

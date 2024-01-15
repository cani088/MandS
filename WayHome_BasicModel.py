from random import random, seed
import math
import time


def calculate_direction_vector(old_dir_vector, direction):
    """
    Calculates a direction vector based on the original direction vector"""
    new_vector = (
        # x value
        (old_dir_vector[0] * round(math.cos(direction), 5) 
         - old_dir_vector[1] * round(math.sin(direction), 5)),
        # y value
        (old_dir_vector[0] * round(math.sin(direction), 5) 
        + old_dir_vector[1] * round(math.cos(direction), 5))
        )
    
    return new_vector

class Street(object):
    def __init__(self, street_position:dict, sidewalk_position:dict, car_probability:float):
        self.position = street_position
        self.sidewalk = sidewalk_position
        self.car_probability = car_probability
        self.car_on_side = {'left':False, 'right':False}

    def spawn_car(self):
        """
        Spawns cars on both sides according to the probability
        """
        # LEFT SIDE
        if random() <= self.car_probability:
            self.car_on_side['left'] = True
            print('Car is coming on the left side')

        # RIGHT SIDE
        if random() <= self.car_probability:
            self.car_on_side['right'] = True
            print('Car is coming on the left side')
    
class Person(object):
    def __init__(self, start_position:set, start_direction:set):
        self.position = start_position
        self.direction_vector = start_direction
        self.car_probability = car_probability
        self.is_alive = True
        self.reached_sidewalk = False

    def change_direction_A(self):
        """
        """
        # can just go forward and not backward, if yes then calculate new direction

        recalculate = True

        while recalculate == True:
            # get random new direction
            number = random()
            if number <= 0.25:
                direction_change = math.pi/2 # left
                print('Changing to left')
            elif number <= 0.5:
                direction_change = math.pi*(3/2) # right
                print('Changing to right')
            else:
                direction_change = math.pi # forward
                print('Staying with same direction')

            # get new direction
            new_direction_vector = calculate_direction_vector(
                self.direction_vector, direction_change)
            
            # get new position
            new_position = (self.position[0] + new_direction_vector[0], self.position[1] + new_direction_vector[1])

            # check if new position is not outside of field
            if new_position[0] >= 0:
                recalculate = False
                self.position = new_position
                self.direction_vector = new_direction_vector
            else: 
                print('Cannot run against the wall. Calculating new direction.')
                #recalculate = False

        print(f'New position: {self.position} \nNew directional vector: {self.direction_vector}')





    def survival_on_street(self, street, t):
        """
        """
        # check if is on left side of street and car is there
        if self.position[0] > street.position['left'][0] and self.position[0] < street.position['left'][1]:
            print('Person is on left side of street.')
            if street.car_on_side['left'] == True:
                print(f'Hit by car on left side. Over after {t} units.')
                self.is_alive = False

        # check if is on right side of street and car is there
        elif self.position[0] > street.position['right'][0] and self.position[0] < street.position['right'][1]:
            print('Person is on right side of street.')
            if street.car_on_side['right'] == True:
                print(f'Hit by car on right side. Over after {t} units.')
                self.is_alive = False

    def reach_sidewalk(self, street, t):
        # at the moment: just if reaching RIGHT sidewalk
        if self.position[0] > street.sidewalk['right'][0]:
            print(f'Reached the right sidewalk after {t} units.')
            self.reached_sidewalk = True

        # optional to activate - just after 1st unit and after person has left
        #if t > 1:
            #if self.position[0] < street.sidewalk['left'][1]:
                #print(f'Went back to left sidewalk after {t} units.')
                #self.reached_sidewalk = True

# PARAMETERS
start_position = (0, 0)   # (x, y)
velocity = 1  # m/t
start_direction = (velocity, 0)  # (x, y)
street_position = {'left':(1, 3), 'right':(5, 7)}
sidewalk_position = {'left':(0, 1), 'right':(7, 8)}
car_probability = 0.05

# MAIN - should be moved to function
person = Person(start_position, start_direction)
street = Street(street_position, sidewalk_position, car_probability)
t = 1

while person.is_alive and not person.reached_sidewalk:
    print(f'\nt = {t}')
    person.change_direction_A()
    street.spawn_car()
    person.survival_on_street(street, t)
    person.reach_sidewalk(street, t)
    time.sleep(1)

    t += 1





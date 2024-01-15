import math
import random
import csv

class Person:
    def __init__(self, initial_location, initial_direction, per_directoin_change_t, velocity):
        self.current_location = initial_location
        self.current_direction = initial_direction
        self.per_directoin_change_t = per_directoin_change_t
        self.velocity = velocity
        
        self.is_hit_by_car = False
        self.is_hit_by_car_left = False
        self.is_hit_by_car_right = False
        self.reaches_sidewalk = False
        self.reaches_sidewalk_left = False
        self.reaches_sidewalk_right = False

    def change_direction(self, case):
        if case == 'A':
            # change in direction is always 1/4 probability left, 1/2 right, 1/2 forward
            new_way = random.choices(['Left', 'Right', 'Forward'], weights=[1/4, 1/4, 1/2])[0]
            if new_way == 'Left':
                self.current_direction += 90
            elif new_way == 'Right':
                self.current_direction -= 90
            self.current_direction %= 360
            
            print(f"Change Direction: turn {new_way} to {self.current_direction}")
        
        if case == 'B' or case == 'C':
            # new direction = old direction +α with α is uniformly distributed in [−2/3π, +2/3π]
            alpha = random.uniform(-2/3 * math.pi, 2/3 * math.pi)
            alpha_degree = round(math.degrees(alpha), 2)
            # convert from radian to degree
            self.current_direction += alpha_degree
            self.current_direction %= 360

            print(f"Change Direction: turn {alpha} to {self.current_direction}")

    def update_location(self):
        distance = self.velocity * 1
        # convert from degree to radian
        direction_radian = math.radians(self.current_direction)
        delta_x = distance * math.cos(direction_radian)
        delta_y = distance * math.sin(direction_radian)
        current_location_x = round(self.current_location[0] + delta_x, 2)
        current_location_y = round(self.current_location[1] + delta_y, 2)
        self.current_location = current_location_x, current_location_y

        print(f"Current Direction: {self.current_direction}")
        print(f"Current Location: {self.current_location}")
    
    def move(self, t, direction_change_case):
        print("The person is moving...")

        if direction_change_case == 'A' or direction_change_case == 'B':
            # starts the right way but every t time units he changes direction
            if t > 1 and t % self.per_directoin_change_t == 0:
                self.change_direction(direction_change_case)
        if direction_change_case == 'C':
            t_exponential = random.expovariate(1/self.per_directoin_change_t)
            print(f"CCC: {t_exponential}")

            if t_exponential > 1:
                self.change_direction(direction_change_case)
        self.update_location()

class Car:
    def __init__(self, come_intensity):
        self.per_come_t = 1 / come_intensity
        
        self.come_interval_count = 1
        self.come_interval_t = 1
        self.come_left_interval_random_t = 0
        self.come_right_interval_random_t = 0
        self.come_left = False
        self.come_right = False
        
    def move(self, t):
        print("The cars are moving...")
        
        self.come_left = False
        self.come_right = False
        
        self.come_interval_count = int((t - 1) / self.per_come_t) + 1
        self.come_interval_t = int(t % self.per_come_t)
        
        # cars have an intensity of $come_intensity/time unit coming from both directions
        # cars coming from both directions with every $come_interval_t t (interval)
        # car is coming at a random t in the interval
        if self.come_interval_t == 1:
            self.come_left_interval_random_t = random.randint(1, self.per_come_t)
            self.come_right_interval_random_t = random.randint(1, self.per_come_t)
            print(f"A car will come to the left lane at interval t: {self.come_left_interval_random_t}")
            print(f"A car will come to the right lane at interval t: {self.come_right_interval_random_t}")
        if self.come_interval_t == self.come_left_interval_random_t:
            self.come_left = True
            print("A car is coming to the left lane...")
        if self.come_interval_t == self.come_right_interval_random_t:
            self.come_right = True
            print("A car is coming to the right lane...")

class Street:
    def __init__(self, sidewalk_left_x, sidewalk_right_x, lane_left_x, lane_right_x):
        self.sidewalk_left_x = sidewalk_left_x
        self.sidewalk_right_x = sidewalk_right_x
        self.lane_left_x = lane_left_x
        self.lane_right_x = lane_right_x

class Simulation:
    def __init__(self):
        person_initial_location = (0, 0)
        person_initial_direction = 0
        person_per_direction_change_t = 2
        person_velocity = 2
        
        car_come_intensity = 0.05
        
        street_sidewalk_left_x = (0, 1)
        street_sidewalk_right_x = (7, 8)
        street_lane_left_x = (1, 3)
        street_lane_right_y = (4, 5)
        
        self.log_export_directory = 'WayHomeResult.csv'
        self.log_export_head = ["t", "direction", "location_x", "location_y", "car_come_left", "car_come_left", "is_hit_by_car", "car_interval", "car_interval_t", ]
        
        self.person = Person(person_initial_location, person_initial_direction, person_per_direction_change_t, person_velocity)
        self.car = Car(car_come_intensity)
        self.street = Street(street_sidewalk_left_x, street_sidewalk_right_x, street_lane_left_x, street_lane_right_y)
        
        self.t = 1
        
    def run(self, person_directoin_change_case):
        print("------------------------------")
        print("------ SIMULATION START ------")
        print("------------------------------")
        print(f"Person is ready")
        print(f"Initial Location: {self.person.current_location}")
        print(f"Initial Direction: {self.person.current_direction}")
        
        # CSV output
        with open(self.log_export_directory, 'a', newline='') as log:
            csv_log_writer = csv.writer(log)
            csv_log_writer.writerow(self.log_export_head)
            
            while self.person.is_hit_by_car == False and self.person.reaches_sidewalk == False:
                print(f"------ Time {self.t} sec")
                
                # Person move
                self.person.move(self.t, person_directoin_change_case)
                
                # Person check reaches_sidewalk
                if self.street.sidewalk_left_x[0] <= self.person.current_location[0] <= self.street.sidewalk_left_x[1]:
                    self.person.reaches_sidewalk_left = True
                    self.person.reaches_sidewalk = True
                    print("------ Drunky reaches sidewalk")
                if self.street.sidewalk_right_x[0] <= self.person.current_location[0] <= self.street.sidewalk_right_x[1]:
                    self.person.reaches_sidewalk_right = True
                    self.person.reaches_sidewalk = True
                    print("------ Drunky reaches sidewalk")

                # Car move
                self.car.move(self.t)
                
                # Person check is_hit_by_car
                if (
                    self.car.come_left == True
                    and self.street.lane_left_x[0] < self.person.current_location[0] < self.street.lane_left_x[1]
                ):
                        self.person.is_hit_by_car_left = True
                        self.person.is_hit_by_car = True
                        print("********** Drunky is hit by car")
                if (
                    self.car.come_right == True
                    and self.street.lane_right_x[0] < self.person.current_location[0] < self.street.lane_right_x[1]
                ):
                        self.person.is_hit_by_car_right = True
                        self.person.is_hit_by_car = True
                        print("********** Drunky is hit by car")
                
                # CSV output
                csv_log_writer.writerow([self.t, self.person.current_direction, self.person.current_location[0], self.person.current_location[1], self.car.come_left, self.car.come_right, self.person.is_hit_by_car, self.car.come_interval_count, self.car.come_interval_t])

                self.t += 1

class Report:
    def __init__(self, export_directory, run_number, t, is_hit_by_car, is_hit_by_car_left, is_hit_by_car_right, reaches_sidewalk, reaches_sidewalk_left, reaches_sidewalk_right):
        self.export_directory = export_directory
        self.run_number = run_number
        self.t = t
        self.is_hit_by_car = is_hit_by_car
        self.is_hit_by_car_left = is_hit_by_car_left
        self.is_hit_by_car_right = is_hit_by_car_right
        self.reaches_sidewalk = reaches_sidewalk
        self.reaches_sidewalk_left = reaches_sidewalk_left
        self.reaches_sidewalk_right = reaches_sidewalk_right
        
    def summarize(self):
        print("------------------------------")
        print("----- SIMULATION  RESULT -----")
        print("------------------------------")
        
        print("----- Detail")
        print(f"run_number: {self.run_number}")
        print(f"t: {self.t}")
        print(f"is_hit_by_car: {self.is_hit_by_car}")
        print(f"is_hit_by_car_left: {self.is_hit_by_car_left}")
        print(f"is_hit_by_car_right: {self.is_hit_by_car_right}")
        print(f"reaches_sidewalk: {self.reaches_sidewalk}")
        print(f"reaches_sidewalk_left: {self.reaches_sidewalk_left}")
        print(f"reaches_sidewalk_right: {self.reaches_sidewalk_right}")
        
        print("----- Summary")
        t_average = sum(self.t) / self.run_number
        print(f"t_average: {t_average}")
        survival_possibility = self.is_hit_by_car.count(False) / self.run_number
        print(f"survival_possibility: {survival_possibility}")
        reaches_sidewalk_right_possibility = self.reaches_sidewalk_right.count(True) / self.run_number
        print(f"reaches_sidewalk_right_possibility: {reaches_sidewalk_right_possibility}")
        
        csv_head2 = ["t", "is_hit_by_car", "is_hit_by_car_left", "is_hit_by_car_right", "reaches_sidewalk", "reaches_sidewalk_left", "reaches_sidewalk_right"]
        with open(self.export_directory, 'w', newline='') as csvfile2:
            csv_writer2 = csv.writer(csvfile2)
            csv_writer2.writerow(csv_head2)
            for i in range(self.run_number):
                csv_writer2.writerow([str(self.t[i-1]), str(self.is_hit_by_car[i-1]), str(self.is_hit_by_car_left[i-1]), str(self.is_hit_by_car_right[i-1]), str(self.reaches_sidewalk[i-1]), str(self.reaches_sidewalk_left[i-1]), str(self.reaches_sidewalk_right[i-1])])

# Main
# Simulation: Case A
case = 'B'
run_number = 3
export_directory = 'WayHomeSummary_A.csv'

batch_t = []
batch_is_hit_by_car = []
batch_is_hit_by_car_left = []
batch_is_hit_by_car_right = []
batch_reaches_sidewalk = []
batch_reaches_sidewalk_left = []
batch_reaches_sidewalk_right = []

for i in range(run_number):
    simulation = Simulation()
    simulation.run(case)
    
    batch_t.append(simulation.t)
    batch_is_hit_by_car.append(simulation.person.is_hit_by_car)
    batch_is_hit_by_car_left.append(simulation.person.is_hit_by_car_left)
    batch_is_hit_by_car_right.append(simulation.person.is_hit_by_car_right)
    batch_reaches_sidewalk.append(simulation.person.reaches_sidewalk)
    batch_reaches_sidewalk_left.append(simulation.person.reaches_sidewalk_left)
    batch_reaches_sidewalk_right.append(simulation.person.reaches_sidewalk_right)

report = Report(export_directory, run_number, batch_t, batch_is_hit_by_car, batch_is_hit_by_car_left, batch_is_hit_by_car_right, batch_reaches_sidewalk, batch_reaches_sidewalk_left, batch_reaches_sidewalk_right)
report.summarize()

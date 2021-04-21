#!/usr/bin/python3
import statistics as st
from random import shuffle
import genetic as ga
import google_sheets as sheets
from team_information import TeamsPartition
from math import floor
from schedule import Schedule

class ClassInformation:
    '''
    Attributes list - because I hate not having declarations

    availability_dict - a dictionary of students to use in team assignment
        with names as keys and availability bit strings
    unused_dict = a dictionary of students not used in evolving a team
        with names as keys and availability bit strings
        Could have not entered enough hours, or not be enrolled.
    team_size - base size of team. Makes extras into teams one bigger by default right now
    population - list of partitions used in the genetic algorithm (a partition is partition of the class into teams)
    best_partition(TeamsInformation) - the currently used partition
    '''

    def __init__(self, size=3, generations=1000):
        self.population = []
        self.team_size = size
        self.num_gen = generations
 

    #TODO allow passing in file information instead of hardcoding
    def load_from_sheet(self):
        """
        Pulls information from the google spreadsheet. 
        TODO: change to pass in file information
        """
        creds = sheets.credential_handling()
        self.availability_dict, self.unused_dict = sheets.parse_availability(creds)
        self.best_partition = TeamsPartition(self.availability_dict, self.unused_dict)

    def generate_teams(self):
        population = []
        names = list(self.availability_dict.keys())    
        popSize = floor(len(names)/self.team_size)

        for x in range (0,popSize):
            tempA = (ga.createGroup(names,self.team_size))
            population.append(tempA)
            '''
            temp = list(tempA)
            counts = ga.countCommon(temp, self.availability_dict)
            for y in range(0,len(temp)):
                print (list(temp[y]), "  ", counts[y])
            print("\n")
            '''

        #print("__________________________________________________________________________")
        #print("Population size: ", len(population))
      
        '''
        This does all the work
        '''
        self.population = ga.evolvePopulation(population, self.availability_dict, self.num_gen, self.team_size)
        
        '''
        did a whole lot of printing to check
        for i, partition in enumerate(newPopulation[0:5]):
            #print("Group {}:".format(i))
            #print("Group has type: ", type(partition))
            #for j, team in enumerate(partition[0]):
            #    print ("Group {}".format(j))
            #    for person in team:
            #        print(person)
            counts = ga.countCommon(partition[0], availability_dict)
            for j, count in enumerate(counts):
                print(partition[0][i], count)
        '''

    def save_partition(self, partition_num):
        if partition_num > len(self.population):
            print("Chosen partition does not exist. No update made.")
        else:
            self.best_partition.save_list(self.population[partition_num])

    def get_unused_student(self, number):
        """
        Gets the name of an unused student based of their position in the list

        Parameters:
            number(int): number of the student

        Returns:
            string: the name of the student. If nubmer is out of bounds, return "Number not in range"
        """
        name_list = list(self.unused_dict.keys())
        if number > len(name_list) or number < 0:
            return "Number not in range"
        return name_list[number]

    def check_student_schedules(self, student_name):
        """
        Check a student against all possible pairings

        Paramenters:
            student_name(string): the name of the student to check

        Returns:
            (list): a list of tuples (student_name(string), common hour count(int))
        """
        #take student out of whichecver dict it is in
        if student_name in self.availability_dict.keys():
            student_schedule = Schedule(self.availability_dict.pop(student_name))
            avail = True
        else:
            student_schedule = Schedule(self.unused_dict.pop(student_name))
            avail = False

        return_list = []
        if student_schedule.count_bits == 0:
            return return_list
        
        #compare against all students in the availability dicitonary
        for temp_student in self.availability_dict.keys():
            if self.availability_dict[temp_student] == 0:
                continue #really, should never be here, but doing it anyway
            temp_schedule = Schedule(self.availability_dict[temp_student])
            temp_compare = Schedule.static_compare([student_schedule,temp_schedule])
            if temp_compare.count_bits() != 0:
                return_list.append((temp_student, temp_compare)
                        )
        #compare against all students in the unused dictionary
        for temp_student in self.unused_dict.keys():
            if self.unused_dict[temp_student] == 0:
                continue #can be here very often I imagine
            temp_schedule = Schedule(self.unused_dict[temp_student])
            temp_compare = Schedule.static_compare([student_schedule,temp_schedule])
            if temp_compare.count_bits() != 0:
                return_list.append((temp_student, temp_compare))


        #return student to the dict you took it from
        if avail:
            self.availbility_dict[student_name]=student_schedule.bit_field
        else:
            self.unused_dict[student_name]=student_schedule.bit_field

        return return_list

    #print the given number of partitions and their common count
    def print_top_partitions(self, number=4):
        #make sure not printing more than I have
        if number > len(self.population):
           number = len(self.population)
        for x in range(0,number):
           temp = list(self.population[x])
           print("Partition {}:".format(x))
           counts = ga.countCommon(temp, self.availability_dict)
           for y in range(0,len(counts)):
               print ("Team {}:({}) {}".format(y, counts[y], list(temp[y])))
           print ("\n")
    
    #print population[number]
    def print_partition_num(self, number):
        if number not in range(0,len(self.population)):
            print ("Number not in range.")
        else:
           temp = list(self.population[number])
           counts = ga.countCommon(temp, self.availability_dict)
           for y in range(0,len(counts)):
               print ("Team {}:({}) {}".format(y, counts[y], list(temp[y])))
           print ("\n")
           
    def print_best_partition(self, print_numbers=False):
        """
        print the best partition with either numbers or names

        Parameters:
            simple (bool): True if you want numbers, false if you want names. Defaults to false
        """

        print("Current Best Team")
        if print_numbers:
            print("Printing Simple")
            self.best_partition.print_numbers()
        else:
            print("Printing Names")
            self.best_partition.print_partition()
    
    def print_available(self):
        print("Names available for group assignment")
        name_list = list(self.availability_dict.keys())
        for name in name_list:
            print (name)
 
    def print_unused(self, print_numbers=False):
        print("Names in class unused for group assignment")
        name_list = list(self.unused_dict.keys())
        counter = 0 #used only if printing the numbers
        for name in name_list:
            if print_numbers:
                print("({:2}) ".format(counter),end="")
                counter = counter +1
            print (name)

if __name__ == '__main__':
    main()
    #test_parser()


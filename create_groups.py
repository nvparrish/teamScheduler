#!/usr/bin/python3
import statistics as st
from random import shuffle
import genetic as ga
import google_sheets as sheets
from math import floor

class ClassInformation:
    '''
    Attributes list - because I hate not having declarations

    availability_dict - a dictionary with names as keys and avialability bit strings
    teamSize - base size of team. Gets one bigger by default right now
    popultion - list of groups (a groups is partition of the class into teams)
    best_team_set - the currently used team_set
    '''


    def __init__(self, size):
        self.teamSize = size
        self.population = []

    def load_from_sheet(self):
        """
        Pulls information from the google spreadsheet. 
        TODO: change to pass in file information
        """
        creds = sheets.credential_handling()
        self.availability_dict = sheets.parse_availability(creds)

    def generate_teams(self):
        numGenerations=int(input("How many generations? "))
        #TO DO: Add input verification
        population = []
        names = list(self.availability_dict.keys())    
        popSize = floor(len(names)/self.teamSize)
        print("popSize: ", popSize)

        
        #print("First population")
        for x in range (0,popSize):
            tempA = (ga.createGroup(names,self.teamSize))
            population.append(tempA)
            temp = list(tempA)
            counts = ga.countCommon(temp, self.availability_dict)
            '''
            for y in range(0,len(temp)):
                print (list(temp[y]), "  ", counts[y])
            print("\n")
            '''

        #print("__________________________________________________________________________")
        #print("Population size: ", len(population))
        
       
        self.population = ga.evolvePopulation(population, self.availability_dict, numGenerations, self.teamSize)
        
        #self.population = newPopulation, was being saved in newPopulation, now jsut saving directly
        #print('My new population type is: ', type(newPopulation))

        '''for i, group in enumerate(newPopulation[0:5]):
            #print("Group {}:".format(i))
            #print("Group has type: ", type(group))
            #for j, team in enumerate(group[0]):
            #    print ("Group {}".format(j))
            #    for person in team:
            #        print(person)
            counts = ga.countCommon(group[0], availability_dict)
            for j, count in enumerate(counts):
                print(group[0][i], count)
    '''

    #print the given number of groups and their common count
    def print_top_groups(self, number=4):
        #make sure not printing more than I have
        if number > len(self.population):
           number = len(self.population)
        for x in range(0,number):
           temp = list(self.population[x])
           print("Group ",x,":")
           counts = ga.countCommon(temp, self.availability_dict)
           for y in range(0,len(counts)):
             print (list(temp[y]), "  ", counts[y])
           print ("\n")
    
    def print_group_num(self, number):
        if number not in range(0,len(self.population)):
            print ("Number not in range.")
        else:
           temp = list(self.population[number])
           counts = ga.countCommon(temp, self.availability_dict)
           for y in range(0,len(counts)):
             print (list(temp[y]), "  ", counts[y])
           print ("\n")
            
    def print_best_group(self):
        print("Best Team Partition:")
        counts = ga.countCommon(self.best_team_set, self.availability_dict)
        for x in range(0,len(self.best_team_set)):
            print("Team ", x, ": ", list(self.best_team_set[x]), "  ",counts[x])
            #TODO: Add printing what the common hours are?
        
    def save_group(self, group_num):
        if group_num > len(self.population):
            print("Chosen group does not exist. No update made.")
        else:
            self.best_team_set = list(self.population[group_num])

    def print_best(self):
       counts = ga.countCommon(self.best_group, self.availability_dict)
       for y in range(0,len(self.best_group)):
         print (list(self.best_group[y]), "  ", self.counts[y])

if __name__ == '__main__':
    main()
    #test_parser()


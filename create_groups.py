#!/usr/bin/python3
from schedule import Schedule
import statistics as st
from random import shuffle
import genetic as ga
import google_sheets as sheets
from math import floor


def main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    numGenerations=int(input("How many generations? "))
    creds = sheets.credential_handling()
    availability_dict = sheets.parse_availability(creds)
    names = list(availability_dict.keys())    
    print ("Hello! I am in main. Here are my names")
    print (names)

    population = []
    teamSize = 3
    popSize = floor(len(names)/teamSize)
    print("popSize: ", popSize)

    print("First population")
    for x in range (0,popSize):
        tempA = (ga.createGroup(names,teamSize))
        population.append(tempA)
        temp = list(tempA)
        counts = ga.countCommon(temp, availability_dict)
        for y in range(0,len(temp)):
            print (list(temp[y]), "  ", counts[y])
        print("\n")

    print("__________________________________________________________________________")
    #print("Population size: ", len(population))
    #numGenerations = 1 #_000_000
    havePreferred = True
    newPopulation = ga.evolvePopulation(population, availability_dict, numGenerations, teamSize)

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
    for x in range (0,4):
       temp = list(newPopulation[x])
       print("Group ",x,":")
       counts = ga.countCommon(temp, availability_dict)
       for y in range(0,len(temp)):
         print (list(temp[y]), "  ", counts[y])
       print ("\n")
'''  
    groups1 = createGroups(names)
    groups2 = createGroups(names)
    print('\nGroup1: ')
    printPretty(groups1)
    ga.fitnessEvaluation(groups1, availability_dict)
        
    print('\n\nGroup 2')
    printPretty(groups2)
    ga.fitnessEvaluation(groups2, availability_dict)
    
    #print('\n\nDoing crossover')
    
    child = crossover(groups1, groups2, names)
    print('\n\nChild')
    printPretty(child)
    ga.fitnessEvaluation(child, availability_dict)
'''
if __name__ == '__main__':
    main()
    #test_parser()


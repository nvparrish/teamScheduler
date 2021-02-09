#!/usr/bin/python3

import math
import statistics as st
from schedule import Schedule
from random import shuffle
from itertools import combinations
import google_preference as pref


creds = pref.credential_handling()
preference_dict = pref.parse_preferences(creds)

def printPretty (teams_set):
    for individual_team in teams_set:
        print (list(individual_team))

#takes a list and returns a set of frozensets, with base or base+1  names per frozenset
def createGroup(nameList, base=3):

    #print('in createGroup\n')
    #print("base in createGroup: ", base)
    size=len(nameList)
    #print("Size :",size)
    #print(nameList)
    count = math.floor(size/base)
    shuffle(nameList)
    #split the list into 3 lists, ingoring any extra names for now
    part1 = nameList[0:count]
    part2 = nameList[count:(2*count)]
    part3 = nameList[(2*count):(3*count)]
    if base == 4:
       #use this is need 4 parts
       part4 = nameList[(3*count):(4*count)]
       teams_set = set(zip(part1, part2, part3, part4))
    else:
       teams_set = set(zip(part1, part2, part3))

    
    #print(teams_set)
    #add any extra names to existing teams, so we have teams of base + 1, not a team of 1 or 2
    extras = size%base
    while extras>0:
        #temp = teams_set.pop()+(nameList[size-1],)
        temp = teams_set.pop()
        #print(temp)
        #print("Going into loop with len(temp)", len(temp), " and base ", base)
        while (len(temp) > base):
            temp2=temp
            temp = teams_set.pop()
            teams_set.add(temp2)

        temp = temp+(nameList[size-extras],)
        teams_set.add(temp)
        extras -= 1
        #if size%3 == 2:
            #print("Size: ",size)
            #print(nameList, "\nPart1\n", part1, "\nPart2\n", part2, "\nPart3\n", part3)
            #temp2=teams_set.pop()+(nameList[size-2],)
            #teams_set.add(temp2)
        #teams_set.add(temp)
    '''
    # This is for our class of 46 with no availability
    temp = teams_set.pop()
    temp = temp+nameList[(4*count):]
    '''
    """
    print ("In createGroups, final return")
    print (teams_set)
    print ("____________________________________________________________________________")
    """
    #return teams_set   
    return frozenset(map(frozenset, teams_set))

#crossover two sets and return the new one
def crossover (set1, set2, nameList, base=3):
    child = set()
    extraNames = set(nameList)
    #print("base in crossover: ", base)
    #print ("Crossover")
    parent1 = set(set1)
    parent2 = set(set2)

    if parent1 == parent2:
        print ("Crossing equal sets.")
    while parent1 and parent2:  #while both parents have teams_set in them
        temp_Team=parent1.pop() 
        canUse = isUnique(child, temp_Team) #temp team is not already in the new child
        while (not canUse) and parent1: #pop off teams until you get one you can use
            temp_Team=parent1.pop()
            canUse = isUnique(child, temp_Team)
        if canUse:
            child.add(temp_Team)
            extraNames -= temp_Team #take out names in the team from the list of all names since it has been used.
        #same as above, but with the seecond parent
        temp_Team=parent2.pop()
        canUse = isUnique(child, temp_Team)
        while (not canUse) and parent2:
            temp_Team=parent2.pop()
            canUse = isUnique(child, temp_Team)
        if canUse:
            child.add(temp_Team)
            extraNames -= temp_Team
    #print('current child\n')
    #printPretty(child)

    
    #print ("How many extra:", len(extraNames))
    #Deal with the leftovers
    if len(extraNames) == 1: #Only 1 extra name, stick it on somebody's team)
        temp_Team=child.pop()
        while len(temp_Team) == base+1: #Don't stick it on a team that has an extra already
            child.add(temp_Team)
            temp_Team=child.pop()
        temp2 = temp_Team | extraNames
        child.add(frozenset(temp2))
        #print("I hope this worked")
        return frozenset(child)
    '''
    if len(extraNames) < base: #We don't have enough extra to make a team on their own
        temp_Team=child.pop()
        #print("only 2 extra")
        extraNames |= temp_Team #take all of the names out of the team so we can make 2 teams with them all 
    if len(extraNames) <  base*2: #We don't have enough extra to make 2 teams
        temp_Team = child.pop()
        #print("only 5 extra")
        extraNames |= temp_Team
    '''

    #If I go to make more teams, but I have the wrong number to make team sizes
    while len(extraNames)%base > len(extraNames)/base:
        temp_Team = child.pop()
        extraNames |= temp_Team
    
    #Make teams with all the extra names
    leftovers = createGroup(list(extraNames),base)
    #print('leftovers\n', leftovers)
    child |= leftovers

    return frozenset(child)

#check to see if any elements of the new team are already in the set
#return true if you can use the new team
def isUnique (teamSet, team):
    for item in teamSet:
        if (item & team): #if there is something in the intersection
            return False #we can't use the new team

    return True


#teams_set is a set of frozensets of strings
#returns a list of counts of common hours for the team
def countCommon (teams_set, availability_dict):
    commonCount = []
    for team in teams_set:
        teamSchedules = [] #a list of all of the availability number things
        for person in team:
            teamSchedules.append(Schedule(availability_dict[person]))

        commonTimes = Schedule.static_compare(teamSchedules)
        commonCount.append(commonTimes.count_bits())
    #print(commonCount)
    return commonCount

#counts how many of the teams have a pair in the preference_dict
def countPrefered (teams_set):
    counter = 0
    for individual_team in teams_set: #team is a frozenset containing the names on the team
        combos = combinations(individual_team,2)
        for item in combos:
            if preference_dict.get(item):
                counter += 1
    return counter



def fitnessEvaluation (teams_set, availability_dict):
    commonCount = countCommon(teams_set, availability_dict) #count the hours common to a team
    commonCount.sort() #not sure why I am sorting it.

    '''mean = st.mean(commonCount)
    print('mean: ', mean)
    print('median: ',st.median(commonCount))
    print('num 0s:', commonCount.count(0))
    print('svar: ',st.variance(commonCount,mean))
    print('pvar ',st.pvariance(commonCount,mean))
    '''
    """
    #if have a preferenceCount
    preferenceCount = countPrefered(teams_set)
    weight = 0.005 #how much I want to take off for each team that has a preferred match
    """

    #measure = commonCount.count(0)+(st.pvariance(commonCount)/100)-(preferenceCount*weight)
    measure = commonCount.count(0)+(st.pvariance(commonCount)/100)
    return measure



def fitFind(item):
    return item[1] #returnthe fitness of the item

def printList (fitnessList):
    for item in fitnessList:
        print (item[1]) #print the fitnes
        printPretty(item[0])

#population is a list of sets
def evolvePopulation (population, availability_dict, generationCount, base=3):
    #print("base in evolvePopulation: ", base)
    nameList = list(availability_dict.keys())
    fitnessList=[]# fitnesslist will be a list of tuples (frozenset team, float fitness)

    for item in population:
        fit = fitnessEvaluation(item, availability_dict)
        fitnessList.append((item, fit))
    fitnessList.sort(key=fitFind)

    #print ("First Generation:")
    #printList(fitnessList)
    
#    for x in range(0,generationCount):
    x = 0
    while (fitnessList[0][1] > 1 and x < generationCount):
        fitnessList=nextGen(fitnessList, nameList, availability_dict, base)
        x = x+1

    #print("\n\n\Last Generation after :", x, " generations")
    #printList(fitnessList)
    
    #seperate out the list of teams
    unzipped = list(zip(*fitnessList))
    newPopulation = list(unzipped[0])
    #print (newPopulation)

    return newPopulation

#fitnessList is a list of tuples (team, fitness)
#nameList is the list of all the students names
#availability_dict is the availability of each student
#base is the size of a team

def nextGen (fitnessList, nameList, availability_dict, base=3):
    #print("\nEvolving\n")
    #print("base in nextGen: ", base)
    cutoff = math.floor(len(fitnessList)/2) 
    newCount = 3 # how many completely new random teams I want to create
    newGeneration = set(fitnessList[0:cutoff-newCount]) #only keep the best half of the teams, minus some number I want as new

    #print("*********************************************************************************************************")
    #Cross over the best half of the teams to create some new teams
    for x in range(0,cutoff):
        #print("*********************************************************************************************************")
        #print("Parent 1")
        #printPretty(fitnessList[x][0])
        #print("Parent 2")
        #printPretty(fitnessList[x+1][0])
        child = crossover(fitnessList[x][0], fitnessList[x+1][0], nameList, base) #crossover two teams
        fit = fitnessEvaluation(child, availability_dict) #get its fitness
        newGeneration.add((child, fit)) #add it new generation
        #newGeneration.append((child, fit))
        #print("Child")
        #printPretty(child)

    # make some new random teams to fill in the newGeneration
    # TO DO: need to deal with the fact that I shouldn't insert one I already have!! 
    while len(newGeneration) < len(fitnessList):
        newItem = createGroup(nameList,base) 
        fit = fitnessEvaluation(newItem, availability_dict)
        newGeneration.add((newItem, fit))
    newGeneration = list(newGeneration)
    newGeneration.sort(key=fitFind)
    #print("New Generation:")
    #printList(newGeneration)
    #print("\n\n")
    return newGeneration


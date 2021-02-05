#!/usr/bin/python3

import math
import statistics as st
from schedule import Schedule
from random import shuffle
from itertools import combinations
import google_preference as pref


creds = pref.credential_handling()
preference_dict = pref.parse_preferences(creds)

def printPretty (groups):
    for item in groups:
        print (list(item))

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
       groups = set(zip(part1, part2, part3, part4))
    else:
       groups = set(zip(part1, part2, part3))


    
    #print(groups)
    #add any extra names to existing groups, so we have groups of base + 1, not a group of 1 or 2
    extras = size%base
    while extras>0:
        #temp = groups.pop()+(nameList[size-1],)
        temp = groups.pop()
        #print(temp)
        #print("Going into loop with len(temp)", len(temp), " and base ", base)
        while (len(temp) > base):
            temp2=temp
            temp = groups.pop()
            groups.add(temp2)

        temp = temp+(nameList[size-extras],)
        groups.add(temp)
        extras -= 1
        #if size%3 == 2:
            #print("Size: ",size)
            #print(nameList, "\nPart1\n", part1, "\nPart2\n", part2, "\nPart3\n", part3)
            #temp2=groups.pop()+(nameList[size-2],)
            #groups.add(temp2)
        #groups.add(temp)
    '''
    # This is for our class of 46 with no availability
    temp = groups.pop()
    temp = temp+nameList[(4*count):]
    '''
    """
    print ("In createGroups, final return")
    print (groups)
    print ("____________________________________________________________________________")
    """
    #return groups   
    return frozenset(map(frozenset, groups))

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
    while parent1 and parent2:  #while both parents have groups in them
        temp_Team=parent1.pop() 
        canUse = isUnique(child, temp_Team) #temp group is not already in the new child
        while (not canUse) and parent1: #pop off groups until you get one you can use
            temp_Team=parent1.pop()
            canUse = isUnique(child, temp_Team)
        if canUse:
            child.add(temp_Team)
            extraNames -= temp_Team #take out names in the group from the list of all names since it has been used.
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
    if len(extraNames) == 1: #Only 1 extra name, stick it on somebody's group)
        temp_Team=child.pop()
        while len(temp_Team) == base+1: #Don't stick it on a group that has an extra already
            child.add(temp_Team)
            temp_Team=child.pop()
        temp2 = temp_Team | extraNames
        child.add(frozenset(temp2))
        #print("I hope this worked")
        return frozenset(child)
    '''
    if len(extraNames) < base: #We don't have enough extra to make a group on their own
        temp_Team=child.pop()
        #print("only 2 extra")
        extraNames |= temp_Team #take all of the names out of the group so we can make 2 groups with them all 
    if len(extraNames) <  base*2: #We don't have enough extra to make 2 groups
        temp_Team = child.pop()
        #print("only 5 extra")
        extraNames |= temp_Team
    '''

    #If I go to make more groups, but I have the wrong number to make group sizes
    while len(extraNames)%base > len(extraNames)/base:
        temp_Team = child.pop()
        extraNames |= temp_Team
    
    #Make groups with all the extra names
    leftovers = createGroup(list(extraNames),base)
    #print('leftovers\n', leftovers)
    child |= leftovers

    return frozenset(child)

#check to see if any elements of the new team are already in the set
#return true if you can use the new team
def isUnique (groupSet, team):
    for item in groupSet:
        if (item & team): #if there is something in the intersection
            return False #we can't use the new team

    return True


#groups is a set of frozensets of strings
#returns a list of counts of common hours for the group
def countCommon (groups, availability_dict):
    commonCount = []
    for team in groups:
        teamSchedules = [] #a list of all of the availability number things
        for person in team:
            teamSchedules.append(Schedule(availability_dict[person]))

        commonTimes = teamSchedules[0].compare(teamSchedules)
        commonCount.append(commonTimes.count_bits())
    #print(commonCount)
    return commonCount

#counts how many of the groups have a pair in the preference_dict
def countPrefered (groups):
    counter = 0
    for team in groups: #team is a frozenset containing the names on the team
        combos = combinations(team,2)
        for item in combos:
            if preference_dict.get(item):
                counter += 1
    return counter



def fitnessEvaluation (groups, availability_dict):
    commonCount = countCommon(groups, availability_dict) #count the hours common to a group
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
    preferenceCount = countPrefered(groups)
    weight = 0.005 #how much I want to take off for each group that has a preferred match
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
    fitnessList=[]# fitnesslist will be a list of tuples (frozenset group, float fitness)

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
    
    #seperate out the list of groups
    unzipped = list(zip(*fitnessList))
    newPopulation = list(unzipped[0])
    #print (newPopulation)
    return newPopulation

#fitnessList is a list of tuples (group, fitness)
#nameList is the list of all the students names
#availability_dict is the availability of each student
#base is the size of a team

def nextGen (fitnessList, nameList, availability_dict, base=3):
    #print("\nEvolving\n")
    #print("base in nextGen: ", base)
    cutoff = math.floor(len(fitnessList)/2) 
    newCount = 3 # how many completely new random teams I want to create
    newGeneration = set(fitnessList[0:cutoff-newCount]) #only keep the best half of the groups, minus some number I want as new

    #print("*********************************************************************************************************")
    #Cross over the best half of the groups to create some new groups
    for x in range(0,cutoff):
        #print("*********************************************************************************************************")
        #print("Parent 1")
        #printPretty(fitnessList[x][0])
        #print("Parent 2")
        #printPretty(fitnessList[x+1][0])
        child = crossover(fitnessList[x][0], fitnessList[x+1][0], nameList, base) #crossover two groups
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


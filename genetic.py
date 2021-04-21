#!/usr/bin/python3

import math
import statistics as st
from schedule import Schedule
from random import shuffle
from itertools import combinations
import google_preference as pref


creds = pref.credential_handling()
preference_dict = pref.parse_preferences(creds)

def printPretty (partition):
    for individual_team in partition:
        print (list(individual_team))

#takes a list and returns a set of frozensets, with base or base+1  names per frozenset
def createGroup(nameList, base=3):
    """
    The function will partition a list of people into sets of size or size+1
    Default group size is 3. 

    Parameters:
        nameList(list): list of names(string)
        base(int): base group size. Default is 3. If list not evenly divisable, groups get one size bigger.
    
    Returns:
        frozenset : items in set are frozensets. Each frozenset contains names(string)
    """

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
       partition = set(zip(part1, part2, part3, part4))
    else:
       partition = set(zip(part1, part2, part3))

    
    #print(partition)
    #add any extra names to existing teams, so we have teams of base + 1, not a team of 1 or 2
    extras = size%base
    while extras>0:
        #temp = partition.pop()+(nameList[size-1],)
        temp = partition.pop()
        #print(temp)
        #print("Going into loop with len(temp)", len(temp), " and base ", base)
        while (len(temp) > base):
            temp2=temp
            temp = partition.pop()
            partition.add(temp2)

        temp = temp+(nameList[size-extras],)
        partition.add(temp)
        extras -= 1
        #if size%3 == 2:
            #print("Size: ",size)
            #print(nameList, "\nPart1\n", part1, "\nPart2\n", part2, "\nPart3\n", part3)
            #temp2=partition.pop()+(nameList[size-2],)
            #partition.add(temp2)
        #partition.add(temp)
    '''
    # This is for our class of 46 with no availability
    temp = partition.pop()
    temp = temp+nameList[(4*count):]
    '''
    """
    print ("In createGroups, final return")
    print (partition)
    print ("____________________________________________________________________________")
    """
    #return partition   
    return frozenset(map(frozenset, partition))

def crossover (partition_set1, partition_set2, nameList, base=3):
    """
    This functions crosses over two partitions and returns a new partition.

    Alternates taking teams from each partition. If the team contains names already in the new partiion, the team is ignored until a unique team is found. After both partitions have been emptied, any students not in the new partition are put into new teams and added to the new partition.

    Parameters:
        partition_set1(frozenset): a frozenset containing teams. 
                    Teams are frozensets of names(string)
        partition_set2(frozenset): a frozenset containing teams.
                    Teams are frozensets of names(string)
        nameList(list): a list of names(string) of the entire class
        base(int): the smallest size of a team

    Returns:
        frozenset: a new frozenset of teams. Teams are frozensets of names(string)

    """
    child = set()
    extraNames = set(nameList)
    #print("base in crossover: ", base)
    #print ("Crossover")
    parent1 = set(partition_set1)
    parent2 = set(partition_set2)

    if parent1 == parent2:
        print ("Crossing equal sets.")
    while parent1 and parent2:  #while both parents have teams in them
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

#TODO change name
def isUnique (teamSet, team):
    """
    This function checks to see if any names in a single team are already contained in any of the teams in a set.

    Parameters:
        teamSet(frozenset): a set or frozenset of teams. Teams are frozensets of names(string)
        team (frozenset): a set or frozenset of names(string)

    Returns:
        bool: True is no elements of team are already in teamSet
    """
    for item in teamSet:
        if (item & team): #if there is something in the intersection
            return False #we can't use the new team

    return True

#TODO fix the variable names
def countCommon (partition, availability_dict):
    """
    This functions counts how many hours all members of each team in the partition have commonly available. 

    Parameters:
        partition(set): a set of teams. Teams are frozensets of names(string) #TODO Rename this partition
        availability_dict: a dictionary of ints. Keys are student names(string). Value is an int representing the availability of the student to be used as a bit_field in a Schedule

    Returns:
        list(int): A list of the common hour count of each team in partition. Each value is an int between 0 and 24
    """
    commonCount = []
    for team in partition:
        teamSchedules = [] #a list of all of the availability number things
        for person in team:
            teamSchedules.append(Schedule(availability_dict[person]))

        commonTimes = Schedule.static_compare(teamSchedules)
        commonCount.append(commonTimes.count_bits())
    #print(commonCount)
    return commonCount

#TODO reimplement this
def countPrefered (partition):
    """
    Counts how many of the teams have a pair int he preference_dict

    Parameter:
        partition: a set of teams. Team is a frozenset of names(string)

    Returns:
        int: how many teams in partition have a preferred pair
    """
    counter = 0
    for individual_team in partition: #team is a frozenset containing the names on the team
        combos = combinations(individual_team,2)
        for item in combos:
            if preference_dict.get(item):
                counter += 1
    return counter


#TODO put the preferences back in. Look into multi factor evaluations
def fitnessEvaluation (partition, availability_dict):
    """
    Evaluations the fitness of a partition. Currently uses 

    commonhours + (pvariance(commonhours)/100

    Parameters:
        partition(set): a set of teams. Teams are frozensets of names(string)
        availability_dict(dict): a dictionary of the availabilty of each student. Keys are student names(string) Values are (int) that can be used as a bit_field in a Schedule.

    Return:
        float: a number expressing the fitness
    """

    commonCount = countCommon(partition, availability_dict) #get the commoncount of each team in the partition
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
    preferenceCount = countPrefered(partition)
    weight = 0.005 #how much I want to take off for each team that has a preferred match
    """

    #measure = commonCount.count(0)+(st.pvariance(commonCount)/100)-(preferenceCount*weight)
    measure = commonCount.count(0)+(st.pvariance(commonCount)/100)
    return measure



def fitFind(item):
    """
    Returns the second item of a tuple. Used to sort a list of tuples containing teams and fitnesses

    Parameters: 
        item(list): a list of tuples. Each tuple is (team, fitness)

    Return:
        int: the fitness of the team tuple[1]
    """
    return item[1] #returnthe fitness of the item
  
def printList (fitnessList):
    """
    Prints a list of teams and fitnesses with fitness first and then the team

    Paramenters:
        fitnessList(list): a list of tuples. Each tuple is (partition, fitness). partition is a frozenset of teams
    """
    for item in fitnessList:
        print (item[1]) #print the fitnes
        printPretty(item[0])

#population is a list of sets
def evolvePopulation (population, availability_dict, generationCount, base=3):
    """
    The evolution portion of a genetic algorithm

    Paramenters:
        population(list): a list of partitions. Each partition is a frozenset of teams. Each team is frozenset of names(string). So [{{string, string, ...}{string, string, ...}...},{{string, string, ...}{string, string, ...}...},...]

        availability_dict(dict): a dictionary of availability of students. Keys are student anems(string). Values are (int) to be used as bit_field in a Schedule

        generationCount(int): how many generations we want to repeat
        base(int): minimum size of a team. Default value is 3

    Returns:
        list: the new population

    """
    #print("base in evolvePopulation: ", base)
    nameList = list(availability_dict.keys())
    fitnessList=[]# fitnesslist will be a list of tuples (frozenset team, float fitness)

    for partition in population:
        fit = fitnessEvaluation(partition, availability_dict)
        fitnessList.append((partition, fit))
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
#TODO fix the variable names for readability and naming convention
def nextGen (fitnessList, nameList, availability_dict, base=3):
    """
    Does one generation of an evolution.

    Takes a list of partitions.
    Keeps the best half of the partitions
    Creates 3 new partitions
    Crosses over the best partitions to fill out a population

    Parameters:
        fitnessList(list): a list of tuples. Each tuple contains (partition, fitness) partition is a frozenset of teams. team is a frozenset of names(string). fitness is a float 
        nameList(list): a list of names(string)
        availability_dict(dict): a dictionary of availability of students. Keys are student anems(string). Values are (int) to be used as bit_field in a Schedule
        base(int): minimum size of a team. Default value is 3

    Returns:
        list: a population of partitions
    """
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


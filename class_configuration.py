#!/usr/bin/python3
from schedule import Schedule
import statistics as st
from random import shuffle
import genetic as ga
import google_sheets as sheets
import google_preference as pref
from math import floor, ceil, log2
import itertools

class GeneSequence:

    #overloaded less than for sort()
    def __lt__ (self, other):
        return self.fitness < other.fitness


    #class_config is the configuration for the availability Dict
    #returns a list of counts of common hours for the group
    def countCommon (self, class_config):
        ''' Counts up the number of hours in common in each group
            Returns a list of number of hours in common for each team '''
        commonCount = []
        for team in self.partition_set:
            teamSchedules = [] #a list of all of the availability number things
            for person in team:
                teamSchedules.append(Schedule(class_config.availability_dict[person]))

            commonTimes = teamSchedules[0].compare(teamSchedules)
            commonCount.append(commonTimes.count_bits())
        #print(commonCount)
        return commonCount

    #counts how many of the groups have a pair in the preference_dict
    def countPrefered (self, class_config):
        counter = 0
        for team in self.partition_set: #team is a frozenset containing the names on the team
            combos = itertools.combinations(team,2)
        for item in combos:
            if class_config.preference_dict.get(item):
                counter += 1
        return counter
    
    def fitness_evaluation (self, class_config):
        commonCount = self.countCommon(class_config) # Count the hours common to a group
        commonCount = [-30 if x == 0 else log2(x) for x in commonCount]
        preferenceCount = 0.5 * self.countPrefered(class_config)

        return -(sum(commonCount) + preferenceCount)

    '''def fitness_evaluation (self, class_config):
        commonCount = self.countCommon(class_config) # Count the hours common to a group
        commonCount = [-30 if x == 0 else x for x in commonCount]
        preferenceCount = self.countPrefered(class_config)

        return -(sum(commonCount) + preferenceCount)
    '''


    '''def fitness_evaluation (self, class_config):
        commonCount = self.countCommon(class_config) #count the hours common to a group
        commonCount.sort() #not sure why I am sorting it.

        preferenceCount = self.countPrefered(class_config)
        #weight = 0.005 #how much I want to take off for each group that has a preferred match
        weight = 0.03 #how much I want to take off for each group that has a preferred match

        measure = commonCount.count(0)+(st.pvariance(commonCount)/100)-(preferenceCount*weight)
        return measure
    '''

    #constructor
    def __init__(self, class_config):
        shuffle(class_config.name_list)
        self.partition_set = set()
        x=0
        for i in range(class_config.adjust_count):
            temp = x + class_config.team_size+class_config.team_adjust
            self.partition_set.add(frozenset(class_config.name_list[x:temp]))
            x = temp
        while len(self.partition_set) < class_config.team_count:
            temp = x + class_config.team_size
            self.partition_set.add(frozenset(class_config.name_list[x:temp]))
            x = temp
        self.fitness = self.fitness_evaluation(class_config)

    def printPretty (self):
        print("Fitness for partition: ")
        print(self.fitness)
        for frozen_item in self.partition_set:
            for name in frozen_item:
                print(" ",name, end=",")
            print("\b ")


    def printWithCounts(self, class_config):
        print("Fitness for partition: ")
        print(self.fitness)
        x = 0
        count_list = self.countCommon(class_config)
        for frozen_item in self.partition_set:
            for name in frozen_item:
                print(" ", name, end=",")
            print(" {{ HOUR COUNT:", count_list[x], "}}")
            x += 1


class ClassConfiguration:

    def __init__(self, team_size=4, go_larger=True):
        creds = sheets.credential_handling()
        self.availability_dict = sheets.parse_availability(creds)
        creds = pref.credential_handling()
        self.preference_dict = pref.parse_preferences(creds)
        self.name_list = list(self.availability_dict.keys())
        self.team_size = team_size

        #team_count is how many groups of team_size I can make
        #extra_count is how many kids are not in a group
        if len(self.name_list) % self.team_size == 0:
            self.team_count = len(self.name_list) // self.team_size
            self.team_adjust = 0
            self.adjust_count = 0
        elif go_larger:
            self.team_count = floor(len(self.name_list)/self.team_size)
            self.team_adjust = 1
            self.adjust_count = len(self.name_list) % self.team_count
        else:
            self.team_count = ceil(len(self.name_list)/self.team_size)
            self.team_adjust = -1
            self.adjust_count = self.team_count - (len(self.name_list)%self.team_count)
        #how many teams need to be adjusted

    def printPretty (self):
        print("Class list: ",self.name_list)
        print("Team Size: ",self.team_size)
        print("Team Count: ",self.team_count)
        print("Adjustment: ",self.team_adjust)
        print("Adjusted teams: ",self.adjust_count)


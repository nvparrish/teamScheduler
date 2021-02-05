
#!/usr/bin/python3
from schedule import Schedule
import statistics as st
import math
import copy
import sys
from class_configuration import GeneSequence
from class_configuration import ClassConfiguration

class Population:

    #population is a list of sets
    def evolve_population (self, generation_count, print_flag=False):
        #ensure that the list of GeneSequence is sorted by fitness 
        self.gene_list.sort()
        if print_flag:
            print("Starting Evolution with population:")
            for item in self.gene_list:
                item.printPretty()
        
        #iterate for generation_count
        #for x in range(generation_count):
        gen_count = 0
        #while self.gene_list[0].fitness > 1 and gen_count < generation_count:
        while gen_count < generation_count:
            sys.stderr.write("Generation [{}]: ".format(gen_count))
            self.gene_list=self.next_gen(print_flag)
            gen_count += 1

        if print_flag:
            print("\n\n\Last Generation after :", gen_count, " generations")
            for item in self.gene_list:
                item.printPretty()
        

    def next_gen (self, print_flag=False):
        if print_flag:
            print("*********************************************************************************")
            print("\nNext Generation\n")
        cutoff = math.floor(len(self.gene_list)/2) 
        newCount = 3 # how many completely new random teams I want to create
        newGeneration = self.gene_list[0:cutoff-newCount] #only keep the best half of the groups, minus some number I want as new

        #Cross over the best half of the groups to create some new groups
        for x in range(0,cutoff):
            child = self.crossover(x,print_flag) #crossover two groups
            newGeneration.append(child) #add it new generation
            if print_flag:
                print(x)
                print("*****************************************************************************************")
                print("Parent 1")
                self.gene_list[x].printPretty()
                print("Parent 2")
                self.gene_list[x+1].printPretty()
                print("Child")
                child.printPretty()

        # make some new random teams to fill in the newGeneration
        # TO DO: need to deal with the fact that I shouldn't insert one I already have!! 
        while len(newGeneration) < len(self.gene_list):
           newGeneration.append(GeneSequence(self.class_config)) 
        
        newGeneration.sort()
        if print_flag:
            print("New Generation:")
            for item in newGeneration:
                item.printPretty()
        sys.stderr.write("Best fitness: {}\n".format(newGeneration[0].fitness))
        return newGeneration

    #check to see if any of the names in name_set are in any of the teams in the big_set
    def isUnique(self, big_set, name_set):
        for item in big_set:
            if (item & name_set): # if there is name in the intersection of the two teams, I can use the new team
                return False
        return True

    def sizeNeeded(self, name_set, counter):
        #if this set is the adjusted size and we need more of them, return true

        if len(name_set) == (self.class_config.team_size+self.class_config.team_adjust):
            if counter:
                return True
            return False
        return True

    #crossover two lists of GeneSequences
    def crossover (self, index, print_flag=False):
        child = set()
        #print("base in crossover: ", base)
        if print_flag:
            print ("Crossover")
        extraNames = set(copy.copy(self.class_config.name_list))
        adjusted_needed = self.class_config.adjust_count
        parent1 = copy.copy(self.gene_list[index].partition_set)
        parent2 = copy.copy(self.gene_list[index+1].partition_set)
        if print_flag:
            print ("Beginning:")
            print ("P1\n", parent1)
            print ("P2\n", parent2)
            print ("Child\n", child)
            print ("ExtraNames\n", extraNames)
            print ("Adjust Needed: ", adjusted_needed)
            print ("#########")

        if parent1 == parent2:
            self.gene_list[index+1] = GeneSequence(self.class_config)
            parent2 = copy.copy(self.gene_list[index+1].partition_set)
            if print_flag:
                print ("Crossing equal sets.")
                print ("New P2\n", parent2)

        while parent1 and parent2:  #while both parents have groups in them
            temp_team=parent1.pop()  #this is a GeneSequence
            canUse = self.isUnique(child, temp_team) and self.sizeNeeded(temp_team, adjusted_needed)#temp group is not already in the new child
            while (not canUse) and parent1: #pop off groups until you get one you can use
                temp_team=parent1.pop()
                canUse = self.isUnique(child, temp_team) and self.sizeNeeded(temp_team, adjusted_needed)#temp group is not already in the new child
            if canUse:
                child.add(temp_team)
                extraNames -= temp_team #take out names in the group from the list of all names since it has been used.
                if len(temp_team) != self.class_config.team_size:
                    adjusted_needed -= 1
                    if print_flag:
                        print("odd sized set")
            #same as above, but with the seecond parent
            temp_team=parent2.pop()
            canUse = self.isUnique(child, temp_team) and self.sizeNeeded(temp_team, adjusted_needed)#temp group is not already in the new child
            while (not canUse) and parent2:
                temp_team=parent2.pop()
                canUse = self.isUnique(child, temp_team) and self.sizeNeeded(temp_team, adjusted_needed)#temp group is not already in the new child
            if canUse:
                child.add(temp_team)
                extraNames -= temp_team
                if len(temp_team) != self.class_config.team_size:
                    adjusted_needed -= 1
        if print_flag:
            print('current child\n', child)

        
        #Deal with the leftovers
        
        #if I have too few extranames to make a full team, that is bad
        if extraNames and len(extraNames)<self.class_config.team_size and len(extraNames)<(self.class_config.team_size+self.class_config.team_adjust):
            print("We are in big fat trouble!!!")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            print(extraNames,"\n---\n")
            print(child,"\n---\n")
            print(parent1,"\n---\n")
            print(parent2,"\n---\n")
            for item in child:
                if len(item) == self.class_config.team_size:
                    #TODO deal with larger sets not just smaller ones
                    temp = set(item)
                    child.remove(item)
                    extraNames.add(temp.pop())
                    child.add(frozenset(temp))
                    if len(extraNames) == self.class_config.team_size+self.class_config.team_adjust:
                        child.add(frozenset(extraNames))
                        adjusted_needed -= 1
                        if True: #print_flag:
                            print("Edited child after big fat trouble")
                            print(child, "\n---\n")
                        break



        size = self.class_config.team_size+self.class_config.team_adjust
        if print_flag:
            print ("Current situation:")
            print ("P1\n", parent1)
            print ("P2\n", parent2)
            print ("Child\n", child)
            print ("ExtraName\n", extraNames)
            print ("Adjust Needed: ", adjusted_needed)
        
        while adjusted_needed:
            temp = set()
            for x in range(size):
                temp.add(extraNames.pop())
            child.add(frozenset(temp))
            adjusted_needed -= 1
        size = self.class_config.team_size
        while extraNames:
            temp = set()
            for x in range(size):
                temp.add(extraNames.pop())
            child.add(frozenset(temp))
                
        newGuy = GeneSequence(self.class_config)
        newGuy.partition_set=child
        newGuy.fitness = newGuy.fitness_evaluation(self.class_config)
        if print_flag:
            print("NewGuy partition Returning to New Gen")
            newGuy.printPretty()

        return newGuy
    
    def printPretty (self):
        print("My Population")
        for item in self.gene_list:
            print("----------------")
            item.printWithCounts(self.class_config)
        

    def __init__(self, class_config, print_flag = False):

        self.class_config = class_config
        self.gene_list = []
        # make some number of genes
        x = self.class_config.team_count #yes, this is a random number. No I don't know why
        for i in range(x):
            self.gene_list.append(GeneSequence(self.class_config))

        self.gene_list.sort()

        if(print_flag):
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")
            print("In Population Constructor:")
            print("Class_Config is:")
            self.class_config.printPretty()
            print("Gene list:")
            for item in self.gene_list:
                print("**************************")
                item.printPretty()
            print("^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^")

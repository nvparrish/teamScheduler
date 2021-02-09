#!/usr/bin/python3
import statistics as st
from random import shuffle
import genetic as ga
import google_sheets as sheets
from math import floor
from schedule import Schedule

class TeamsPartition:
    """
    Holds information about a team partition of a class. 

    Can print the entire partition, an individaul team with schedule.
    Can edit teams as well

    Attributes:
        team_dict (dict):    A dictionary containing team tuples keyed on the name of the team
            each entry is a tuple of (list of team members(frozen_set), bit_field of common meeting times(int))
        team_count (int):    How many teams are in the partition
        schedule_dict(dict): A dictionary containing a Schedule for each student assigned to a team, keyed on the name of the student

        team_names (list): A list of names to give to each team. Currently ancient prophets
        days (list):       A list of the days of the week for printing
        meidian (list:     A list with AM and PM for printing
    """
    
    def __init__(self, availability_dict):
        """
        The Constructor for TeamsParition class.

        Sets up the team_names, days and maridian resources
        Copies availability_dict into schedule_dict, converting bit_field into Schedules

        Parameters:
            availability_dict (dict): A dictionary with bit_field(int) for each student. Keyed on student names
        """

        self.days = ['Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat', 'Sun']
        self.meridian = ["AM", "PM"]
        self.team_names = ["Adam", "Moses", "Nephi", "Lehi", 
                "Mormon", "Moroni", "Elisha", "Enoch","John", "Peter", 
                "James", "Luke", "Paul", "Isaiah", "Jerimiah", "Malachi",
                "Jeremiah", "Joshua", "Nathan", "Samuel", "Alma", "Abinadi", "Helaman"]
        self.team_dict = dict()
        self.team_count = 0 #used for accessing the next team name
        
        self.schedule_dict = dict()
        #copy the availability dictionary and store as Scheudules instead of bit strings, because I have a lot to handle and it means I don't have to cast each time I use it.
        for student_key in availability_dict.keys():
            self.schedule_dict[student_key] = Schedule(availability_dict[student_key])
            #Shifted to MST because it makes things easier?
            self.schedule_dict[student_key].shift(7)
            #TODO Deal with being in MST or MDT


    def save_list(self, team_set):
        """
        A function to save a class partition to team_dict.

        Copies each team(frozen_set) and gets a Schedule with the common avialable time.
        Saves each team and schedule as a tuple into a dict keyed on team_name
        
        Parameters:
            team_set: a set of teams(frozen_set)
        """
       
        #temporary new dictionary 
        temp_dict = dict()
        temp_count = 0
        for team in team_set:  #type of team is frozenset
            #get a bit string with their hours
            schedule_list = []
            for person in team:
                schedule_list.append(self.schedule_dict[person])
            meeting_schedule = Schedule.static_compare(schedule_list)
            #meeting_schedule.shift(7) #shift the meeting schedule to Mountain Standard Time
            #TODO Deal with being in MST or MDT

            #put a tuple into the dict (team, meeting_schedule)
            temp_dict[self.team_names[temp_count]] = (team, meeting_schedule)
            temp_count = temp_count+1

        #store the temps
        self.team_dict = temp_dict
        self.team_count = temp_count

    def check_student(self, student_tuple, all_teams=False, team=""):
        if all_teams:
            temp_dict = dict()
            for name in self.team_dict.keys():
                if self.team_dict[name][1].bit_field != 0:
                    team, schedule = self.check_student_team(student_tuple, name)
                    temp_dict[name]=schedule #only save the common hours
            return temp_dict
        elif team != "":
            return self.check_student_team(student_tuple, team)
            
        else:
            print("Nothing to check {} against".format(student))
            #TODO deal with what to pass back

    def check_student_team(self, student_tuple, team_name):
        """Prints the availability of a student against the given team. 
        If sub_team = True, includes the sub_teams
        
        Parameters:
            student_tuple(tuple): tuple of (student_name(string), bit_field(int))
            team_name(string): name of the team to compare to
            sub_team(boolean): if True, compare to all sub_teams
        
        Returns:
            (tuple): (team members(list), schedule_bit_field(list))
        """
        temp_schedule = Schedule(student_tuple[1])
        temp_schedule.shift(7) #shift to MST like everyone else
        #print("Old schedule for student", temp_schedule.bit_field)
        temp_schedule.compare([self.team_dict[team_name][1]])
        #print("New schedule for student", temp_schedule.bit_field)
        #print()
        #print("New common hours for {} with Team {:9}: {:2}".format(student_tuple[0], team_name,
        #    temp_schedule.count_bits()))
        temp_team = list(self.team_dict[team_name][0])
        temp_team.append(student_tuple[0])
        '''
        print("Old Team {}".format(team_name))
        self.print_team(self.team_dict[team_name])
        print("\nNew Team")
        self.print_team((temp_team,temp_schedule))
        '''

        return temp_team, temp_schedule

        #TODO Subteams
        
    def change_team(self, team_name, team_tuple):
        '''Updates team with team_name to the information held in team_tuple

        Parameters:
            team_name(string): name of the team to change
            team_tuple(tuple): tuple of (team members(list), bit_field(int))
        '''
        self.team_dict[team_name]=team_tuple


    def print_simple(self):
        """
        Prints the teams in the team_dict with numbers instead of names
        """

        for y in range(0, self.team_count):
            name = self.team_names[y]
            count = self.team_dict[name][1].count_bits() #gets the teams Schedule and counts common hours
            print("Team {:2} ({:2}) ".format(y, count),end="")
            for person in self.team_dict[name][0]:
                print("*{:30} ".format(person),end="")
            print()

    def print_partition(self):
        """
        Prints all the teams in team_dict with their names and count of the common hours.
        """

        for name in self.team_dict.keys():
            count = self.team_dict[name][1].count_bits() #gets the teams Schedule and counts common hours
            print("Team {:10} ({:2}) ".format(name, count),end="")
            for person in self.team_dict[name][0]:
                print("*{:30} ".format(person),end="")
            print()
        #print("##################################")
        #self.print_team(name)

    def print_team(self, team):
        """
        Prints an individual team with a nicely formated schedule of the common hours

        Parameters:
            team: 
                (string): team name to get from team_dict
                (tuple): (set of members, bit_field of common)
        """

        
        if type(team) is str:
            team_tuple = self.team_dict[team]
        elif type(team) is tuple:
            team_tuple = team
        else:
            print("Bad team sent to print. Recieved: ", type(team))
            return

        for person in team_tuple[0]:
            print("    {:30}".format(person))
        count = team_tuple[1].count_bits() 
        print("Common Meeting Times: {:d} hours".format(count))

        hour_list = [] #list of tuples of common hours
        
        #This converts the schedule bit field into tuples for the hours of the week
        if count != 0:
            bit_int = team_tuple[1].bit_field #Stored as Schedule, just need bits
            #comparitor = 1 # Checking Monday at 0:00
            comparitor = 1 << 167 # Checking Monday at 0:00
            start_time = -10 #need it to not be a real hour
            end_time = -10 #ditto
            for hour in range(0,168):
                if bit_int & comparitor:
                    # It is a common hour
                    if hour == (end_time+1): #I am consecutive to the previous hour seen
                        end_time = hour #new end of consecutive block
                    else: #I have a block I've started. I need to close it and start a new one
                        if start_time >= 0: #not the first block, so add tuple to list
                            hour_list.append((start_time, end_time))
                        start_time = hour
                        end_time = hour
                comparitor = comparitor >> 1 # Check next hour
            hour_list.append((start_time, end_time)) #puts in the last time chunk found

        #This converts the tuples into pretty times
        for time_block in hour_list:
            start_day = time_block[0] // 24 #34 hours in a day
            start_hour = (time_block[0] % 24) % 12 
            if start_hour == 0:
                start_hour = 12 #fix midnight
            start_AMPM = (time_block[0] % 24) // 12
            end_day = time_block[1] // 24 #24 hours in a day
            end_hour = (time_block[1] % 24) % 12 + 1 #add 1 because I want to move one hour forward
            if end_hour == 0:
                end_hour = 1 #fix midnight
            end_AMPM = (time_block[1] % 24) // 12 #0 is AM, 1 is PM

            if end_hour == 12: #I am ending at noon or midnight, so need to fix the AMPM and day?
                if end_AMPM == 0:
                    end_AMPM = 1 #moved from 11 AM to 12 PM
                else: 
                    end_AMPM = 0 #moved from 11 PM to 12 AM
                    end_day = (end_day+1) % 7 #moved to the next day. Mod to account for Sun to Mon
            
            
            print("{} {:2} {} - {} {:2} {}".format(
                self.days[start_day],start_hour,self.meridian[start_AMPM],
                self.days[end_day],  end_hour,  self.meridian[end_AMPM]))






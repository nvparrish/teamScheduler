#!/usr/bin/python3
import statistics as st
from random import shuffle
import genetic as ga
import google_sheets as sheets
from math import floor
from schedule import Schedule
import itertools
import pytz
from datetime import datetime

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
        meridian (list):     A list with AM and PM for printing
        shift (int): How many hours to shift to MST or MDT
    """
    
    def __init__(self, availability_dict, unused_dict):
        """
        The Constructor for TeamsParition class.

        Sets up the team_names, days and maridian resources
        Copies availability_dict into schedule_dict, converting bit_field into Schedules

        Parameters:
            availability_dict (dict): A dictionary with bit_field(int) for each student. Keyed on student names
        """
        
        #setup the constants for printing pretty
        self.days = ['Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat', 'Sun']
        self.meridian = ["AM", "PM"]
        self.team_names = ["Adam", "Moses", "Nephi", "Lehi", 
                "Mormon", "Moroni", "Elisha", "Enoch","John", "Peter", 
                "James", "Luke", "Paul", "Isaiah", "Jerimiah", "Malachi",
                "Jeremiah", "Joshua", "Nathan", "Samuel", "Alma", "Abinadi", "Helaman"]
        #Get the current daylight savings time information and set up the shift
        timezone = pytz.timezone("US/Mountain")
        mountain_time_date = timezone.localize(datetime.today(), is_dst=None)
        if mountain_time_date.tzinfo._dst.seconds == 0:  #if today is standard time
            self.shift_time = 7 #shift GMT 7 hours for MST
        else:
            self.shift_time = 8 #shift GMT 8 hours for MDT
        self.zone = { 7:"MST", 8:"MDT"}

        
        #setup the other stuff
        self.team_dict = dict()
        self.team_count = 0 #used for accessing the next team name
        
        self.schedule_dict = dict()
        #copy all the schedules and shift to Mountain Time
        for student_key in availability_dict.keys():
            self.schedule_dict[student_key] = Schedule(availability_dict[student_key])
            #Shifted to Mountain because it makes things easier?
            self.schedule_dict[student_key].shift(self.shift_time)
        for student_key in unused_dict.keys():
            self.schedule_dict[student_key] = Schedule(unused_dict[student_key])
            #Shifted to mountain because it makes things easier?
            self.schedule_dict[student_key].shift(self.shift_time)


    def save_list(self, team_set):
        """
        A function to save a class partition to team_dict.

        Copies each team(frozen_set) and gets a Schedule with the common available time.
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
            #meeting_schedule.shift(self.shift_time) #shift the meeting schedule to Mountain Standard Time

            #put a tuple into the dict (team, meeting_schedule)
            temp_dict[self.team_names[temp_count]] = (team, meeting_schedule)
            temp_count = temp_count+1

        #store the temps
        self.team_dict = temp_dict
        self.team_count = temp_count

    def check_student(self, student_tuple, all_teams=False, team=""):
        """Checks a student against one or more teams and returns a dictionary of the new common hours
        Paramenters:
            student_tuple (tuple): contains (student name(strint), bit filed(int))
            all_teams (Boolean): set to True if you wish to check against all teams
            team (stirng): name of a specific team
        Returns:
            (tuple): (team_members, schedule_bit_field) if specific team
            (dict): a dict of schedule_bitfields if all teams
        """
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
        temp_schedule.shift(self.shift_time) #shift to Mountain Time like everyone else
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

        #TODO Subteams? Done in the print for now
        
    #TODO change this to update_team 
    def change_team(self, team_name, team_tuple):
        '''Updates team with team_name to the information held in team_tuple

        Parameters:
            team_name(string): name of the team to change
            team_tuple(tuple): tuple of (team members(list), bit_field(int))
        '''
        self.team_dict[team_name]=team_tuple


#Various print functions

    def print_simple(self, file_name="sys.stdout"):
        """
        Prints the teams in team_dict with only the members names
        """
        for team in self.team_dict.values():
            for person in team[0]:
                print("{}, ".format(person),end="",file=file_name)
            print("",file=file_name)


    def print_numbers(self):
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
        DOES NOT PRINT TEAM NAME

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
       
        if count !=0:
            #start_times, end_times = self.get_hours(team_tuple[1])
            hour_string_list = team_tuple[1].format_hours(self.zone[self.shift_time])
            for hour_string in hour_string_list:
                print(hour_string)
  


    def print_subteams(self, team):
        """
        Prints an individual team with a nicely formated schedule of the common hours 
        of the whole teams and all the subteams

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
            print("Bad team sent to print. Received: ", type(team))
            return
        
        #Whole team print
        self.print_team(team_tuple)

        #find sub groups
        sub_team_list = list(itertools.combinations(team_tuple[0], len(team_tuple[0])-1))
        for sub_team in sub_team_list:
            #get the common count for the sub_team
            sub_schedule_list=[]
            print ("\nSub team: ")
            for person in sub_team:
                print("   ",person)
                sub_schedule_list.append(self.schedule_dict[person])
            if 0 in sub_schedule_list: #if a team member has no availability 
                print("Common hours: 0")
            else:
                #print the common hours for the subteam
                common_hours = Schedule.static_compare(sub_schedule_list)
                common_count = common_hours.count_bits()
                if(common_count == 0):
                    print("Common hours: 0")
                else:
                    print("Common hours: {}".format(common_count))
                    hour_string_list = common_hours.format_hours(self.zone[self.shift_time])
                    for hour_string in hour_string_list:
                        print(hour_string)







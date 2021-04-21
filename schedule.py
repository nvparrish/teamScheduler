#!/usr/bin/python3
'''
file: schedule.py
author: Nathan V. Parrish

This code implements an hour-by-hour weekly schedule represented by a 1 for
available during that hour and a 0 as unavailable.  It also supports doing
a rotational bit shift to put schedules on the same timezone.
'''

import random
import math

MAX_SCHEDULE = 2**(24*7) - 1

class Schedule:
    def __init__(self, bit_field = 0):
        self.bit_field = bit_field

    def random(self):
        self.bit_field = random.randrange(0, MAX_SCHEDULE)

    def shift(self, hours):
        ''' Shift by a specifc number of hours based on time zones in GMT.
            This is realized by doing a rotational bit shift.'''
        if hours > 0:
            # Shift left by hour number and rotate left-most to the right
            low_bits = self.bit_field >> 168-hours
            high_bits = self.bit_field << hours
            self.bit_field = (high_bits | low_bits) & MAX_SCHEDULE
            
        elif hours < 0:
            # Shift right and rotate right most to the left end
            high_bits = self.bit_field & (2**(-hours) - 1)
            low_bits = self.bit_field >> -hours
            high_bits = high_bits << 168 + hours
            self.bit_field = (high_bits | low_bits) & MAX_SCHEDULE

    def compare(self, schedule_list):
        ''' This takes in a list of schedules represented in bit fields and does a bitwise
            and across all input schedules.  If one of the schedules is equal to zero,
            that is ignored in the bitwise and, since students who provide zero available
            hours may be randomly assigned.
            input:
            schedule_list - a list of Schedule objects; each contains a 168-bit bit_field 
                        representing each of the hours in a week
            return:
            self '''
        mixed_schedule = self.bit_field
        for schedule in schedule_list:
            if schedule.bit_field != 0: # Don't use comparisons with uninitialized schedules
                mixed_schedule &= schedule.bit_field
        self.bit_field = mixed_schedule
        return self

    def static_compare(schedule_list):
        ''' This takes in a list of schedules represented in bit fields and does a bitwise
            and across all input schedules.  If one of the schedules is equal to zero,
            that is ignored in the bitwise and, since students who provide zero available
            hours may be randomly assigned.
            
            Parameters:
            schedule_list(list) - a list of Schedule objects; each contains a 168-bit bit_field 
                        representing each of the hours in a week
            Returns:
              Schedule: representing a bitwise and of all schedules in the schedule_list '''
        if not isinstance(schedule_list[0], Schedule):
            raise TypeError("Schedule.static_compare() expects a non-empty list of Schedule objects");
        mixed_schedule = schedule_list[0].bit_field
        for schedule in schedule_list:
            if schedule.bit_field != 0: # Don't use comparisons with uninitialized schedules
                mixed_schedule &= schedule.bit_field
        return Schedule(mixed_schedule)

    def count_bits(self):
        ''' This function uses a clever and efficient method to count the
            number of set bits in up to a 256-bit number, which is more than
            the 168-bit number being used for the schedule representation'''
        n = self.bit_field
        n = (n & 0x5555555555555555555555555555555555555555555555555555555555555555) + \
            ((n & 0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA) >> 1)
        n = (n & 0x3333333333333333333333333333333333333333333333333333333333333333) + \
            ((n & 0xCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC) >> 2)
        n = (n & 0x0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F) + \
            ((n & 0xF0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0) >> 4)
        n = (n & 0x00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF) + \
            ((n & 0xFF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00) >> 8)
        n = (n & 0x0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF) + \
            ((n & 0xFFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000) >> 16)
        n = (n & 0x00000000FFFFFFFF00000000FFFFFFFF00000000FFFFFFFF00000000FFFFFFFF) + \
            ((n & 0xFFFFFFFF00000000FFFFFFFF00000000FFFFFFFF00000000FFFFFFFF00000000) >> 32)
        n = (n & 0x0000000000000000FFFFFFFFFFFFFFFF0000000000000000FFFFFFFFFFFFFFFF) + \
            ((n & 0xFFFFFFFFFFFFFFFF0000000000000000FFFFFFFFFFFFFFFF0000000000000000) >> 64)
        n = (n & 0x00000000000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) + \
            ((n & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000000000000000000000000000) >> 128)
        return n
    
    def static_count(n):
        ''' This function uses the clever method use to counts bits, but you pass in a 
            bit_field. There is not verification.'''

        n = (n & 0x5555555555555555555555555555555555555555555555555555555555555555) + \
            ((n & 0xAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA) >> 1)
        n = (n & 0x3333333333333333333333333333333333333333333333333333333333333333) + \
            ((n & 0xCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC) >> 2)
        n = (n & 0x0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F) + \
            ((n & 0xF0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0F0) >> 4)
        n = (n & 0x00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF) + \
            ((n & 0xFF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00FF00) >> 8)
        n = (n & 0x0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF) + \
            ((n & 0xFFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000FFFF0000) >> 16)
        n = (n & 0x00000000FFFFFFFF00000000FFFFFFFF00000000FFFFFFFF00000000FFFFFFFF) + \
            ((n & 0xFFFFFFFF00000000FFFFFFFF00000000FFFFFFFF00000000FFFFFFFF00000000) >> 32)
        n = (n & 0x0000000000000000FFFFFFFFFFFFFFFF0000000000000000FFFFFFFFFFFFFFFF) + \
            ((n & 0xFFFFFFFFFFFFFFFF0000000000000000FFFFFFFFFFFFFFFF0000000000000000) >> 64)
        n = (n & 0x00000000000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF) + \
            ((n & 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF00000000000000000000000000000000) >> 128)
        return 
    
    def format_hours(self, time_zone="GMT"):
        '''
        Format the hour blocks of the bit_field for pretty printing

        Parameter:
            Optional: time_zone(stirng): a string for the time zone. Defaults to GMT

        Returns:
            list(strings): a list of formatted strings "starttime - endtime timezone"
        '''
        hour_list = [] #list of tuples of common hours
        days = ['Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat', 'Sun']
        meridian = ["AM", "PM"]
        
        #This converts the schedule bit field into tuples for the hours of the week
        #bit_int = schedule_thing.bit_field #Stored as Schedule, just need bits
        #bit_int = team_tuple[1].bit_field #Stored as Schedule, just need bits
        #comparitor = 1 # Checking Monday at 0:00
        comparitor = 1 << 167 # Checking Monday at 0:00
        start_time = -10 #need it to not be a real hour
        end_time = -10 #ditto
        for hour in range(0,168):
            if self.bit_field & comparitor:
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

        start_list = []
        end_list = []
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
            start_list.append((start_day, start_hour, start_AMPM))
            end_list.append((end_day, end_hour, end_AMPM))
           
        string_list =[]
        for block in range(0, len(start_list)):
            string_list.append("{} {:2} {} - {} {:2} {} {}".format(
                days[start_list[block][0]],
                start_list[block][1],
                meridian[start_list[block][2]],
                days[end_list[block][0]],  
                end_list[block][1],  
                meridian[end_list[block][2]],
                time_zone))

        return string_list


if __name__ == "__main__":
    my_schedule = Schedule()
    my_schedule.random()

    print("Original schedule:")
    print("{:0168b}".format(my_schedule.bit_field))
    
    my_schedule.shift(-3)

    print("Shift -3:")
    print("{:0168b}".format(my_schedule.bit_field))

    my_schedule.shift(3)
    print("Shift back to original")
    print("{:0168b}".format(my_schedule.bit_field))

    my_schedule.shift(3)
    print("Shift +3")
    print("{:0168b}".format(my_schedule.bit_field))

    # Create a unit test for this
    print("Hours available: {}".format(my_schedule.count_bits()))
    print("Hours available manual: {}".format(bin(my_schedule.bit_field).count("1")))


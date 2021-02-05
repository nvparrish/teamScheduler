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
        mixed_schedule = self.bit_field
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


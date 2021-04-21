#!/usr/bin/python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pandas as pd
import numpy as np
from schedule import Schedule
import statistics as st
from random import shuffle
import genetic as ga
#from .geneticAlgorithm import fitnessEvaluation

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# TODO: Enter a value for SPREADSHEET_ID here
with open('spreadsheet.cfg') as spreadsheet_cfg:
    SPREADSHEET_ID = spreadsheet_cfg.readline()[:-1] # Ignore newline
    print("Spreadsheet is set to:", SPREADSHEET_ID)


def credential_handling():
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def parse_availability(creds):
    ''' Accept credentials for the spreadsheet.  This function then downloads
        data from the google spreadsheet, fills the empty cells with zero
        values, identifies the names (keys for dictionaries) and the timzeone
        shift and generates a number where each bit represents availability
        for one hour.  The availability is shifted by the timezone.

        Returns the bit-rotated availability dictionary and unused dictionary.'''

    service = build('sheets', 'v4', credentials=creds)

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Call the Sheets API
    sheet = service.spreadsheets()

    availability_dict = dict()
    timezone_dict = dict()
    unused_dict = dict()
    
    # Pull information about which students are active in the course:
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
            range='\'Total avail\'!A2:E').execute()
    student_summary = result.get('values', [])
    student_summary_df = pd.DataFrame(student_summary)
    student_summary_df.replace([''], [0])
    student_summary_df.replace([np.nan], [0])

    for i, day in enumerate(days):
        range_name = day + '!A2:Z'

        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                range=range_name).execute()
        values = result.get('values', [])

        # Convert values into dataframe (to handle empty cells)
        df = pd.DataFrame(values)
        df = df.replace([''], [0])
        df = df.replace(['1'], [1])
        df = df.replace([np.nan], [0])
        #print(day)
        #print(df)

        # Convert data in each row
        for df_index, df_row in df.iterrows():
            # Check to see if a new name must be added
            try:
                #Students that recorded enough hours to justify putting them in a team
                if student_summary_df.loc[df_index, 4] == '1':
                    #print(student_summary_df.loc[df_index,0], student_summary_df.loc[df_index, 4])
                    if df_row[0] not in availability_dict:
                        availability_dict[df_row[0]] = 0x0
                        s = df_row[1]
                        timezone_dict[df_row[0]] = int(s[s.find("(")+1:s.find(")")])
                    for j, cell in enumerate(df_row):
                        if cell == 1:
                            availability_dict[df_row[0]] |= (1 << 24*(6-i)+(25-j))
                #Students that are still enrolled that have too few hours or did not complete
                elif student_summary_df.loc[df_index, 4] == '0':
                    if df_row[0] not in unused_dict:
                        unused_dict[df_row[0]] = 0x0
                        s = df_row[1]
                        try:
                            timezone_dict[df_row[0]] = int(s[s.find("(")+1:s.find(")")])
                        except AttributeError as e:
                            #saves a 0 if no timezone is found
                            #print("Failed to identify time zone for {}.  Setting shift to 0".format(df_row[0]))
                            timezone_dict[df_row[0]] = 0 
                    for j, cell in enumerate(df_row):
                        if cell == 1:
                            unused_dict[df_row[0]] |= (1 << 24*(6-i)+(25-j))

            except Exception as e:
                print("Error on line", df_index, "with error", e)
                print(student_summary_df.shape)
                continue # Ignore error line


    # Apply the timezone changes
    for key, value in availability_dict.items():
        schedule = Schedule(value)
        schedule.shift(timezone_dict[key])
        availability_dict[key] = schedule.bit_field
        '''
        if schedule.bit_field == 0:
            print("{} has zero availability".format(key))
        '''
    # Apply the timezone change to the unused students 
    for key, value in unused_dict.items():
        schedule = Schedule(value)
        schedule.shift(timezone_dict[key])
        unused_dict[key] = schedule.bit_field
        '''
        if schedule.bit_field == 0:
            print("{} has zero availability".format(key))
        '''

    #print(availability_dict)
    #print("{:0168b}".format(availability_dict['Elizabeth Pomazal']))
    #print("{:0168b}".format(availability_dict['Tashinga Chigwedere']))


    #if not values:
    #    print('No data found.')
    #else:
    #    #print('Name, Major:')
    #    for row in values:
    #        # Print columns A and E, which correspond to indices 0 and 4.
    #        #print('%s, %s' % (row[0], row[4]))
    #        #print(row)
    #        pass
    return availability_dict, unused_dict


def print_pretty(availability_dict):
    
    days = ['Mon', 'Tue', 'Wed', 'Thr', 'Fri', 'Sat', 'Sun']
    meridian = ["AM", "PM"]
    for person in availability_dict.keys():
        print(person)
        
        hour_list = [] #list of tuples of common hours
        #This converts the schedule bit field into tuples for the hours of the week
        bit_int = availability_dict[person] #Stored as Schedule, just need bits
        if bit_int != 0:
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
            print("   {} {:2} {} - {} {:2} {}".format(
                days[start_day],start_hour,meridian[start_AMPM],
                days[end_day],  end_hour,  meridian[end_AMPM]))
        print("--------------------------------------------")




def test_parser():
    creds = credential_handling()
    availability_dict, unused_dict = parse_availability(creds)
    print_pretty(availability_dict)

if __name__ == '__main__':
    #old_main()
    test_parser()


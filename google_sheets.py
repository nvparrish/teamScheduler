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
SPREADSHEET_ID = ''

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

        Returns the bit-rotated availability dictionary.'''

    service = build('sheets', 'v4', credentials=creds)

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Call the Sheets API
    sheet = service.spreadsheets()

    availability_dict = dict()
    timezone_dict = dict()
    
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
                if student_summary_df.loc[df_index, 4] != '1':
                    continue # Ignore students who are not active
            except:
                print("Error on line", df_index)
                print(student_summary_df.shape)
                continue # Ignore error line
            #print(student_summary_df.loc[df_index,0], student_summary_df.loc[df_index, 4])
            if df_row[0] not in availability_dict:
                availability_dict[df_row[0]] = 0x0
                s = df_row[1]
                timezone_dict[df_row[0]] = int(s[s.find("(")+1:s.find(")")])
            for j, cell in enumerate(df_row):
                if cell == 1:
                    availability_dict[df_row[0]] |= (1 << 24*(6-i)+(25-j))


    # Apply the timezone changes
    for key, value in availability_dict.items():
        schedule = Schedule(value)
        schedule.shift(timezone_dict[key])
        availability_dict[key] = schedule.bit_field
        if schedule.bit_field == 0:
            print("{} has zero availability".format(key))

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
    return availability_dict


def printPretty (groups):
    for item in groups:
        print (list(item))

def test_parser():
    creds = credential_handling()
    availability_dict = parse_availability(creds)
    names = list(availability_dict.keys())    
    print(names)
    print(len(names))

def old_main():
    """Shows basic usage of the Sheets API.
    Prints values from a sample spreadsheet.
    """
    creds = credential_handling()
    availability_dict = parse_availability(creds)
    names = list(availability_dict.keys())    
    print ("Hello! I am in main") 
    popSize = 9
    population = []
    teamSize = 4

    print("First population")
    for x in range (0,popSize):
        tempA = (ga.createGroup(names,teamSize))
        population.append(tempA)
        temp = list(tempA)
        counts = ga.countCommon(temp, availability_dict)
        for y in range(0,len(temp)):
            print (list(temp[y]), "  ", counts[y])
        print("\n")


    #print("Population size: ", len(population))
    numGenerations = 100000000
    newPopulation = ga.evolvePopulation(population, availability_dict, numGenerations,teamSize)

    print('My new population type is: ', type(newPopulation))

    '''for i, group in enumerate(newPopulation[0:5]):
        #print("Group {}:".format(i))
        #print("Group has type: ", type(group))
        #for j, team in enumerate(group[0]):
        #    print ("Group {}".format(j))
        #    for person in team:
        #        print(person)
        counts = ga.countCommon(group[0], availability_dict)
        for j, count in enumerate(counts):
            print(group[0][i], count)
'''
    for x in range (0,4):
       temp = list(newPopulation[x])
       print("Group ",x,":")
       counts = ga.countCommon(temp, availability_dict)
       for y in range(0,len(temp)):
        print (list(temp[y]), "  ", counts[y])
       print("\n")
'''  
    groups1 = createGroups(names)
    groups2 = createGroups(names)
    print('\nGroup1: ')
    printPretty(groups1)
    ga.fitnessEvaluation(groups1, availability_dict)
        
    print('\n\nGroup 2')
    printPretty(groups2)
    ga.fitnessEvaluation(groups2, availability_dict)
    
    #print('\n\nDoing crossover')
    
    child = crossover(groups1, groups2, names)
    print('\n\nChild')
    printPretty(child)
    ga.fitnessEvaluation(child, availability_dict)
'''
if __name__ == '__main__':
    #old_main()
    test_parser()


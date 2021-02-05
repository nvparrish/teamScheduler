#!/usr/bin/python3

from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
#import pandas as pd
#import numpy as np
#from schedule import Schedule
#import statistics as st
#from random import shuffle
#import genetic as ga
#

VERBOSE = False

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']


# TODO: Add a spreadsheet ID for the preference matrix
SPREADSHEET_ID = ''
# TODO: Specify approrpiate range
RANGE_NAME = 'Sheet1!A1:AU47'

excel_col_num_to_name = lambda n: '' if n <= 0 else excel_col_num_to_name((n-1) // 26) + chr((n-1)%26 + ord('A'))

excel_col_name_to_num = lambda a: 0 if a == '' else 1 + ord(a[-1]) - ord('A') + 26 * excel_col_name_to_num(a[:-1])

def credential_handling():
    ''' The file token.pickle stores the user's access and refresh tokens, and 
        is created automatically when the authorization flow completes for the
         first time. '''
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

def parse_preferences(creds):
    ''' Accept credentials for the spreadsheet.  This function downloads data
        from the Google spreadsheet, and then populates a dictionary keyed
        using pairs of names as variables. 

        Returns the dictionary of preferences. '''

    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    preference_dict = dict()

    # Pull information
    result = sheet.values().get(spreadsheetId = SPREADSHEET_ID,
            range='A2:A').execute()
    student_list = result.get('values', [])
    #print(student_list)
    #print(student_list[0][0])
    last_column = excel_col_num_to_name(len(student_list)+1)
    #print(last_column)
    #last_row = excel_col_name_to_num(last_column)
    #print(last_row)
    # Generate the range of values to pull
    result = sheet.values().get(spreadsheetId = SPREADSHEET_ID,
            range='B2:' + last_column + str(len(student_list)+1)).execute()
    preferences = result.get('values', [])
    #print(result.get('values', []))

    for i, preference in enumerate(preferences):
        indices = [(j, x) for j, x in enumerate(preference) if x !='']
        for index, pref in indices:
            if VERBOSE:
                print('Student {} prefers student {}'.format(
                    student_list[i][0], student_list[index][0]))
            preference_dict[(student_list[i][0], student_list[index][0])] = int(pref)
    if VERBOSE:
        print(preference_dict)
    return(preference_dict)
    

def main():
    creds = credential_handling()
    preference_dict = parse_preferences(creds)
    print(preference_dict)

if __name__ == "__main__":
    main()

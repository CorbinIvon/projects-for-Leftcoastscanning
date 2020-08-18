from __future__ import print_function
from tkinter import *
import tkinter as tk
import time as time
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import string
from datetime import date
# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

#GLOBALS
day_of_year = ''
sheet = ''
starting_column = 'M'
ending_column = 'P'
row_offset = 1
letter_to_ascii_offset = 65

#Obtained through Spreadsheet URL
sheet_id = '1NhNcYMRfVZadlkkJENGSBQx7M2cjbTGJrgAMWWdREWI'
def main():
    global day_of_year

    day_of_year = datetime.now().timetuple().tm_yday + row_offset
    print (day_of_year)
    # Call the Sheets API
    command = ""
    punch_time()
    while True:
        day_of_year = datetime.now().timetuple().tm_yday + row_offset
        command = input("Command: ")
        if command == "help":
            print("record - records times\n"
                  "time - previously recorded times\n")
        elif command == "record":
            punch_time()
        elif command == "time":
            choice = input("Please Choose:\n  0: Last recorded time\n  1: All times recorded today\n  2: Total Hours of Month\nChoice: ")
            if not choice.isnumeric():
                print("Please choose a number as shown.")
            elif int(choice) < 2:
                get_clocked_times(True, choice)
            else:
                get_month()
def start_services():
    global sheet

    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)
    sheet = service.spreadsheets()



def get_creds():
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    creds = None
    if os.path.exists('token.crd'):
        with open('token.crd', 'rb') as token:
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
        with open('token.crd', 'wb') as token:
            pickle.dump(creds, token)
    return creds
def get_clocked_times(display, numb):
    #0 is last time, 1 is whole day
    global day_of_year, sheet,  starting_column, ending_column
    day_of_year = datetime.now().timetuple().tm_yday +  + row_offset
    sheet_name_prefix = "Employee "
    while True:
        sheet_employee_id = input("User ID: ")
        sheet_and_range = sheet_name_prefix + sheet_employee_id + "!" + starting_column + (str)(day_of_year) + ":" + ending_column + (str)(day_of_year)
        # print (range_field)
        if sheet_employee_id == "quit":
            return
        try:
            result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_and_range).execute()
            values = result.get('values', [])
            if not values:
                print('No data found.')
            else:
                if numb == '0':
                    if display:
                        print(values[0][-1])
                    return values[0][-1]
                elif numb == '1':
                    if display:
                        print(values[0])
                    return values[0]
        except:
            print("ERROR: Incorrect ID")
    #return
def get_month():
    global day_of_year, sheet, ending_column
    day_of_year = datetime.now().timetuple().tm_yday + row_offset
    sheet_name_prefix = "Employee "
    month_number = input("January = 1, Feb. = 2, etc...\nMonth Number: ")
    sheet_employee_id = input("User ID: ")
    sheet_and_range = sheet_name_prefix + sheet_employee_id + "!A1:" + ending_column
    # print (range_field)
    if sheet_employee_id == "quit" or month_number == "quit":
        return
    result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_and_range).execute()
    values = result.get('values', [])
    if not values:
        print('No data found.')
        return
    filter_for_correct_month(month_number, values)



    return
def filter_for_correct_month(number, values):
    #Calculates the total hours from the month of 'number'.
    #Finds the month number, and gets the B Column, or the time column and adds that together.
    for one in values:
        print (values[one])
        #for two in values[one]:
            #return
def punch_time():
    global day_of_year, sheet, starting_column, letter_to_ascii_offset
    day_of_year = datetime.now().timetuple().tm_yday + row_offset
    sheet_name_prefix = "Employee "
    sheet_employee_id = ""
    while True:
        sheet_employee_id = input("User ID: ")
        if sheet_employee_id == "back":
            return
        day_of_year = datetime.now().timetuple().tm_yday + row_offset
        sheet_and_range = sheet_name_prefix + sheet_employee_id + "!" + starting_column + (str)(day_of_year) + ":" + ending_column + (str)(day_of_year)
        n = 0
        values = None
        try:
            result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_and_range).execute()
            values = result.get('values', [])
            if not values:
                n = 0
            else:
                n = (len)(values[0])
        except:
            print("ERROR: Timed Out. Please Try Again.")
            return punch_time()
        now_time = datetime.now().strftime("%H:%M:%S")
        if n > 0:
            tmn = get_time_in_seconds(now_time)
            tml = get_time_in_seconds(values[0][-1]) #Error here because the last thing in the list is not a recorded time, but a SUM Equation. exclude all non hour numbers. :(
            time_remaining = tmn - tml
            clock_buffer = 60 * 30  # time in minutes
            if time_remaining < clock_buffer:
                s = (clock_buffer - time_remaining) % 60
                remain = (clock_buffer - time_remaining) - s
                error_message = ("Please wait at least 30 minutes before clocking again.\n" + str(
                    int(remain / 60)) + " minutes, " + str(s) + " seconds remaining.")
                print(error_message)
                return punch_time()
            else:
                sheet_and_range = sheet_name_prefix + sheet_employee_id + "!" + string.ascii_uppercase[int(ord(starting_column) - letter_to_ascii_offset) + n] + (str)(day_of_year) + ":" + (str)(day_of_year)
        else:
            sheet_and_range = sheet_name_prefix + sheet_employee_id + "!" + string.ascii_uppercase[int(ord(starting_column) - letter_to_ascii_offset) + n] + (str)(day_of_year) + ":" + (str)(day_of_year)

        if sheet_employee_id == "back":
            return
        values = [
            [
                now_time
            ]
        ]
        Body = {
            'values': values,
        }
        try:
            sheet.values().update(spreadsheetId=sheet_id, range=sheet_and_range, valueInputOption='RAW', body=Body).execute()
            print ("Clocked at " + now_time)
        except:
            print("ERROR: Failed to clock in, please try again.\n"
                  "If the error continues, please tell the supervisor.")
def is_non_time(value):
    # Checks the string passed in to check for any unwanted characters.
    # True if only time
    # False if anything else
    for c in value:
        if not c.isnumeric():
            if c != "":
                return False

        return True
def get_time_in_seconds(raw_time):
    #raw_time = remove_non_number(raw_time)
    h=(int)(raw_time[0] + raw_time[1])
    m=(int)(raw_time[3] + raw_time[4])
    s=(int)(raw_time[6] + raw_time[7])
    m = m + h * 60
    s = s + m * 60
    return s
def is_existing_id(id, label_error_message):
    global sheet, starting_column, ending_column
    sheet_name_prefix = "Employee "
    sheet_employee_id = id
    day_of_year = datetime.now().timetuple().tm_yday + row_offset
    sheet_and_range = sheet_name_prefix + sheet_employee_id + "!" + starting_column + (str)(day_of_year) + ":" + ending_column + (str)(day_of_year)
    try:
        result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_and_range).execute()
        values = result.get('values', [])
        return True
    except:
        error_message = "Can not find ID: " + str(id)
        label_error_message.config(text=error_message)
        return False

error_message = ""
is_in_time_window = False



if __name__ == '__main__':
    start_services()
    main()

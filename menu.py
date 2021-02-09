#!/usr/bin/python3
import genetic as ga
import google_sheets as sheets
from create_groups import ClassInformation

def main():
    #Welcome
    '''
    First menu:
    1. Get names from spreadsheet file. Goes to Branch A
    2. Get names from previous run. Goes to Branch B
    '''
    print ("Welcome to Team Creator")
    print ("Would you like to \n A. Create teams from a spreadsheet of student data \n B. Pull existing team data from a file.")
    input_choice = input ("Enter A or B:  ")
    while input_choice not in ("A", "B"):
        input_choice = input ("Please enter only A or B: ")



    '''
    Branch A
    Print spreadsheet info to screen. Change to request file name when needed.
    Pull and store all info from the file.
    Call generate_random_groups
    '''
    #Get the team size, make an object and load from the sheet
    teamSize = int(input("How many people would you like in a team? "))
    print("Please wait for file to load")
    teams_info = ClassInformation(teamSize)
    teams_info.load_from_sheet()

    #evolve a population and save the first partition as the best
    teams_info.generate_teams()
    teams_info.save_group(0)
    teams_info.print_top_groups(4)
    teams_info.print_best_group()
    
    '''
    Branch B
    Request file name for previous iteration
    import information
    print information
    go to Main Menu
    '''

    '''
    Evolution Menu:
    Print the current population and best partition
    Ask if want to replace, evolve, or continue
    '''

    print("______________________________________________")
    print("EVOLUATION MENU\n")
    
    repeat_choice = input("Enter P to Print the lists, R to replace the current best partition, E to evolve a new set of partitions, or C to continue: ")

    while repeat_choice != "C":
        #Print
        if repeat_choice == "P":
            teams_info.print_top_groups(4)
            teams_info.print_best_group()
        #Replace
        elif repeat_choice == "R":
            new_best = input("\nEnter number of the partition you wish to save, P to print the lists again, or C to continue withot changes: ")
            #Print the lists again, ask for the partition number or to continue
            if new_best == "P":
                teams_info.print_top_groups(4)
                teams_info.print_best_group()
                new_best = input("\nEnter the number of the partition you wish to save, or C to continue without changes: ")
            #Whether we printed or not, choice should now be either 0-3 or C
            while new_best != "C" and (not(new_best.isdigit()) or int(new_best) > 3):
                if not(new_best.isdigit()):
                    new_best = input("\nEnter the number of the partition you wish to save, or C to continue without changes: ")
                else:
                    new_best = input("Please enter number between 0 and 3: ") #hard coded for now. Change this?
            #if we got a digit between 0-3, now we can change the best partition
            if new_best != "C":
                new_best = int(new_best)
                print("Replace old best: ")
                teams_info.print_best_group()
                print("With new best: ")
                teams_info.print_group_num(new_best)
                replace_choice = input("(Y)es or (N)o: ")
                while replace_choice not in ("Y", "y", "N", "n"):
                    replace_choice = input("(Y)es or (N)o: ")
                #TODO input verification
                if replace_choice in ("Y", "y"):
                    teams_info.save_group(new_best)
                    print("Saved")
        elif repeat_choice == "E":
            print ("Evolving a new set of teams")
            teams_info.generate_teams()
            teams_info.print_top_groups(4)
            teams_info.print_best_group()

        if repeat_choice not in ("R", "E", "C"):
            print("Incorrect input. Please try again.")

        
        repeat_choice = input("\nEnter R to replace the current best partition, E to evolve a new set of partitions, or C to continue: ")



    '''
    Main Menu:
    1. Print Current teams to screen (call a print, return to this menu)
    2. Print Unassigned students to screen (call a print, return to this menu)
    3. Create teams manually (Manual Team Menu)
    4. Update student information from spreadsheet. (Update Menu)
    5. Assign individual students (Student Menu)
    6. Export Data (call a function)
    '''

    
if __name__ == '__main__':
    main()




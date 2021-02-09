#!/usr/bin/python3
import genetic as ga
import google_sheets as sheets
from create_partitions import ClassInformation
from schedule import Schedule

class MenuStructure:
    
    def main_menu(self):
        main_choice = "H"
        while main_choice != "Q":
            print("\n\n___________________________________________________________")
            print("MAIN MENU")
            print("(E)volve New Team Partitions")
            print("(M)anually Edit Current Team Configuration")
            print("(S)ave Current Infomation to a File")
            print("(Q)uit")
            print("______________________________________________________________\n")
            main_choice = input("Please enter your choice: ").upper()

            while main_choice not in ("M", "E", "S", "Q"):
                print("Invalid.")
                main_choice = input("Please enter your choice: ").upper()
            if main_choice == "E":
                self.evolve_menu()
            elif main_choice == "M":
                self.manual_edit_menu()


   #END OF MAIN MENU

    def manual_edit_menu(self):
        edit_choice = 'L'

        while edit_choice != "M":
            print("\n\n___________________________________________________________")
            print("MANUAL EDIT MENU")
            print("(P)rint the current team configuration and a list of unassigned students")
            print("(A)dd a student to a team")
            print("(R)emove a student from a team")
            print("Return to (M)AIN MENU")
            print("______________________________________________________________\n")
            edit_choice = input("Please enter your choice: ").upper()

            while edit_choice not in ("P", "A", "R", "M"):
                print("Invalid")
                edit_choice = input("Please enter your choice: ").upper()

            if edit_choice == "P":
                self.partitions.print_best_partition()
                print("\n")
                self.partitions.print_unused()
            
            elif edit_choice == "A":
                print("Students available to add.")
                self.partitions.print_unused(print_numbers=True)
                student = input("\nEnter either the number or name of the student you wish to add:  ")

                if student.isdigit():
                    num = int(student)
                    student = self.partitions.get_unused_student(num)

                #input verification
                while student not in self.partitions.unused_dict:
                    print("Error in input")
                    print("You entered: ", student)
                    student = input("\nEnter either the number or name of the student you wish to add:  ")
                    if student.isdigit():
                        num = int(student)
                        student = self.partitions.get_unused_student(num)

                print("\nYou are adding student: {} with {} available hours".format(student, Schedule.static_count(self.partitions.unused_dict[student])))
                
                choice = "d"
                choice = input("\n Would you like to check against (A)ll teams, or choose a (S)pecific team? ").upper()
                while choice != "X":
                    while choice not in ("A", "S", "X"):
                        choice = input("\nWould you like to check against (A)ll teams, choose a (S)pecific team or e(x)it to the previous menu").upper()

                    if choice == "A":
                        print("Checking availability against all teams.")
                        '''
                        print only common hours > 0, with team member names
                        allow add to group or cancel without adding
                        '''
                        comparison_dict = self.partitions.best_partition.check_student(
                                (student, self.partitions.unused_dict[student]),
                                all_teams= True)
                        count_teams =0
                        for team_name in comparison_dict:
                            common_hours = comparison_dict[team_name].count_bits()
                            if common_hours > 0:
                                count_teams = count_teams+1
                                #TODO add the old availability amount
                                print ("Team {:8}: ({:2}) to ({:2}) {}".format(
                                    team_name, 
                                    self.partitions.best_partition.team_dict[team_name][1].count_bits(),
                                    common_hours, 
                                    list(self.partitions.best_partition.team_dict[team_name][0])))
                        if count_teams == 0:
                            print ("No teams with a common meeting time. Exiting this menu.")
                            choice = "X"
                        else:
                            choice = "R"


                    elif choice == "S":
                        choice = "R"
                        self.partitions.print_best_partition()
                    if choice == "R":
                        #TODO add an exit clause
                        team_name = input("\nPlease enter the name of the team to add {} to. Or X to exit: ".format(student))

                        if team_name in ("X", "x"):
                            choice = "X"
                            continue

                        while (team_name not in self.partitions.best_partition.team_names):
                            print("You entered {}, which is not a team name".format(team_name))
                            team_name = input("Please enter a correct team name or x to exit. ")

                        new_name, new_schedule = self.partitions.best_partition.check_student(
                                (student, self.partitions.unused_dict[student]), 
                                team = team_name)
                        new_team_tuple = (new_name, new_schedule)
                        
                        print("Old Team {}".format(team_name))
                        self.partitions.best_partition.print_team(team_name)
                        print("\nNew Team")
                        self.partitions.best_partition.print_team(new_team_tuple)

                        change_choice=input("\n Confirm change? (Y)es or (N)o: ").upper()
                        
                        if change_choice == "Y":
                            self.partitions.best_partition.change_team(team_name, new_team_tuple)
                            item=self.partitions.unused_dict.pop(student)
                            self.partitions.availability_dict[student]=item
                            print("Team updated")
                            choice = "X"
                        else:
                            print("No changes made")
                            print("\nYou are adding student: {} with {} available hours".format(
                                student, 
                                Schedule.static_count(self.partitions.unused_dict[student])))
                            choice = input("\nWould you like to check against (A)ll teams, a (s)pecific team or e(x)it to the previous menu? ").upper()
                            
                                        
        
    def evolve_menu(self):
        print("\n\n___________________________________________________________")
        print("EVOLUATION MENU")
        print("(P)rint list of recent partitions and current best partion")
        print("(R)eplace the current best partition from the list of recent")
        print("(E)volve a new set of partitions")
        print("Return to (M)AIN MENU")
        print("______________________________________________________________\n")
        
        repeat_choice = input("Please enter your choice: ").upper()

        while repeat_choice != "M":
            #Print
            if repeat_choice == "P":
                self.partitions.print_top_partitions(4)
                self.partitions.print_best_partition(print_numbers=True) #print it simple with nubmers
            #Replace
            elif repeat_choice == "R":
                new_best = input("""Enter 0-3 for number of partition you wish to save
                        (P)rint list of partions and current best
                        Return to EVOLUTION (M)ENU

                        Please enter your choice:""")
                #Print the lists again, ask for the partition number or to continue
                if new_best == "P":
                    self.partitions.print_top_partitions(4)
                    self.partitions.print_best_partition(print_numbers=True) #print it simple with numbers
                    new_best = input("\nEnter 0-3 for number of partition you wish to save\
                            \nReturn to EVOLUTION (M)ENU\n\
                            \nPlease enter your choice: ")
                #Whether we printed or not, choice should now be either 0-3 or C
                while new_best != "M" and (not(new_best.isdigit()) or int(new_best) > 3):
                    if not(new_best.isdigit()):
                        new_best = input("\nEnter 0-3 for number of partition you wish to save\n\
                                Return to EVOLUTION (M)ENU\n\
                                \nPlease enter your choice: ")
                    else:
                        new_best = input("Please enter number between 0 and 3: ") #hard coded for now. Change this?
                #if we got a digit between 0-3, now we can change the best partition
                if new_best != "M":
                    new_best = int(new_best)
                    print("Replace old best: ")
                    self.partitions.print_best_partition(print_number=True) #print with numbers for simplicity
                    print("\nWith new best: ")
                    self.partitions.print_partition_num(new_best)
                    replace_choice = input("(Y)es or (N)o: ")
                    while replace_choice not in ("Y", "y", "N", "n"):
                        replace_choice = input("(Y)es or (N)o: ")
                    #TODO input verification
                    if replace_choice in ("Y", "y"):
                        self.partitions.save_partition(new_best)
                        print("Saved")
            elif repeat_choice == "E":
                print ("Evolving a new set of teams")
                self.partitions.generate_teams()
                self.partitions.print_top_partitions(4)
                self.partitions.print_best_partition(print_numbers=True)

            if repeat_choice not in ("P", "R", "E", "M"):
                print("Incorrect input")
     
            print("\n\n___________________________________________________________")
            print("EVOLUATION MENU")
            print("(P)rint list of recent partitions and current best partion")
            print("(R)eplace the current best partition from the list of recent")
            print("(E)volve a new set of partitions")
            print("Return to (M)AIN MENU")
            print("______________________________________________________________\n")
            
            repeat_choice = input("Please enter your choice: ").upper()

    #End of evolve_menu
           

    def __init__(self):
        #Welcome
        '''
        First menu:
        1. Get names from spreadsheet file. Goes to Branch A
        2. Get names from previous run. Goes to Branch B
        '''
        print ("Welcome to Team Creator")
        print ("Would you like to \n\
                A. Create teams from a spreadsheet of student data \n\
                B. Pull existing team data from a file.")
        input_choice = input("Enter A or B:  ").upper()
        while input_choice not in ("A", "B"):
            input_choice = input ("Please enter only A or B: ").upper()

        '''
        Branch A
        Print spreadsheet info to screen. Change to request file name when needed.
        Pull and store all info from the file.
        Call generate_random_partitions
        '''
        if input_choice == "A":
            #Get the team size, make an object and load from the sheet
            team_size = int(input("How many people would you like in a team? "))
            number_generations = int(input("How many generations would you like to run? "))
            #TODO Input verification

            print("Please wait for file to load")
            self.partitions = ClassInformation(team_size, number_generations)
            print("Running first evolution")
            self.partitions.load_from_sheet()

            #evolve a population and save the first partition as the best
            self.partitions.generate_teams()
            self.partitions.save_partition(0)
        
        '''
        Branch B
        Request file name for previous iteration
        import information
        print information
        
        elif input_choice == 'B':
            #get the file_name
            file_name="team_setup"
            with open(file_name, mode='r', encoding='utf-8') as f:
                #read in the teams
                #load_from_sheet
                
                copy list of avai_dict_keys
                #for team in file
                    for each student in team
                        check studet in copy of avial_keys
                        if in a_dict, add schedule to schedule list, remove studetn from avil_keys
                        if not, if in unused, add schedule to schedule list, move to a_dict
                    get the common count of the team.
                    add team and count to partition
                 save parition to best_partition
                 if any keys left in copy list, move from avail to unused
                 
                 could we have a student in availability_dict not in team?
                 
                 '''

        
        
        self.partitions.print_best_partition()
        print("\n")
        self.partitions.print_unused()

          
if __name__ == '__main__':
    menu = MenuStructure()
    menu.main_menu()




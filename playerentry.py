from tkinter import *
from tkinter import messagebox
import socket
import subprocess
import psycopg2
from psycopg2 import sql
from countdownscreen import CountdownScreen
from player import Player
from transmission import Transmission


class PlayerEntry:
    def __init__(self):
        self.red_entries = []
        self.green_entries = []
        self.players = []
        self.curr_red_row = 0
        self.curr_green_row = 0
        self.all_player_ids = []

    
    def row_is_full(self, entries, row):
        if (entries[row][0].get() and 
            entries[row][1].get() and
            entries[row][2].get()):
            return True
        return False


    def player_id_is_full(self, entries, row):
        if (entries[row][0].get() and
            not(entries[row][1].get()) and
            not(entries[row][2].get())):
            return True
        return False


    def hardware_id_empty(self, entries, row):
        if (entries[row][0].get() and
            not(entries[row][1].get()) and
            entries[row][2].get()):
            return True
        return False


    def readonly_row(self, entries, row):
        entries[row][0].config(state="readonly")
        entries[row][1].config(state="readonly")
        entries[row][2].config(state="readonly")


    def open_database(self):
        #define database connection parameters
        config = {
            'dbname': 'photon'
        }
        try:
            self.conn = psycopg2.connect(**config)
            self.cur = self.conn.cursor()

            #execute a query
            self.cur.execute("SELECT version();")

            #fetch and display the result
            version = self.cur.fetchone()
            print(f"Connected to - {version}")

        except Exception as error:
            print(f"Error connecting to SQL database: {error}")

    
    def query_database(self, id):
        self.cur.execute("SELECT * FROM players;")
        rows = self.cur.fetchall()
        for row in rows:
            if (str(row[0]) == id):
                return str(row[1])
        return ""


    def add_to_database(self, id, name):
        self.cur.execute('''
                INSERT INTO players (id, codename)
                VALUES (%s, %s);
                ''', (id, name))
        self.conn.commit()

    
    # IK THIS IS A HUGE METHOD DW I WILL BREAK IT UP LATER SO ITS MORE READABLE & EFFICIENT - ellie
    def handle_entry_table(self, *args):
        # get current values of current red row
        red_player_id = self.red_entries[self.curr_red_row][0].get()
        red_hardware_id = self.red_entries[self.curr_red_row][1].get()
        red_codename = self.red_entries[self.curr_red_row][2].get()
        transmission = Transmission()

        # check if the whole red row is filled with values
        if (self.row_is_full(self.red_entries, self.curr_red_row)):
            msgToSend = int(red_hardware_id)
            transmission.transmit(msgToSend, 7500)
            # check if id has already been seen
            if (red_player_id in self.all_player_ids):
                # make every entry in row read only so it can't be edited
                self.readonly_row(self.red_entries, self.curr_red_row)
                # move to row below
                self.curr_red_row = self.curr_red_row + 1
                # un-disable players id entry field of new row & move mouse to field
                self.red_entries[self.curr_red_row][0].config(state='normal')
                self.red_entries[self.curr_red_row][0].focus_set()
                # add to players
                self.players.append(Player(red_player_id, red_hardware_id, red_codename, "red"))

            # if id has not been seen before:
            else:
                self.add_to_database(str(red_player_id), str(red_codename))
                
                # log that id has been seen before
                self.all_player_ids.append(red_player_id)
                # make whole row readonly
                self.readonly_row(self.red_entries, self.curr_red_row)
                # move to row below
                self.curr_red_row = self.curr_red_row + 1
                # un-disable player id entry field of new row & move mouse to field
                self.red_entries[self.curr_red_row][0].config(state='normal')
                self.red_entries[self.curr_red_row][0].focus_set()

        
        # check if player id field is full and others are empty
        elif (self.player_id_is_full(self.red_entries, self.curr_red_row)):
            # unlock the codename
            self.red_entries[self.curr_red_row][2].config(state='normal')
            
            # query database for id
            found = self.query_database(str(red_player_id))

            if (found != ""):
                # log that player id has been seen
                self.all_player_ids.append(red_player_id)
                # fill in codename field
                self.red_entries[self.curr_red_row][2].insert(0, found)
                # lock in player id and codename, move focus to hardware id field 
                self.red_entries[self.curr_red_row][0].config(state='readonly')
                self.red_entries[self.curr_red_row][1].config(state='normal')
                self.red_entries[self.curr_red_row][2].config(state='readonly')
                self.red_entries[self.curr_red_row][1].focus_set()
            # player was not found in database
            else:
                # move mouse to codename field
                self.red_entries[self.curr_red_row][2].focus_set()
        
        # check if all fields are full except for harware id
        elif (self.hardware_id_empty(self.red_entries, self.curr_red_row)):
            # unlock hardware id and move mouse to it
            self.red_entries[self.curr_red_row][1].config(state='normal')
            self.red_entries[self.curr_red_row][1].focus_set()


        # exact same thing except for green entries, maybe will find a way to pass params so i dont repeat
        # get current values of current green row
        green_player_id = self.green_entries[self.curr_green_row][0].get()
        green_hardware_id = self.green_entries[self.curr_green_row][1].get()
        green_codename = self.green_entries[self.curr_green_row][2].get()

        # check if the whole green row is filled with values
        if (self.row_is_full(self.green_entries, self.curr_green_row)):
            msgToSend = int(green_hardware_id)
            transmission.transmit(msgToSend, 7500)
            
            # check if id has already been seen
            if (green_player_id in self.all_player_ids):
                # make every entry in row read only so it can't be edited
                self.readonly_row(self.green_entries, self.curr_green_row)
                # move to row below
                self.curr_green_row = self.curr_green_row + 1
                # un-disable player id entry field of new row & move mouse to field
                self.green_entries[self.curr_green_row][0].config(state='normal')
                self.green_entries[self.curr_green_row][0].focus_set()
                # add to players
                self.players.append(Player(green_player_id, green_hardware_id, green_codename, "green"))

            # if id has not been seen before:
            else:
                self.add_to_database(str(green_player_id), str(green_codename))
                
                # log that id has been seen before
                self.all_player_ids.append(green_player_id)
                # make whole row readonly
                self.readonly_row(self.green_entries, self.curr_green_row)
                # move to row below
                self.curr_green_row = self.curr_green_row + 1
                # un-disable player id entry field of new row & move mouse to field
                self.green_entries[self.curr_green_row][0].config(state='normal')
                self.green_entries[self.curr_green_row][0].focus_set()

        
        # check if player id field is full and others are empty
        elif (self.player_id_is_full(self.green_entries, self.curr_green_row)):
            # unlock the codename
            self.green_entries[self.curr_green_row][2].config(state='normal')
            
            # query database for id
            found = self.query_database(str(green_player_id))

            if (found != ""):
                # log that player id has been seen
                self.all_player_ids.append(green_player_id)
                # fill in codename field
                self.green_entries[self.curr_green_row][2].insert(0, found)
                # lock in player id and codename, move focus to hardware id field 
                self.green_entries[self.curr_green_row][0].config(state='readonly')
                self.green_entries[self.curr_green_row][1].config(state='normal')
                self.green_entries[self.curr_green_row][2].config(state='readonly')
                self.green_entries[self.curr_green_row][1].focus_set()
            # player was not found in database
            else:
                # move mouse to codename field
                self.green_entries[self.curr_green_row][2].focus_set()
        
        # check if all fields are full except for harware id
        elif (self.hardware_id_empty(self.green_entries, self.curr_green_row)):
            # unlock hardware id and move mouse to it
            self.green_entries[self.curr_green_row][1].config(state='normal')
            self.green_entries[self.curr_green_row][1].focus_set()


    def capture_text(self, event):

        self.captured_text = self.net_entry_field.get()  # Get the text from the Entry widget

        print(f"Using IP: {self.captured_text}")  # Process or use the text as needed

        with open("network.txt", "w") as file:

            file.write(self.captured_text)
      
        self.net_entry_field.place_forget()



    def show_network_entry_field(self):
        
        # Pack the Entry widget to show it when the button is clicked

        self.net_entry_field.place(x=610, y=558)

        self.net_entry_field.focus()  # Set focus on the entry field

        self.net_entry_field.bind('<Return>', self.capture_text)


    def change_network(self):

        print("Changing network...")
        for i in range(3):
            print(2)

        self.show_network_entry_field()

    
    def clear_entries(self, *args):
        print("Clearing entries...")
        # Clear all red team entries
        for row in self.red_entries:
            for entry in row:
                entry.config(state='normal')  # Unlock the entry field in case it's disabled
                entry.delete(0, END)  # Clear the content
                entry.config(state='disabled') # need to disable it again so it matching beginning
        
        # Clear all green team entries:
        for row in self.green_entries:
            for entry in row:
                entry.config(state='normal') # Unlock the entry field in case it's disabled
                entry.delete(0, END) # Clear the content
                entry.config(state='disabled')

        # Reset current rows to 0, so it starts from the first row again
        self.curr_red_row = 0
        self.curr_green_row = 0
        # also need to unlock row 0 col 0
        self.red_entries[self.curr_red_row][0].config(state='normal')
        self.green_entries[self.curr_green_row][0].config(state='normal')
        # and also set focus again
        self.red_entries[self.curr_red_row][0].focus_set()

        # Optionally, you can also reset the IDs list if you want
        self.all_player_ids.clear()
           

    def start_game(self, *args):
        #should i destroy the root? it's prob fine 
        #if i dont destroy the root then there's going to be 2 pages open
        self.root.destroy()
        countdown_screen = CountdownScreen(self.players)
        countdown_screen.run()
    

    def create_widgets(self):
        # create main window
        self.root = Tk()
        self.root.title("Entry Terminal")
        self.root.configure(background='gray17')
        self.root.geometry("1300x800")

        # create title label
        title = Label(self.root, 
                      bg='gray17', 
                      fg='DeepSkyBlue2', 
                      font=("Corier New", 16, "bold"), 
                      text="ADD PLAYERS TO GAME")
        title.place(x=620, y=10)

        # create red frame
        red_frame = LabelFrame(self.root, 
                               bg='red4', 
                               fg='RosyBrown1', 
                               labelanchor="n", 
                               height="500", 
                               width="415", 
                               font=("Corier New", 10, "bold"), 
                               text="RED TEAM")
        red_frame.place(x=350, y=50)
        red_frame.grid_propagate(False)
        
        # create red frame labels
        r_player_id_label = Label(red_frame, 
                                   bg='red4', 
                                   fg='RosyBrown1', 
                                   font=("Corier New", 8), 
                                   text='PLAYER ID')
        r_player_id_label.grid(row=0, column=1, padx=5, pady=1)
        r_hardware_id_label = Label(red_frame, 
                                    bg='red4', 
                                    fg='RosyBrown1',
                                    font=("Corier New", 8), 
                                    text='HARDWARE ID')
        r_hardware_id_label.grid(row=0, column=2, padx=5, pady=1)
        r_name_label = Label(red_frame,
                             bg='red4', 
                             fg='RosyBrown1',
                             font=("Corier New", 8), 
                             text='CODENAME')
        r_name_label.grid(row=0, column=3, padx=5, pady=1)

        # create green frame
        green_frame = LabelFrame(self.root,
                                 bg='dark green',
                                 fg='PaleGreen1',
                                 labelanchor="n",
                                 height="500",
                                 width="415", 
                                 font=("Corier New", 10, "bold"), 
                                 text="GREEN TEAM")
        green_frame.place(x=765, y=50)
        green_frame.grid_propagate(False)

        # create green frame labels
        g_player_id_label = Label(green_frame,
                                  bg='dark green',
                                  fg='DarkSeaGreen1',
                                  font=("Corier New", 8),
                                  text='PLAYER ID')
        g_player_id_label.grid(row=0, column=1, padx=5, pady=1)
        g_hardware_id_label = Label(green_frame,
                                    bg='dark green',
                                    fg='DarkSeaGreen1',
                                    font=("Corier New", 8),
                                    text='HARDWARE ID')
        g_hardware_id_label.grid(row=0, column=2, padx=5, pady=1)
        g_name_label = Label(green_frame,
                             bg='dark green',
                             fg='DarkSeaGreen1',
                             font=("Corier New", 8), 
                             text='CODENAME')
        g_name_label.grid(row=0, column=3, padx=5, pady=1)

        # create entry tables
        rows = 15
        cols = 3

        for row in range(rows):
            red_row = []
            green_row = []
            r_idx_label = Label(red_frame, bg="red4", fg="RosyBrown1", text=str(row+1))
            g_idx_label = Label(green_frame, bg="dark green", fg="pale green", text=str(row+1))
            r_idx_label.grid(row=row+1, column=0, padx=5, pady=3)
            g_idx_label.grid(row=row+1, column=0, padx=5, pady=3)
            for col in range (cols):
                r_entry = Entry(red_frame, bg="LavenderBlush2", fg="red4", disabledbackground="indian red", justify="center")
                g_entry = Entry(green_frame, bg="DarkSeaGreen1", fg="dark green", disabledbackground="PaleGreen4", justify="center")
                r_entry.grid(row=row+1, column=col+1, padx=5, pady=3)
                g_entry.grid(row=row+1, column=col+1, padx=5, pady=3)
                if col <= 1:
                    r_entry.configure(width=6)
                    g_entry.configure(width=6)
                if col !=0 or row != 0:
                    r_entry.configure(state='disabled')
                    g_entry.configure(state='disabled')
                else:
                    r_entry.focus_set()
                red_row.append(r_entry)
                green_row.append(g_entry)
            self.red_entries.append(red_row)
            self.green_entries.append(green_row)

        # create network entry field
        self.net_entry_field = Entry(self.root, font=("Arial", 20), bg='white')

        # create buttons
        network_button = Button(self.root, 
                                activebackground="DeepSkyBlue3", 
                                activeforeground="snow",
                                disabledforeground="DeepSkyBlue3",
                                bg="DeepSkyBlue2",
                                fg="LightBlue1",
                                text="CHANGE NETWORK",
                                height=2,
                                width=15,
                                command=self.change_network)
        network_button.place(x=690, y=600)

        clear_button = Button(self.root, 
                               activebackground="DeepSkyBlue3", 
                               activeforeground="snow",
                               disabledforeground="DeepSkyBlue3",
                               bg="DeepSkyBlue2",
                               fg="LightBlue1",
                               text="<F12>\nCLEAR\nPLAYERS",
                               height=5,
                               width=9,
                               command=self.clear_entries)
        clear_button.place(x=100, y=50)

        start_button = Button(self.root, 
                              activebackground="DeepSkyBlue3", 
                              activeforeground="snow",
                              disabledforeground="DeepSkyBlue3",
                              bg="DeepSkyBlue2",
                              fg="LightBlue1",
                              text="<F5>\nSTART\nGAME",
                              height=5,
                              width=9,
                              command=self.start_game)
        start_button.place(x=100, y=200)

        # bind keys for buttons & entries
        self.root.bind("<Return>", self.handle_entry_table)
        self.root.bind("<F5>", self.start_game)
        self.root.bind("<F12>", self.clear_entries)


    # run player entry screen
    def run(self):
        self.create_widgets()
        self.open_database()
        self.root.mainloop()

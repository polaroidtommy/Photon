from tkinter import *
import socket
import multiprocessing
from transmission import Transmission


class GameScreen:
    def __init__(self, players):
        self.root = None
        self.players = players
        
        #initializes bind and starts multiprocess for listen function
        self.UDPServerSocketReceive = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.UDPClientSocketTransmit = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        with open("network.txt", "r") as file:
            localIp = file.read()

        clientAddressPort   = (localIp, 7501)
        self.UDPServerSocketReceive.bind(clientAddressPort)
        process = multiprocessing.Process(target=self.listen)
        process.start()
        

    def listen(self):
        bufferSize  = 1024
        with open("network.txt", "r") as file:
            localIp = file.read()

        serverAddressPort   = (localIp, 7500)

        #starting game
        transmission = Transmission()
        transmission.transmit(202, 7500)

        received_data = ' '
        while received_data != '202':
            received_data, address = self.UDPServerSocketReceive.recvfrom(bufferSize)
            received_data = received_data.decode('utf-8')
            print ("Received from traffic generator: " + received_data)
            player_hit = received_data.split(":")
            message = player_hit[1]
            self.UDPClientSocketTransmit.sendto(str.encode(str(message)), serverAddressPort)
            print ('')

    def create_widgets(self):
        self.root = Tk()
        self.root.title("Game Screen")
        self.root.configure(background='gray17')
        self.root.geometry("1300x800")

        # update geometry
        self.root.update()

        # calculate dimensions for the frames
        frame_width = int(self.root.winfo_width() * 0.333) 
        frame_height = self.root.winfo_height()

        # red teams frame
        red_frame = LabelFrame(self.root,
                               bg='red4',
                               fg='RosyBrown1',
                               labelanchor="n",
                               height=frame_height,
                               width=frame_width,
                               font=("Courier New", 10, "bold"),
                               text="RED TEAM")
        red_frame.place(x=0, y=0)

        # green teams frame
        green_frame = LabelFrame(self.root,
                                 bg='dark green',
                                 fg='PaleGreen1',
                                 labelanchor="n",
                                 height=frame_height,
                                 width=frame_width,
                                 font=("Courier New", 10, "bold"),
                                 text="GREEN TEAM")
        green_frame.place(x=int(self.root.winfo_width() * 0.666), y=0)
        # add red team names 
        r = 0
        g = 0
        for player in (self.players):
            codename = player.codename
            if player.team == "red":
                player_label = Label(red_frame,
                                    bg='red4',
                                    fg='RosyBrown1',
                                    font=("Courier New", 8),
                                    text=f"{codename}")
                player_label.place(x=10, y=30 + (r * 20))
                r = r + 1 
            else:
                player_label = Label(green_frame,
                                    bg='dark green',
                                    fg='RosyBrown1',
                                    font=("Courier New", 8),
                                    text=f"{codename}")
                player_label.place(x=10, y=30 + (g * 20)) 
                g = g + 1

        

    def run(self):
        self.create_widgets()
        self.root.mainloop()


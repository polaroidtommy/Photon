import socket


class Transmission():
    def __init__(self):
        self.UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    #function to not have to type this out whenever we want to transmit hardware and codes
    def transmit(self, message, port):
       with open("network.txt", "r") as file:
           localIp = file.read()
       clientAddressPort = (localIp, port)
       
        
       self.UDPClientSocket.sendto(str.encode(str(message)), clientAddressPort)



       
# load additional Python modules
import socket
import threading
import time
from Constants import Constants

class Client(threading.Thread):

    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter


    def runClient(self):

        # create TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # retrieve local hostname
        local_hostname = socket.gethostname()

        # get fully qualified hostname
        local_fqdn = socket.getfqdn()

        # get the according IP address
        ip_address = socket.gethostbyname(local_hostname)

        # bind the socket to the port 23456, and connect
        server_address = (ip_address, 2169)
        sock.connect(server_address)
        print("connecting to %s (%s) with %s" % (local_hostname, local_fqdn, ip_address))

        # define example data to be sent to the server
        while True:
            try:
                new_data = (str(Constants.x) + "\n").encode("utf-8")
                sock.sendall(new_data)
                rec = sock.recv(1024)
            except:
                print("epic sad")
                break

    def startThread(self):
        while True:
            try:
                self.runClient()
            except ConnectionRefusedError:
                print("Couldn't Connect, retrying in 1 second")
                time.sleep(1)


    def run(self):
        self.startThread()
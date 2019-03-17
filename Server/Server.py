from sys import argv

from CameraServer import CameraServer

# Set global variables
starting_port = 5801
num_sockets = 4

# Load command line arguments
for arg in argv[1:]:
    arg = arg.split('=')
    if arg[0] == 'port' or arg[0] == 'sp':
        starting_port = arg[1]
    elif arg[0] == 'sockets' or arg[0] == 'ns':
        num_sockets = int(arg[1])
    else:
        print("Invalid Argument:", arg[0])

# Method that starts the ServerFolde system
def startStreamer():
    # Create and start the camera threads
    # These threads cannot die.  They now only need to be started once.

    # Start the camera servers
    for i in range(num_sockets):
        CameraServer(starting_port + i).start()


# Start this flaming pile of garbage
startStreamer()

import sys

import cv2

from CameraServer import CameraServer

# Method that starts the ServerFolde system
def startStreamer():

    # Create and start the camera threads
    # These threads cannot die.  They now only need to be started once.

    # Get number of sockets from command line
    try:
        num_sockets = int(sys.argv[1])
    except IndexError:
        num_sockets = 4
    except ValueError:
        print("Epic Sad: First command line argument is not an integer")
        sys.exit(1)

    # Get starting port from command line
    try:
        starting_port = int(sys.argv[2])
    except IndexError:
        starting_port = 1111
    except ValueError:
        print("Epic Sad: Second command line argument is not an integer")
        sys.exit(1)

    # Start the camera servers
    for i in range(num_sockets):
        CameraServer(starting_port + i).start()


# Start this flaming pile of garbage
startStreamer()

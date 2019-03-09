# RoyalVision-DeepSpace

### Dependencies
* Numpy
* OpenCV 3.0

### RoyalVision Example Server
To launch the RoyalVision example server, naviage into the RoyalVision-Deepspace
directory, and run `python Vision/Server/Server.py`.

The example server accepts up to two command line arguments:
1. Number of sockets to open.
1. Port number of the first socket.

Neither of these arguments are required. The default for the first argument is 4, and
the default for the second argument is 1111.

For each socket, the server will open a window where it displays the image feed
it receives from the client.

### RoyalVision Client
To launch the royal vision client, navigate into the RoyalVision-Deepspace directory,
and run `python Vision/Client/Main.py`.

The client accepts up to three command line arguments:
1. Port number
1. Camera ID
1. Compression rate

Again, none of these arguments are required. The default port number is 1111, the
default camera ID is 0, and the default compression rate is 7.

The client uses OpenCV to identify any visible pieces of retroreflective tape, and
marks the center point between the two pieces with a yellow circle. If it can only
identify one piece of retroreflective tape, it will estimate the position of the other
and calculate the midpoint. Finally, the client will use JPEG compression to reduce the
size of the image, and send it over the socket on the specified port.

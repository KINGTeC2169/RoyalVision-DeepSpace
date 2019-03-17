# RoyalVision-DeepSpace

### Dependencies
* Numpy
* OpenCV 3.0

### RoyalVision Example Server
To launch the RoyalVision example server, naviagte into the RoyalVision-Deepspace
directory, and run `python Server/Server.py`.

The example server accepts two command line arguments:
1. Port number of the first socket.
1. Number of sockets to open.

To pass the first parameter, use either `port=value` or `sp=value`. To pass the second
parameter, use either `sockets=value` or `ns=value`. An example command would be
`python Server/Server.py ns=3 sp=1111`.

The starting port defaults to `5801` and the number of sockets defaults to `4`.

For each socket, the server will open a window where it displays the image feed
it receives from the client. The port of the first socket will be the starting port,
and the port of each following socket will be 1 greater than the last. If we opened
3 sockets with a starting port of `1111`, the sockets' ports would be `1111`, `1112`,
and `1113`.

### RoyalVision Client
To launch the royal vision client, navigate into the RoyalVision-Deepspace directory,
and run `Main.py`.

The client accepts three command line arguments:
1. TCP IP
1. TCP Port
1. Camera Port
1. Compression rate

To pass the first parameter, use `ip=value`. To pass the second parameter, use either
`port=value` or `p=value`. To pass the third parameter, use either `camera=value` or
`cam=value`. To pass the fourth parameter, use either `compression=value` or
`cr=value`. An example command would be `python Main.py p=2000 cr=12`.

The default ip is `DS2169.local`, the default port is `5801`, the default camera port
is `0`, and the default compression rate is `7`.

The client uses OpenCV to identify any visible pieces of retroreflective tape, and
marks the center point between the two pieces with a yellow circle. If it can only
identify one piece of retroreflective tape, it will estimate the position of the other
and calculate the midpoint. Finally, the client will use JPEG compression to reduce the
size of the image, and send it over the socket on the specified port.

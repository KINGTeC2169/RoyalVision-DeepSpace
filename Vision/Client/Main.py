import socket
import sys
from typing import List, Any

import cv2
import numpy
import numpy as np

from Constants import Constants
from Vision.Client.Client import Client
from Vision.Client.MathHandler import MathHandler

from enum import Enum

#Enum for tilt that clear up need for multiple booleans
class Tilt(Enum):
    LEFT = "Left"
    RIGHT = "Right"
    STRAIGHT = "Straight"


# Method for 1 visible rectangle.  Accepts 1 contour parameter.
def calculateRectangle(contour):

    # Set up our return variables
    area = cv2.contourArea(contour)

    # Create a bounding rectangle from the largest contour
    rect = cv2.minAreaRect(contour)

    # Take said bounding rectangle and simplify it onto integer coordinates.
    box = cv2.boxPoints(rect)
    box = np.int0(box)

    # Check if any of the points on the bounding box fall on the edge of the image.
    # If this is the case, the target is partially off-screen, and indicate to the
    # InRange variables that this is the case.
    points: List[Any] = []

    # OpenCV doesn't register the BoxPoints object as iterable, so this will fire a false warning on
    # PyCharm.  The next line disables that warning.  If you aren't in PyCharm, it won't do anything.

    inRangeX = True
    # noinspection PyTypeChecker
    for point in box:
        if point[0] <= 0 or point[0] >= frame.shape[1]:
            inRangeX = False

        points.append(point)

    # Sort the points by the slope of the line generated between them and (0,0)
    # This will allow us to determine where each point lies on the rectangle for the center-point
    # estimation process that will follow
    points.sort(key=m.getX, reverse=True)

    # Create arrays that will hold the points about the lines that connect the corners of the bounding
    # box to estimate the center point
    line1 = []
    line2 = []

    # Append the appropriate points to their respective lines
    # Since the points array is already sorted by slope relative to (0,0), and we know the rectangle
    # Has 4 corner points, append the points with the largest and smallest slopes to one line, and the
    # two remaining points to the other.  This will almost certainly yield two lines running in an X pattern
    # across the bounding box to find the estimated center point of the contour, accounting for the shift
    # in perspective, which is the reason this system required cross-lines in the first place and couldn't
    # just simply use the width and height of the contour
    line1.append(points[0])
    line1.append(points[3])
    line2.append(points[1])
    line2.append(points[2])

    line1.sort(key=m.getY, reverse=True)
    topPoint = line1[0]
    bottomPoint = line1[1]

    slope = m.getSlopeDuo(points[0], points[3])
    if slope is None or slope is 0.0 or not inRangeX:
        boundTilt = Tilt.STRAIGHT
    elif slope < 0:
        boundTilt = Tilt.LEFT
    elif slope > 0:
        boundTilt = Tilt.RIGHT
    else:
        boundTilt = Tilt.STRAIGHT

    # Using some basic algebra, find the intersection point of the two lines and return that point
    # to variables x and y respectively
    if boundTilt == Tilt.STRAIGHT:
        # calculate moments for each contour
        M = cv2.moments(contour)

        # calculate x,y coordinate of center
        x = int(M["m10"] / M["m00"])
        y = int(M["m01"] / M["m00"])

        boundCent = [x, y]

        if c.isDebug():
            cv2.circle(frame, (x, y), 5, (255, 255, 255), -1)


    else:
        x, y = m.line_intersection(line1, line2)
        boundCent = [x, y]

        if c.isDebug():
            cv2.line(frame, (points[0][0], points[0][1]), (points[3][0], points[3][1]), (255, 0, 255), 2)
            cv2.circle(frame, (points[0][0], points[0][1]), 5, (255, 0, 0), -1)
            cv2.circle(frame, (points[3][0], points[3][1]), 5, (255, 255, 255), -1)
    diff = (topPoint - bottomPoint)

    diff = np.math.sqrt(diff[0] * diff[0] + diff[1] * diff[1])

    return bottomPoint, topPoint, boundCent, area, boundTilt, diff



def handleOneRectangle(contour):
    top1, bottom1, cent1, size1, tilt1, lenTilt1 = calculateRectangle(contour)
    if tilt1 is Tilt.LEFT:
        if c.getDebug():
            cv2.line(frame, (top1[0], top1[1]), (int(top1[0] + (4 * lenTilt1 / 5.5)), int(top1[1])), (0, 255, 0), 3)
        return top1[0] + (4 * lenTilt1 / 5.5)
    elif tilt1 is Tilt.RIGHT:
        if c.getDebug():
            cv2.line(frame, (top1[0], top1[1]), (int(top1[0] - (4 * lenTilt1 / 5.5)), int(top1[1])), (0, 255, 0), 3)
        return top1[0] - (4 * lenTilt1 / 5.5)
    return frame.shape[1]

# Method for 2 visible rectangles.  Accepts two contour parameters.
def handleTwoRectangles(contour1, contour2):
    top1, bottom1, cent1, size1, tilt1, lenTilt1 = calculateRectangle(contour1)
    top2, bottom2, cent2, size2, tilt2, lenTilt2 = calculateRectangle(contour2)

    if c.getDebug():
        font = cv2.FONT_HERSHEY_PLAIN
        cv2.putText(frame, tilt1.value, (int(cent1[0]), int(cent1[1])), font,2.0, (255,255,255), lineType=16)
        cv2.putText(frame, tilt2.value, (int(cent2[0]), int(cent2[1])), font, 2.0, (255, 255, 255), lineType=16)
        cv2.putText(frame, str(int((frame.shape[1]/2)-abs(cent1[0]))), (int(cent1[0]), int(cent1[1]) + 30), font,2.0, (255,255,255), lineType=16)
        cv2.putText(frame, str(int((frame.shape[1]/2)-abs(cent2[0]))), (int(cent2[0]), int(cent2[1]) + 30), font, 2.0, (255, 255, 255), lineType=16)

    if ((tilt1 is Tilt.RIGHT and tilt2 is Tilt.LEFT) and (cent1[0] < cent2[0])) or \
            ((tilt1 is Tilt.LEFT and tilt2 is Tilt.RIGHT) and (cent1[0] > cent2[0])):
            if size1 != size2:
                if abs((frame.shape[1]/2)-abs(cent1[0])) < abs((frame.shape[1]/2)-abs(cent2[0])) :
                    # One Rectangle Calculations on Rectangle 1
                    return handleOneRectangle(contour1)
                else:
                    # One Rectangle Calculations on Rectangle 2
                    return handleOneRectangle(contour2)
            else:
                if size1 > size2:
                    # One Rectangle Calculations on Rectangle 1
                    return handleOneRectangle(contour1)
                else:
                    # One Rectangle Calculations on Rectangle 2
                    return handleOneRectangle(contour2)
    else:

        try:

            if tilt1 is not Tilt.STRAIGHT and tilt2 is not Tilt.STRAIGHT:
                x, y = m.line_intersection([top1, bottom2], [top2, bottom1])
                return x
            else:
                if (tilt1 is Tilt.LEFT and cent1[0] < cent2[0]) or (tilt2 is Tilt.LEFT and cent2[0] < cent1[0]):
                    x = (cent1[0] + cent2[0]) / 2
                    y = (cent1[1] + cent2[1]) / 2
                    return x
                else:
                    if tilt1 is not Tilt.STRAIGHT:
                        return handleOneRectangle(contour1)
                    else:
                        return handleOneRectangle(contour2)
        except:
            pass
    return 0

def getYaw(contours):
    if len(contours) is 0:
        return frame.shape[1] / 2
        # Return information telling the system not to move on regard of the lack of rectangles
        # Return <0,0>
    elif len(contours) is 1:
        # Feed the handle method the largest contour
        top, bottom, cent, size, tilt, diff = calculateRectangle(contours[0])
        return handleOneRectangle(contours[0])
    else:
        # Feed the handle method the two largest contours
        return handleTwoRectangles(contours[0], contours[1])

if __name__ == '__main__':

    # Create instances of MathHandler class and Constants classes.  These will keep all of the numbers
    # and calculations of of this class so that this space can be dedicated to the pipeline.  Functions and
    # constants will, as a result, have their own dedicated space for editing and optimization in their respective
    # classes
    m = MathHandler()
    c = Constants()

    # Read the values of the constants, since they may have changed as the tuning system may have changed the
    # CSV that stores the values shared by the programs
    c.readValues()

    # Create VideoCapture object to grab frames from the USB Camera as color matrices
    cap = cv2.VideoCapture(0)
    client = Client(2, "Thread", 1)

    client.start()

    sock = socket.socket()

    # Set those constants for easy access
    TCP_IP = '127.0.0.1'

    # Grab the port number from the command line
    try:
        TCP_PORT = int(sys.argv[1])
    except IndexError:
        print("Epic Sad: Expected a port number as a command line argument")
        sys.exit(1)
    except ValueError:
        print("Epic Sad: Port number is not an integer")
        sys.exit(1)


    # Connect to the socket with the previous information
    print("Connecting to Socket")
    try:
        sock.connect((TCP_IP, TCP_PORT))
    except ConnectionRefusedError:
        print("Epic Sad: Make sure to run the server and disable your firewall")
        sys.exit(1)

    # Enable instant reconnection and disable timeout system
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    while True:
        # Read a frame from the camera
        ret, frame = cap.read()

        # Convert the frame to HSV Colorspace for filtering
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Convert the HSV Image into a bitmap mask using the two arrays defined from tuning
        mask = cv2.inRange(hsv, c.lowArray, c.highArray)

        # Find contours in the mask image and save to the contours array
        contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Iterate through the contours array, and remove anything that doesn't pass the size threshold
        bigArrays = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 1500:
                bigArrays.append(cnt)
        contours = bigArrays

        # Sort the arrays by size, and then take the largest array.
        # This solves any sub-selections, or large static in the image.
        contoursSorted = sorted(contours, key=lambda contourArea: cv2.contourArea(contourArea))
        contoursSorted.reverse()
        contours = contoursSorted

        yaw = getYaw(contours)
        Constants.x = ((yaw-frame.shape[1]/2)/(frame.shape[1]/2))
        cv2.circle(frame, (int(yaw), int(480/2)), 15, (0, 255, 255), thickness=2)

        # C R O N C H   that image down to half size
        newX, newY = frame.shape[1] * .5, frame.shape[0] * .5
        frame = cv2.resize(frame, (int(newX), int(newY)))

        # C R O N C H   that image down to extremely compressed JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 7]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)

        # Encode that JPEG string into a NumPy array for compatibility on the other side
        data = numpy.array(imgencode)

        # Turn NumPy array into a string so we can ship er' on over the information superhighway
        stringData = data.tostring()

        # Send the size of the data for efficient unpacking
        sock.send(str(len(stringData)).ljust(16).encode())

        # Might as well send the actual data while we're sending things
        sock.send(stringData)

        # If in debug mode, show the image.  If not, keep this disabled, as it slows down the program
        # significantly
        if c.isDebug():
            cv2.imshow("frame", frame)

        # Mandatory break statement that will trigger a clean shutdown of the program upon the ESC key being
        # pressed.  Using this method to stop the program is recommended since OpenCV leaves windows hanging and
        # camera streams open if the program is forcibly quit.
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break

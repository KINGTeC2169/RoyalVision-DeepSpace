import time
from typing import List, Any

import cv2
import numpy as np

from Constants import Constants
from Vison.MathHandler import MathHandler

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

    return topPoint, bottomPoint, boundCent, area, boundTilt


def handleOneRectangle(contour):
    cv2.drawContours(frame, contour, -1, (0, 0, 255), 3)
    pass

# Method for 2 visible rectangles.  Accepts two contour parameters.
def handleTwoRectangles(contour1, contour2):
    top1, bottom1, cent1, size1, tilt1 = calculateRectangle(contour1)
    top2, bottom2, cent2, size2, tilt2 = calculateRectangle(contour2)

    font = cv2.FONT_HERSHEY_PLAIN
    # cv2.putText(frame, tilt1.value, (int(cent1[0]), int(cent1[1])), font,2.0, (255,255,255), lineType=16)
    # cv2.putText(frame, tilt2.value, (int(cent2[0]), int(cent2[1])), font, 2.0, (255, 255, 255), lineType=16)
    # cv2.putText(frame, str(int((frame.shape[1]/2)-abs(cent1[0]))), (int(cent1[0]), int(cent1[1]) + 30), font,2.0, (255,255,255), lineType=16)
    # cv2.putText(frame, str(int((frame.shape[1]/2)-abs(cent2[0]))), (int(cent2[0]), int(cent2[1]) + 30), font, 2.0, (255, 255, 255), lineType=16)

    if ((tilt1 is Tilt.RIGHT and tilt2 is Tilt.LEFT) and (cent1[0] < cent2[0])) or \
            ((tilt1 is Tilt.LEFT and tilt2 is Tilt.RIGHT) and (cent1[0] > cent2[0])):
            if size1 != size2:
                if abs((frame.shape[1]/2)-abs(cent1[0])) < abs((frame.shape[1]/2)-abs(cent2[0])) :
                    # One Rectangle Calculations on Rectangle 1
                    handleOneRectangle(contour1)
                else:
                    # One Rectangle Calculations on Rectangle 2
                    handleOneRectangle(contour2)
            else:
                if size1 > size2:
                    # One Rectangle Calculations on Rectangle 1
                    handleOneRectangle(contour1)
                else:
                    # One Rectangle Calculations on Rectangle 2
                    handleOneRectangle(contour2)
    else:

        try:

            if tilt1 is not Tilt.STRAIGHT and tilt2 is not Tilt.STRAIGHT:
                x, y = m.line_intersection([top1, bottom2], [top2, bottom1])
                cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 255), -1)
            else:
                x = (cent1[0] + cent2[0]) / 2
                y = (cent1[1] + cent2[1]) / 2
                cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 255), -1)

        except:
            print("Rectangle is Not Correct")
            cv2.imwrite("images/"+str(time.time()) + ".jpg", frame)

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
    cap = cv2.VideoCapture(1)

    while True:

        # Read a frame from the camera
        ret, frame = cap.read()

        # Convert the frame to HSV Colorspace for filtering
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Convert the HSV Image into a bitmap mask using the two arrays defined from tuning
        mask = cv2.inRange(hsv, c.lowArray, c.highArray)

        # Find contours in the mask image and save to the contours array
        unpack, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        # Iterate through the contours array, and remove anything that doesn't pass the size threshold
        bigArrays = []
        for cnt in contours:
            if cv2.contourArea(cnt) > 2000:
                bigArrays.append(cnt)
        contours = bigArrays

        # Sort the arrays by size, and then take the largest array.
        # This solves any sub-selections, or large static in the image.
        contoursSorted = sorted(contours, key=lambda contourArea: cv2.contourArea(contourArea))
        contoursSorted.reverse()
        contours = contoursSorted

        if len(contours) is 0:
            pass
            # Return information telling the system not to move on regard of the lack of rectangles
            # Return <0,0>
        elif len(contours) is 1:
            # Feed the handle method the largest contour
            top, bottom, cent, size, tilt = calculateRectangle(contours[0])
            handleOneRectangle(contours[0])
        else:
            # Feed the handle method the two largest contours
            handleTwoRectangles(contours[0], contours[1])

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

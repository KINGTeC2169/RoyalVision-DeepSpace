from typing import List, Any

import cv2
import numpy as np

from Constants import Constants
from Vison.MathHandler import MathHandler

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
            if cv2.contourArea(cnt) > 2000:
                bigArrays.append(cnt)
        contours = bigArrays
        print(cv2.contourArea(cnt))


        # Try-Catch loop here to handle instances where no rectangles are found.
        # In this case, the system is told not to move
        try:



            # Variables for determining if the target is partially off-screen on any axis
            inRangeY = True
            inRangeX = True

            # Sort the arrays by size, and then take the largest array.
            # This solves any sub-selections, or large static in the image.
            contoursSorted = sorted(contours, key=lambda contourArea: cv2.contourArea(contourArea))
            contoursSorted.reverse()
            #cnt = contoursSorted[0]
            for cnt in contours:
                # Create a bounding rectangle from the largest contour
                rect = cv2.minAreaRect(cnt)

                # Take said bounding rectangle and simplify it onto integer coords.
                box = cv2.boxPoints(rect)
                box = np.int0(box)

                # Check if any of the points on the bounding box fall on the edge of the image.
                # If this is the case, the target is partially off-screen, and indicate to the
                # InRange variables that this is the case.
                points: List[Any] = []

                # OpenCV doesn't register the BoxPoints object as iterable, so this will fire a false warning on
                # PyCharm.  The next line disables that warning.  If you aren't in PyCharm, it won't do anything.

                # noinspection PyTypeChecker
                for point in box:
                    if point[0] <= 0 or point[0] >= frame.shape[1]:
                        inRangeX = False
                    if point[1] <= 0 or point[1] >= frame.shape[0]:
                        inRangeY = False

                    points.append(point)

                # Sort the points by the slope of the line generated between them and (0,0)
                # This will allow us to determine where each point lies on the rectangle for the center-point
                # estimation process that will follow
                points.sort(key=m.getFirstIndex, reverse=True)

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



                if m.getSlopeDuo(points[0], points[3]) < 0:
                    print("Left!")
                    #print("Slope:", m.getSlope(points[0]))
                if m.getSlopeDuo(points[0], points[3]) > 0:
                    print("Right!")
                    #print("Slope:", m.getSlope([points[0]]))





                # Using some basic algebra, find the intersection point of the two lines and return that point
                # to variables x and y respectively
                x, y = m.line_intersection(line1, line2)

                # Use OpenCV functions to determine the width and height of the original image.  These will be used
                # when calculating yaw and pitch errors later
                imageWidth = frame.shape[1]
                imageHeight = frame.shape[0]

                # Calculate the yaw of center-point relative to the center of the image, with -1 being on the far left
                # side of the screen, 1 being on the far right, and 0 being right in the center.  This makes writing a
                # PID loop for other closed-loop feedback system extremely easy on the other side.
                yaw = m.calculateYawError(x, imageWidth)

                # Calculate the pitch of the target with the exact same system as yaw
                pitch = m.calculatePitchError(y, imageHeight)

                # If system is in debug mode, print and display all of this data.  Otherwise, don't
                # in order to keep loop times as low as possible
                if c.isDebug():
                    if c.getDebug() is 1 or c.getDebug() is 3:
                        cv2.line(frame, (points[0][0], points[0][1]), (points[3][0], points[3][1]), (255, 0, 255), 2)
                    if inRangeX:
                        # In range, green center point
                        cv2.circle(frame, (int(x), int(y)), 5, (0, 255, 0), -1)
                        cv2.circle(frame, (points[0][0], points[0][1]), 5, (255, 0, 0), -1)
                        cv2.circle(frame, (points[1][0], points[1][1]), 5, (0, 255, 0), -1)
                        cv2.circle(frame, (points[2][0], points[2][1]), 5, (0, 0, 255), -1)
                        cv2.circle(frame, (points[3][0], points[3][1]), 5, (255, 255, 255), -1)
                        #print colored point values
                        #print("Blue: ", points[0])
                        #print("Green: ", points[1])
                        #print("Red: ", points[2])
                        #print("White: ", points[3])
                    else:
                        # Out of range, red center point
                        cv2.circle(frame, (int(x), int(y)), 5, (0, 0, 255), -1)
                    if c.getDebug() > 1:
                        pass
                    cv2.drawContours(frame, [box], 0, (0, 0, 255), 2)

        # This catch will occur when no fitting contours are found in the image
        except Exception as err:
            # If in debug mode, print out the error
            if c.getDebug() > 1:
                print(err)

        # If in debug mode, show the image.  If not, keep this disabled, as it slows down the program
        # significantly
        if c.isDebug():
            cv2.imshow("frame", frame)

        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break

        # Mandatory break statement that will trigger a clean shutdown of the program upon the ESC key being
        # pressed.  Using this method to stop the program is recommended since OpenCV leaves windows hanging and
        # camera streams open if the program is forcibly quit.


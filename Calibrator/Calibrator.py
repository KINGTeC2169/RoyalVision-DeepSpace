import cv2
import numpy as np

from Constants import Constants

c = Constants()

cap = cv2.VideoCapture(0)

def nothing(x):
    pass

# Creating a window for later use
cv2.namedWindow('low')
cv2.namedWindow('high')
cv2.namedWindow('result')

# Starting with 100's to prevent error while masking
lH, lS, lV, hH, hS, hV = c.readIndividualValues()

# Creating track bar
cv2.createTrackbar('Low H', 'low',0,179,nothing)
cv2.setTrackbarPos('Low H', 'low', lH)
cv2.createTrackbar('Low S', 'low',0,255,nothing)
cv2.setTrackbarPos('Low S', 'low', lS)
cv2.createTrackbar('Low V', 'low',0,255,nothing)
cv2.setTrackbarPos('Low V', 'low', lV)

cv2.createTrackbar('High H', 'high',0,179,nothing)
cv2.setTrackbarPos('High H', 'high', hH)
cv2.createTrackbar('High S', 'high',0,255,nothing)
cv2.setTrackbarPos('High S', 'high', hS)
cv2.createTrackbar('High V', 'high',0,255,nothing)
cv2.setTrackbarPos('High V', 'high', hV)

while True:

    _, frame = cap.read()

    #converting to HSV
    hsv = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)

    # get info from track bar and appy to result
    lH = cv2.getTrackbarPos('Low H', 'low')
    lS = cv2.getTrackbarPos('Low S', 'low')
    lV = cv2.getTrackbarPos('Low V', 'low')
    hH = cv2.getTrackbarPos('High H', 'high')
    hS = cv2.getTrackbarPos('High S', 'high')
    hV = cv2.getTrackbarPos('High V', 'high')

    c.writeValues(lH, lS, lV, hH, hS, hV)

    # Normal masking algorithm
    lower = np.array([lH, lS, lV])
    upper = np.array([hH, hS, hV])

    mask = cv2.inRange(hsv, lower, upper)

    result = cv2.bitwise_and(frame,frame,mask = mask)

    filtered = result.copy()

    contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(result, contours, -1, (0, 255, 0), 3)

    images = np.hstack((frame, filtered, result))

    cv2.imshow('result', images)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cap.release()

cv2.destroyAllWindows()
from threading import Thread
import cv2
from Constants import Constants


class ImageThread(Thread):
    def __init__(self, mat):
        super(ImageThread, self).__init__()
        self.mat = mat

    def run(self):
        print("Starting Proccessing\n")
        hsv = cv2.cvtColor(self.mat, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, Constants.lower_red, Constants.upper_red)
        im2, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(self.mat, contours, -1, (0, 255, 0), 3)
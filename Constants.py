import numpy as np
import csv

class Constants:

    lowArray = np.array([])
    highArray = np.array([])

    '''
    Debug Modes:
    0 - No Debugging.  For use on field
    1 - Display Image.  Print Yaw and Pitch
    2 - Print All Points and Slopes
    3 - 1 & 2
    '''

    debugLevel = 3

    def isDebug(self):
        return self.debugLevel > 0

    def getDebug(self):
        return self.debugLevel

    def readValues(self):
        with open('HSV_Values.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            low = next(csv_reader)
            high = next(csv_reader)

            for val in low:
                self.lowArray = np.append(self.lowArray, int(val))

            for val in high:
                self.highArray = np.append(self.highArray, int(val))

            return self.lowArray, self.highArray


    def readIndividualValues(self):
        vals = self.readValues()
        print(vals[0][0],vals[0][1],vals[0][2],vals[1][0],vals[1][1],vals[1][2])
        return int(vals[0][0]),int(vals[0][1]),int(vals[0][2]),int(vals[1][0]),int(vals[1][1]),int(vals[1][2])

    def writeValues(self,lH,lS,lV,hH,hS,hV):
        with open('HSV_Values.csv', 'w', newline='') as csvfile:
            output = csv.writer(csvfile, delimiter=',', )
            output.writerow([lH,lS,lV])
            output.writerow([hH,hS,hV])

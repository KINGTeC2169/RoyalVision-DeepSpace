class MathHandler:

    def getSlope(self, point):
        try:
            return float(point[1]) / float(point[0])
        except:
            return 1000

    def getFirstIndex(self, point):
        return  point[0]

    def getSlopeDuo(self, first, second):
        try:
            return float(first[1] - second[1]) / float(first[0] - second[0])
        except:
            return 1000

    def line_intersection(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            raise Exception('lines do not intersect')

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

    def calculateYawError(self,x,width):
        return -(x - .5 * width) / (.5 * width)

    def calculatePitchError(self, y, height):
        return -(y - .5 * height) / (.5 * height)
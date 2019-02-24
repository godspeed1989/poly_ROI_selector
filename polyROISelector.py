import cv2
import numpy as np
import math
from min_bbox import compute_min_bbox

def plot_dot(img, pos):
    cv2.line(img, pos, pos, (0, 0, 255), 8)

def plot_line(img, p1, p2):
    cv2.line(img, p1, p2, (0, 255, 0), 2)

def plot_rect(img, rect, color):
    p1 = (int(rect[0]), int(rect[1]))
    p2 = (int(rect[0]), int(rect[1]+rect[3]))
    p3 = (int(rect[0]+rect[2]), int(rect[1]+rect[3]))
    p4 = (int(rect[0]+rect[2]), int(rect[1]))
    cv2.line(img, p1, p2, color, 1)
    cv2.line(img, p2, p3, color, 1)
    cv2.line(img, p3, p4, color, 1)
    cv2.line(img, p4, p1, color, 1)

def plot_poly(img, corners, color):
    # (N,2)
    corners = np.array(corners).astype(np.int32)
    N = corners.shape[0]
    for i in range(N):
        j = (i+1) % N
        p1 = (corners[i,0], corners[i,1])
        p2 = (corners[j,0], corners[j,1])
        cv2.line(img, p1, p2, color, 1)

class orientedROISelector(object):
    """Class providing various functionalities for the selecting polygonal ROI and
    obtaining associated metrics from it.
    Returns a list of dictionaries, where each of the list elements corresponds to a ROI.
    """
    def __init__(self, img, windowName=None):
        self.img = img
        self.__backup = self.img.copy()

        self.ROIs = []
        self.__polygon = []

        self.m_idle = 0
        self.m_polyselection = 1
        self.mode = self.m_idle

        self.windowName = windowName

        if windowName != None:
            cv2.setMouseCallback(self.windowName, self.click)
        else:
            self.windowName = "ROI Selection"
            cv2.imshow(self.windowName, self.img)
            cv2.setMouseCallback(self.windowName, self.click)

    def resetCanvas(self, img):
        self.img = img
        self.__backup = self.img.copy()
        self.ROIs = []
        self.__polygon = []

        self.mode = self.m_idle
        cv2.imshow(self.windowName, self.img)

    def __updateROI(self):
        if len(self.__polygon) > 2:
            mask = np.zeros(self.img.shape[:2], np.uint8)
            polygon = np.array([self.__polygon], np.int32)

            # find contours
            cv2.fillPoly(mask, polygon, 255)
            major = cv2.__version__.split('.')[0]
            if major == '3':
                _, contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            else:
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # find bounding box
            if len(contours) > 0:
                rBoundingBox, hull_idx = compute_min_bbox(polygon[0])
                contours = contours[0]
                moment = cv2.moments(contours)
                cx = int(moment["m10"]/moment["m00"])
                cy = int(moment["m01"]/moment["m00"])
                rect = cv2.boundingRect(contours)
                centroid = (cx, cy)
                boundingBox = rect
                center = (int(rect[0]+rect[2]/2), int(rect[1]+rect[3]/2))
                tmpDict = {'Polygon': polygon[0],
                        'rBoundingBox': rBoundingBox,
                        'Convex_Polygon': polygon[0][hull_idx],
                        'Centroid': centroid,
                        'Center': center,
                        'BoundingBox': boundingBox}
                self.ROIs.append(tmpDict)
                self.__polygon = []
                return True
        return False

    def click(self, event, x, y, flags, param):
        """Main click event for the mouse. Allowed actions:
        Left click: If a ROI is open, that is, it is not enclosed, it adds another point
        Right click: If the ROI is open, then it closes the ROI polygon.
        """
        if event == cv2.EVENT_FLAG_LBUTTON:
            if self.mode == self.m_idle:
                plot_dot(self.img, (x, y))
                self.__polygon.append((x, y))
                self.__backup = self.img.copy()
                self.mode = self.m_polyselection
            elif self.mode == self.m_polyselection:
                prev = self.__polygon[-1]
                plot_line(self.img, prev, (x, y))
                plot_dot(self.img, (x, y))
                self.__polygon.append((x, y))
                self.__backup = self.img.copy()
        elif event == cv2.EVENT_FLAG_RBUTTON:
            if self.mode == self.m_idle:
                pass
            elif self.mode == self.m_polyselection:
                prev = self.__polygon[0]
                cur = self.__polygon[-1]
                ret = self.__updateROI()
                if ret:
                    self.img = self.__backup.copy()
                    plot_line(self.img, prev, cur)
                    roi = self.ROIs[-1]
                    plot_poly(self.img, roi['rBoundingBox'], (255, 0, 0))
                    plot_poly(self.img, roi['Convex_Polygon'], (0, 255, 255))
                    plot_rect(self.img, roi['BoundingBox'], (255, 0, 255))
                    self.__backup = self.img.copy()
                    self.mode = self.m_idle
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.mode == self.m_idle:
                pass
            elif self.mode == self.m_polyselection:
                self.img = self.__backup.copy()
                prev = self.__polygon[-1]
                plot_line(self.img, prev, (x, y))
        else:
            pass
        cv2.imshow(self.windowName, self.img)

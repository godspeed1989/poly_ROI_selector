import sys
import numpy as np
from scipy.spatial import ConvexHull

def compute_min_bbox(points, vis=False):
    if vis:
        import matplotlib.pyplot as plt
    # compute convex hull
    hull = ConvexHull(points)
    def AngleToXAxis(p1, p2):
        '''
        Calculates the angle to the X axis.
        '''
        delta = p1 - p2
        return -np.arctan(delta[1] / delta[0])
    def RotateToXAxis(vector, angle):
        '''
        Rotates vector by an angle to the x-Axis
        '''
        newX = vector[0] * np.cos(angle) - vector[1] * np.sin(angle)
        newY = vector[0] * np.sin(angle) + vector[1] * np.cos(angle)
        return np.array([newX, newY])
    def Area(box):
        rng_x = box[1,0] - box[0,0]
        rng_y = box[1,1] - box[0,1]
        return rng_x * rng_y
    # compute min bbox
    # https://github.com/cansik/LongLiveTheSquare
    minBox = None
    minAngle = 0
    # foreach edge of the convex hull
    num_hull = len(hull.vertices)
    for i in range(num_hull):
        curr_pt = points[hull.vertices[i]]
        next_pt = points[hull.vertices[(i + 1) % num_hull]]
        if vis:
            print('points')
            print(curr_pt, hull.vertices[i])
        # min / max points
        top = -sys.maxsize
        bottom = sys.maxsize
        left = sys.maxsize
        right = -sys.maxsize
        # get angle of segment to x axis
        angle = AngleToXAxis(curr_pt, next_pt)
        # rotate every point and get min and max values for each direction
        for p in hull.vertices:
            pt = points[p]
            rotatedPoint = RotateToXAxis(pt, angle)
            top = max(top, rotatedPoint[1])
            bottom = min(bottom, rotatedPoint[1])
            left = min(left, rotatedPoint[0])
            right = max(right, rotatedPoint[0])
        box = np.array([[left, bottom], [right, top]])
        if minBox is None or Area(minBox) > Area(box):
            minBox = box
            minAngle = angle

    mbox_points = np.array([(minBox[0,0], minBox[0,1]),
                            (minBox[1,0], minBox[0,1]),
                            (minBox[1,0], minBox[1,1]),
                            (minBox[0,0], minBox[1,1])])

    # rotate axis algined box back
    bbox_points = np.zeros_like(mbox_points)
    for i in range(mbox_points.shape[0]):
        bbox_points[i] = RotateToXAxis(mbox_points[i], -minAngle)

    if vis:
        plt.plot(points[:,0], points[:,1], 'o', ms=2)
        for i in range(num_hull):
            pi = hull.vertices[i]
            pj = hull.vertices[(i + 1) % num_hull]
            #plt.plot(points[(pi,pj),0], points[(pi,pj),1], 'g-.')
            plt.arrow(points[pi,0], points[pi,1],
                      points[pj,0]-points[pi,0], points[pj,1]-points[pi,1],
                      head_width=0.02, color='g')
        for i in range(bbox_points.shape[0]):
            j = (i + 1) % bbox_points.shape[0]
            plt.plot(bbox_points[(i,j),0], bbox_points[(i,j),1], 'r-', lw=2)
            plt.arrow(bbox_points[i,0], bbox_points[i,1],
                      bbox_points[j,0]-bbox_points[i,0], bbox_points[j,1]-bbox_points[i,1],
                      head_width=0.02, color='r')
        print('orthogonality validation')
        print(np.sum(np.dot((bbox_points[0] - bbox_points[1]), (bbox_points[0] - bbox_points[3]))))
        print(np.sum(np.dot((bbox_points[1] - bbox_points[0]), (bbox_points[1] - bbox_points[2]))))
        print(np.sum(np.dot((bbox_points[2] - bbox_points[1]), (bbox_points[2] - bbox_points[3]))))
        print(np.sum(np.dot((bbox_points[3] - bbox_points[0]), (bbox_points[3] - bbox_points[2]))))
        plt.plot(bbox_points[:,0], bbox_points[:,1], 'x')
        plt.show()

    return bbox_points, hull.vertices

if __name__ == '__main__':
    points = np.random.rand(15, 2)   # 30 random points in 2-D
    bbox_points, hull = compute_min_bbox(points, vis=True)
    print('bbox_points')
    print(bbox_points)
    print('hull index')
    print(hull)
    print(points[hull])

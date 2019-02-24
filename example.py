import cv2
import polyROISelector

image = cv2.imread("test.jpg") # Or any of your images
clone = image.copy()
windowName = "Test"
cv2.imshow(windowName, image)

ROISelector = polyROISelector.orientedROISelector(image, windowName=windowName)

while True:
    k = cv2.waitKey(1)
    # Handle the reset event by explicitly calling the member function.
    # Keep in mind this only resets the canvas, not the ROI list. If you
    # want to separate the ROIs between each canvas, you must store the ROIs so far
    # before the function call. Then explicitly set the ROI list to an empty list
    # Useful for situation like data annotating, where you can just pass a new image
    # and reset the canvas with that image. You can then have separate ROI handlers
    # for each image separately and can navigate through the a dataset either way.
    if k == ord('r'):
        print(ROISelector.ROIs)
        ROISelector.resetCanvas(clone.copy())
    elif k == (27):
        break
cv2.destroyAllWindows()

# import the necessary packages
from skimage.metrics import structural_similarity as compare_ssim
from mss import mss
import keyboard
import imutils
import win32api
import cv2
import numpy
from time import sleep

corners = []
state_left = win32api.GetKeyState(0x01) 

while True:
    if keyboard.is_pressed('q') or len(corners) >= 2:
        break
    new_state_left = win32api.GetKeyState(0x01)
    if state_left != new_state_left:
        state_left = new_state_left
        if state_left < 0:
            corners.append(win32api.GetCursorPos())
            print(win32api.GetCursorPos())
    c = win32api.GetCursorPos()
    print(c)

r0 = numpy.array(corners[0])
r1 = numpy.array(corners[1])
wh = r1 - r0


with mss() as sct:
    m1 = {"mon": 1, "top": r0[1].item(), "left": r0[0].item(), "width": wh[0].item(), "height": wh[1].item()}
try:
    imageA = numpy.array(sct.grab(m1))
    sleep(2)
    imageB = numpy.array(sct.grab(m1))
except ScreenShotError:
    details = sct.get_error_details()
    print(f"grab error: {details}")
    quit()

# convert the images to grayscale
grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

# compute the Structural Similarity Index (SSIM) between the two
# images, ensuring that the difference image is returned
(score, diff) = compare_ssim(grayA, grayB, full=True)
diff = (diff * 255).astype("uint8")
print("SSIM: {}".format(score))

# threshold the difference image, followed by finding contours to
# obtain the regions of the two input images that differ
thresh = cv2.threshold(diff, 0, 255,
	cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
	cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

# loop over the contours
for c in cnts:
	# compute the bounding box of the contour and then draw the
	# bounding box on both input images to represent where the two
	# images differ
	(x, y, w, h) = cv2.boundingRect(c)
	cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
	cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)
# show the output images
#cv2.imshow("Original", imageA)
cv2.imshow("Modified", imageB)
cv2.imshow("Diff", diff)
cv2.imshow("Thresh", thresh)
cv2.waitKey(0)

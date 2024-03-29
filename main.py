from mss import mss, ScreenShotError
from PIL import Image
import time
import numpy
import cv2
import win32api, win32gui
import keyboard

state_left = win32api.GetKeyState(0x01) 

corners = []

while True:
    if keyboard.is_pressed('q') or len(corners) >= 2:
        break
    new_state_left = win32api.GetKeyState(0x01)
    if state_left != new_state_left:
        state_left = new_state_left
        if state_left < 0:
            corners.append(win32api.GetCursorPos())

r0 = numpy.array(corners[0])
r1 = numpy.array(corners[1])
dxdy = r1 - r0

print(r0)
print(r1)
print(dxdy)

bad_colorhi = numpy.array([213, 241, 213])
bad_colorlo = numpy.array([208, 240, 208])
to_color = numpy.array([9.8, 9.8, 9.8])

with mss() as sct:
    m1 = {"mon": 1, "top": r0[1].item(), "left": r0[0].item(), "width": dxdy[0].item(), "height": dxdy[1].item()}
    cur_ss = numpy.array(sct.grab(m1))
    while True:
        try:
            ss = numpy.array(sct.grab(m1))
            #ss = cv2.imread("C:\\Users\\GameBox\\Desktop\\Capture.png")
        except ScreenShotError:
            details = sct.get_error_details()
            print(f"grab error: {details}")
            quit()

        ss = cv2.cvtColor(ss, cv2.COLOR_RGBA2BGR)

        grey = cv2.cvtColor(ss, cv2.COLOR_BGRA2GRAY)
        cv2.imshow("grey", grey)

        (ret, grey) = cv2.threshold(grey, 127, 255, cv2.THRESH_OTSU)
        cv2.imshow("threshold", grey)

        edges = cv2.Canny(grey, threshold1=100, threshold2=200, apertureSize=3, L2gradient=False)
        cv2.imshow("edges", edges)        
        
        minLineLen = 40
        maxLineGap = 1
        lines = cv2.HoughLinesP(
            image=edges, 
            rho=1,
            theta=numpy.pi/180, 
            threshold=10,
            minLineLength=minLineLen, 
            maxLineGap=maxLineGap)

        for l in lines:
            for x1, y1, x2, y2 in l:
                cv2.line(ss, (x1, y1), (x2, y2), (0, 0, 255), 1)
        cv2.imshow("output", ss)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break
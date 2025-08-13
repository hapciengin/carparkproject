import cv2
import numpy as np
from mss import mss
import time

sct = mss()

monitor = sct.monitors[1]

while True:
    img_sct = sct.grab(monitor)
    
    img = np.array(img_sct)
    
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    edges = cv2.Canny(img_gray, 50, 100)
    
    cv2.imshow("secreen shot", img)
    
    cv2.imshow("kenar", edges)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
    time.sleep(2)

cv2.destroyAllWindows()

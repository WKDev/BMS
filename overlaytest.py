import cv2
import numpy as np
from datetime import datetime
frame = np.zeros((480, 640, 3), np.uint8)*128

cv2.putText(frame, f"| {datetime.today().strftime('%Y-%m-%d %H:%M:%S')}", (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

cv2.imshow("Hello World", frame)

cv2.waitKey(0)

cv2.destroyAllWindows()
import cv2
import sys
import inspect
import time
import threading

#TODO 1. make a logger with inspect and 3 colors for each error levels
class FlirCV:
    def __init__(self,
                 camera_ip : str,
                 encoding : str,
                overlay : str,
                flask_mode : bool = True) -> None:
        assert encoding in [ "avc", "mpeg4", "mjpg" ], "Invalid encoding.."

        self._camera_ip = camera_ip
        self._encoding = encoding
        self._overlay = overlay
        self.load_count = 0

        self.isInitialized = True
        self.url = f"rtsp://{self._camera_ip}/{self._encoding}?overlay={overlay}"

        self._cap = cv2.VideoCapture(self.url)
        print(f"[{self.__class__.__name__}] init")
        self.vc_init()

    def vc_init(self):
        self._cap = cv2.VideoCapture(self.url)
        print(f"[{self.__class__.__name__}] vc_init")

    def proc(self) -> None:
        assert self._cap.isOpened(), "VideoCapture is not opened.."
        print(f"[{inspect.currentframe().f_code.co_name}] Press 'q' to quit")
        while True:
            Good, frame = self.getFrame()
            cv2.imshow("test_video", frame)
            if not Good:
                break
            elif cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self._cap.release()

    def getFrame(self):
        assert self._cap.isOpened(), "VideoCapture doesn't work"
        return self._cap.read()

    def getFramesForFlask(self):
        self.load_count +=1
        print(f"[{self.__class__.__name__}][{inspect.currentframe().f_back.f_code.co_name}] called")
        if self.load_count > 1:
            self.vc_init()
        while True:
            Good, frame = self.getFrame()
            if Good:
                _, buffer = cv2.imencode('.jpg', frame,[cv2.IMWRITE_JPEG_QUALITY, 50]) #, [cv2.IMWRITE_JPEG_QUALITY, 80]
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' +
                        buffer.tobytes() + b'\r\n')
                # time.sleep(0.1)
            else:
                # print("retrying to get a frame")
                continue

    def __del__(self):
        if self._cap.isOpened():
            self._cap.release()
            print(f"[{self.__class__.__name__}][{inspect.currentframe().f_code.co_name}] Abnormaly Terminated..")
            sys.exit(-1)
        else:
            print("Bye.")

if __name__ == "__main__":
    flir = FlirCV(camera_ip="169.254.202.73",
                  encoding="mpeg4",
                  overlay="on")
    flir.proc()

import cv2

class IRCam:
    def __init__(self) -> None:
        self.cap = cv2.VideoCapture(0)
        self.this_name = self.__class__.__name__
        print(f"[{self.this_name}] Initialized")

    def proc(self) -> None:
        assert self.cap.isOpened(), \
                f"[{self.this_name}] Video Capture doesn't work"
        while self.cap.isOpened():
            good, frame = self.cap.read()

            cv2.imshow('IRCam', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        self.cap.release()

if __name__ == "__main__":
    cam = IRCam()
    cam.proc()

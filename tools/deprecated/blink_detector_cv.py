from flir_with_cv import FlirCV
import cv2
class BlinkDetectorCV(FlirCV):
    def __init__(self,
                camera_ip : str,
                encoding : str,
                overlay : str) -> None:
        super().__init__(camera_ip = camera_ip,
                        encoding = encoding,
                        overlay = overlay)
    def proc(self):
        face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
        eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
        while True:
            ret, frame = super().getFrame()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            for (x,y,w,h) in faces:
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]

                eyes = eye_cascade.detectMultiScale(roi_gray)

                for (ex,ey,ew,eh) in eyes:
                    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)

                    eye_roi_gray = roi_gray[ey:ey+eh, ex:ex+ew]
                    eye_roi_color = roi_color[ey:ey+eh, ex:ex+ew]

                    eye_ratio = cv2.countNonZero(eye_roi_gray) / (eye_roi_gray.shape[0] * eye_roi_gray.shape[1])

                    if eye_ratio < 0.2:
                        print("Eye Blink Detected")

            cv2.imshow('frame',frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    # def __del__(self) -> None:
    #     super().__del__()
    #     print(f"[{self.__name__}][{inspect.currentframe().f_code.co_name}] Deleted")

if __name__ == "__main__":
    flicker = BlinkDetectorCV(camera_ip="169.254.202.73",
                  encoding="mpeg4",
                  overlay="on")
    flicker.proc()
import cv2
import dlib
from functools import wraps
from scipy.spatial import distance
import os
import sys
from datetime import datetime,time
import inspect

from tools.db import Table

CAM_PATH = '/dev/v4l/by-id/usb-ID002_ID002_V20201203002-video-index0'


def calculate_EAR(eye): # 눈 거리 계산
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear_aspect_ratio = (A+B)/(2.0*C)
    return ear_aspect_ratio

class BlinkDetectorDlib:
    def __init__(self, db, app) -> None:
        self.cap = None

        self.frame = None
        self.load_count = 0

        self.visual : bool = False
        self.closed : bool = False
        self.sleep_duration = None
        self.lastsave = 0
        self.blink_duration_cnt = 0
        self.isSleeping = False

        self.db = db
        self.app = app

        print(f"[{self.__class__.__name__}] init")
        self.vc_init()

    def vc_init(self):
        self.cap = cv2.VideoCapture(CAM_PATH)
        self.cap.set(3, 640)
        self.cap.set(4, 480)

        print(f"[{self.__class__.__name__}] vc_init")

        self.hog_face_detector = dlib.get_frontal_face_detector()
        dat_file = os.path.abspath("/home/motion/Desktop/flir/tools/dlib_parameters/shape_predictor_68_face_landmarks.dat")
        self.dlib_facelandmark = dlib.shape_predictor(dat_file)
        print(f"[{self.__class__.__name__}] vc_init |-> predictor init")

    def dynamic_zoom(self, setting : bool):
        self.dynamic_zoom = setting

    def show_me(self, setting : bool):
        self.visual = setting

    def detectEyesAndDraw(self,face_landmarks, ref_x = 0, ref_y = 0):
        leftEye=[]
        rightEye=[]
        for n in range(36,42): # 오른쪽 눈 감지
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            leftEye.append((x,y))
            next_point = n+1
            if n == 41:
                next_point = 36
            x2 = face_landmarks.part(next_point).x
            y2 = face_landmarks.part(next_point).y
            cv2.line(self.frame,(x+ref_x,y+ref_y),(x2+ref_x,y2+ref_y),(0,255,0),1)

        for n in range(42,48): # 왼쪽 눈 감지
            x = face_landmarks.part(n).x
            y = face_landmarks.part(n).y
            rightEye.append((x,y))
            next_point = n+1
            if n == 47:
                next_point = 42
            x2 = face_landmarks.part(next_point).x
            y2 = face_landmarks.part(next_point).y
            cv2.line(self.frame,(x+ref_x,y+ref_y),(x2+ref_x,y2+ref_y),(0,255,0),1)
        return leftEye, rightEye

    def getFramesForFlask(self):
        self.load_count +=1
        print(f"[{self.__class__.__name__}][{inspect.currentframe().f_back.f_code.co_name}] called")
        if self.load_count > 1:
            self.vc_init()
        while True:
            Good, frame = self.process()
            if Good:
                _, buffer = cv2.imencode('.jpg', frame,[cv2.IMWRITE_JPEG_QUALITY, 50]) #, [cv2.IMWRITE_JPEG_QUALITY, 80]
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' +
                        buffer.tobytes() + b'\r\n')
                    # time.sleep(0.1)
            else:
                # print("retrying to get a frame")
                continue
    def getSleepDuration(self):
        if self.sleep_duration != None:
            def timedelta_to_time(td):
                seconds = td.total_seconds()
                hours = int(seconds // 3600)
                minutes = int((seconds % 3600) // 60)
                return time(hours, minutes, td.seconds)
            return timedelta_to_time(self.sleep_duration)
        else:
            return None
    def process(self):
        Good, self.frame = self.cap.read()
        if Good:
            gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

            faces = self.hog_face_detector(gray)
            for face in faces:
                if self.dynamic_zoom:
                    x1, y1, x2, y2 = face.left(), face.top(), face.right(), face.bottom()

                    face_gray = gray[y1:y2, x1:x2]
                    face_crop = dlib.rectangle(0, 0, face_gray.shape[1], face_gray.shape[0])
                    face_landmarks = self.dlib_facelandmark(face_gray,face_crop)

                    leftEye, rightEye = self.detectEyesAndDraw(face_landmarks, x1, y1)

                    if self.visual:
                        cv2.imshow("dynamic_zoom", face_gray)
                else:
                    face_landmarks = self.dlib_facelandmark(gray, face)
                    leftEye, rightEye = self.detectEyesAndDraw(face_landmarks)

                left_ear = calculate_EAR(leftEye)
                right_ear = calculate_EAR(rightEye)

                EAR = (left_ear+right_ear)/2
                EAR = round(EAR,2)

                #Check Blinking
                # Closing Eyes
                prev_closed = self.closed
                if EAR<0.19:
                    self.closed = True
                    self.blink_duration_cnt +=1
                    # Getting sleep
                    if self.blink_duration_cnt >=30 and not self.isSleeping:
                        print(f"[{self.__class__.__name__}] Baby is sleeping, counting...")
                        self.lastsave = datetime.now()
                        self.isSleeping = True
                    elif self.blink_duration_cnt >=30 and self.isSleeping:
                        cv2.putText(self.frame,"SLEEPING",(20,100), cv2.FONT_HERSHEY_SIMPLEX,3,(0,0,255),4)
                # Opening Eyes
                else:
                    self.closed = False
                    #Is the baby sleeping?
                    # After Sleeping
                    if self.blink_duration_cnt>=30 and self.isSleeping:
                        self.blink_duration_cnt = 0
                        self.isSleeping = False
                        self.sleep_duration = datetime.now() - self.lastsave
                        print(f"[{self.__class__.__name__}] Awake! Baby has slept for {self.sleep_duration}")
                        with self.app.app_context():
                            self.db.session.add(Table(sleeptime = self.getSleepDuration() ))
                            self.db.session.commit()
                        print(f"[{self.__class__.__name__}] Data saved in DB. Please Refresh Browser")

                    # Before Sleeping
                    elif( not self.isSleeping and prev_closed == True):
                        cv2.putText(self.frame,"BLINK!",(20,100), cv2.FONT_HERSHEY_SIMPLEX,3,(0,0,255),4)
                        self.blink_duration_cnt = 0
                        pass

                # print(f'close count : {self.blink_duration_cnt}')
            if self.visual:
                cv2.imshow("Are you Sleepy", self.frame)

            return Good, self.frame

        else:
            self.vc_init()
            pass

    def proc(self):
        while self.cap.isOpened():
            self.process()
            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

    def __del__(self):
        if self.cap.isOpened():
            self.cap.release()
            print(f"[{self.__class__.__name__}][{inspect.currentframe().f_code.co_name}] Abnormaly Terminated..")
            sys.exit(-1)
        else:
            print("Bye.")

if __name__ == "__main__":
    blink = BlinkDetectorDlib()
    blink.dynamic_zoom(True)
    blink.proc()

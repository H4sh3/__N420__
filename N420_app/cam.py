
from datetime import date, datetime, timedelta
from time import time
import cv2
from pathlib import Path
import os
from threading import Thread


class Cam():
    capture_interval = timedelta(minutes=10)
    last_capture = datetime.now() - capture_interval
    path = "data\\pictures"

    cam = cv2.VideoCapture(0)

    def __init__(self):
        Thread(target=self.camptureLoop).start()

    def safe_frame(self, frame):
        path = self.path
        Path("data\\pictures").mkdir(parents=True, exist_ok=True)
        name = datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ".png"
        path = os.path.join(path, name)
        print(path)
        cv2.imwrite(path, frame)

    def camptureLoop(self):
        print('starting loop')
        while True:
            success, frame = Cam.cam.read()  # read the cam frame
            if not success:
                pass
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                self.frame = buffer.tobytes()

            if datetime.now() >= self.last_capture + self.capture_interval:
                self.safe_frame(frame)
                self.last_capture = datetime.now()

    def get_frame(self):
        return self.frame

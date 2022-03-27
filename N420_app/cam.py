
from datetime import datetime
from time import time
import cv2
from pathlib import Path
import os
from threading import Thread
import time


class Cam():
    capture_interval_minutes = 10
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
        print('capture loop started')
        while True:
            success, frame = Cam.cam.read()  # read the cam frame

            if success:
                _, buffer = cv2.imencode('.jpg', frame)
                self.frame = buffer.tobytes()
                self.safe_frame(frame)
                self.last_capture = datetime.now()
                time.sleep(self.capture_interval*60)

    def get_frame(self):
        return self.frame


from datetime import date, datetime, timedelta
from time import time
import cv2
from pathlib import Path
import os
from threading import Thread

class Cam(object):
    capture_interval = timedelta(minutes=10)
    last_capture = datetime.now()- capture_interval
    path = "data\\pictures"

    cam = cv2.VideoCapture(0)
    def __init__(self):
        Thread(target=self.camptureLoop).start()
        

    @classmethod
    def safe_frame(cls, frame):
        path = cls.path
        Path("data\\pictures").mkdir(parents=True, exist_ok=True)
        name = datetime.now().strftime("%m-%d-%Y_%H-%M-%S") + ".png"
        path = os.path.join(path, name)
        print(path)
        cv2.imwrite(path,frame)

    @classmethod
    def camptureLoop(cls):
        print('starting loop')
        while True:
            success, frame = Cam.cam.read()  # read the cam frame
            if not success:
                pass
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                cls.frame = buffer.tobytes()

            if datetime.now() >= cls.last_capture + cls.capture_interval: 
                cls.safe_frame(frame)
                cls.last_capture = datetime.now()
                   
    @classmethod
    def get_frame(cls):        
        return cls.frame
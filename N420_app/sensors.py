import numpy as np
from time import time

class Sensor():
    def __init__(self):
        pass

    @classmethod
    def get_data(cls):
        _sensordata = {}
        _sensordata['temp'] = round(abs(np.sin(time())*10),2)
        _sensordata['hum'] = 10
        _sensordata['soil1'] = round(abs(np.sin(time())),2)
        _sensordata['soil2']= round(abs(np.sin(time())),2)
        _sensordata['soil3']= round(abs(np.sin(time())),2)
        _sensordata['pres'] = 10
        return _sensordata


if __name__ == '__main__':
    sensor = Sensor()
    print(sensor.get_data())
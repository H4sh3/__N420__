
from datetime import datetime, timedelta
from time import sleep, time
from log_data import Logger

from sensors import Sensor
import json as js



class Growbox():
    actuators = []
    sensor = Sensor()
    data_logger = Logger('data')
    error_logger = Logger('error_growbox')
    log_interval = timedelta(seconds=2)
    last_log = datetime.now()-log_interval

    def __init__(self, pin, id):
        self.pin = pin
        self.id = id
        self.state = False
        Growbox.actuators.append(self)

    def set_state(self, state=False):
        self.state = state

    def toggle_state(self):
        self.state = not self.set_state

    @classmethod
    def path_data(cls):
        return cls.data_logger.get_path()

    @staticmethod
    def get_time():
        return datetime.now()

    @classmethod
    def update_sensordata(cls):
        cls.sensordata =  cls.sensor.get_data()    

    @classmethod
    def init_actuators(cls):
        print('init growbox')
        Growbox.update_sensordata()
        Lamp(1, 'lamp_g', 18 , growth_phase='g')
        Lamp(2, 'lamp_f', 12, growth_phase='f')
        Pot(3, 'pot1', 6, 'soil1')
        Pot(4, 'pot2', 6, 'soil2')
        Pot(5, 'pot3', 6, 'soil3')
        Fan(7, 'fan')
        
        cls.update_sensordata()
        Lamp.update_lamps()
        Pot.update_pots()
        Fan.update_fans()

    @classmethod
    def log_data(cls):
        if datetime.now() >= cls.last_log + cls.log_interval:
            print("loging data")
            cls.last_log = datetime.now()
            
            cls.data_logger.write(js.dumps(cls.build_data()))

    @classmethod
    def main_loop(cls):
        print('starting growbox')
        while True:
            try:
                cls.update_sensordata()
                Lamp.update_lamps()
                Pot.update_pots()
                Fan.update_fans()
                cls.log_data()
                sleep(0.5)
            except Exception as e:
                cls.error_logger(repr(e))
                raise e
           

    @classmethod
    def build_data(cls):
        _data = {}
        _data['time'] = datetime.now().strftime("%H:%M:%S")
        _data['date'] = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        _data = _data | Growbox.sensordata
        _data = _data | Lamp.get_data()
        _data = _data | Pot.get_data()
        _data = _data | Fan.get_data()
        return _data
        ## print(js.dumps(_data, indent=4))
        #exit()


class Lamp(Growbox):

    lamps = []
    phase = 'g'
    lamp_state = False
    on_time = datetime.now() # time how long lamp stays on
   
    def __init__(self, pin, id, duration, growth_phase='g'):
        super().__init__(pin, id)
        self.duration = duration
        duration = timedelta(hours=duration) # time when lmap turns on
 
        
        self.off_time = Lamp.on_time + duration # in hours
        self.growth_phase = growth_phase
        Lamp.lamps.append(self)


    @classmethod
    def get_data(cls):
        _data = {}
        _data['lamp_phase'] = cls.phase
        _data['lamp_state'] = cls.lamp_state
        _data['lamp_ontime']=  cls.on_time.strftime("%H:%M")

        for lamp in cls.lamps:
            _data[lamp.id+ '_state']=lamp.state
            _data[lamp.id+ '_duration']=lamp.duration
            _data[lamp.id+ '_phase']=lamp.growth_phase
        return _data

    def update(self):
        _time =Growbox.get_time()

        #turn off if not right phase
        if Lamp.phase != self.growth_phase and self.state:
            self.state = False
            # print(f"turning off {self.id}, not in phase")

        elif Lamp.phase == self.growth_phase:
             # turning off
            if self.state:
                if _time> self.off_time or _time < Lamp.on_time:
                    self.state = False
                    Lamp.lamp_state = False
                    # print(f"turning off {self.id}")
            # turn on
            elif not self.state and _time > Lamp.on_time and _time < self.off_time:
                self.state = True
                Lamp.lamp_state = True
                # print(f"turning on {self.id}")

    @classmethod
    def set_phase(cls, phase):
        cls.phase = phase
                
    @classmethod
    def update_lamps(cls):
        for lamp in cls.lamps:
            lamp.update()


    @classmethod
    def set_phase(cls, phase):
        cls.phase = phase # 'g' or ''f'

    @classmethod
    def set_starttime(cls, starttime):
        cls.on_time = datetime.strptime(starttime, "%H:%M")


class Pot(Growbox):
    pin_pump = 0
    state_pump= False
    pots = []
    irrigation_interval = 80 # in seconds
    irrigation_duration = 2 # in seconds
    soil_moist_hyst_min = 10
    soil_moist_hyst_max = 20

    def __init__(self, pin, state, pin_pump, index_soil):
        super().__init__(pin, state)
        Pot.pin_pump=pin_pump
        Pot.pots.append(self)
        self. index_soil = index_soil # index for dict form sensordate (available: "soil1", "soil2", "siol3")
        self.flag_dry = False
        self.last_irrigation = datetime.now()-timedelta(seconds=Pot.irrigation_interval)


    @classmethod
    def get_data(cls):
        _data = {}
        _data['state_pump'] = cls.state_pump
        _data['irrigation_interval'] = cls.irrigation_interval
        _data['irrigation_duration'] = cls.irrigation_duration
        _data['soil_moist_hyst_min'] = cls.soil_moist_hyst_min
        _data['soil_moist_hyst_max'] = cls.soil_moist_hyst_max
        for pot in cls.pots:
            _data[pot.id + '_state'] = pot.state
            _data[pot.id + '_dry'] = pot.flag_dry
            _data[pot.id + '_soil_moist'] = pot.soil_moist
       
        return _data

    def update(self):
        #update soil moist
        self.soil_moist = Growbox.sensordata[self.index_soil]
        # raise flag if dry
        if self.soil_moist <= Pot.soil_moist_hyst_min:
            self.flag_dry = True
        elif self.soil_moist >= Pot.soil_moist_hyst_max:
            self.flag_dry = False
        # call pummp and valve if pump state is false
        if not Pot.state_pump and self.flag_dry and datetime.now() - self.last_irrigation > timedelta(seconds=Pot.irrigation_interval):
            Pot.start_time = datetime.now()
            _time_string = Pot.start_time.strftime("%H:%M:%S")
            Pot.state_pump = True
            Pot.pumping_pot_id = self.id
            self.last_irrigation = datetime.now()
            self.state = True
            # print(f"turning on pump at {_time_string}")
            # print(f"turning on {self.id}")
        elif Pot.state_pump and Pot.pumping_pot_id == self.id and datetime.now() - Pot.start_time > timedelta(seconds=self.irrigation_duration):
            Pot.state_pump = False
            Pot.pumping_pot_id = ''
            _time_string = datetime.now().strftime("%H:%M:%S")
            # print(f"turning of pump at {_time_string}")
            # print(f"turning off {self.id}")
            
    @classmethod
    def update_pots(cls):
        for pot in cls.pots:
            pot.update()


    @classmethod
    def set_irrigation_interval(cls, irrigation_interval): # in hours
        cls.irrigation_interval = irrigation_interval

    @classmethod
    def set_irrigation_duration(cls, irrigation_duration): # in seconds
        cls.irrigation_duration = irrigation_duration

    @classmethod
    def set_soil_moist_hyst_min(cls, soil_moist_hyst_min): 
        cls.soil_moist_hyst_min = soil_moist_hyst_min
    
    @classmethod
    def set_soil_moist_hyst_max(cls, soil_moist_hyst_max): 
        cls.soil_moist_hyst_max = soil_moist_hyst_max



    
class Fan(Growbox):

    fans=[]
    temp_hyst_min = 25
    temp_hyst_max = 30
    hum_hyst_min = 50
    hum_hyst_max = 60
    fans_state = False
   
    def __init__(self, pin, id):
        super().__init__(pin, id)

        Fan.fans.append(self)
    

    @classmethod
    def get_data(cls):
        _data = {}
        _data['temp_hyst_min'] = cls.temp_hyst_min
        _data['temp_hyst_max'] = cls.temp_hyst_max
        _data['hum_hyst_min'] = cls.hum_hyst_min
        _data['hum_hyst_max'] = cls.hum_hyst_max
        _data['state'] = cls.fans_state
        for fan in cls.fans:
            _data[fan.id + '_state'] =  fan.state
        return _data

    def update(self):
        temp = Growbox.sensordata['temp']
        hum = Growbox.sensordata['hum']

        if not self.state:
            if temp >= Fan.temp_hyst_max or hum >= Fan.hum_hyst_max:
                self.state = True
                Fan.fans_state = True
                # print(f"turning on {self.id}")
        
        elif self.state and  Fan.temp_hyst_min > temp and Fan.hum_hyst_min > hum:
                self.state = False
                Fan.fans_state = False
                # print(f"turning on {self.id}") 

    @classmethod
    def update_fans(cls):
        for fan in cls.fans:
            fan.update()

    @classmethod
    def set_temp_hyst_min(cls, temp_hyst_min): 
        cls.temp_hyst_min = temp_hyst_min

    @classmethod
    def set_temp_hyst_max(cls, temp_hyst_max): 
        cls.temp_hyst_max = temp_hyst_max

    @classmethod
    def set_hum_hyst_min(cls, hum_hyst_min): 
        cls.hum_hyst_min = hum_hyst_min

    @classmethod
    def set_hum_hyst_max(cls, hum_hyst_max): 
        cls.hum_hyst_max = hum_hyst_max

 

if __name__=='__main__':

    Growbox.init_actuators()
    Growbox.main_loop()
    

        

  
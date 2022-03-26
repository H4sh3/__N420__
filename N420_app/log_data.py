from pathlib import Path
import os
from datetime import datetime, timedelta
my_time = lambda: datetime.now().strftime("%m_%d_%Y-%H_%M_%S")

class Logger():
    def __init__(self, name):
        path ="data\\pictures"
        Path(path).mkdir(parents=True, exist_ok=True)  
        date = my_time()   
        name = f"{name}_log_{date}.txt"
        self.path = os.path.join(path, name)


    def get_path(self):
        return self.path

    def write(self, data):
        new_line = my_time() +  data + '\n'
        with open(self.path, 'a') as f:
            f.write(new_line)



if __name__ == '__main__':
    logger_data = Logger('data')
    logger_error = Logger('error')

    for i in range(100):
        try:
            logger_data.write(f'test{i}')
            n = 1/(i%10)
        except Exception as e:
            logger_error.write(repr(e))
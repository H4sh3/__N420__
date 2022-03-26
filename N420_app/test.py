


from tkinter import E
import pandas as pd
import json as js
import pandas as pd
import numpy as np


with open('data\pictures\data_log_03_26_2022-02_30_08.txt', 'r') as f:
            data =[js.loads(i[i.find('{'): i.rfind('}')+1]) for i in f.readlines()]
            df = pd.DataFrame(data)
            lengthPlot = 5 # int(options.pop('days'))  
            options = {'fan_state':'on', 'lamp_state':'on'}
            lengthData = len(df.index)   
            index = lengthData-lengthPlot
            index = lengthData-lengthPlot
            thisData = df.iloc[index:][[i for i in options]]
            try:
                max = thisData.select_dtypes(include=[np.number]).to_numpy().max()
                min = thisData.select_dtypes(include=[np.number]).to_numpy().min()
            except:
                max = 1
                min = 0
            for option in options:
                if thisData[option].iloc[0] == True or thisData[option].iloc[0] == False:
                    values = [max if i == True else min for i in thisData[option]]                
                    thisData[option] = values
            thisData['time'] = df['time'][index:]       
            thisData = df.reset_index().to_json(orient='records')
            
            
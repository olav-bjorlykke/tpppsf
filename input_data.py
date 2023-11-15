import pandas as pd
import numpy as np


class InputData:
    """
    The input Data class reads in and stores the input data in a pandas Dataframe, making it more accessible
    """
    temperatures = None
    TGC = None
    mortality_rates = None

    def __init__(self):
        pass

    def read_input_temperatures(self,filepath):
        file = open(filepath, "r")
        data = file.readlines()
        for i in range(len(data)):
            data[i] = data[i].split("(")
            data[i][0] = data[i][0].strip().split(" ")
            data[i][1] = data[i][1].strip()
        df = pd.DataFrame([elem[0] for elem in data],  columns=[i for i in range(len(data[0][0]))], index=[elem[1] for elem in data])
        return df

    def read_input_tgc(self,filepath):
        file = open(filepath,"r")
        data = file.readlines()
        for i in range(len(data)):
            data[i] = data[i].split("(")
            data[i][0] = data[i][0].strip().split(",")
            data[i][1] = data[i][1].strip()
        df = pd.DataFrame([elem[0] for elem in data], columns=[i for i in range(len(data[0][0]))],
                          index=[elem[1] for elem in data])
        return df

    def read_input_mortality_rates(self,filepath):
        file = open(filepath, "r")
        data = file.readlines()
        for i in range(len(data)):
            data[i] = data[i].strip().split(",")

        indices = [elem[0] for elem in data]
        rates = [elem[1:] for elem in data]

        df = pd.DataFrame(rates,index=indices, columns=[i for i in range(len(rates[0]))])
        return df








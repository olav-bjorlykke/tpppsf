import numpy as np
import pandas as pd


class Site:
    harvest_sets = None  # TODO: define
    growth_sets = None  # TODO: define
    number_periods = 60  # TODO: set as an input parameter
    max_periods_deployed = 19  # TODO: Set as an input parameter

    def __init__(self,
                 temperatures,
                 capacity,
                 init_biomass,
                 TGC_array,
                 ):
        self.temp_array = temperatures
        self.TGC_array = TGC_array
        self.capacity = capacity
        self.init_biomass = init_biomass
        self.weight_frame = self.calculate_weight_frame()
        self.growth_frame = self.calculate_growth_frame(self.weight_frame)


    def growth_factor(self, weight, TGC, temperature, duration): #TODO:put into its own class or set of functions
        new_weight = (weight**(1/3) + (1/1000)*TGC*temperature*duration)**(3)
        G = new_weight/weight
        return G

    def weight_growth(self, weight, TGC, temperature, duration): #TODO: put into its own class or set of fucntions along with growth factor
        new_weight = (weight**(1/3) + TGC*temperature*duration/1000)**(3)
        return new_weight

    def calculate_weight_frame(self, init_weight=250):
        weight_array = np.zeros((self.number_periods, self.number_periods))
        for i in range(self.number_periods):
            weight_array[i][i] = init_weight
            for j in range(i, min(self.number_periods - 1, i + self.max_periods_deployed)):
                weight = weight_array[i][j]
                weight_array[i][j + 1] = self.weight_growth(weight, temperature=self.temp_array[j], TGC=self.TGC_array[j-i],duration=30)

        weight_df = pd.DataFrame(weight_array, columns=[i for i in range(self.number_periods)], index=[i for i in range(self.number_periods)])
        return weight_df

    def calculate_growth_frame(self, weight_frame):
        growth_array = np.zeros((self.number_periods, self.number_periods))
        for i in range(self.number_periods):
            for j in range(i, min(self.number_periods - 1, i + self.max_periods_deployed)):
                growth_array[i][j] = weight_frame.iloc[i][j+1]/weight_frame.iloc[i][j]

        growth_df = pd.DataFrame(growth_array, columns=[i for i in range(self.number_periods)],index=[i for i in range(self.number_periods)])
        return growth_df








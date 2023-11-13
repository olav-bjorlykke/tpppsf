import numpy as np

import constants
import pandas as pd


class Site:
    def __init__(self,
                 temperatures,
                 capacity,
                 init_biomass,
                 ):
        self.temp_array = temperatures
        self.capacity = capacity
        self.init_biomass = init_biomass
        self.growth_data_frame = self.calculate_growth_frame()

    def G(self, temp, weight):
        if weight == 0:
            return 0
        return 1.3

    def calculate_growth_frame(self):
        growth_array = np.zeros((constants.NUMBER_PERIODS, constants.NUMBER_PERIODS, 2))
        for i in range(constants.NUMBER_PERIODS):
            # Sets the deployment weight to be 150 grams
            growth_array[i][i] = [150, 0]
        for i in range(constants.NUMBER_PERIODS):
            # Iterate through every reease period
            for j in range(i, min(i + constants.MAX_PERIODS_DEPLOYED, constants.NUMBER_PERIODS)):
                # For every release period, iterate through the possible periods employed and determine the growth factor and weight
                weight_previous = growth_array[i][j - 1][0]
                growth_factor = self.G(1, weight_previous)
                if weight_previous != 0.0:
                    growth_array[i][j][0] = weight_previous * growth_factor
                    growth_array[i][j][1] = growth_factor

        return growth_array


import numpy as np
import pandas as pd


class Site:
    """
    EXPLANATION OF CLASS:
    This class shall contain all the necessarry data to solve the tactical production planning problem for a single site
    """


    harvest_sets = None  # TODO: define                             #Sets where harvest is allowed given a certain deploy period
    growth_sets = None  # TODO: define                              #Set of periods where havest is not allowed given a certain deploy period
    number_periods = 60  # TODO: set as an input parameter          #Number of periods in the planning problem
    max_periods_deployed = 19  # TODO: Set as an input parameter    #Max number of sets that a cohort can be deployed

    def __init__(self,
                 temperatures,
                 capacity,
                 init_biomass,
                 TGC_array,
                 ):
        self.temp_array = temperatures                                            #Temperature array of temperatures for all periods in the planning horizon
        self.TGC_array = TGC_array                                                #Array of all TGC for a possible deploy period
        self.capacity = capacity                                                  #Max capacity at a single site
        self.init_biomass = init_biomass                                          #Initial biomass at the site, i.e biomass in the first period
        self.weight_frame = self.calculate_weight_frame()                         #A dataframe containing expected weight developments for all possible release periods
        self.growth_frame = self.calculate_growth_frame(self.weight_frame)        #A dataframe containing expected growth coefficient for all possible deployments of salmon


    def growth_factor(self, weight, TGC, temperature, duration): #TODO:put into its own class or set of functions
        """
        A function for calculating the growth factor for one period
        :param weight: the weight of an individual salmon in the growth period
        :param TGC: The growth coefficient
        :param temperature: The average sea temperature in the period
        :param duration: The duration of the period in days
        :return: A float G which is the growth factor
        """
        new_weight = (weight**(1/3) + (1/1000)*TGC*temperature*duration)**(3)
        G = new_weight/weight
        return G

    def weight_growth(self, weight, TGC, temperature, duration): #TODO: put into its own class or set of fucntions along with growth factor
        """
        A function calculating the weight of a single salmon in period t+1, given the weight in period t. The calculation is based on Aasen(2021) and Thorarensen & Farrel (2011)
        :param weight: weight in period t
        :param TGC: the growth coefficient in period t
        :param temperature: the average sea temperature in period t
        :param duration: the duration of period t
        :return: new_weight, a float that defines the expected weight in period t+1
        """
        new_weight = (weight**(1/3) + TGC*temperature*duration/1000)**(3)
        return new_weight

    def calculate_weight_frame(self, init_weight=100):
        """
        A function that calculates the expected weigh development for all possible release periods in a planning horizon
        :param init_weight: The deploy weight of a Salmon
        :return: weight_df  -  an array containing expected weight development for every possible release period and subsequent growth and harvest periods
        """
        #Defining a weight array to contain the calculated data
        weight_array = np.zeros((self.number_periods, self.number_periods))
        for i in range(self.number_periods):
            #Iterate through all possible release periods i and set the initial weight
            weight_array[i][i] = init_weight
            for j in range(i, min(self.number_periods - 1, i + self.max_periods_deployed)):
                #Iterate through all possible growth periods j given release period i
                #Calculate the weight for period j+1 given the weight in period j using weight_growth() function and put into the array
                weight = weight_array[i][j]
                weight_array[i][j + 1] = self.weight_growth(weight, temperature=self.temp_array[j], TGC=self.TGC_array[j-i],duration=30)
        #Read data from array into dataframe
        weight_df = pd.DataFrame(weight_array, columns=[i for i in range(self.number_periods)], index=[i for i in range(self.number_periods)])
        return weight_df

    def calculate_growth_frame(self, weight_frame):
        """
        A function that calculates a growth factor for every possible relase and subsequent growth and harvest period. The growth factor indicates the growth from a period t to a period t+1
        :param weight_frame: The weight frame is a dataframe containing all possible weight developments.
        :return: growth_df  -  A dataframe with all the growth factors for every possible period
        """
        #Declare a growth_factor array containing all calculated growth factors
        growth_array = np.zeros((self.number_periods, self.number_periods))
        for i in range(self.number_periods):
            #Iterate through all possible release periods i
            for j in range(i, min(self.number_periods - 1, i + self.max_periods_deployed)):
                # Iterate through all possible growth periods j given release period i
                # Calculate the growth factor, using expected weight developments from the weight fram and input into array
                growth_array[i][j] = weight_frame.iloc[i][j+1]/weight_frame.iloc[i][j]
        #Read data from array into dataframe
        growth_df = pd.DataFrame(growth_array, columns=[i for i in range(self.number_periods)],index=[i for i in range(self.number_periods)])
        return growth_df








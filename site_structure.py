import numpy as np
import pandas as pd


class Site:
    """
    EXPLANATION OF CLASS:
    This class shall contain all the necessary data to solve the tactical production planning problem for a single site
    """
    #Callable parameters
    harvest_sets = None  # TODO: define                             #Sets where harvest is allowed given a certain deploy period
    growth_sets = None  # TODO: define                              #Set of periods where havest is not allowed given a certain deploy period
    number_periods = 60  # TODO: set as an input parameter          #Number of periods in the planning problem
    max_periods_deployed = 19  # TODO: Set as an input parameter    #Max number of sets that a cohort can be deployed
    capacity = None
    init_biomass = None
    growth_frames = None

    #Parameters for calculations within this class
    TGC_array = None
    scenario_temperatures = None



    def __init__(self,
                 scenario_temperatures,
                 capacity,
                 init_biomass,
                 TGC_array,
                 possible_smolt_weights
                 ):
        self.TGC_array = TGC_array                                                #Array of all TGC for a possible deploy period
        self.capacity = capacity                                                  #Max capacity at a single site
        self.init_biomass = init_biomass                                          #Initial biomass at the site, i.e biomass in the first period
        self.possible_smolt_weights = possible_smolt_weights                                 #Global parameters object containing the global parameters
        self.scenario_temperatures = scenario_temperatures
        self.growth_frames = self.calculate_growth_frame_for_scenarios_and_smolt_weights(possible_smolt_weights, scenario_temperatures)

    def calculate_growth_frame_for_scenarios_and_smolt_weights(self, smolt_weights, scenarios_temperatures):
        data_storage = []
        for weight in smolt_weights:
            scenario_growth_frames_given_weight = self.calculate_growth_frame_for_scenarios(weight, scenarios_temperatures)
            data_storage.append(scenario_growth_frames_given_weight)

        growth_frame_all_scenarios_and_weights = pd.concat(data_storage, keys=smolt_weights)
        return growth_frame_all_scenarios_and_weights

    def calculate_growth_frame_for_scenarios(self, smolt_weight, scenarios_temperatures):
        data_storage = []
        for i in range(len(scenarios_temperatures.index)):
            temp_array = scenarios_temperatures.iloc[i]
            scenario_growth_frame = self.calculate_growth_frame(self.calculate_weight_frame(temp_array,smolt_weight))
            data_storage.append(scenario_growth_frame)



        growth_frame_all_scenarios = pd.concat(data_storage, keys=scenarios_temperatures.index)
        return growth_frame_all_scenarios


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

    def calculate_weight_frame(self, temp_array, init_weight=100):
        """
        A function that calculates the expected weigh development for all possible release periods in a planning horizon
        :param init_weight: The deploy weight of a Salmon
        :return: weight_df  -  an array containing expected weight development for every possible release period and subsequent growth and harvest periods
        """
        #Defining a weight array to contain the calculated data
        temp_array = np.tile(temp_array, 5) #TODO: Remove this and define the scenario temperatures for 60 periods
        weight_array = np.zeros((self.number_periods, self.number_periods))
        for i in range(self.number_periods):
            #Iterate through all possible release periods i and set the initial weight
            weight_array[i][i] = init_weight
            for j in range(i, min(self.number_periods - 1, i + self.max_periods_deployed)):
                #Iterate through all possible growth periods j given release period i
                #Calculate the weight for period j+1 given the weight in period j using weight_growth() function and put into the array
                weight = weight_array[i][j]
                weight_array[i][j + 1] = self.weight_growth(weight, temperature=temp_array[j], TGC=self.TGC_array[j-i],duration=30)
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








import numpy as np
import pandas as pd


class Site:
    """
    EXPLANATION OF CLASS:
    This class shall contain all the necessary data to solve the tactical production planning problem for a single site
    """
    #Callable parameters
    growth_sets = None  # TODO: define                              #Set of periods where havest is not allowed given a certain deploy period
    max_periods_deployed = 19  # TODO: Get from the size of the TGC array    #Max number of sets that a cohort can be deployed
    capacity = None
    init_biomass = None
    growth_per_scenario_df = None
    weight_development_per_scenario_df = None


    #Parameters for calculations within this class
    TGC_array = None
    scenario_temperatures = None



    def __init__(self,
                 scenario_temperatures,
                 capacity,
                 init_biomass,
                 TGC_array,
                 possible_smolt_weights,
                 weight_req_for_harvest
                 ):
        #Setting class variables
        self.TGC_array = TGC_array                                                #Array of all TGC for a possible deploy period
        self.capacity = capacity                                                  #Max capacity at a single site
        self.init_biomass = init_biomass                                          #Initial biomass at the site, i.e biomass in the first period
        self.possible_smolt_weights = possible_smolt_weights                                 #Global parameters object containing the global parameters
        self.scenario_temperatures = scenario_temperatures

        #Calulating growth and weight development dataframes for all scenarios and possible smolt weights
        self.growth_per_scenario_df = self.calculate_growth_df_for_scenarios_and_smolt_weights(possible_smolt_weights, scenario_temperatures)
        self.weight_development_per_scenario_df = self.calculate_weight_df_for_scenarios_and_smolt_weights(possible_smolt_weights, scenario_temperatures)

        #Calculating the growth sets
        self.growth_sets = self.calculate_growth_sets_from_weight_dev_df(self.weight_development_per_scenario_df, weight_req_for_harvest)


    def calculate_growth_sets_from_weight_dev_df(self, weight_development_df, weight_req_for_harvest):
        data_storage = []
        weights = weight_development_df.index.get_level_values("weight").unique()
        scenarios = weight_development_df.index.get_level_values("scenario").unique()
        print("Here", weights, scenarios)
        for weight in weights:
            scenario_growth_sets = []
            for scenario in scenarios:
                growth_sets = self.calculate_growth_sets_for_single_scenario_and_weight(weight_development_df.loc[(weight,scenario)], weight_req_for_harvest)
                scenario_growth_sets.append(growth_sets)
                print()

            scenario_df = pd.DataFrame(scenario_growth_sets, index=scenarios)
            data_storage.append(scenario_df)

        growth_sets_df = pd.concat(data_storage, keys=weights)

        return growth_sets_df

    def calculate_growth_sets_for_single_scenario_and_weight(self, weight_development_df, weight_req_for_harvest):
        growth_set_array = []
        for i in range(weight_development_df.index.size):
            for j in range(len(weight_development_df.iloc[i])):
                if weight_development_df.iloc[i][j] > weight_req_for_harvest:
                    growth_set_array.append([i,j])
                    break

        return growth_set_array


    def calculate_weight_df_for_scenarios_and_smolt_weights(self, smolt_weights, scenarios_temperatures):
        """
               EXPLANATION: Calculates the weight development, for all smolt weights, for very scenario, release period and subsequent growth periods.

               :param smolt_weights: An array containing all possible smolt weights for release
               :param scenarios_temperatures: A dataframe containing temperaturs for all scenarios
               :return: growth_frame_all_scenarios_and_weights - a 4-D dataframe with the data described in the explanation.
               """

        data_storage = []
        for weight in smolt_weights:
            scenario_weight_frames_given_weight = self.calculate_weight_df_for_scenarios(weight, scenarios_temperatures)
            data_storage.append(scenario_weight_frames_given_weight)

        weight_frame_all_scenarios_and_weights = pd.concat(data_storage, keys=smolt_weights)

        #Naming the indexes for easier access
        weight_frame_all_scenarios_and_weights.index.names = ["weight", "scenario", "period"]
        return weight_frame_all_scenarios_and_weights

    def calculate_weight_df_for_scenarios(self, smolt_weight, scenarios_temperatures):
        """
                EXPLANATION: Calculates the expected weight for every period, following every possible release in every scenario for a given smolt weight.

                :param smolt_weight: The weight of the smolt at release
                :param scenarios_temperatures: a dataframe containing the temperatures for all scenarios across the planning period
                :return: growth_frame_all_scenarios - a 3-D dataframe containing the growth factor for every period, following every release and every scenario.
                """

        data_storage = []
        for i in range(len(scenarios_temperatures.index)):
            temp_array = scenarios_temperatures.iloc[i]
            scenario_weight_frame = self.calculate_weight_df(temp_array, smolt_weight)
            data_storage.append(scenario_weight_frame)

        weight_frame_all_scenarios = pd.concat(data_storage, keys=scenarios_temperatures.index)
        return weight_frame_all_scenarios

    def calculate_growth_df_for_scenarios_and_smolt_weights(self, smolt_weights, scenarios_temperatures):
        """
        EXPLANATION: Calculates the growth factor, for all smolt weights, for very scenario, release period and subsequent growth periods.

        :param smolt_weights: An array containing all possible smolt weights for release
        :param scenarios_temperatures: A dataframe containing temperaturs for all scenarios
        :return: growth_frame_all_scenarios_and_weights - a 4-D dataframe with the data described in the explanation.
        """


        data_storage = []
        for weight in smolt_weights:
            scenario_growth_frames_given_weight = self.calculate_growth_df_for_scenarios(weight, scenarios_temperatures)
            data_storage.append(scenario_growth_frames_given_weight)

        growth_frame_all_scenarios_and_weights = pd.concat(data_storage, keys=smolt_weights)
        return growth_frame_all_scenarios_and_weights

    def calculate_growth_df_for_scenarios(self, smolt_weight, scenarios_temperatures):
        """
        EXPLANATION: Calculates the growth factor for every period, following every possible release in every scenario for a given smolt weight.

        :param smolt_weight: The weight of the smolt at release
        :param scenarios_temperatures: a dataframe containing the temperatures for all scenarios across the planning period
        :return: growth_frame_all_scenarios - a 3-D dataframe containing the growth factor for every period, following every release and every scenario.
        """

        data_storage = []
        for i in range(len(scenarios_temperatures.index)):
            temp_array = scenarios_temperatures.iloc[i]
            scenario_growth_frame = self.calculate_growth_df_from_weight_df(self.calculate_weight_df(temp_array, smolt_weight))
            data_storage.append(scenario_growth_frame)



        growth_frame_all_scenarios = pd.concat(data_storage, keys=scenarios_temperatures.index)
        return growth_frame_all_scenarios

    def calculate_growth_factor(self, weight, TGC, temperature, duration): #TODO:put into its own class or set of functions
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

    def calculate_weight_development(self, weight, TGC, temperature, duration): #TODO: put into its own class or set of fucntions along with growth factor
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

    def calculate_weight_df(self, temp_array, init_weight=100):
        """
        A function that calculates the expected weigh development for all possible release periods in a planning horizon
        :param init_weight: The deploy weight of a Salmon
        :return: weight_df  -  an array containing expected weight development for every possible release period and subsequent growth and harvest periods
        """
        #Defining a weight array to contain the calculated data
        number_periods = len(temp_array)
        weight_array = np.zeros((number_periods, number_periods))
        for i in range(number_periods):
            #Iterate through all possible release periods i and set the initial weight
            weight_array[i][i] = init_weight
            for j in range(i, min(number_periods - 1, i + self.max_periods_deployed)):
                #Iterate through all possible growth periods j given release period i
                #Calculate the weight for period j+1 given the weight in period j using weight_growth() function and put into the array
                weight = weight_array[i][j]
                weight_array[i][j + 1] = self.calculate_weight_development(weight, temperature=temp_array[j], TGC=self.TGC_array[j - i], duration=30)
        #Read data from array into dataframe
        weight_df = pd.DataFrame(weight_array, columns=[i for i in range(number_periods)], index=[i for i in range(number_periods)])
        return weight_df

    def calculate_growth_df_from_weight_df(self, weight_frame):
        """
        A function that calculates a growth factor for every possible relase and subsequent growth and harvest period. The growth factor indicates the growth from a period t to a period t+1
        :param weight_frame: The weight frame is a dataframe containing all possible weight developments.
        :return: growth_df  -  A dataframe with all the growth factors for every possible period
        """
        #Getting the number of periods from the growth array
        number_periods = weight_frame[0].size
        #Declare a growth_factor array containing all calculated growth factors
        growth_array = np.zeros((number_periods, number_periods))
        for i in range(number_periods):
            #Iterate through all possible release periods i
            for j in range(i, min(number_periods - 1, i + self.max_periods_deployed)):
                # Iterate through all possible growth periods j given release period i
                # Calculate the growth factor, using expected weight developments from the weight fram and input into array
                growth_array[i][j] = weight_frame.iloc[i][j+1]/weight_frame.iloc[i][j]
        #Read data from array into dataframe
        growth_df = pd.DataFrame(growth_array, columns=[i for i in range(number_periods)],index=[i for i in range(number_periods)])
        return growth_df








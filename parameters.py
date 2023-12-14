import numpy as np
import pandas as pd

class GlobalParameters:
    smolt_deployment_upper_bound = 2400000 #Upper bound for number of smolt deployed
    smolt_deployment_lower_bound = 10000 #Lower bound of smolt deployed
    max_harvest = 2000 * 1000 #Max biomass that can be harvested in any period in tons
    min_harvest = 100 *1000 #Minimum amount of biomass that can be harvested if biomass is harvested in tons
    max_harvest_company = 6000 * 1000 #Max biomass that can be havested across the company in tons, currently unlimited
    expected_production_loss = 0.002 #Expected loss per period
    MAB_company_limit = 5000 * 1000 #Max biomass deployed across the company
    MAB_site_limit = 3000 * 1000 #TODO: This is a placeholder, get the real thing from the site datastructure
    smolt_type_df = pd.DataFrame( #All possible smolt type and weights, with corresponding number of smolt per kilo
        data=[[100,10],[150,6.66],[250,4]],
        columns=["weight","num-smolt-kilo"]
    )
    smolt_weights = [100,250]
    min_fallowing_periods = 2
    max_fallowing_periods = 36
    max_periods_deployed = 24
    number_periods = 60
    temp_growth_period = 6 #TODO: implement this stochastically
    bigM = 100000000
    weight_req_for_harvest = 3000.0
    scenario_probabilities = [0.1, 0.8, 0.1]

    def __init__(self):
        pass


global_parameters = GlobalParameters()
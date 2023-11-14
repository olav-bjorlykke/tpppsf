import numpy as np
import pandas as pd

class GlobalParameters:
    scenario_probabilities = np.array([0.2,0.2,0.6]) #Probability for every scenario
    smolt_deployment_upper_bound = 1000000 #Upper bound for smolt deployed
    smolt_deployment_lower_bound = 10000 #Lower bound of smolt deployed
    max_harvest = 2000 * 1000 #Max biomass that can be harvested in any period in tons
    min_harvest = 100 *1000 #Minimum amount of biomass that can be harvested if biomass is harvested in tons
    max_harvest_company = 10000 * 1000 #Max biomass that can be havested across the company in tons, currently unlimited
    expected_production_loss = 0.005 #Expected loss per period
    MAB_company_limit = 16488 * 1000 #Max biomass deployed across the company
    MAB_site_limit = 3000 * 1000 #TODO: This is a placeholder, get the real thing from the site datastructure
    smolt_type_df = pd.DataFrame(
        data=[[100,10],[150,6.66],[250,4]],
        columns=["weight","num-smolt-kilo"]
    )
    min_fallowing_periods = 2
    max_fallowing_periods = 36
    growth_factor = 1.3 #TODO: This will have to be changed and put into its own set of preprocessing
    max_periods_deployed = 24
    temp_growth_period = 6 #TODO: implement this stochastically
    bigM = 100000000

    def __init__(self):
        pass



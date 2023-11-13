import numpy as np
import pandas as pd

class GlobalParameters:
    scenario_probabilities = np.array([0.2,0.2,0.6])
    smolt_upper_bound = 200000
    smolt_lower_bound = 5000
    max_harvest = 2000 #Max biomass that can be harvested in any period in tons
    min_biomass = 100 #Minimum amount of biomass that can be harvested if biomass is harvested in tons
    max_biomass_company = 100000000 #Max biomass that can be havested across the company in tons, currently unlimited
    expected_production_loss = 0.005 #Expected loss per period
    MAB_company_limit = 16488 #Max biomass deployed across the company
    smolt_type_df = pd.DataFrame(
        data=[[100,10],[150,6.66],[250,4]],
        columns=["weight","num-smolt-kilo"]
    )
    min_fallowing_periods = 2
    max_fallowing_periods = 36
    growth_factor = 1.3 #TODO: This will have to be changed and put into its own set of preprocessing

    def __init__(self):
        pass



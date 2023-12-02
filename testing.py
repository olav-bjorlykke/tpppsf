import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from sub_problem_class import SubProblem
from master_problem import MasterProblem


input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)

site_test_1 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Senja"],
    MAB_capacity=4000 * 1000,
    init_biomass=100 * 1000,
    init_avg_weight=2000,
    init_biomass_months_deployed=10,
    TGC_array=input_test.TGC_df.iloc[0],
    smolt_weights=[150, 200, 250],
    weight_req_for_harvest = 3000.0,
    site_name="Senja"
)

site_test_2 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Nord-Troms"],
    MAB_capacity=2200 * 1000,
    init_biomass=0,
    TGC_array=input_test.TGC_df.iloc[0],
    smolt_weights=[150, 200, 250],
    weight_req_for_harvest=3000.0,
    site_name="Nord-Troms"
)

site_test_3 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Vesteralen"],
    MAB_capacity=3500 * 1000,
    init_biomass=0,
    TGC_array=input_test.TGC_df.iloc[0],
    smolt_weights=[150, 200, 250],
    weight_req_for_harvest=3000.0,
    site_name="Vesteralen"
)

print(site_test_1.growth_sets)
print(site_test_1.calculate_weight_df(site_test_1.scenario_temps.iloc[1], smolt_weight=150))


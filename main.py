import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from sub_problem_class import SubProblem


input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)
site_test = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Senja"],
    capacity=1000,
    init_biomass=100,
    TGC_array=input_test.TGC_df.iloc[1],
    smolt_weights=[150, 200, 250],
    weight_req_for_harvest = 3000.0
)



sub_problem_test = SubProblem(
    input_data_obj=input_test,
    parameters_obj= GlobalParameters(),
    scenarios_obj=scenarios_test,
    site_obj=site_test
)

sub_problem_test.solve_and_print_model()


"""
growth_sets = site_test.growth_sets
growth_factor_df = site_test.growth_per_scenario_df.loc[(site_test.smolt_weights[0], f"Scenario 0", 1)][1]
print(growth_sets.loc[(site_test.smolt_weights[0], f"Scenario 0")])

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
print(growth_sets.loc[(site_test.smolt_weights[0])])
"""
#print("GROWTH SETS:", site_test.growth_sets)







#print(site_test.weight_development_per_scenario_df.index[1][0])










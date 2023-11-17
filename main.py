import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_structure import Site
from scenarios import Scenarios


input =InputData()

scenarios_test = Scenarios(input.temperatures_df)


site_test = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Senja"],
    capacity=1000,
    init_biomass=100,
    TGC_array=input.TGC_df.iloc[1],
    smolt_weights=[150, 200, 250],
    weight_req_for_harvest = 3000
)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print("GROWT SETS:", site_test.growth_sets)

site_test.weight_dev_per_scenario_df.index.names = ["weight", "scenario", "period"]






#print(site_test.weight_development_per_scenario_df.index[1][0])










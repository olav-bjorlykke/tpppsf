import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_structure import Site
from scenarios import Scenarios


input =InputData()

print(input.temperatures_df)

scenarios_test = Scenarios(input.temperatures_df)


site_test = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Senja"],
    capacity=1000,
    init_biomass=100,
    TGC_array=input.TGC_df.iloc[1],
    possible_smolt_weights=[150,200,250]
)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(site_test.growth_frames)










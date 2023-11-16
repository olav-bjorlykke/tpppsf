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
    possible_smolt_weights=[150,200,250]
)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(site_test.growth_frames)






"""
site = Site(
    temperatures=np.tile(input.temperatures_df.iloc[0].astype(float).to_numpy(),5),
    TGC_array=input.TGC_df.iloc[0].astype(float).to_numpy(),
    init_biomass=500,
    capacity=1000,
)

print(input.temperatures_df)
print(input.TGC_df)
print(input.mortality_rates_df)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(site.growth_frames.loc["250"])
print(site.growth_frames.loc["150"])
"""




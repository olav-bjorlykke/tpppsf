import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_structure import Site


input =InputData()

site = Site(
    temperatures=np.tile(input.temperatures_df.iloc[0].astype(float).to_numpy(),5),
    TGC_array=input.TGC_df.iloc[0].astype(float).to_numpy(),
    init_biomass=500,
    capacity=1000,
)

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

print(site.weight_frame)
print(site.growth_frame)






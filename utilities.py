import os

import pandas as pd

directory_path = './init_columns/'


for item in os.listdir(directory_path):
    df = pd.read_csv(directory_path + item, index_col=["Location", "Scenario", "Smolt type", "Deploy period", "Period"])
    df.to_excel(directory_path + item.split(".")[0] + ".xlsx")
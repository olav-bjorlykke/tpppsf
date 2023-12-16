import os

import pandas as pd

directory_path = './init_columns/'


for item in os.listdir(directory_path):
    if item.split(".")[1] == "csv":
        df = pd.read_csv(directory_path + item, index_col=["Location", "Scenario", "Smolt type", "Deploy period", "Period"])
        rounded_df = df.round(2)

        rounded_df.to_csv(directory_path + item.split(".")[0] + ".csv")
        rounded_df.to_excel(directory_path + item.split(".")[0] + ".xlsx")
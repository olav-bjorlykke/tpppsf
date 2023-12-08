import pandas as pd

def generate_zero_column(num_smolt_weight, num_scenarios):

    df_storage = []
    for s in range(num_scenarios):
        l1_df_storage = []
        for f in range(num_smolt_weight):
            l2_df_storage = []
            for deploy_period in range(1):
                l3_data_storage = []
                for t in range(60):
                    x_entry = 0
                    w_entry = 0
                    employ_entry = 0
                    harvest_entry = 0
                    deploy_entry = 0
                    deploy_type_entry = 0
                    l3_data_storage.append(
                        [x_entry, w_entry, employ_entry, harvest_entry, deploy_entry, deploy_type_entry])
                columns = ["X", "W", "Employ bin", "Harvest bin", "Deploy bin", "Deploy type bin"]
                index = [i + deploy_period for i in range(len(l3_data_storage))]
                l2_df_storage.append(pd.DataFrame(l3_data_storage, columns=columns, index=index))
            keys_l2 = [i for i in range(1)]
            l1_df_storage.append(pd.concat(l2_df_storage, keys=keys_l2))
        keys_l1 = [i for i in range(len(l1_df_storage))]
        df_storage.append(pd.concat(l1_df_storage, keys=keys_l1))
    keys = [i for i in range(len(df_storage))]
    df = pd.concat(df_storage, keys=keys)

    df.index.names = ["Scenario", "Smolt type", "Deploy period", "Period"]
    return df

do_nothing_column = generate_zero_column(num_smolt_weight=1,num_scenarios=2)
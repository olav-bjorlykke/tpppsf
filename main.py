import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from sub_problem_class import SubProblem
from master_poblem import MasterProblem


input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)
site_test_1 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Senja"],
    capacity=1000,
    init_biomass=100,
    TGC_array=input_test.TGC_df.iloc[0],
    smolt_weights=[150, 200, 250],
    weight_req_for_harvest = 3000.0
)

site_test_2 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Nord-Troms"],
    capacity=1200,
    init_biomass=0,
    TGC_array=input_test.TGC_df.iloc[0],
    smolt_weights=[150, 200, 250],
    weight_req_for_harvest=3000.0
)

site_test_3 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc["Vesteralen"],
    capacity=1200,
    init_biomass=0,
    TGC_array=input_test.TGC_df.iloc[0],
    smolt_weights=[150, 200, 250],
    weight_req_for_harvest=3000.0
)


sub_problem_test_1 = SubProblem(
    input_data_obj=input_test,
    parameters_obj= GlobalParameters(),
    scenarios_obj=scenarios_test,
    site_obj=site_test_1
)


sub_problem_test_2 = SubProblem(
    input_data_obj=input_test,
    parameters_obj=GlobalParameters(),
    scenarios_obj=scenarios_test,
    site_obj=site_test_2
)

sub_problem_test_3 = SubProblem(
    input_data_obj=input_test,
    parameters_obj=GlobalParameters(),
    scenarios_obj=scenarios_test,
    site_obj=site_test_3
)

sub_problem_test_1.solve_and_print_model()
sub_problem_test_2.solve_and_print_model()
sub_problem_test_3.solve_and_print_model()

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

df_1 = sub_problem_test_1.get_second_stage_variables_df(sub_problem_test_1.get_deploy_period_list())
df_2 = sub_problem_test_2.get_second_stage_variables_df(sub_problem_test_2.get_deploy_period_list())
df_3 = sub_problem_test_3.get_second_stage_variables_df(sub_problem_test_3.get_deploy_period_list())



df = pd.concat([df_1,df_2], keys=["Nord-troms", "Senja"])
new_df_3 = pd.concat([df_3], keys=["Vesteralen"])

new_df = pd.concat([df,new_df_3])
new_df.index.names = ["Location", "Scenario", "Smolt type", "Deploy Period", "Period"]
print(new_df.index, new_df.index.names)


master_poblem_test = MasterProblem()

master_poblem_test.add_first_column(new_df)
master_poblem_test.add_new_column_to_columns(new_df)

master_poblem_test.columns.to_excel("master_problem.xlsx", index=True)


# Write the DataFrame to an Excel file







#print(site_test.weight_development_per_scenario_df.index[1][0])










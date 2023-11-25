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
    MAB_capacity=4000 * 1000,
    init_biomass=100,
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

sub_problems = [sub_problem_test_1, sub_problem_test_2, sub_problem_test_3]

# Solving the sub problems
sub_problem_test_1.solve_and_print_model()
sub_problem_test_2.solve_and_print_model()
sub_problem_test_3.solve_and_print_model()

# Setting column dataframes
df_1 = sub_problem_test_1.get_second_stage_variables_df()
df_2 = sub_problem_test_2.get_second_stage_variables_df()
df_3 = sub_problem_test_3.get_second_stage_variables_df()

# Concatinating into a single columns
df = pd.concat([df_1, df_2, df_3], keys=[i for i in range(len([df_1, df_2, df_3]))])


master_poblem = MasterProblem(
    parameters=GlobalParameters(),
    scenarios=scenarios_test,
    initial_column=df
)

shadow_prices = None
lambda_list = []

for i in range(5):
    #Solving the sub problems
    sub_problem_test_1.solve_and_print_model()
    sub_problem_test_2.solve_and_print_model()
    sub_problem_test_3.solve_and_print_model()

    #Setting column dataframes
    df_1 = sub_problem_test_1.get_second_stage_variables_df()
    df_2 = sub_problem_test_2.get_second_stage_variables_df()
    df_3 = sub_problem_test_3.get_second_stage_variables_df()

    #Concatinating into a single columns
    df = pd.concat([df_1, df_2, df_3], keys=[i for i in range(len([df_1, df_2, df_3]))])

    #Adds the new column to the master problem
    master_poblem.add_new_column_to_columns_df(df)

    #Solving the master problem
    master_poblem.run_and_solve_master_problem()

    lambda_list.append(master_poblem.get_results_df())

    #Printing the shadow prices to the shadow prices variable
    shadow_prices = master_poblem.get_MAB_constr_shadow_prices_df()

    #Putting shadow prices into subproblem
    sub_problem_test_1.set_shadow_prices_df(shadow_prices)
    sub_problem_test_2.set_shadow_prices_df(shadow_prices)
    sub_problem_test_3.set_shadow_prices_df(shadow_prices)

    #Repeat flow

for elem in lambda_list:
    print(elem)
from site_class import Site
from input_data import InputData
from scenarios import Scenarios
from monolithic_model import MonolithicProblem

input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)

area_vesteralen_string = "Vesteralen"
area_nordtroms_string = "Nord-Troms"
area_senja_string = "Senja"

site_4 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_vesteralen_string],
    MAB_capacity=3120*1000,
    site_name="KUNESET"
)

site_16 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_nordtroms_string],
    MAB_capacity=5000*1000,
    site_name="HAUKØYA Ø",
)

site_12 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_senja_string],
    MAB_capacity=3600*1000,
    init_biomass=1600 * 1000,
    init_avg_weight=6536,
    init_biomass_months_deployed=18,
    site_name="FLESEN"
)

site_13 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_senja_string],
    MAB_capacity=3900*1000,
    site_name="KVENBUKTA V"
)

mon_test = MonolithicProblem(
    [site_12, site_4, site_13]
)

mon_test.create_initial_columns()

test_df = mon_test.get_solution_df_from_csv("./init_columns/column_s2_l2.csv")
print(test_df.head(n=5))
test_df.to_excel("test_csv_excel.xlsx")

from site_class import Site
from input_data import InputData
from scenarios import Scenarios
from monolithic_model import MonolithicProblem

input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)

area_vesteralen_string = "Vesteralen"
area_nordtroms_string = "Nord-Troms"
area_senja_string = "Senja"

site_16 = Site(
    scenario_temperatures=scenarios_test.scenario_temperatures_per_site_df.loc[area_nordtroms_string],
    MAB_capacity=5000*1000,
    site_name="HAUKØYA Ø",
)


mon_test = MonolithicProblem(
    site_16
)

mon_test.solve_and_print_model()
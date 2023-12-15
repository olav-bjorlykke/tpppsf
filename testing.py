from site_class import Site
from input_data import InputData
from scenarios import Scenarios
from monolithic_model import MonolithicProblem
import subproblem_list

input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)

area_vesteralen_string = "Vesteralen"
area_nordtroms_string = "Nord-Troms"
area_senja_string = "Senja"



mon_test = MonolithicProblem(
    subproblem_list.short_sites_list
)

mon_test.create_initial_columns()



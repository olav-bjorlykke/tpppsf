from site_class import Site
from input_data import InputData
from scenarios import Scenarios
from monolithic_model import SubProblem
import subproblem_list

input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)

area_vesteralen_string = "Vesteralen"
area_nordtroms_string = "Nord-Troms"
area_senja_string = "Senja"



mon_test = SubProblem(
    subproblem_list.SITE_LIST
)

test = mon_test.create_initial_columns()



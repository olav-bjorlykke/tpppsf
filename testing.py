from site_class import Site
from input_data import InputData
from scenarios import Scenarios
from model import Model
import subproblem_list
import time

input_test =InputData()
scenarios_test = Scenarios(input_test.temperatures_df)

area_vesteralen_string = "Vesteralen"
area_nordtroms_string = "Nord-Troms"
area_senja_string = "Senja"

start_time = time.perf_counter()

model = Model(
    subproblem_list.SITE_LIST
)

model.solve_and_print_model()

model.plot_solutions_agregate_vs_MAB_limit()
model.print_solution_to_excel()

end_time = time.perf_counter()
duration = end_time - start_time
model.write_objective_value_to_file(duration)



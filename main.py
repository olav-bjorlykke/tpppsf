import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from sub_problem_class import SubProblem
from master_problem import MasterProblem
from node import Node
import subproblem_list
from orchestration_class import Orchestration


orchestration = Orchestration(
    subproblems=subproblem_list.short_sub_problem_list
)

orchestration.run_branching_algorithm()

for node_label in orchestration.explored_nodes:
    print("ITERATION", node_label.iterations_number)
    print("UP LIST",node_label.up_list)
    print("DOWN LIST", node_label.down_list)
    print("LOWER BOUND", node_label.lower_bound)





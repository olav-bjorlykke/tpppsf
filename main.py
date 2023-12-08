import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from sub_problem_class import SubProblem
from master_problem import MasterProblem
from node import Node
import time
import subproblem_list
from orchestration_class import Orchestration


orchestration = Orchestration(
    subproblems=subproblem_list.medium_sub_problem_list
)

orchestration.run_branching_algorithm()

orchestration.print_explored_node_to_file(orchestration.explored_nodes)





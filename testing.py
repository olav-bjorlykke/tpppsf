import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from sub_problem_class import SubProblem
from master_problem import MasterProblem
from orchestration_class import Orchestration
import subproblem_list

orchestration = Orchestration(
    subproblems=subproblem_list.sub_problem_list
)

orchestration.run_one_node_in_branch_and_price()


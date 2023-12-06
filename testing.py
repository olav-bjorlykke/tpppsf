import numpy as np
import pandas as pd
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
from sub_problem_class import SubProblem
from master_problem import MasterProblem
from orchestration_class import Orchestration
from node import Node
from orchestration_class import NodeLabel
#import subproblem_list



node_label_test_1 = NodeLabel(
            iterations_number=1,
            parent=1,
            up_list= [[1,2]],
            down_list=[[2,3],[4,2]],
            upper_bound=1000.0,
            feasible_solution=5500005.0
)

node_label_test_2 = NodeLabel(
            iterations_number=2,
            parent=1,
            up_list= [[1,2]],
            down_list=[[2,3],[4,2]],
            upper_bound=1000.0,
            feasible_solution=5500005.0
)

""" 
orchestration = Orchestration(
    subproblems=subproblem_list.short_sub_problem_list
)

orchestration.print_explored_node_to_file([node_label_test_1, node_label_test_2])
"""



node_label_test_1.print_node_label_to_file(20000)
node_label_test_2.print_node_label_to_file(1450)



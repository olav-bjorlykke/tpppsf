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
import subproblem_list



node = Node(
    subproblems=subproblem_list.short_sub_problem_list
)

node.solve_node_to_optimality()

node.set_up_branching_constraint()

print("#######################\n",
"#######################\n",
"#######################\n",
"#######################\n"
      )

for subproblem in node.sub_problems:
    print(subproblem.branching_variable_indices_up)

print(node.master_problem.branched_variable_indices_up)

node.solve_node_to_optimality()

node.set_up_branching_constraint()

print("#######################\n",
"#######################\n",
"#######################\n",
"#######################\n"
      )

for subproblem in node.sub_problems:
    print(subproblem.branching_variable_indices_up)

print(node.master_problem.branched_variable_indices_up)

node.solve_node_to_optimality()

node.set_up_branching_constraint()

print("#######################\n",
"#######################\n",
"#######################\n",
"#######################\n"
      )

for subproblem in node.sub_problems:
    print(subproblem.branching_variable_indices_up)

print(node.master_problem.branched_variable_indices_up)
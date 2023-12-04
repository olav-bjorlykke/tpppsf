import copy

import pandas as pd
from master_problem import MasterProblem
from node import Node

class Orchestration:
    """
    This is a class for orchestrating the interplay between the master and the sub-problem,
    running the Branch and Price framework for solving the Dantzig-Wolfe decomposition with column generation
    """


    def __init__(self,
                 subproblems,
                 ):
        self.sub_problems = subproblems
        self.unexplored_nodes = [Node(subproblems)]
        self.explored_nodes = []
        self.lower_bound = 0
        self.upper_bound = 1000000000000000 #TODO: this is supposed to represent infinity, find a more elegant way to achieve that


    def run_branching_algorithm(self):


        #Repeat while there are more unexplored child nodes or we reach the desired optimality gap

        pass



class NodeLabels:
    def __init__(self,
                 iterations_number,
                 parent,
                 up_list,
                 down_list
                 ):
        self.iterations_number = iterations_number
        self.parent = parent
        self.up_list = up_list
        self.down_list = down_listgi

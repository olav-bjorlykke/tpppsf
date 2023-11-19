import gurobipy as gp
from gurobipy import GRB


class MasterProblem:
    def __init__(self,
                 columns
                 ):
        self.model = gp.Model("Master Problem")
        self.columns = columns

    def set_objective(self):
        #TODO: define this function
        pass

    def add_constraints(self):
        #TODO: define this function
        pass

    def solve_and_print_solution(self):
        #TODO: define this function
        pass

    def get_reduced_costs(self):
        #TODO: define this function
        pass

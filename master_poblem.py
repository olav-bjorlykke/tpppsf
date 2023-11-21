import gurobipy as gp
from gurobipy import GRB
import pandas as pd


class MasterProblem:
    iterations_counter_k = 0
    num_locations = 3
    def __init__(self,
                 ):
        self.model = gp.Model("Master Problem")



    def add_new_column_to_columns(self, new_column):
        new_column_formated = pd.concat([new_column], keys=[f"Iteration {self.iterations_counter_k}"])
        columns = pd.concat([self.columns, new_column_formated])
        self.columns = columns
        self.iterations_counter_k += 1

    def add_first_column(self, column):
        self.columns = pd.concat([column], keys=[f"Iteration {self.iterations_counter_k}"])
        self.columns.index.names = ["Iteration","Location", "Scenario", "Smolt type", "Deploy Period", "Period"]
        self.iterations_counter_k += 1



    def declare_variables(self):
        self.lambda_var = self.model.addVars(self.num_locations, self.iterations_counter_k, vtype=GRB.CONTINUOUS)



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

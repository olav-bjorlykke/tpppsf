import pandas as pd
from master_problem import MasterProblem

class Orchestration:
    """
    This is a class for orchestrating the interplay between the master and the sub-problem,
    running the Branch and Price framework for solving the Dantzig-Wolfe decomposition with column generation
    """
    sub_problems = []
    master_problem = None
    branched_variables = []


    def __init__(self,
                 subproblems,
                 ):
        self.sub_problems = subproblems
        self.master_problem = MasterProblem(self.generate_initial_columns())



    def generate_initial_columns(self):
        #Storage for the dataframes containing the sub problem results
        new_column = []
        #Iterating through every column in the subproblems list
        for sub_problem in self.sub_problems:
            #Solving the sub problem
            sub_problem.solve_initial_model()
            #Adding the results df from the solved model to the list
            new_column.append(sub_problem.get_second_stage_variables_df())

        #Concatinating the results dataframe from every location to one multiindex dataframe
        new_column_df = pd.concat(new_column, keys=[i for i in range(len(new_column))])
        return new_column_df

    def solve_sub_problems(self):
        for sub_problem in self.sub_problems:
            sub_problem.solve_initial_model()

    def get_columns_from_sub_problems(self):
        new_column = []
        for sub_problem in self.sub_problems:
            new_column.append(sub_problem.get_second_stage_variables_df())

        # Concatinating the results dataframe from every location to one multiindex dataframe
        new_column_df = pd.concat(new_column, keys=[i for i in range(len(new_column))])
        return new_column_df

    def run_one_node_in_branch_and_price(self):
        i=1
        for j in range(8):
        #while not self.master_problem.is_model_solved:
            self.solve_sub_problems()
            new_column = self.get_columns_from_sub_problems()
            self.master_problem.add_new_column_to_columns_df(new_column)
            self.master_problem.run_and_solve_master_problem()

            shadow_prices_MAB = self.master_problem.get_MAB_constr_shadow_prices_df()

            for sub_problem in self.sub_problems:
                sub_problem.set_shadow_prices_df(shadow_prices_MAB)

            print(f"Iteration {i}")
            i += 1

        #The branching variable index is a tuple, where the first element is the location number. And the second element is the time period.
        branching_variable_index = self.master_problem.find_deploy_branching_variable()
        self.master_problem.add_up_branching_constraint(branching_variable_index)
        self.sub_problems[branching_variable_index[0]].add_up_branching_constraint(indice=branching_variable_index[1])

        #TODO: Add functionality for the branched variables to be actually run!gi




    def do_branching(self, branching_variable_indice):
        self.master_problem.find_deploy_branching_variable()


    def run_branch_and_price(self):
        pass


import pandas as pd
from master_problem import MasterProblem



class Node:
    """
    This is a class for orchestrating the interplay between the master and the sub-problem,
    running the Branch and Price framework for solving the Dantzig-Wolfe decomposition with column generation
    """
    sub_problems = []
    master_problem = None
    branching_variable_index = None


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
            sub_problem.solve_and_print_model()
            #Adding the results df from the solved model to the list
            new_column.append(sub_problem.get_second_stage_variables_df())

        #Concatinating the results dataframe from every location to one multiindex dataframe
        new_column_df = pd.concat(new_column, keys=[i for i in range(len(new_column))])
        return new_column_df

    def solve_sub_problems(self):
        for sub_problem in self.sub_problems:
            sub_problem.solve_and_print_model()

    def get_columns_from_sub_problems(self):
        new_column = []
        for sub_problem in self.sub_problems:
            new_column.append(sub_problem.get_second_stage_variables_df())

        # Concatinating the results dataframe from every location to one multiindex dataframe
        new_column_df = pd.concat(new_column, keys=[i for i in range(len(new_column))])
        return new_column_df

    def solve_node_to_optimality(self):
        i=1
        while not self.master_problem.is_model_solved:
            self.solve_sub_problems()
            new_column = self.get_columns_from_sub_problems()
            self.master_problem.add_new_column_to_columns_df(new_column)
            self.master_problem.run_and_solve_master_problem()

            shadow_prices_MAB = self.master_problem.get_MAB_constr_shadow_prices_df()

            for sub_problem in self.sub_problems:
                sub_problem.set_shadow_prices_df(shadow_prices_MAB)

            print(f"Iteration {i}")
            i += 1

        self.branching_variable_index = self.master_problem.find_deploy_branching_variable()
        print("Self branching variable",self.branching_variable_index)

    def set_down_branching_constraint(self):
        pass
    def set_up_branching_constraint(self):
        pass

    def run_branch_and_price(self):
        pass





    """
    sub_problems = []
    master_problem = None
    previously_branched_variable_indexes = []
    branching_variable_index = None
    parent_node = None
    child_nodes = []

    def __init__(self,
                 subproblems,
                 ):
        self.sub_problems = subproblems
        self.master_problem = MasterProblem(self.generate_initial_columns())



    def generate_initial_columns(self):
        # Storage for the dataframes containing the sub problem results
        new_column = []
        # Iterating through every column in the subproblems list
        for sub_problem in self.sub_problems:
            # Solving the sub problem
            sub_problem.solve_model()
            # Adding the results df from the solved model to the list
            new_column.append(sub_problem.get_second_stage_variables_df())

        # Concatinating the results dataframe from every location to one multiindex dataframe
        new_column_df = pd.concat(new_column, keys=[i for i in range(len(new_column))])
        return new_column_df

    def solve_sub_problems(self):
        for sub_problem in self.sub_problems:
            sub_problem.solve_model()

    def get_columns_from_sub_problems(self):
        new_column = []
        for sub_problem in self.sub_problems:
            if not sub_problem.get_second_stage_variables_df().empty: #TODO: This line might do some weird things to the indexing of the sub problems, fix
                new_column.append(sub_problem.get_second_stage_variables_df())

        # Concatinating the results dataframe from every location to one multiindex dataframe
        new_column_df = pd.concat(new_column, keys=[i for i in range(len(new_column))])
        return new_column_df

    def solve_node_to_optimality(self):
        while not self.master_problem.is_model_solved:
            self.solve_sub_problems()
            new_column = self.get_columns_from_sub_problems()
            self.master_problem.add_new_column_to_columns_df(new_column)
            self.master_problem.run_and_solve_master_problem()

            shadow_prices_MAB = self.master_problem.get_MAB_constr_shadow_prices_df()

            for sub_problem in self.sub_problems:
                sub_problem.set_shadow_prices_df(shadow_prices_MAB)

        #The branching variable index is a tuple, where the first element is the location number. And the second element is the time period.
        #We pass the previously found indexes to the function, so that it does not return previously branched variables
        print("Finding branching variable")
        self.branching_variable_index = self.master_problem.find_deploy_branching_variable(self.previously_branched_variable_indexes)
        print("BRANCHING VARIABLE",self.branching_variable_index)
        self.previously_branched_variable_indexes.append(self.branching_variable_index)

    def add_up_branching_constraint(self):
        #Adding the period deploy index (branched variable index 1) to the sub problem (branched variable index 0)
        self.sub_problems[self.branching_variable_index[0]].branched_variables_up.append(self.branching_variable_index[1])

        #Adding the branching index to the master problem

    def add_down_branching_constraint(self):
        # Adding the period deploy index (branched variable index 1) to the sub problem (branched variable index 0)
        self.sub_problems[self.branching_variable_index[0]].branched_variables_down.append(self.branching_variable_index[1])

        #Adding the branching index to the master problem

    def create_MIP_solution(self):
        pass
    """

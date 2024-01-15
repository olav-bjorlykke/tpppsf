import pandas as pd
from master_problem import MasterProblem
from gurobipy import GRB
import model
import subproblem_list
from archive.zero_column import do_nothing_column
import configs



class Node:
    """
    This is a class for orchestrating the interplay between the master and the sub-problem,
    running the Branch and Price framework for solving the Dantzig-Wolfe decomposition with column generation
    """



    def __init__(self,
                 subproblems,
                 ):
        self.sub_problems = subproblems
        self.master_problem = MasterProblem(self.generate_initial_columns())
        self.branching_variable_index = None



    def generate_initial_columns(self): #TODO: set to get initial column from generated column
        #Storage for the dataframes containing the sub problem results
        #initial_column = pd.read_csv(f"./init_columns/column_s{configs.NUM_SCENARIOS}_l{configs.NUM_LOCATIONS}.csv",index_col=["Location", "Scenario", "Smolt type", "Deploy period", "Period"])
        mon_model = model.Model(
            subproblem_list.SITE_LIST
        )

        initial_column = mon_model.create_initial_columns()

        return initial_column


    def solve_sub_problems(self):
        for sub_problem in self.sub_problems:
            sub_problem.solve_as_sub_problem()

    def get_columns_from_sub_problems(self):
        new_column = []
        for sub_problem in self.sub_problems:
            new_column.append(sub_problem.get_second_stage_variables_df()[0])

        # Concatinating the results dataframe from every location to one multiindex dataframe
        new_column_df = pd.concat(new_column, keys=[i for i in range(len(new_column))])
        return new_column_df

    def solve_node_to_optimality(self):
        self.master_problem.is_model_solved = False
        i=1
        while not self.master_problem.is_model_solved:

            self.master_problem.run_and_solve_master_problem()

            if self.master_problem.model.status == GRB.INFEASIBLE or self.master_problem.model.status == GRB.UNBOUNDED:
                return False

            shadow_prices_MAB = self.master_problem.get_MAB_constr_shadow_prices_df()
            shadow_prices_EOH = self.master_problem.get_eoh_shadow_price_df()



            if type(shadow_prices_MAB) == type(None):
                return False


            for sub_problem in self.sub_problems:
                sub_problem.set_shadow_prices_df(shadow_prices_df_mab=shadow_prices_MAB, shadow_prices_df_EOH=shadow_prices_EOH)

            self.solve_sub_problems()
            new_column = self.get_columns_from_sub_problems()
            self.master_problem.add_new_column_to_columns_df(new_column)

            print(f"Iteration {i}")
            i += 1

            print("TIME MASTER",self.master_problem.time_in_master)
            print("TIME SUB",self.sub_problems[0].time_in_subproblem)

            self.write_time_spent_to_file(self.master_problem.time_in_master, self.sub_problems[0].time_in_subproblem, i)

        new_index = self.master_problem.find_deploy_branching_variable()
        self.branching_variable_index = [new_index[0], new_index[1]]
        print("Self branching variable",self.branching_variable_index)

        return True

    def set_down_branching_constraint(self):
        self.master_problem.branched_variable_indices_down.append(self.branching_variable_index)
        self.sub_problems[self.branching_variable_index[0]].branching_variable_indices_up.append(self.branching_variable_index[1])

    def set_up_branching_constraint(self):
        self.master_problem.branched_variable_indices_up.append(self.branching_variable_index)
        self.sub_problems[self.branching_variable_index[0]].branching_variable_indices_up.append(self.branching_variable_index[1])

    def perform_up_branching(self):
        self.set_up_branching_constraint()
        self.master_problem.is_model_solved = False
        self.branching_variable_index = None

    def reset_for_new_node(self, node_label):
        print("####################\n\n")
        print("ITERATION OLAV AND HENRIK", node_label.iterations_number)
        print(node_label.up_list)
        print(node_label.down_list)
        print("\n\n####################")

        self.master_problem.branched_variable_indices_up = node_label.up_list
        self.master_problem.branched_variable_indices_down = node_label.down_list
        self.master_problem.iterations = 0 #Should allow 10 runs with warm start

        for i in range(len(self.sub_problems)):
            self.sub_problems[i].branching_variable_indices_up = []
            self.sub_problems[i].branching_variable_indices_down = []

            for indice in node_label.up_list:
                if indice[0] == i:
                    self.sub_problems[i].branching_variable_indices_up.append(indice[1])

            for indice in node_label.down_list:
                if indice[0] == i:
                    self.sub_problems[i].branching_variable_indices_down.append(indice[1])


    def preform_down_branching(self):
        self.set_down_branching_constraint()
        self.master_problem.is_model_solved = False
        self.branching_variable_index = None

    def write_time_spent_to_file(self, master_time, sub_time, iteration):
        file_path = configs.OUTPUT_DIR + "/time_track.txt"
        with open(file_path, "a") as file:
            file.write(f"Iter:{iteration};")
            file.write(f"Master: {master_time};")
            file.write(f"Sub:{sub_time}\n")






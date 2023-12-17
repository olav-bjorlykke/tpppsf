import time

import pandas as pd
from master_problem import MasterProblem
from node import Node
from gurobipy import GRB
from node_label import NodeLabel
import subproblem_list

class Orchestration:
    """
    This is a class for orchestrating the interplay between the master and the sub-problem,
    running the Branch and Price framework for solving the Dantzig-Wolfe decomposition with column generation
    """

    is_one_feasible_solution_found = False


    def __init__(self,
                 subproblems,
                 ):
        self.sub_problems = subproblems
        self.unexplored_nodes = []
        self.explored_nodes = []
        self.lower_bound = 0
        self.upper_bound = 1000000000000000 #TODO: this is supposed to represent infinity, find a more elegant way to achieve that
        self.node_obj = Node(subproblems)


    def run_branching_algorithm(self):
        init_node_label = NodeLabel(
            iterations_number=0,
            parent=None,
            up_list=subproblem_list.NODE_INIT_LIST,
            down_list = [],
            parent_feasible_solution=0,
            parent_iteration=0
        )

        self.unexplored_nodes.append(init_node_label)
        i = 0
        #Solve Node in unexplored nodes
        while self.unexplored_nodes and len(self.explored_nodes) < 1000:
            start_time = time.perf_counter()

            current_node_label = self.unexplored_nodes.pop(0)
            current_node_label.iterations_number = i

            self.node_obj.reset_for_new_node(current_node_label)

            continue_value = self.node_obj.solve_node_to_optimality()
            if continue_value:
                #Set Node_Label values
                current_node_label.upper_bound = self.node_obj.master_problem.model.ObjVal
                new_branching_index = self.node_obj.branching_variable_index


                #Solve the Node for the MIP problem
                self.node_obj.master_problem.run_MIP_problem()
                if self.node_obj.master_problem.model.status == GRB.OPTIMAL and not self.node_obj.master_problem.model.status == GRB.INFEASIBLE:
                    self.is_one_feasible_solution_found = True
                    current_node_label.feasible = True
                    current_node_label.feasible_solution = self.node_obj.master_problem.model.ObjVal


                    if current_node_label.feasible_solution >= current_node_label.parent_feasible_solution * 0.99:
                        #Create children
                        up_child, down_child = current_node_label.create_children(new_branching_index)
                        self.unexplored_nodes.append(up_child)
                        self.unexplored_nodes.append(down_child)

                if not self.is_one_feasible_solution_found:
                    up_child, down_child = current_node_label.create_children(new_branching_index)
                    self.unexplored_nodes.append(up_child)
                    self.unexplored_nodes.append(down_child)


            #Create children



            else:
                current_node_label.feasible = False

            #Add current node to explored nodes
            end_time = time.perf_counter()
            time_to_run_node = end_time - start_time
            current_node_label.print_node_label_to_file(time_to_run_node)
            self.explored_nodes.append(current_node_label)

            i += 1

    def print_explored_node_to_file(self, explored_nodes):
        pass







        #Repeat while there are more unexplored child nodes or we reach the desired optimality gap








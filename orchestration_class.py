import copy

import pandas as pd
from master_problem import MasterProblem
from node import Node
from gurobipy import GRB

class Orchestration:
    """
    This is a class for orchestrating the interplay between the master and the sub-problem,
    running the Branch and Price framework for solving the Dantzig-Wolfe decomposition with column generation
    """


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
            up_list=[[0,0]],
            down_list = [],
        )

        self.unexplored_nodes.append(init_node_label)
        i = 0
        #Solve Node in unexplored nodes
        while self.unexplored_nodes and len(self.explored_nodes) < 12:
            current_node_label = self.unexplored_nodes.pop(0)
            current_node_label.iterations_number = i

            self.node_obj.reset_for_new_node(current_node_label)
            continue_value = self.node_obj.solve_node_to_optimality()
            if continue_value:
                #Set Node_Label values
                current_node_label.lower_bound = self.node_obj.master_problem.model.ObjVal


                #Solve the Node for the MIP problem
                self.node_obj.master_problem.run_MIP_problem()
                if self.node_obj.master_problem.model.status == GRB.OPTIMAL and not self.node_obj.master_problem.model.status == GRB.INFEASIBLE:
                    current_node_label.feasible = True
                    current_node_label.feasible_solution = self.node_obj.master_problem.model.ObjVal

                new_branching_index = self.node_obj.branching_variable_index
            #Create children
                up_child,down_child = current_node_label.create_children(new_branching_index)
                self.unexplored_nodes.append(up_child)
                self.unexplored_nodes.append(down_child)


            else:
                current_node_label.feasible = False

            #Add current node to explored nodes
            self.explored_nodes.append(current_node_label)

            i += 1






        #Repeat while there are more unexplored child nodes or we reach the desired optimality gap




class NodeLabel:
    def __init__(self,
                 iterations_number,
                 parent,
                 up_list,
                 down_list,
                 lower_bound = 0,
                 feasible_solution = None
                 ):
        self.iterations_number = iterations_number
        self.parent = parent
        self.up_list = up_list
        self.down_list = down_list
        self.solution = 0
        self.feasible = None
        self.lower_bound = lower_bound
        self.feasible_solution = feasible_solution

    def create_children(self, branching_index):
        up_child = NodeLabel(
            iterations_number=1000,
            parent=self.iterations_number,
            up_list= self.up_list + [branching_index],
            down_list=self.down_list
        )
        down_child = NodeLabel(
            iterations_number=1000,
            parent=self,
            up_list= self.up_list,
            down_list=self.down_list + [branching_index]
        )

        return up_child, down_child




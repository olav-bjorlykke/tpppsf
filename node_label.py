import configs
class NodeLabel:
    def __init__(self,
                 iterations_number,
                 parent,
                 up_list,
                 down_list,
                 parent_feasible_solution,
                 parent_iteration,
                 upper_bound=None,
                 feasible_solution = None,
                 ):
        self.iterations_number = iterations_number
        self.parent = parent
        self.up_list = up_list
        self.down_list = down_list
        self.solution = 0
        self.feasible = None
        self.upper_bound = upper_bound
        self.feasible_solution = feasible_solution
        self.parent_feasible_solution = parent_feasible_solution
        self.parent_iteration = parent_iteration

    def create_children(self, branching_index):
        up_child = NodeLabel(
            iterations_number=1000,
            parent=self.iterations_number,
            up_list= self.up_list + [branching_index],
            down_list=self.down_list,
            parent_feasible_solution=self.feasible_solution,
            parent_iteration=self.iterations_number
        )
        down_child = NodeLabel(
            iterations_number=1000,
            parent=self,
            up_list= self.up_list,
            down_list=self.down_list + [branching_index],
            parent_feasible_solution=self.feasible_solution,
            parent_iteration=self.iterations_number,
        )

        return up_child, down_child

    def print_node_label_to_file(self, time_to_run):
        file_path = configs.OUTPUT_DIR + "/results.txt"
        with open(file_path, "a") as file:
            file.write("ITERATION:" + str(self.iterations_number))
            file.write("PARENT:" + str(self.parent_iteration))
            file.write(";TIME:" + str(time_to_run))
            file.write(";FEASIBLE SOLUTION:" + str(self.feasible_solution))
            file.write(";UPPER BOUND:" + str(self.upper_bound))
            file.write(";up_list:|")
            for inner_list in self.up_list:
                # Convert each inner list to a string with a space separator
                inner_string = ','.join(map(str, inner_list))
                file.write(inner_string + '|')
            file.write(";Down_list:|")
            for inner_list in self.down_list:
                # Convert each inner list to a string with a space separator
                inner_string = ','.join(map(str, inner_list))
                file.write(inner_string + '|')
            file.write("\n")



class NodeLabel:
    def __init__(self,
                 iterations_number,
                 parent,
                 up_list,
                 down_list,
                 upper_bound = 0,
                 feasible_solution = None
                 ):
        self.iterations_number = iterations_number
        self.parent = parent
        self.up_list = up_list
        self.down_list = down_list
        self.solution = 0
        self.feasible = None
        self.upper_bound = upper_bound
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

    def print_node_label_to_file(self, time_to_run):
        with open("results.txt", "a") as file:
            file.write("ITERATION:" + str(self.iterations_number))
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


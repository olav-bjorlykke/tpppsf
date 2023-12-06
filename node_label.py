
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


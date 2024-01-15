import subproblem_list
from orchestration_class import Orchestration

def main():
    orchestration = Orchestration(
        subproblems=subproblem_list.SUB_PROBLEM_LIST
    )

    orchestration.run_branching_algorithm()

    orchestration.print_explored_node_to_file(orchestration.explored_nodes)


if __name__ == "__main__":
    main()





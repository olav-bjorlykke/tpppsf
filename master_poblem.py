import gurobipy as gp
from gurobipy import GRB
import pandas as pd


class MasterProblem:
    #Sets
    iterations_k = None
    locations_l = None
    scenarios_s = None
    smolt_types_f = None

    #Variable containing the name of all columns in the colucmns dataframe
    column_index_names = ["Iteration","Location", "Scenario", "Smolt type", "Deploy period", "Period"]


    def __init__(self,
                 parameters,
                 scenarios,
                 initial_column
                 ):
        self.parameters = parameters
        self.scenarios = scenarios
        self.columns = self.add_first_column(initial_column)


    def add_first_column(self, column):
        #Formatting the added column, by adding the iteration counter as index
        columns = pd.concat([column], keys=[0])
        #Setting the index names, as to be able to reference more easily
        columns.index.names = self.column_index_names

        return columns

    def add_new_column_to_columns(self, new_column):
        #Getting the number of columns previously added, to use as counter
        num_columns_added = len(self.columns.index.get_level_values('Iteration').unique().tolist())

        #Formating the newly added column, by adding the interation we are in as inde
        new_column_formated = pd.concat([new_column], keys=[num_columns_added])

        #Adding the new_column to the columns dataframe
        columns = pd.concat([self.columns, new_column_formated])
        self.columns = columns

        #Renaming the index, so it also applies to the newly added column
        self.columns.index.names = self.column_index_names

    def set_sets(self):
        #Declaring sets for easier use in other functions
        self.iterations_k = self.columns.index.get_level_values('Iteration').unique().tolist()
        self.locations_l = self.columns.index.get_level_values('Location').unique().tolist()
        self.scenarios_s = self.columns.index.get_level_values('Scenario').unique().tolist()
        self.smolt_types_f = self.columns.index.get_level_values('Smolt type').unique().tolist()

    def declare_variables(self):
        #Declaring the decision variable
        self.lambda_var = self.model.addVars(len(self.locations_l), len(self.iterations_k), vtype=GRB.CONTINUOUS, lb=0)

    def set_objective(self):
        self.model.setObjective(
             gp.quicksum(
                 self.scenarios.scenario_probabilities[s]*
                    gp.quicksum(
                        self.columns.loc[(k,l,s,f,t_hat,t)]["W"] * self.lambda_var[l,k]
                        for l in self.locations_l
                        for k in self.iterations_k
                        for f in self.smolt_types_f
                        for t_hat in self.columns.loc[(k,l,s,f)].index.get_level_values("Deploy period").unique().tolist()
                        for t in self.columns.loc[(k,l,s,f,t_hat)].index.get_level_values("Period").unique().tolist()
                    )
                 for s in self.scenarios_s
             )
            ,sense=GRB.MAXIMIZE
        )

    def add_convexity_constraint(self):
        self.model.addConstrs(
            gp.quicksum(
                self.lambda_var[l, k]
                for k in self.iterations_k
            ) == 1
            for l in self.locations_l
        )

    def add_MAB_constraint(self):
        for s in self.scenarios_s:
            for t in self.columns.index.get_level_values("Period").unique().tolist():
                self.model.addConstr(
                    gp.quicksum(
                        gp.quicksum(
                                    self.columns.loc[(k,l,s,f,t_hat,t)]["X"] if (k,l,s,f,t_hat,t) in self.columns.index else 0.0
                                    for f in self.smolt_types_f
                                    for t_hat in self.columns.loc[(k,l,s,f)].index.get_level_values("Deploy period").unique().tolist()
                                    )
                        * self.lambda_var[l,k]
                        for l in self.locations_l
                        for k in self.iterations_k
                    )
                    <= 5000*1000*3 #TODO: set a prober limit

                    , name=f"MAB constraint[{s},{t}]"
                )

    def run_and_solve_master_problem(self):
        #Declare model
        self.model = gp.Model(f"Master Problem {self.iterations_k}")

        #Set sets and declare variables
        self.set_sets()
        self.declare_variables()

        #Set objective
        self.set_objective()

        #Add constraints to the mode
        self.add_convexity_constraint()
        self.add_MAB_constraint()

        #Solve model
        self.model.optimize()

        #Print solution
        self.print_solution()

    def print_solution(self):
        if self.model.status == GRB.OPTIMAL:
            print("Optimal Master solution found:")
            for k in self.iterations_k:
                for l in self.locations_l:
                    print(f"Lambda [{l}, {k}]", self.lambda_var[l,k].X)

    def get_results_df(self):
        lambda_list = []
        if self.model.status == GRB.OPTIMAL:
            for l in self.locations_l:
                location_list = []
                for k in self.iterations_k:
                    location_list.append(self.lambda_var[l,k].X)
                lambda_list.append(location_list)
        else:
            print("Model not optimal")

        df = pd.DataFrame(lambda_list, columns=[k for k in self.iterations_k], index=[l for l in self.locations_l])
        df.index.names = ["Location"]
        return df

    def get_reduced_costs_df(self):
        if self.model.status == GRB.OPTIMAL:
            shadow_prices = self.model.getAttr("Pi", self.model.getConstrs())
            for i, constraint in enumerate(self.model.getConstrs()):
                print(f"Shadow price for constraint {i + 1} ({constraint.constrName}): {shadow_prices[i]}")







import gurobipy as gp
from gurobipy import GRB
import pandas as pd


class MasterProblem:
    iterations_counter_k = 0
    num_locations = 3


    #Sets =
    iterations_k = None
    locations_l = None
    scenarios_s = None
    smolt_types_f = None

    def __init__(self,
                 parameters,
                 scenarios
                 ):
        self.model = gp.Model("Master Problem")
        self.parameters = parameters
        self.scenarios = scenarios

        #Declaring set sizes:



    def add_new_column_to_columns(self, new_column):
        new_column_formated = pd.concat([new_column], keys=[f"Iteration {self.iterations_counter_k}"])
        columns = pd.concat([self.columns, new_column_formated])
        self.columns = columns
        self.columns.index.names = ["Iteration", "Location", "Scenario", "Smolt type", "Deploy Period", "Period"]
        self.iterations_counter_k += 1

    def add_first_column(self, column):
        self.columns = pd.concat([column], keys=[f"Iteration {self.iterations_counter_k}"])
        self.columns.index.names = ["Iteration","Location", "Scenario", "Smolt type", "Deploy Period", "Period"]
        self.iterations_counter_k += 1

    def set_sets(self):
        self.iterations_k = self.columns.index.get_level_values('Iteration').unique()
        self.locations_l = self.columns.index.get_level_values('Location').unique()
        self.scenarios_s = self.columns.index.get_level_values('Scenario').unique()
        self.smolt_types_f = self.columns.index.get_level_values('Smolt type').unique()

    def declare_variables(self):
        self.lambda_var = self.model.addVars(len(self.locations_l), len(self.scenarios_s), vtype=GRB.CONTINUOUS, lb=0)


    def set_objective(self):
        self.model.setObjective(
             gp.quicksum(
                 self.scenarios.scenario_probabilities[s] *
                 gp.quicksum(
                     self.columns.loc[(self.iterations_k[k], self.locations_l[l], self.scenarios_s[s], self.smolt_types_f[f], t_hat, t)]["W"]
                     * self.lambda_var[l,k]

                     for k in range(len(self.iterations_k))
                     for l in range(len(self.locations_l))
                     for f in range(len(self.smolt_types_f))
                     for t_hat in self.columns.loc[(self.iterations_k[k], self.locations_l[l], self.scenarios_s[s], self.smolt_types_f[f])].index.get_level_values("Deploy Period").unique()
                     for t in self.columns.loc[(self.iterations_k[k], self.locations_l[l], self.scenarios_s[s], self.smolt_types_f[f], t_hat)].index.get_level_values("Period").unique()

                 )
                 for s in range(len(self.scenarios_s))
             )
            ,GRB.MAXIMIZE
        )


    def add_MAB_constraints_new(self):
        #TODO: This is not working at all, fix!
        for k in range(len(self.iterations_k)):
            for scenario in self.scenarios_s:
                    growth_period_list = self.columns.loc[(self.iterations_k[k])].index.get_level_values("Period").unique()
                    for period in growth_period_list:
                        self.model.addConstrs(
                            gp.quicksum(
                                    self.columns.loc[(self.iterations_k[k],self.locations_l[l], scenario)][(self.columns.loc[(self.iterations_k[k], self.locations_l[l], scenario)]["Period"] == period)]["X"].sum() * self.lambda_var[l, k]
                                for l in range(len(self.locations_l))
                            )
                        )


    def add_convexity_constraint(self):
        self.model.addConstr(
            gp.quicksum(
                self.lambda_var[l, k]
                for k in range(len(self.iterations_k))
                for l in range(len(self.locations_l))
            ) == 1, name="convexity constraint"
        )

    def solve_model(self):
        self.model.optimize()

    def print_solution(self):
        "if self.model.status == GRB.OPTIMAL:"
        print("Optimal solution found:")
        for lambda_var in self.model.getVars():
            print(lambda_var.x)

    def add_MAB_constraints(self):
        """
        self.model.addConstrs(
            gp.quicksum(
                self.columns.loc[
                    (self.iterations_k[k], self.locations_l[l], self.scenarios_s[s], self.smolt_types_f[f], t_hat, f"Period {t}")][ "X"]
            for k in range(len(self.iterations_k))
            for l in range(len(self.locations_l))
            for f in range(len(self.smolt_types_f))
            for t_hat in self.columns.loc[(self.iterations_k[k], self.locations_l[l], self.scenarios_s[s],self.smolt_types_f[f])].index.get_level_values.unique()
            )

        for s in range(len(self.scenarios_s))
        )
        """
        #TODO: define this function
        pass


    def add_convex_weighting_constraint(self):
        pass
    def solve_and_print_solution(self):
        #TODO: define this function
        pass

    def get_reduced_costs(self):
        #TODO: define this function
        pass

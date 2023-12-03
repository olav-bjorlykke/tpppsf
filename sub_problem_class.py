import gurobipy as gp
import pandas as pd
from gurobipy import GRB
import numpy as np
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
import matplotlib.pyplot as plt

class SubProblem:
    iterations = 0
    def __init__(self,
                 site_obj,
                 MAB_shadow_prices_df = pd.DataFrame()
                 ):
        #Imported classes, containing parameters and data
        self.input_data = InputData()
        self.parameters = GlobalParameters()
        self.scenario = Scenarios(self.input_data.temperatures_df)
        self.site = site_obj

        #Setting variables to contain the size of sets
        self.f_size = 1  #TODO: declare using the smolt set
        self.t_size = self.parameters.number_periods
        self.s_size = 2  #TODO: len(parameters.scenario_probabilities)

        #Defining some variables from the data objects for easier reference
        self.growth_factors = self.site.growth_per_scenario_df
        self.smolt_weights = self.parameters.smolt_weights
        self.growth_sets = self.site.growth_sets
        self.site = site_obj
        self.MAB_shadow_prices_df = MAB_shadow_prices_df

    def solve_and_print_model(self):
        self.model = gp.Model(f"Single site solution {self.site.name}")

        #Declaing variables
        self.declare_variables()

        #Setting objective
        self.set_decomped_objective()

        #Adding constraints
        self.add_smolt_deployment_constraints()
        self.add_fallowing_constraints()
        self.add_inactivity_constraints()
        self.add_harvesting_constraints()
        self.add_biomass_development_constraints()
        self.add_MAB_requirement_constraint()
        self.add_initial_condition_constraint()
        self.add_forcing_constraints()

        #Running gurobi to optimize model
        self.model.optimize()

        #Printing solution
        self.print_solution_to_excel()
        self.plot_solutions_x_values()
        self.iterations += 1

        #Putting solution into variables for export

    def declare_variables(self):
        self.x = self.model.addVars(self.f_size, self.t_size, self.t_size, self.s_size, vtype=GRB.CONTINUOUS, lb=0)
        self.y = self.model.addVars(self.f_size, self.t_size, vtype=GRB.CONTINUOUS, lb=0)
        self.w = self.model.addVars(self.f_size, self.t_size, self.t_size, self.s_size, vtype=GRB.CONTINUOUS, lb=0)

        # Declaring the binary decision variables
        self.deploy_type_bin = self.model.addVars(self.f_size, self.t_size, vtype=GRB.BINARY)
        self.deploy_bin = self.model.addVars(self.t_size, vtype=GRB.BINARY)
        self.harvest_bin = self.model.addVars(self.t_size, self.s_size, vtype=GRB.BINARY)
        self.employ_bin = self.model.addVars(self.t_size, self.s_size, vtype=GRB.BINARY)

    def set_objective(self):
        self.model.setObjective(  # This is the objective (5.2) - which represents the objective for biomass maximization
            gp.quicksum(
                self.scenario.scenario_probabilities[s] *
                gp.quicksum(
                    self.w[f, t_hat, t, s]
                    for f in range(self.f_size)
                    for t_hat in range(self.t_size)
                    for t in range(min(t_hat + self.parameters.temp_growth_period, self.t_size), self.t_size)
                )
                for s in range(self.s_size)
            )
            , GRB.MAXIMIZE
        )

    def set_decomped_objective(self):
        if not self.MAB_shadow_prices_df.empty:
            self.model.setObjective(
                # This is the objective (5.2) - which represents the objective for biomass maximization
                gp.quicksum(
                    self.scenario.scenario_probabilities[s] *
                    gp.quicksum(
                        self.w[f, t_hat, t, s] -
                        self.x[f, t_hat, t, s] * self.MAB_shadow_prices_df.loc[(s, t)] if (s,t) in self.MAB_shadow_prices_df.index else 0.0
                        for f in range(self.f_size)
                        for t_hat in range(self.t_size)
                        for t in range(min(t_hat + self.parameters.temp_growth_period, self.t_size), self.t_size)
                    )
                    for s in range(self.s_size)
                )
                , GRB.MAXIMIZE
            )

        else:
            self.set_objective()

    def add_smolt_deployment_constraints(self):
        self.model.addConstrs(
            # This is the constraint (5.4) - which restricts the deployment of smolt to an upper bound, while forcing the binary deploy variable
            gp.quicksum(self.parameters.smolt_weights[f] / 1000 * self.y[f, t] for f in
                        range(self.f_size)) <= self.parameters.smolt_deployment_upper_bound * self.deploy_bin[t]
            # Divide by thousand, as smolt weight is given in grams, while deployed biomass is in kilos
            for t in range(self.t_size)
        )

        self.model.addConstrs(
            # This is the constraint (5.4) - which restricts the deployment of smolt to a lower bound bound, while forcing the binary deploy variable
            gp.quicksum(self.parameters.smolt_weights[f] / 1000 * self.y[f, t] for f in
                        range(self.f_size)) >= self.parameters.smolt_deployment_lower_bound * self.deploy_bin[t]
            # Divide by thousand, as smolt weight is given in grams, while deployed biomass is in kilos
            for t in range(self.t_size)
        )

        self.model.addConstrs(  # This is constraint (5.5) - setting a lower limit on smolt deployed from a single cohort
            self.parameters.smolt_weights[f] / 1000 * self.y[f, t] >= self.parameters.smolt_deployment_lower_bound * self.deploy_type_bin[
                f, t]
            for t in range(self.t_size)
            for f in range(self.f_size)
        )

        self.model.addConstrs(
            # This is constraint (Currently not in model) - setting an upper limit on smolt deployed in a single cohort #TODO: Add to mathematical model
            self.parameters.smolt_deployment_upper_bound * self.deploy_type_bin[f, t] >= self.parameters.smolt_weights[f] / 1000 * self.y[
                f, t]
            for t in range(self.t_size)
            for f in range(self.f_size)
        )

    def add_fallowing_constraints(self):
        self.model.addConstrs(
            # This is the constraint (5.6) - It ensures that the required fallowing is done before the deploy variable can be set to 1
            self.parameters.min_fallowing_periods * self.deploy_bin[t] + gp.quicksum(
                self.employ_bin[tau, s] for tau in range(t - self.parameters.min_fallowing_periods, t))
            <= self.parameters.min_fallowing_periods
            for t in range(self.parameters.min_fallowing_periods, self.t_size)
            for f in range(self.f_size)
            for s in range(self.s_size)
        )

        self.model.addConstrs(
            # This is an additional constraint - ensuring that only 1 deployment happens during the initial possible deployment period TODO: See if this needs to be implemented in the math model
            gp.quicksum(self.deploy_bin[t] for t in range(self.parameters.min_fallowing_periods)) <= 1
            for f in range(self.f_size)
        )

    def add_inactivity_constraints(self):
        self.model.addConstrs(
            # This is the constraint (5.7) - ensuring that the site is not inactive longer than the max fallowing limit
            gp.quicksum(self.employ_bin[tau, s] for tau in range(t, min(t + self.parameters.max_fallowing_periods, self.t_size))) >= 1
            # The sum function and therefore the t set is not implemented exactly like in the mathematical model, but functionality is the same
            for s in range(self.s_size)
            for t in range(self.t_size)
        )

    def add_harvesting_constraints(self):
        self.model.addConstrs(
            # This is the first part of constraint (5.8) - which limits harvest in a single period to an upper limit
            gp.quicksum(self.w[f, t_hat, t, s] for f in range(self.f_size) for t_hat in range(t)) <= self.parameters.max_harvest *
            self.harvest_bin[t, s]
            for t in range(self.t_size)
            for s in range(self.s_size)
        )

        self.model.addConstrs(
            # This is the second part of constraint (5.8) - which limits harvest in a single period to a lower limit
            gp.quicksum(self.w[f, t_hat, t, s] for f in range(self.f_size) for t_hat in range(t)) >= self.parameters.min_harvest *
            self.harvest_bin[t, s]
            for t in range(self.t_size)
            for s in range(self.s_size)
        )

    def add_biomass_development_constraints(self):
        self.model.addConstrs(  # This is constraint (5.9) - which ensures that biomass x = biomass deployed y
            self.x[f, t_hat, t_hat, s] == self.y[f, t_hat]
            for f in range(self.f_size)
            for t_hat in range(self.t_size)
            for s in range(self.s_size)
        )

        self.model.addConstrs(  # This represents the constraint (5.10) - which ensures biomass growth in the growth period
            self.x[f, t_hat, t + 1, s] == (1 - self.parameters.expected_production_loss) * self.x[f, t_hat, t, s] *
            self.growth_factors.loc[(self.smolt_weights[f], f"Scenario {s}", t_hat)][t]
            # TODO:Introduce scenario and period specific G
            for t_hat in range(self.t_size - 1)
            for f in range(self.f_size)
            for s in range(self.s_size)
            for t in
            range(min(t_hat, self.t_size - 1), min(self.growth_sets.loc[(self.smolt_weights[f], f"Scenario {s}")][t_hat], self.t_size - 1))

        )

        self.model.addConstrs(  # This is the constraint (5.11) - Which tracks the biomass employed in the harvest period
            self.x[f, t_hat, t + 1, s] == (1 - self.parameters.expected_production_loss) * self.x[f, t_hat, t, s] *
            self.growth_factors.loc[(self.smolt_weights[f], f"Scenario {s}", t_hat)][t] - self.w[f, t_hat, t, s]
            for t_hat in range(self.t_size - 1)
            for f in range(self.f_size)
            for s in range(self.s_size)
            for t in range(min(self.growth_sets.loc[(self.smolt_weights[f], f"Scenario {s}")][t_hat], self.t_size - 1),
                           min(t_hat + self.parameters.max_periods_deployed, self.t_size - 1))

        )

        self.model.addConstrs(
            # This is the constraint (5.12) - Which forces the binary employement variable to be positive if biomass is employed
            gp.quicksum(self.x[f, t_hat, t, s] for f in range(self.f_size)) <= self.employ_bin[t, s] * self.parameters.bigM
            for s in range(self.s_size)
            for t_hat in range(self.t_size)
            for t in range(t_hat, min(t_hat + self.parameters.max_periods_deployed, self.t_size))
        )

    def add_MAB_requirement_constraint(self):
        self.model.addConstrs(
            gp.quicksum(self.x[f, t_hat, t, s] for f in range(self.f_size)) <= self.site.MAB_capacity
            for t_hat in range(self.t_size)
            for t in range(t_hat, min(t_hat + self.parameters.max_periods_deployed, self.t_size))
            for s in range(self.s_size)
        )

    def add_initial_condition_constraint(self): #TODO: Add initial constraints
        if self.site.init_biomass_at_site:
            self.model.addConstr(
                self.y[0,0] == self.site.init_biomass,
                name="Initial Condition"
            )

    def add_forcing_constraints(self):
        self.model.addConstrs(
            # TODO:This is a forcing constraint that is not in the mathematical model, put it in the model somehow
            self.w[f, t_hat, t, s] == 0
            for f in range(self.f_size)
            for t_hat in range(self.t_size)
            for s in range(self.s_size)
            for t in range(0, min(self.growth_sets.loc[(self.smolt_weights[f], f"Scenario {s}")][t_hat], self.t_size))
        )

        self.model.addConstrs(
            # TODO:This is a second forcing constraint that is not in the mathematical model, put it in the model somehow
            self.w[f, t_hat, t, s] == 0
            for f in range(self.f_size)
            for t_hat in range(self.t_size)
            for t in range(min(t_hat + self.parameters.max_periods_deployed, self.t_size), self.t_size)
            for s in range(self.s_size)
        )

    def print_solution_to_excel(self):
        data_list = []

        if self.model.status == GRB.OPTIMAL:
            self.get_second_stage_variables_df().to_excel(f"./results/sub_problem{self.site.name}.xlsx", index=True)

    def plot_solutions_x_values(self):
        """
        EXPLANATION: This function plots the x values, i.e the biomass at the location for every period in the planning horizion
        :return:
        """
        #Fetching the solution dataframe
        df = self.get_second_stage_variables_df()
        scenarios = df.index.get_level_values("Scenario").unique()

        #Declaring a list for storing the x values
        x_values = []

        #Iterating through the dataframe to sum together the biomass at location for every site
        for s in scenarios:
            scenarios_x_values = []
            for t in range(self.t_size):
                x_t = 0
                for t_hat in range(self.t_size):
                    for f in range(self.f_size):
                        x_t += df.loc[(s, f, t_hat, t)]["X"] if (s, f, t_hat, t) in df.index else 0.0

                scenarios_x_values.append(x_t)
            x_values.append(scenarios_x_values)

        #Declaring a variable for storing the x-axis to be used in the plot
        x_axis = np.arange(0,self.t_size)

        #Adding to the plots
        for scenario in x_values:
            plt.plot(x_axis, scenario)

        plt.title(f"Biomass at site {self.site.name} iteration {self.iterations}")
        plt.ylabel("Biomass")
        plt.xlabel("Periods")
        path = f'results/plots/{self.site.name}{self.iterations}.png'
        plt.savefig(path)

        plt.show()


        pass

    def get_deploy_period_list(self):
        deploy_period_list = [i for i in range(0, self.t_size) if self.deploy_bin[i].x == 1]
        return deploy_period_list

    def get_deploy_period_list_per_cohort(self):
        data_storage =[]
        for f in range(self.f_size):
            deploy_period_list_f = [t for t in range(0, self.t_size) if self.deploy_type_bin[f,t].x == 1]
            data_storage.append(deploy_period_list_f)

        df = pd.DataFrame(data_storage, index=[f"Smolt type {f}" for f in range(self.f_size)])
        return df

    def get_deploy_amounts_df(self):
        deploy_periods_list = self.get_deploy_period_list()

        data_storage = []
        for f in range(self.f_size):
            deploy_amounts_f = [self.y[f,t].x for t in deploy_periods_list]
            data_storage.append(deploy_amounts_f)

        df = pd.DataFrame(data_storage, index=[f"Smolt type {f}" for f in range(self.f_size)], columns=deploy_periods_list)
        return df

    def get_second_stage_variables_df(self):
        """
        This is the for loop from hell. 
        It iterates through all non-zero variables and writes the variables for X, W, Employ_bin and Harvest_bin to a ginormous dataframe
        Please don't touch it
        """
        deploy_period_list = self.get_deploy_period_list()

        df_storage = []
        for s in range(self.s_size):
            l1_df_storage = []
            for f in range(self.f_size):
                l2_df_storage = []
                for deploy_period in deploy_period_list:
                    l3_data_storage = []
                    for t in range(deploy_period, min(deploy_period + self.parameters.max_periods_deployed, self.t_size)):
                        x_entry = self.x[f, deploy_period, t, s].x
                        w_entry = self.w[f, deploy_period, t, s].x
                        employ_entry = self.employ_bin[t,s].x
                        harvest_entry = self.harvest_bin[t,s].x
                        deploy_entry = self.deploy_bin[t].x
                        deploy_type_entry = self.deploy_type_bin[f,t].x
                        l3_data_storage.append([x_entry,w_entry,employ_entry, harvest_entry, deploy_entry, deploy_type_entry])
                    columns = ["X", "W", "Employ bin", "Harvest bin", "Deploy bin", "Deploy type bin"]
                    index = [i + deploy_period for i in range(len(l3_data_storage))]
                    l2_df_storage.append(pd.DataFrame(l3_data_storage, columns=columns, index=index))
                keys_l2 = [i for i in deploy_period_list]
                l1_df_storage.append(pd.concat(l2_df_storage, keys=keys_l2))
            keys_l1 = [i for i in range(len(l1_df_storage))]
            df_storage.append(pd.concat(l1_df_storage, keys=keys_l1))
        keys = [i for i in range(len(df_storage))]
        df = pd.concat(df_storage, keys=keys)

        df.index.names = ["Scenario", "Smolt type", "Deploy period", "Period"]

        self.second_stage_variables = df

        return df

    def set_shadow_prices_df(self, shadow_prices_df):
        self.MAB_shadow_prices_df = shadow_prices_df



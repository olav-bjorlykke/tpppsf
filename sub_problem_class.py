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
    def __init__(self,
                 input_data_obj,
                 parameters_obj,
                 scenarios_obj,
                 site_obj
                 ):
        #Imported classes, containing parameters and data
        self.input_data = input_data_obj
        self.parameters = parameters_obj
        self.scenario = scenarios_obj
        self.site = site_obj

        #Creating model object
        self.model = gp.Model(f"Single site solution {self.site.name}")

        #Setting variables to contain the size of sets
        self.f_size = 1  #TODO: declare using the smolt set
        self.t_size = self.parameters.number_periods
        self.s_size = 2  #TODO: len(parameters.scenario_probabilities)

        #Defining some variables from the data objects for easier reference
        self.growth_factors = self.site.growth_per_scenario_df
        self.smolt_weights = self.parameters.smolt_weights
        self.growth_sets = self.site.growth_sets

    def solve_and_print_model(self):
        #Declaing variables
        self.declare_variables()

        #Setting objective
        self.set_objective()

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
        self.print_solution()

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
                self.parameters.scenario_probabilities[s] *
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
            # TODO:Introduce scenario and period specific G
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
            gp.quicksum(self.x[f, t_hat, t, s] for f in range(self.f_size)) <= self.parameters.MAB_site_limit
            for t_hat in range(self.t_size)
            for t in range(t_hat, min(t_hat + self.parameters.max_periods_deployed, self.t_size))
            for s in range(self.s_size)
        )

    def add_initial_condition_constraint(self):#TODO: Add initial constraints
        pass

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

    def print_solution(self):
        data_list = []

        if self.model.status == GRB.OPTIMAL:



            print("Optimal solution found:")
            # Print values of continuous variables w
            print("Values of w:")
            for s in range(self.s_size):
                data_list.append([])
                for f in range(self.f_size):
                    for t_hat in range(self.t_size):
                        for t in range(t_hat, self.t_size):
                            if (self.x[f, t_hat, t, s].x) > 5:
                                print(
                                    f"x[{f},{t_hat},{t},{s}] = {round(self.x[f, t_hat, t, s].x / 1000)}",
                                    f"employ_bin[{f},{t_hat},{t},{s}] = {round(self.employ_bin[t, s].x)}",
                                    "\n"
                                    f"w[{f},{t_hat},{t},{s}] = {round(self.w[f, t_hat, t, s].x / 1000)}",
                                    f"harvest_bin[{f},{t_hat},{t},{s}] = {round(self.harvest_bin[t, s].x)}"
                                )  # , f"w[{f},{t_hat},{t},{s}] = {w[f,t_hat, t, s].x/1000}") #Divide by 1000 to get print in tonnes
                                data_list[s].append(self.x[f, t_hat, t, s].x / 1000)


            for f in range(self.f_size):
                for t in range(self.t_size):
                    #if (self.y[f, t].x) > 5:
                        print(f"y[{f},{t}] = {self.y[f, t].x / 1000}", f"deploy type bin[{f},{t}] = {self.deploy_type_bin[f, t].x}", f"deploy bin[{f},{t}] = {self.deploy_bin[t].x }")  # Divide by 1000 to get print in tonnes

        else:
            print("No optimal solution found.")

        for sublist in data_list:
            line_style = '-' if sublist[-1] == 0 else '--'
            plt.plot(sublist[:-1], label=f'Line Type: {line_style}')

        plt.legend()
        plt.xlabel('Periods')
        plt.ylabel('Biomass')
        plt.title('Biomass plot')
        plt.show()

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

    def get_deploy_amounts_df(self, deploy_periods_list):
        data_storage = []
        for f in range(self.f_size):
            deploy_amounts_f = [self.y[f,t].x for t in deploy_periods_list]
            data_storage.append(deploy_amounts_f)

        df = pd.DataFrame(data_storage, index=[f"Smolt type {f}" for f in range(self.f_size)], columns=deploy_periods_list)
        return df

    def get_second_stage_variables_df(self, deploy_period_list):
        """
        This is the for loop from hell. 
        It iterates through all non-zero variables and writes the variables for X, W, Employ_bin and Harvest_bin to a ginormous dataframe
        Please don't touch it
        """
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
                        l3_data_storage.append([x_entry,w_entry,employ_entry, harvest_entry])
                    columns = ["X", "W", "EB", "HB"]
                    index = [f"Period {i + deploy_period}" for i in range(len(l3_data_storage))]
                    l2_df_storage.append(pd.DataFrame(l3_data_storage, columns=columns, index=index))
                keys_l2 = [f"Deploy period {i}" for i in deploy_period_list]
                l1_df_storage.append(pd.concat(l2_df_storage, keys=keys_l2))
            keys_l1 = [f"Smolt Type {i}" for i in range(len(l1_df_storage))]
            df_storage.append(pd.concat(l1_df_storage, keys=keys_l1))
        keys = [f"Scenario {i}" for i in range(len(df_storage))]
        df = pd.concat(df_storage, keys=keys)

        return df



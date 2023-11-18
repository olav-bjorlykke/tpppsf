import gurobipy as gp
from gurobipy import GRB
import numpy as np
from parameters import GlobalParameters
from input_data import InputData
from site_class import Site
from scenarios import Scenarios
import matplotlib.pyplot as plt

"""
EXPLANATION: 
This file contains a model that solves the tactical production planning problem for a single site using Gurobi. 
At the top it also contains the necesarry input variables from the rest of the directory
"""


#Declaring instances of the input data, parameters and scenario classes
input_data =InputData()
parameters =GlobalParameters()
scenarios_obj = Scenarios(input_data.temperatures_df)

#Declaring an instance of the site class to get site spesific information
site = Site(
    scenario_temperatures = scenarios_obj.scenario_temperatures_per_site_df.loc["Senja"],
    capacity = 3000.0 * 1000,
    init_biomass = 500 * 1000,
    TGC_array= input_data.TGC_df.iloc[0],
    smolt_weights = parameters.smolt_weights,
    weight_req_for_harvest = 3000.0
)



"""
EXPLANATION OF MODEL:
In this file we see an optimization model using gurobi that solves the tactical planning problem in salmon farming for a single site.
"""



#Crating variables to contain the size of different sets
f_size = 2  #
l_size = 1
t_size = parameters.number_periods
s_size = 3  #len(parameters.scenario_probabilities)

#Defining a variable for the growth frame G
G = 1.2
growth_factors = site.growth_per_scenario_df
smolt_weights = parameters.smolt_weights
growth_sets = site.growth_sets

#Creating an instance of the gurobi model object
model = gp.Model("single site solution")

"""
DECLARING VARIABLES
In this section we declare the necesarry variable for the model
"""
x = model.addVars(f_size, t_size, t_size, s_size, vtype=GRB.CONTINUOUS, lb=0)
y = model.addVars(f_size, t_size, vtype=GRB.CONTINUOUS, lb=0)
w = model.addVars(f_size, t_size, t_size, s_size, vtype=GRB.CONTINUOUS, lb=0)

#Declaring the binary decision variables
deploy_type_bin = model.addVars(f_size, t_size, vtype=GRB.BINARY)
deploy_bin = model.addVars(t_size, vtype=GRB.BINARY)
harvest_bin = model.addVars(t_size, s_size, vtype=GRB.BINARY)
employ_bin = model.addVars( t_size, s_size, vtype=GRB.BINARY)


"""
OBJECTIVE
In this section we declare the objective fucntion for the model
"""
#Setting the objective
model.setObjective( #This is the objective (5.2) - which represents the objective for biomass maximization
        gp.quicksum(
            parameters.scenario_probabilities[s] *
            gp.quicksum(
            w[f,t_hat,t,s]
            for f in range(f_size)
            for t_hat in range(t_size)
            for t in range(min(t_hat + parameters.temp_growth_period,t_size), t_size)
        )
        for s in range(s_size)
    )
    ,GRB.MAXIMIZE
)

"""
CONSTRAINTS
In this section we declare the constraints of the model, each constraint is labeled with a number and has mathematical equivalent in Bjorlykke & Vassbotten 2023
"""


#TODO: Add smolt deployment constraints
model.addConstrs(#This is the constraint (5.4) - which restricts the deployment of smolt to an upper bound, while forcing the binary deploy variable
    gp.quicksum(parameters.smolt_weights[f]/1000 * y[f,t] for f in range(f_size)) <= parameters.smolt_deployment_upper_bound * deploy_bin[t]    #Divide by thousand, as smolt weight is given in grams, while deployed biomass is in kilos
    for t in range(t_size)
)


model.addConstrs(#This is constraint (5.5) - setting a lower limit on smolt deployed from a single cohort
    parameters.smolt_weights[f]/1000 * y[f,t] >= parameters.smolt_deployment_lower_bound * deploy_type_bin[f,t]
    for t in range(t_size)
    for f in range(f_size)
)


model.addConstrs(#This is constraint (Currently not in model) - setting an upper limit on smolt deployed in a single cohort #TODO: Add to mathematical model
    parameters.smolt_deployment_upper_bound * deploy_type_bin[f,t] >= parameters.smolt_weights[f]/1000 * y[f,t]
    for t in range(t_size)
    for f in range(f_size)
)

#TODO: Add fallowing constraint
model.addConstrs(#This is the constraint (5.6) - It ensures that the required fallowing is done before the deploy variable can be set to 1
    parameters.min_fallowing_periods * deploy_bin[t] + gp.quicksum(employ_bin[tau,s] for tau in range(t - parameters.min_fallowing_periods,t))
    <= parameters.min_fallowing_periods
    for t in range(parameters.min_fallowing_periods,t_size)
    for f in range(f_size)
    for s in range(s_size)
)

model.addConstrs(#This is an additional constraint - ensuring that only 1 deployment happens during the initial possible deployment period TODO: See if this needs to be implemented in the math model
    gp.quicksum(deploy_bin[t] for t in range(parameters.min_fallowing_periods)) <= 1
    for f in range(f_size)
)

#TODO: Add inactivity constraints
model.addConstrs(#This is the constraint (5.7) - ensuring that the site is not inactive longer than the max fallowing limit
    gp.quicksum(employ_bin[tau,s] for tau in range(t,min(t + parameters.max_fallowing_periods, t_size))) >= 1 #The sum function and therefore the t set is not implemented exactly like in the mathematical model, but functionality is the same
    for s in range(s_size)
    for t in range(t_size)
)

#TODO: Add harvesting constraints
model.addConstrs(#This is the first part of constraint (5.8) - which limits harvest in a single period to an upper limit
    gp.quicksum(w[f,t_hat,t,s] for f in range(f_size) for t_hat in range(t)) <= parameters.max_harvest * harvest_bin[t,s]
    for t in range(t_size)
    for s in range(s_size)
)

model.addConstrs(#This is the second part of constraint (5.8) - which limits harvest in a single period to a lower limit
    gp.quicksum(w[f,t_hat,t,s] for f in range(f_size) for t_hat in range(t)) >= parameters.min_harvest * harvest_bin[t,s]
    for t in range(t_size)
    for s in range(s_size)
)


#TODO: Add Biomass development constraints
model.addConstrs( # This is constraint (5.9) - which ensures that biomass x = biomass deployed y
    x[f,t_hat,t_hat,s] == y[f,t_hat]
    for f in range(f_size)
    for t_hat in range(t_size)
    for s in range(s_size)
)

model.addConstrs(#This represents the constraint (5.10) - which ensures biomass growth in the growth period
    x[f,t_hat,t + 1,s] == (1-parameters.expected_production_loss)*x[f,t_hat, t,s]*growth_factors.loc[(smolt_weights[f], f"Scenario {s}", t_hat)][t] #TODO:Introduce scenario and period specific G
    for t_hat in range(t_size -1)
    for f in range(f_size)
    for s in range(s_size)
    for t in range(min(t_hat, t_size -1),min(growth_sets.loc[(smolt_weights[f], f"Scenario {s}")][t_hat], t_size - 1))

)

model.addConstrs(#This is the constraint (5.11) - Which tracks the biomass employed in the harvest period
    x[f,t_hat,t + 1,s] == (1-parameters.expected_production_loss)*x[f,t_hat, t,s]*growth_factors.loc[(smolt_weights[f], f"Scenario {s}", t_hat)][t] - w[f,t_hat,t,s] #TODO:Introduce scenario and period specific G
    for t_hat in range(t_size -1)
    for f in range(f_size)
    for s in range(s_size)
    for t in range(min(growth_sets.loc[(smolt_weights[f], f"Scenario {s}")][t_hat], t_size -1), min(t_hat+parameters.max_periods_deployed, t_size -1))

)

model.addConstrs(#This is the constraint (5.12) - Which forces the binary employement variable to be positive if biomass is employed
    gp.quicksum(x[f,t_hat,t,s] for f in range(f_size)) <= employ_bin[t,s] *parameters.bigM
    for s in range(s_size)
    for t_hat in range(t_size)
    for t in range(t_hat, min(t_hat +parameters.max_periods_deployed,t_size))
)

#TODO: Add MAB requirement constraints
model.addConstrs(
    gp.quicksum(x[f,t_hat,t,s] for f in range(f_size)) <= parameters.MAB_site_limit
    for t_hat in range(t_size)
    for t in range(t_hat, min(t_hat + parameters.max_periods_deployed, t_size))
    for s in range(s_size)
)


#TODO: Add Initial conditions and end of horizon constraints


"""
TESTING CONSTRAINTS
In this section we see some testing constraints, they are employed during the development of the model to ensure that the model works as specified
"""


model.addConstrs( #TODO:This is a forcing constraint that is not in the mathematical model, put it in the model somehow
    w[f,t_hat,t,s] == 0
    for f in range(f_size)
    for t_hat in range(t_size)
    for s in range(s_size)
    for t in range(0, min(growth_sets.loc[(smolt_weights[f], f"Scenario {s}")][t_hat],t_size))
)

model.addConstrs( #TODO:This is a second forcing constraint that is not in the mathematical model, put it in the model somehow
    w[f,t_hat,t,s] == 0
    for f in range(f_size)
    for t_hat in range(t_size)
    for t in range(min(t_hat + parameters.max_periods_deployed,t_size),t_size)
    for s in range(s_size)
)

#Running the opimize method to solve the problem
model.optimize()

"""
PRINTING THE SOLUTION
"""
data_list = []

if model.status == GRB.OPTIMAL:
        print("Optimal solution found:")
        # Print values of continuous variables w
        print("Values of w:")
        for s in range(s_size):
            for f in range(f_size):
                data_list.append([])
                for t_hat in range(t_size):
                    for t in range(t_hat, t_size):
                        if (x[f, t_hat, t, s].x) > 5:
                            print(f"x[{f},{t_hat},{t},{s}] = {round(x[f, t_hat, t, s].x/1000)}")#, f"w[{f},{t_hat},{t},{s}] = {w[f,t_hat, t, s].x/1000}") #Divide by 1000 to get print in tonnes
                            data_list[s].append(x[f, t_hat, t, s].x/1000)


        for f in range(f_size):
            for t in range(t_size):
                if (y[f, t].x) > 5:
                    print(f"y[{f},{t}] = {y[f,t].x/1000}") #Divide by 1000 to get print in tonnes

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
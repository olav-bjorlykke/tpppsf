import gurobipy as gp
from gurobipy import GRB

import constants
from parameters import GlobalParameters

parameters = GlobalParameters

f_size = 1 #TODO:Change to be the correct size and connected to where it is declared
l_size = 1 #TODO: Change to be number of locations
t_size = constants.NUMBER_PERIODS
s_size = parameters.scenario_probabilities.size
G = 1.2 #TODO: implement on a per site and per period basis

model = gp.Model("single site solution")

x = model.addVars(f_size, t_size, t_size, s_size, vtype=GRB.CONTINUOUS, lb=0)
y = model.addVars(f_size, t_size, vtype=GRB.CONTINUOUS, lb=0)
w = model.addVars(f_size, t_size, t_size, s_size, vtype=GRB.CONTINUOUS, lb=0)

deploy_type_bin = model.addVars(f_size, t_size, vtype=GRB.BINARY)
deploy_bin = model.addVars(t_size, vtype=GRB.BINARY)
harvest_bin = model.addVars(t_size, s_size, vtype=GRB.BINARY)
employ_bin = model.addVars( t_size, s_size, vtype=GRB.BINARY)


model.setObjective(

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

#TODO: Add smolt deployment constraints
#TODO: Add fallowing and inactivity constraints
#TODO: Add harvesting constraints
#TODO: Add Biomass development constraints
#TODO: Add MAB requirement constraints
#TODO: Add Initial conditions and end of horizon constraints








model.addConstrs(#TODO: This is a testing constraint, should be removed
    w[f,t_hat,t,s] <= 5000
    for f in range(f_size)
    for t_hat in range(t_size)
    for t in range(t_size)
    for s in range(s_size)
)

model.addConstrs( #TODO:This is a forcing constraint that is not in the model, put it in the model somehow
    w[f,t_hat,t,s] == 0
    for f in range(f_size)
    for t_hat in range(t_size)
    for t in range(0, min(t_hat + parameters.temp_growth_period,t_size))
    for t in range(min(t_hat + parameters.max_periods_deployed,t_size),t_size)
    for s in range(s_size)
)



model.optimize()

if model.status == GRB.OPTIMAL:
    print("Optimal solution found:")
    # Print values of continuous variables w
    print("Values of w:")
    for s in range(s_size):
        for f in range(f_size):
            for t_hat in range(t_size):
                for t in range(t_hat,t_size):
                    print(f"w[{f},{t_hat},{t},{s}] = {w[f,t_hat, t, s].x}")

else:
    print("No optimal solution found.")


import gurobipy as gp
from gurobipy import GRB

import constants
from parameters import GlobalParameters

#Fetching parameters and sets
parameters = GlobalParameters

f_size = 5 #TODO: CHhange to be number of smolttypes
l_size = 5 #TODO: Change to be number of locations
t_size = constants.NUMBER_PERIODS
s_size = 2 #TODO: Change to be number of scenarios




model = gp.Model("tpppsf")

#Declaring all variables for the model:
x = model.addVars(f_size, l_size, t_size, t_size, s_size, vtype=GRB.CONTINUOUS, lb=0)
y = model.addVars(f_size, l_size, t_size, vtype=GRB.CONTINUOUS, lb=0)
w = model.addVars(f_size, l_size, t_size, t_size, s_size, vtype=GRB.CONTINUOUS, lb=0)

deploy_type_bin = model.addVars(f_size, l_size, t_size, vtype=GRB.BINARY)
deploy_bin = model.addVars(f_size, l_size, vtype=GRB.BINARY)
harvest_bin = model.addVars(l_size, t_size, s_size, vtype=GRB.BINARY)
employ_bin = model.addVars(l_size, t_size, s_size, vtype=GRB.BINARY)

model.setObjective(
    gp.quicksum(parameters.scenario_probabilities[s] *
                gp.quicksum(w[f,l,t_hat,t,s]
                            for f in range(f_size)
                            for l in range(l_size)
                            for t_hat in range(t_size)
                            for t in range(t_hat,t_size) #TODO:Define by using the proper set
                            ) for s in range(s_size)
                )
    , GRB.MAXIMIZE)



model.addConstrs(
    w[f,l,t_hat,t,s] <= 10  for f in range(f_size)
                            for l in range(l_size)
                            for t_hat in range(t_size)
                            for t in range(t_hat,t_size) #TODO:Define by using the proper set
                            for s in range(s_size)
)

model.optimize()

if model.status == GRB.OPTIMAL:
    print("Optimal solution found:")
    # Print values of continuous variables w
    print("Values of w:")
    for f in range(f_size):
        for l in range(l_size):
            for t_hat in range(t_size):
                for t in range(t_hat,t_size):
                    for s in range(s_size):
                        print(f"w[{f},{l},{t_hat},{t},{s}] = {w[f, l, t_hat, t, s].x}")

else:
    print("No optimal solution found.")



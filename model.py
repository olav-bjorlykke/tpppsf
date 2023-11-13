import gurobipy as gp
from gurobipy import GRB

import constants
from parameters import GlobalParameters

#Fetching parameters and sets
parameters = GlobalParameters

f_size = 1 #TODO: CHhange to be number of smolttypes
l_size = 1 #TODO: Change to be number of locations
t_size = constants.NUMBER_PERIODS
s_size = 1 #TODO: Change to be number of scenarios
G = 1.2 #TODO: implement on a per site and per period basis




model = gp.Model("tpppsf")

#Declaring all variables for the model:
x = model.addVars(f_size, l_size, t_size, t_size, s_size, vtype=GRB.CONTINUOUS, lb=0)
y = model.addVars(f_size, l_size, t_size, vtype=GRB.CONTINUOUS, lb=0)
w = model.addVars(f_size, l_size, t_size, t_size, s_size, vtype=GRB.CONTINUOUS, lb=0)

deploy_type_bin = model.addVars(f_size, l_size, t_size, vtype=GRB.BINARY)
deploy_bin = model.addVars(l_size, t_size, vtype=GRB.BINARY)
harvest_bin = model.addVars(l_size, t_size, s_size, vtype=GRB.BINARY)
employ_bin = model.addVars(l_size, t_size, s_size, vtype=GRB.BINARY)


#Defining the objective of the model
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



"""
In this section we add the constraints, each constraint shall have a comment declaring which constraint it belongs to
"""

#Smolt deployment constraint for all cohorts
#Constraint (5.4)
#This represnts the less than part of equation 5.4
model.addConstrs((
    parameters.smolt_deployment_lower_bound * deploy_bin[l,t]
    <=
    gp.quicksum(
           y[f,l,t] * parameters.smolt_type_df.iloc[f]["num-smolt-kilo"] for f in range(f_size)
    ) for l in range(l_size) for t in range(t_size)
    ))
#This represents the greater then part of equation 5.4
model.addConstrs((
    parameters.smolt_deployment_upper_bound * deploy_bin[l,t]
    >=
    gp.quicksum(
           y[f,l,t] * parameters.smolt_type_df.iloc[f]["num-smolt-kilo"] for f in range(f_size)
    ) for l in range(l_size) for t in range(t_size)
    ))

#Constraint (5.5) - smolt deployment for single cohort lower bound
model.addConstrs((
    parameters.smolt_deployment_upper_bound * deploy_bin[l, t]
    >=
        y[f, l, t] * parameters.smolt_type_df.iloc[f]["num-smolt-kilo"] for f in range(f_size)
    for l in range(l_size) for t in range(t_size) for f in range(f_size)
))

#Fallowing and Inactivity constraints
#Constraint 5.6 - fallowing constraint
model.addConstrs((
    parameters.min_fallowing_periods * deploy_type_bin[f,l,t] +
    gp.quicksum(employ_bin[l,t,s] for tau in range(t - parameters.min_fallowing_periods,t))
    <=
    parameters.min_fallowing_periods
    for f in range(f_size)
    for s in range(s_size)
    for l in range(l_size)
    for t in range(parameters.min_fallowing_periods,t_size)
))

#Constraint 5.7 - Inactivity constraint
model.addConstrs((
  gp.quicksum(employ_bin[l,tau,s] for tau in range(t - parameters.max_fallowing_periods,t)) >=1
  for l in range(l_size) for t in range(parameters.max_fallowing_periods,t_size) for s in range(s_size)
))

#Harvesting constraint
#Constraint 5.8 - harvesting lower bound enforcement
model.addConstrs((
    parameters.min_harvest * harvest_bin[l,t,s] <=
    gp.quicksum(w[f,l,t_hat,t,s]
                for f in range(f_size)
                for t_hat in range(0,t)
                )
    for l in range(l_size)
    for t in range(t_size)
    for s in range(s_size)
)) #TODO: Implement with H dependent on location

#Constraint 5.8 - harvesting upper bound enforcement - Notice switched signs and variables in the first line
model.addConstrs((
    parameters.max_harvest * harvest_bin[l,t,s] >=
    gp.quicksum(w[f,l,t_hat,t,s]
                for f in range(f_size)
                for t_hat in range(0,t)
                )
    for l in range(l_size)
    for t in range(t_size)
    for s in range(s_size)
)) #TODO: Implement with H dependent on location


#Biomass development constraints
#Initial biomass development constraint - 5.9
model.addConstrs((
    x[f,l,t_hat,t_hat,s] == y[f,l,t_hat]
    for t_hat in range(t_size)
    for l in range(l_size)
    for s in range(s_size)
    for f in range(f_size)
))

#Growth period development constraint - 5.10
model.addConstrs((
    x[f,l,t_hat,t+1,s] == (1 - parameters.expected_production_loss)* x[f,l,t_hat,t+1,s] * G #TODO:Implement with an indexed G
    for t_hat in range(t_size)
    for t in range(t_hat, t_size - 1) #TODO: Implement with the proper set
    for l in range(l_size)
    for s in range(s_size)
    for f in range(f_size)
))

#Harvest period development constraint - 5.11
model.addConstrs((
    x[f, l, t_hat, t + 1, s] == (1 - parameters.expected_production_loss) * x[f, l, t_hat, t + 1, s] * G - w[f,l,t_hat,t,s]# TODO:Implement with an indexed G
    for t_hat in range(t_size)
    for t in range(t_hat, t_size - 1)  # TODO: Implement with the proper set
    for l in range(l_size)
    for s in range(s_size)
    for f in range(f_size)
)) #TODO: Currently this constraint does not allow slaughter in the last period, that needs to be adressed

#Constraint 5.12 - forcing constraint
model.addConstrs((
    gp.quicksum(
        x[f,l,t_hat,t,s] for f in range(f_size)
    ) <= employ_bin[l,t,s] * parameters.bigM
    for l in range(l_size)
    for t_hat in range(t_size)
    for t in range(t_hat, min(t_hat + parameters.max_periods_deployed,t_size)) #TODO: implement with the proper set
    for s in range(s_size)
))


#MAB requirement constraints
#Site level MAB constraint - 5.13
model.addConstrs((
    gp.quicksum(
        x[f,l,t_hat,t,s] for f in range(f_size)
    ) <= parameters.MAB_site_limit #TODO:Implement with the proper MAB site limit
    for t_hat in range(t_size)
    for t in range(t_hat,t_size) #TODO: implement with correct set
    for l in range(l_size)
    for s in range(s_size)
))

#MAB company level limit
model.addConstrs(
    gp.quicksum(
        x[f,l,t_hat,t,s] for f in range(f_size) for l in range(f_size) for t_hat in range(t_size)
    ) <= parameters.MAB_site_limit
    for t in range(t_size)
    for s in range(s_size)
)

"""
#W forcing constraint #TODO:this is just a testing constraint, remove
model.addConstrs(
    gp.quicksum(
        w[f,l,t_hat,t,s] for t in range(0,t_hat)
    ) == 0
    for f in range(f_size)
    for l in range(l_size)
    for t_hat in range(t_size)
    for s in range(s_size)
)
"""

#W testing constraint #TODO: remove this constraint, it is only here for understanding the model
model.addConstrs(
    w[f,l,t_hat,t,s]  <= 10000
    for f in range(f_size)
    for l in range(l_size)
    for t_hat in range(t_size)
    for t in range(t_hat,t_size)
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



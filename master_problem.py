import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import numpy as np


class MasterProblem:
    #Sets
    iterations_k = None
    locations_l = None
    scenarios_s = None
    smolt_types_f = None
    periods_t = None
    lambdas = None
    previous_solution = None
    is_model_solved = False

    #Variable containing the name of all columns in the columns dataframe. Set here to avoid naming errors
    column_df_index_names = ["Iteration", "Location", "Scenario", "Smolt type", "Deploy period", "Period"]


    def __init__(self,
                 parameters,
                 scenarios,
                 initial_column
                 ):
        #Declaring objects containing data needed to run the master problem
        self.parameters = parameters
        self.scenarios = scenarios
        self.columns = self.add_first_column(initial_column)


    def add_first_column(self, column):
        """
        Takes in a dataframe containing the results from solving the subproblems. The function then re-indexes the dataframe by adding an interation counter k as the outer index.
        Then stores it as a class variable.

        :param column: A dataframe containing the resulting non-zero decision variables from the sub-problems
        :return: a dataframe containing the results from the sub-problems.
        """
        #Formatting the added column, by adding the iteration counter as index
        columns = pd.concat([column], keys=[0])
        #Setting the index names, as to be able to reference more easily
        columns.index.names = self.column_df_index_names

        return columns

    def add_new_column_to_columns_df(self, new_column):
        """
        Takes in a Dataframe, containing the results from one iteration of solving the sub-problems. Then adds this column to the columns dataframe

        :param new_column: A dataframe containing the results from one iteration of solved sub-problems
        :return:
        """
        #Getting the number of columns previously added, to use as counter
        num_columns_added = len(self.columns.index.get_level_values('Iteration').unique().tolist())

        #Formating the newly added column, by adding the interation we are in as index
        new_column_formated = pd.concat([new_column], keys=[num_columns_added])

        #Adding the new_column to the columns dataframe
        columns = pd.concat([self.columns, new_column_formated])
        self.columns = columns

        #Renaming the index, so it also applies to the newly added column
        self.columns.index.names = self.column_df_index_names

    def set_sets(self):
        #Declaring sets for easier use in other functions.
        #Fetches the index from every level of index in the columns dataframe and stores all unique values in a list
        self.iterations_k = self.columns.index.get_level_values('Iteration').unique().tolist()
        self.locations_l = self.columns.index.get_level_values('Location').unique().tolist()
        self.scenarios_s = self.columns.index.get_level_values('Scenario').unique().tolist()
        self.smolt_types_f = self.columns.index.get_level_values('Smolt type').unique().tolist()
        self.periods_t = self.columns.index.get_level_values("Period").unique().tolist()

    def declare_variables(self):
        #Declaring the decision variables for the model
        self.lambda_var = self.model.addVars(len(self.locations_l), len(self.iterations_k), vtype=GRB.CONTINUOUS, lb=0)
        self.penalty_var = self.model.addVars(len(self.locations_l))

    def set_objective(self):
        """
        Sets the objective function for the model - chapter 6.3 in Bjorlykke & Vassbotten
        :return:
        """
        self.model.setObjective(
            #This objective corresponds to the objective function in the decomposition model in chapter 6.3 in Bjorlykke and Vassbotten
             gp.quicksum(
                 #Fetches scenario probabilities from the scenarios object and multiplicates it with the below expression
                 self.scenarios.scenario_probabilities[s]*
                    #Sums the product of the harvest parameter and the lambda variable for all combinations of location, iteraiont, smolt weight, deploy period and current period
                    gp.quicksum(
                        #Fetches the parameter from the columns dataframe and products it with the lambda variable
                        self.columns.loc[(k,l,s,f,t_hat,t)]["W"] * self.lambda_var[l,k]
                        for l in self.locations_l
                        for k in self.iterations_k
                        for f in self.smolt_types_f
                        for t_hat in self.columns.loc[(k,l,s,f)].index.get_level_values("Deploy period").unique().tolist()
                        for t in self.columns.loc[(k,l,s,f,t_hat)].index.get_level_values("Period").unique().tolist()
                    )
                 for s in self.scenarios_s
             )
             -
             #Adds a penalty variable. This variable ensures feasibility when the iteration count is low. However the penalty is set to be so high as to it never being used in a real solution.
             gp.quicksum(self.penalty_var[l] * 10000000 for l in self.locations_l)
            ,sense=GRB.MAXIMIZE
        )

    def add_convexity_constraint(self):
        """
        Adds the convecity constraint, see chapter 6.3 in Bjorlykke and Vasbotten for mathematical description
        :return:
        """
        for l in self.locations_l:
            self.model.addConstr(
                gp.quicksum(
                    self.lambda_var[l, k]
                    for k in self.iterations_k
                )
                +
                self.penalty_var[l] == 1
                , name=f"Convexity;{l}"
            )

    def add_MAB_constraint(self):
        """
        Adds the MAB limit across all sites constraint - see 6.3 in Bjorlykke and Vasbotten
        :return:
        """
        for s in self.scenarios_s:
            for t in self.periods_t:
                self.model.addConstr(
                    gp.quicksum(
                        gp.quicksum(
                                    #Iterates across the columns dataframe, returns the x value if the index exists. Returns 0 otherwise
                                    self.columns.loc[(k,l,s,f,t_hat,t)]["X"] if (k,l,s,f,t_hat,t) in self.columns.index else 0.0
                                    for f in self.smolt_types_f
                                    for t_hat in self.columns.loc[(k,l,s,f)].index.get_level_values("Deploy period").unique().tolist()
                                    )
                        * self.lambda_var[l,k]
                        for l in self.locations_l
                        for k in self.iterations_k
                    )
                    <= 2300*1000*3 #TODO: set the actual limit for MAB across the sites as the limit

                    #Naming the constraint by the pattern "{Constraint type}; {indice}, {indice}" enabling transformation identification and sorting of shadow prices
                    , name=f"MAB Constr;{s},{t}"
                )

    def run_and_solve_master_problem(self):
        """
        Runs the optimization problem and prints the solution to the terminal
        :return:
        """
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

        #Check if we have reached optimality for the LP relaxed problem
        self.check_optimality()

    def print_solution(self):
        """
        Prints the lambda variables to terminal, if the model is finished and optimal
        :return:
        """
        if self.model.status == GRB.OPTIMAL:
            print("Optimal Master solution found:")
            for k in self.iterations_k:
                for l in self.locations_l:
                    print(f"Lambda [{l}, {k}]", self.lambda_var[l,k].X)

    def get_results_df(self):
        """
        Exports the lambda variable values from a solution to a Dataframe - for easier use by other functions
        :return:
        """
        lambda_list = []
        if self.model.status == GRB.OPTIMAL:
            for l in self.locations_l:
                location_list = []
                for k in self.iterations_k:
                    location_list.append(self.lambda_var[l,k].X)
                lambda_list.append(location_list)
        else:
            print("Model not optimal")
            return None

        df = pd.DataFrame(lambda_list, columns=[k for k in self.iterations_k], index=[l for l in self.locations_l])
        df.index.names = ["Location"]
        return df

    def print_shadow_prices(self):
        """
        Prints the shadow prices and names of the corresponding constraint to the terminal
        :return:
        """
        #Checks if the model has been solved to optimality
        if self.model.status == GRB.OPTIMAL:
            #Gets the shadow prices from the model, it is in the form of a dictionary
            shadow_prices = self.model.getAttr("Pi", self.model.getConstrs())
            #Iterates through all constraints in the dictionary
            for i, constraint in enumerate(self.model.getConstrs()):
                #Prints the constraint name - and the reduced cost related to that constraint
                print(f"Shadow price for constraint {i + 1} ({constraint.constrName}): {shadow_prices[i]}")

    def get_convexity_constr_shadow_prices_df(self):
        """
        Exports the shadow prices for the convexity constraints to a dataframe for easier use by other functions
        :return:
        """
        # Checks if the model has been solved to optimality
        if self.model.status == GRB.OPTIMAL:
            # Gets the shadow prices from the model, it is in the form of a dictionary. The Pi argument specifies that we get the shadow price attribute
            shadow_prices = self.model.getAttr("Pi", self.model.getConstrs())
            #Creates a list for storing the shadow prices
            shadow_prices_list = []
            #Iterates thorugh all constraints
            for i, constraint in enumerate(self.model.getConstrs()):
                #Splits the name into a constraint type component and a constraint number component
                #The type corresponds to the function for adding constraints - MAB and convexity in this model
                #The constraint number is the enumeration of the particular constraint
                constraint_type = constraint.constrName.split(";")[0]
                if constraint_type == "Convexity":
                    constraint_number = int(constraint.constrName.split(";")[1])
                    shadow_prices_list.append([constraint_number, shadow_prices[i]])

            df = pd.DataFrame([elem[1] for elem in shadow_prices_list],index=[elem[0] for elem in shadow_prices_list])
            df.index.names = ["Location"]

            return df

    def get_MAB_constr_shadow_prices_df(self):
        """
        Exports the shadow prices for the MAB constraints to a Dataframe for easier use by other functions
        :return:
        """
        # Checks if the model has been solved to optimality
        if self.model.status == GRB.OPTIMAL:
            # Gets the shadow prices from the model, it is in the form of a dictionary. The Pi argument specifies that we get the shadow price attribute
            shadow_prices = self.model.getAttr("Pi", self.model.getConstrs())
            # Create a list for storing the relevant shadow prices, and corresponding indices
            shadow_prices_list = []
            indices = []
            # Iterates through all constraints
            for i, constraint in enumerate(self.model.getConstrs()):
                #Fetches the constraint name from the constr object and split them into name and indices
                #The constraint name string is structured like this:  "{Type name};{Indice 1}, {Indice 2}, ..."

                #Fetching the constraint name
                constraint_type = constraint.constrName.split(";")[0]
                #Fetches the indices of the constraint
                constraint_indices = constraint.constrName.split(";")[1].split(",")
                #Transforms the indices from list of string elements into a list of int elements
                constraint_indices = [int(elem) for elem in constraint_indices]
                # Ensures that we only export the shadow prices for the constraints of the correct type
                if constraint_type == "MAB Constr":
                    #Appends the indices and the shadow prices to the storage lists
                    indices.append((constraint_indices[0], constraint_indices[1]))
                    shadow_prices_list.append(shadow_prices[i])

            #Constructs the index
            index = pd.MultiIndex.from_tuples(indices, names=["Scenario", "Period"])

            #Constructs the dataframe
            df = pd.DataFrame(shadow_prices_list, index=index)

            #Reorders the dataframe based on the index values
            df.sort_index(level="Period", inplace=True)
            df.sort_index(level="Scenario", inplace=True)

            return df

    def check_optimality(self):
        """
        Checks if the Dantzig-Wolfe decomposition has been solved to optimality.
        We check for optimality by comparing the lambda variables in this iteration with the iteration in the previous solution.
        If the Lambda variables are the same, no new information will be generated by the subproblems, thus we have reached optimality for the LP-relaxed problem.
        If optimality is reached we set the "self.model_is_optimal" to be true.

        :return:
        """

        #Checks it the previous solution objec is None. If so this is the first iteration and there is no previous solution.
        #If it is None, we set the previous solution to be the current solution
        try:
            if self.previous_solution == None:
                self.previous_solution = self.get_results_df()
                return None
        except:
            pass

        #Fetces the current solution using the get_results_df method. Which returns a df with the lambda variables in the current iteration
        new_solution = self.get_results_df()

        #The new solution will, since this function is run once every iteration, have one more column than the previous solution
        #Common columns returns the columns that the dataframes have in common
        common_columns = self.previous_solution.columns.intersection(new_solution.columns)

        #Checks if all elements in the columns the dataframe have in common are the same within a tolerance.
        is_the_same_within_tolerance = np.allclose(new_solution[common_columns], self.previous_solution[common_columns], rtol=0.01)
        if is_the_same_within_tolerance:
            #If te dataframes are the same -> We have reachec optimality -> Set is_model_solved variable to be true.
            self.is_model_solved = True

        #Sets current solution to be previous solution
        self.previous_solution = new_solution

    #TODO: Add tracker constraints for the dual variables
    #TODO: If optimale choose one variable to branch on









# TPPSF - Tactical production planning in salmon farming
This project is undertaken by two graduate students at the Norwegian University of Science and Technology. 
It´s purpose is to create a decision support system for the deployment and harvest of salmon under uncertainty, and provide a computational study to complement our masters degree. 

# Installation and requirements
To run this project, install the requirements from the `requirements.txt` file to your environment. 
You will also need a gurobi license installed to your system. 

# Navigating this project
| File                   | Description                                                                                                                           |
|------------------------|---------------------------------------------------------------------------------------------------------------------------------------|
| `input_data.py`        | Contains a class that reads in the data from the txt files in data and stores it in more useful pandas dataframes                     |
| `main.py`              | The main file, from where the other classes is orchestrated and the top level logic flow happens                                      |
| `master_problem.py`    | Contains the MasterProblem class, which instiantiates and solves an instance of the master problem                                    |
| `parameters.py`        | Contains a class, where we set all parameters that are global and not read from the data files                                        |
| `scenarios.py`         | Contains a class that takes temperatures as input and creates scenarios. The place to manage all data that is scenario specific       |
| `site_class.py`        | Contains a class, which shall contain all data that is site specific. Most prominently the growth factors dataframes are created here |
| `sub_problem_class.py` | Contains the SubProblem class, which instantiates and solves the sub problem                                                          |
| `sub_problem.py`       | Contains a script that solves a the tppsf for a single site.                                                                          |






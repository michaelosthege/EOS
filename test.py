#!/usr/bin/env python3

import numpy as np
from datetime import datetime
from pprint import pprint
import matplotlib.pyplot as plt
from deap import base, creator, tools, algorithms

# Import necessary modules from the project
from modules.class_optimize import optimization_problem
from modules.visualize import *

start_hour = 10

# PV Forecast (in W)
pv_forecast = [
    0, 0, 0, 0, 0, 0, 0, 8.05, 352.91, 728.51, 930.28, 1043.25, 
    1106.74, 1161.69, 6018.82, 5519.07, 3969.88, 3017.96, 1943.07, 
    1007.17, 319.67, 7.88, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5.04, 335.59, 
    705.32, 1121.12, 1604.79, 2157.38, 1433.25, 5718.49, 4553.96, 
    3027.55, 2574.46, 1720.4, 963.4, 383.3, 0, 0, 0
]

# Temperature Forecast (in degree C)
temperature_forecast = [
    18.3, 17.8, 16.9, 16.2, 15.6, 15.1, 14.6, 14.2, 14.3, 14.8, 15.7, 
    16.7, 17.4, 18.0, 18.6, 19.2, 19.1, 18.7, 18.5, 17.7, 16.2, 14.6, 
    13.6, 13.0, 12.6, 12.2, 11.7, 11.6, 11.3, 11.0, 10.7, 10.2, 11.4, 
    14.4, 16.4, 18.3, 19.5, 20.7, 21.9, 22.7, 23.1, 23.1, 22.8, 21.8, 
    20.2, 19.1, 18.0, 17.4
]

# Electricity Price (in Euro per Wh)
strompreis_euro_pro_wh = [
    0.0003384, 0.0003318, 0.0003284, 0.0003283, 0.0003289, 0.0003334, 
    0.0003290, 0.0003302, 0.0003042, 0.0002430, 0.0002280, 0.0002212, 
    0.0002093, 0.0001879, 0.0001838, 0.0002004, 0.0002198, 0.0002270, 
    0.0002997, 0.0003195, 0.0003081, 0.0002969, 0.0002921, 0.0002780, 
    0.0003384, 0.0003318, 0.0003284, 0.0003283, 0.0003289, 0.0003334, 
    0.0003290, 0.0003302, 0.0003042, 0.0002430, 0.0002280, 0.0002212, 
    0.0002093, 0.0001879, 0.0001838, 0.0002004, 0.0002198, 0.0002270, 
    0.0002997, 0.0003195, 0.0003081, 0.0002969, 0.0002921, 0.0002780
]

# Overall System Load (in W)
gesamtlast = [
    676.71, 876.19, 527.13, 468.88, 531.38, 517.95, 483.15, 472.28, 
    1011.68, 995.00, 1053.07, 1063.91, 1320.56, 1132.03, 1163.67, 
    1176.82, 1216.22, 1103.78, 1129.12, 1178.71, 1050.98, 988.56, 
    912.38, 704.61, 516.37, 868.05, 694.34, 608.79, 556.31, 488.89, 
    506.91, 804.89, 1141.98, 1056.97, 992.46, 1155.99, 827.01, 
    1257.98, 1232.67, 871.26, 860.88, 1158.03, 1222.72, 1221.04, 
    949.99, 987.01, 733.99, 592.97
]

# Start Solution (binary)
start_solution = [
    1, 1, 1, 1, 0, 1, 0, 0, 1, 1, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 
    1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 
    1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 
    1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 
    1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1
]

# Define parameters for the optimization problem
parameter = {
    "preis_euro_pro_wh_akku": 10e-05,                # Cost of storing energy in battery (per Wh)
    'pv_soc': 80,                                    # Initial state of charge (SOC) of PV battery (%)
    'pv_akku_cap': 26400,                            # Battery capacity (in Wh)
    'year_energy': 4100000,                          # Yearly energy consumption (in Wh)
    'einspeiseverguetung_euro_pro_wh': 7e-05,        # Feed-in tariff for exporting electricity (per Wh)
    'max_heizleistung': 1000,                        # Maximum heating power (in W)
    "gesamtlast": gesamtlast,                        # Overall load on the system
    'pv_forecast': pv_forecast,                      # PV generation forecast (48 hours)
    "temperature_forecast": temperature_forecast,    # Temperature forecast (48 hours)
    "strompreis_euro_pro_wh": strompreis_euro_pro_wh, # Electricity price forecast (48 hours)
    'eauto_min_soc': 0,                              # Minimum SOC for electric car
    'eauto_cap': 60000,                              # Electric car battery capacity (Wh)
    'eauto_charge_efficiency': 0.95,                 # Charging efficiency of the electric car
    'eauto_charge_power': 11040,                     # Charging power of the electric car (W)
    'eauto_soc': 54,                                 # Current SOC of the electric car (%)
    'pvpowernow': 211.137503624,                     # Current PV power generation (W)
    'start_solution': start_solution,                # Initial solution for the optimization
    'haushaltsgeraet_wh': 937,                       # Household appliance consumption (Wh)
    'haushaltsgeraet_dauer': 0                       # Duration of appliance usage (hours)
}

# Initialize the optimization problem
opt_class = optimization_problem(prediction_hours=48, strafe=10, optimization_hours=24)

# Perform the optimisation based on the provided parameters and start hour
ergebnis = opt_class.optimierung_ems(parameter=parameter, start_hour=start_hour)

# Print or visualize the result
pprint(ergebnis)

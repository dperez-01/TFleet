'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        settings.py

 Author:      Diego Pérez

 Created:     10/06/2025
 Copyright:   (c) perez 2025
-------------------------------------------------------------------------------
'''
import json
import traceback
import sys
from tkinter import messagebox

from pathlib import Path
settingspath = Path(__file__).parent / Path(r".\settings")
def relative_to_settings(path: str) -> Path:
    return settingspath / Path(path)

LANGUAGE = None
# OPTIMISER = None
SAVELOAD_CONFIRMATION = None
GAP_HOUR = None
GAP_MINUTES = None
MDURATION_TO_EXCEL = None
MAINTENANCE_COLOR = None
EXTRA_ROWS = None
HEURISTIC_STEPS = None
HEURISTIC_ITERS_PER_STEP = None
HEURISTIC_SOLVE_ABOVE_ALL = None
AVOIDANCE_MARGIN = None
CRITICAL_MARGIN = None
# GUROBI_MIPFOCUS = None
# GUROBI_PRESOLVE = None
# GUROBI_METHOD = None
DEFAULT_INTERVENTION = None
DEFAULT_INTERVENTION_KM = None
DEFAULT_INTERVENTION_TIME = None
HEURISTIC_DAYS_PER_CUT = None
HEURISTIC_NUMBER_OF_CUTS = None

COLOUR_PALETTE = None
DISP_COLOUR_PALETTE = None

def import_from_JSON():
    global LANGUAGE, MAINTENANCE_COLOR, EXTRA_ROWS, MDURATION_TO_EXCEL, SAVELOAD_CONFIRMATION, HEURISTIC_STEPS, HEURISTIC_ITERS_PER_STEP, HEURISTIC_SOLVE_ABOVE_ALL, GAP_MINUTES, GAP_HOUR, AVOIDANCE_MARGIN, CRITICAL_MARGIN, DEFAULT_INTERVENTION, DEFAULT_INTERVENTION_KM, DEFAULT_INTERVENTION_TIME, HEURISTIC_DAYS_PER_CUT, HEURISTIC_NUMBER_OF_CUTS, COLOUR_PALETTE, DISP_COLOUR_PALETTE

    file = open(relative_to_settings('settings.json'), 'r')
    try:
        assets = json.load(file)
        file.close()

        LANGUAGE = assets['LANGUAGE']
        # OPTIMISER = assets['OPTIMISER']
        MAINTENANCE_COLOR = assets['MAINTENANCE_COLOR']
        EXTRA_ROWS = assets['EXTRA_ROWS']
        MDURATION_TO_EXCEL = assets['MDURATION_TO_EXCEL']
        SAVELOAD_CONFIRMATION = assets['SAVELOAD_CONFIRMATION']
        HEURISTIC_STEPS = assets['HEURISTIC_STEPS']
        HEURISTIC_ITERS_PER_STEP = assets['HEURISTIC_ITERS_PER_STEP']
        HEURISTIC_SOLVE_ABOVE_ALL = assets['HEURISTIC_SOLVE_ABOVE_ALL']
        # GUROBI_MIPFOCUS = assets['GUROBI_MIPFOCUS']
        # GUROBI_PRESOLVE = assets['GUROBI_PRESOLVE']
        # GUROBI_METHOD = assets['GUROBI_METHOD']
        GAP_MINUTES = assets['GAP_MINUTES']
        GAP_HOUR = GAP_MINUTES / 60
        AVOIDANCE_MARGIN = assets['AVOIDANCE_MARGIN']
        CRITICAL_MARGIN = assets['CRITICAL_MARGIN']
        DEFAULT_INTERVENTION = assets['DEFAULT_INTERVENTION']
        DEFAULT_INTERVENTION_KM = assets['DEFAULT_INTERVENTION_KM']
        DEFAULT_INTERVENTION_TIME = assets['DEFAULT_INTERVENTION_TIME']
        HEURISTIC_DAYS_PER_CUT = assets['HEURISTIC_DAYS_PER_CUT']
        HEURISTIC_NUMBER_OF_CUTS = assets['HEURISTIC_NUMBER_OF_CUTS']
        COLOUR_PALETTE = assets['COLOUR_PALETTE']
        DISP_COLOUR_PALETTE = assets['DISP_COLOUR_PALETTE']

    except:
        error = traceback.format_exc()
        messagebox.showerror('Error when looking for settings file', 'An error occurred when looking for settings file. Did you delete or modify it?\n' + str(error))
        file.close()
        sys.exit()

import_from_JSON()
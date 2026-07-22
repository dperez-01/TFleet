'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        HEURISTIC_handler.py

 Author:      Diego Pérez

 Created:     27/05/2024
 Copyright:   (c) perez 2024
-------------------------------------------------------------------------------
'''
from copy import deepcopy
from tkinter import Toplevel, PhotoImage, Frame, Text, Button, messagebox

from canvasclass import FullCanvas

from HEURISTIC_model_V2 import heuristic_handler, multienvironment_heuristic_handler

import settings

# Now, import language and assets
from pathlib import Path
from time import time
if settings.LANGUAGE == 'English':
    import language.EN as lang
    if settings.COLOUR_PALETTE == 'Dark':
        import colour.night_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\night\solved")
    elif settings.COLOUR_PALETTE == 'Light':
        import colour.day_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\day\solved")
    elif settings.COLOUR_PALETTE == 'Blue':
        import colour.blue_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\blue\solved")

elif settings.LANGUAGE == 'Castellano':
    import language.ES as lang
    if settings.COLOUR_PALETTE == 'Dark':
        import colour.night_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\night\solved")
    elif settings.COLOUR_PALETTE == 'Light':
        import colour.day_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\day\solved")
    elif settings.COLOUR_PALETTE == 'Blue':
        import colour.blue_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\blue\solved")

import webbrowser
import threading
import ctypes
from help_manager import open_help

results_object = None # TODO por que es encesario ir andando con esta variable por ahi. Seguro que al cerrar la ventana la memoria asociada a la variable no se borra tras ahber sido un FullCanvas?

def relative_to_solved(path: str) -> Path:
    return OUTPUT_PATH / Path(path)

def log_and_solve(startmenu, numtrains, basetrainid, basenodes, baseshortenings, baseservices, baseiniservices, basenext_m_duration, basenext_mname, basekm_limit, basedepot, baselinkers, basetransfers, basesleepers, *args):
    global results_object
    results_object = None

    matrix = args[0]
    numservices = args[1]
    starting_day = args[2]

    if isinstance(matrix['predecessors'], int):
        return messagebox.showerror(lang.cc36, lang.hh1 + str(matrix['table_conversion'][matrix['predecessors']]))

    solved = Toplevel(startmenu)

    screen_width = solved.winfo_screenwidth()
    screen_height = solved.winfo_screenheight()
    x = (screen_width - 1280) // 2
    y = (screen_height - 720) // 2
    solved.geometry(f"1440x810+{x}+{y}")

    solved.configure(bg="pink")
    solved.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
    solved.title(lang.hh2)
    solved_icon = PhotoImage(file=relative_to_solved("icon1.png"))
    solved.iconphoto(False, solved_icon)
    solved.lift()

    log_text = Text(solved, bd=8, font=('TkFixedFont', 11), relief='flat', highlightcolor='#0b141a', highlightbackground='#0b141a', highlightthickness=2, bg="#0b141a", fg="#ebeff1")
    log_text.pack(side='top', fill='both', expand=True)
    log_text.configure(state="disabled")

    solvedbuttonframe = Frame(solved, bg=colour.WINDOW_BACKGROUNDS, highlightthickness=0)
    solvedbuttonframe.pack(side='bottom', fill='x')

    extrabuttonframe = Frame(solvedbuttonframe, bg=colour.WINDOW_BACKGROUNDS, highlightthickness=0)

    optimiser = heuristic_handler(windowlog=solved, textlog=log_text, km_limit=matrix['trimmed_km_limit'], next_m_duration=basenext_m_duration, numtrains=numtrains, numservices=numservices, table_conversion=matrix['table_conversion'], km_service=matrix['km_service'], departure_time=matrix['departure_time'], predecessors=matrix['predecessors'], condition=matrix['condition'], depot=matrix['depot'], total_capacity=matrix['total_capacity'], capacities_management=matrix['capacities_management'], uses_linkers = matrix['uses_linkers'], valid_linkers = matrix['valid_linkers'], kmlinker = matrix['linkers_km'], total_linkers_capacity = matrix['linkers_capacity'], avoidance_margin=settings.AVOIDANCE_MARGIN, critical_margin=settings.CRITICAL_MARGIN)
    def kill_env():
        optimiser.stop_order = True

    def rerun():
        thread = threading.Thread(target=optimiser.optimise, args=(settings.HEURISTIC_STEPS, settings.HEURISTIC_ITERS_PER_STEP, False))
        thread.start()

    def plot(rerun_button, proceed_button, log_text, solvedbuttonframe):
        global results_object

        log_text.pack_forget()
        rerun_button.pack_forget()
        proceed_button.pack_forget()
        solvedbuttonframe.pack_forget()

        # Var storing required
        best_schedule = [[int(optimiser.best_schedule[i,j]) for i in range(optimiser.best_schedule.shape[0])] for j in range(optimiser.best_schedule.shape[1])]
        best_maintenance = [float(time) for time in optimiser.best_maintenance]
        best_linkers = optimiser.best_linkers.copy()

        results_object = FullCanvas(init_mode='standard', parentwindow=solved, basenodes=deepcopy(basenodes), baseshortenings=deepcopy(baseshortenings), baseservices=deepcopy(baseservices), baselinkers=deepcopy(baselinkers), basetransfers=deepcopy(basetransfers), basesleepers=deepcopy(basesleepers), iniservices=deepcopy(baseiniservices), numtrains=numtrains, starting_day=starting_day, trainid=deepcopy(basetrainid), km_limit=deepcopy(basekm_limit), depot=deepcopy(basedepot), maintenance_duration=deepcopy(basenext_m_duration), maintenance_name=deepcopy(basenext_mname), solution_x=best_schedule, departure_time=matrix['departure_time'], duration_service=matrix['duration_service'], conditioned_successor=matrix['stringed_condition'], banned_successors=matrix['bans'], origins=matrix['origins'], destinies=matrix['destinies'], table_conversion=matrix['table_conversion'], km_service=matrix['km_service'], dict_color=matrix['dict_color'], str_departures=matrix['stringed_departures'], str_arrivals=matrix['stringed_arrivals'], solution_maintenance=best_maintenance, solution_linkers=best_linkers, info_linkers=matrix['info_linkers'])
        solved.update()


    kill_button = Button(master=solvedbuttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg="#15181a", command=kill_env)
    kill_button.image = PhotoImage(file=relative_to_solved('kill_button.png'))
    kill_button.configure(image=kill_button.image)

    rerun_button = Button(master=extrabuttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg="#15181a", command=rerun)
    rerun_button.image = PhotoImage(file=relative_to_solved('rerun.png'))
    rerun_button.configure(image=rerun_button.image)

    proceed_button = Button(master=extrabuttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg="#15181a", command=lambda: plot(rerun_button, proceed_button, log_text, solvedbuttonframe))
    proceed_button.image = PhotoImage(file=relative_to_solved('proceed.png'))
    proceed_button.configure(image=proceed_button.image)

    kill_button.pack(padx=20, pady=10)
    rerun_button.pack(side='left', padx=20, pady=10)
    proceed_button.pack(side='right', padx=20, pady=10)

    solved.update()
    def solved_status(old_value, new_value):
        if optimiser.nuke_order:
            return

        # Case: finished current run
        if not old_value and new_value:  # old value == False and new value == True
            kill_button.pack_forget()
            extrabuttonframe.pack()

        # Case: do another run
        elif old_value and not new_value:  # old value == False and new value == True
            extrabuttonframe.pack_forget()
            kill_button.pack(padx=20, pady=10)

    optimiser.finishtracker.register_callback(solved_status)

    thread = threading.Thread(target=optimiser.optimise, args=(settings.HEURISTIC_STEPS, settings.HEURISTIC_ITERS_PER_STEP))
    thread.start()

    def nuke_the_env(event):
        global results_object

        if event.widget == event.widget.winfo_toplevel():
            if not optimiser.finishtracker.value: # noqa
                optimiser.nuke_order = True
                # for tid, tobj in threading._active.items(): print(tid, tobj, tobj.is_alive())

            # try:
            #     del results_object
            # except:
            #     pass

            results_object = None

    solved.bind('<Destroy>', nuke_the_env)

    solved.mainloop()

def autocut_log_and_solve(startmenu, numtrains, basetrainid, basenodes, baseshortenings, baseweekday, baseiniservices, baseservices, basenext_m_duration, basenext_mname, basekm_limit, basedepot, basetransfers, basesleepers, baselinkers):
    global results_object
    results_object = None


    solved = Toplevel(startmenu)
    st_time = time()

    screen_width = solved.winfo_screenwidth()
    screen_height = solved.winfo_screenheight()
    x = (screen_width - 1280) // 2
    y = (screen_height - 720) // 2
    solved.geometry(f"1440x810+{x}+{y}")

    solved.configure(bg="pink")
    solved.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
    solved.title(lang.hh2)
    solved_icon = PhotoImage(file=relative_to_solved("icon1.png"))
    solved.iconphoto(False, solved_icon)
    solved.lift()

    log_text = Text(solved, bd=8, font=('TkFixedFont', 11), relief='flat', highlightcolor='#0b141a', highlightbackground='#0b141a', highlightthickness=2, bg="#0b141a", fg="#ebeff1")
    log_text.pack(side='top', fill='both', expand=True)
    log_text.configure(state="disabled")

    solvedbuttonframe = Frame(solved, bg="#15181a", highlightthickness=0)
    solvedbuttonframe.pack(side='bottom', fill='x')

    # Optimiser
    optimiser = multienvironment_heuristic_handler(cuts=settings.HEURISTIC_NUMBER_OF_CUTS, days_per_cut=settings.HEURISTIC_DAYS_PER_CUT, starting_weekday=baseweekday, windowlog=solved, textlog=log_text, depotnodes=basedepot, realservices=baseservices, iniservices=baseiniservices, km_limit=basekm_limit, next_m_duration=basenext_m_duration, next_m_name=basenext_mname, numtrains=numtrains, transfers=basetransfers, reallinkers=baselinkers, avoidance_margin=settings.AVOIDANCE_MARGIN, critical_margin=settings.CRITICAL_MARGIN)
    def kill_env():
        optimiser.stop_order = True

    def plot(log_text, solvedbuttonframe):
        global results_object

        log_text.pack_forget()
        solvedbuttonframe.pack_forget()

        # Embebido de figura compleja:
        # Var storing required
        best_schedule = [[int(optimiser.store_schedule[i,j]) for i in range(optimiser.store_schedule.shape[0])] for j in range(optimiser.store_schedule.shape[1])]
        print('TOTAL TIME:', time() - st_time)

        results_object = FullCanvas(init_mode='standard', parentwindow=solved, basenodes=deepcopy(basenodes), baseshortenings=deepcopy(baseshortenings), baseservices=deepcopy(baseservices), baselinkers=deepcopy(baselinkers), basetransfers=deepcopy(basetransfers), basesleepers=deepcopy(basesleepers), iniservices=deepcopy(baseiniservices), numtrains=numtrains, starting_day=baseweekday, trainid=deepcopy(basetrainid), km_limit=basekm_limit, depot=deepcopy(basedepot), maintenance_duration=deepcopy(basenext_m_duration), maintenance_name=deepcopy(basenext_mname), solution_x=best_schedule, departure_time=optimiser.store_departure_time, duration_service=optimiser.store_duration_service, conditioned_successor=optimiser.store_str_condition, banned_successors=optimiser.store_banned_successors, origins=optimiser.store_origins, destinies=optimiser.store_destinies, table_conversion=optimiser.store_table_conversion, km_service=optimiser.store_km_service, dict_color=optimiser.store_dict_color, str_departures=optimiser.store_str_departures, str_arrivals=optimiser.store_str_arrivals, solution_maintenance=optimiser.store_maintenance, multiple_next_m_name=optimiser.store_next_m_name, multiple_next_m_duration=optimiser.store_next_m_duration, multiple_km_limit=optimiser.store_km_limit, solution_linkers=optimiser.store_linkers_solution, info_linkers=optimiser.store_info_linkers)
        solved.update()

    def solved_status(old_value, new_value):
        if optimiser.nuke_order:
            return

        # finished run
        if not old_value and new_value:  # old value == False and new value == True
            plot(log_text, solvedbuttonframe)

    optimiser.finishtracker.register_callback(solved_status)
    thread = threading.Thread(target=optimiser.multiple_run)
    thread.start()

    kill_button = Button(master=solvedbuttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg="#15181a", command=kill_env)
    kill_button.image = PhotoImage(file=relative_to_solved('kill_button.png'))
    kill_button.configure(image=kill_button.image)


    def nuke_the_env(event):
        global results_object
        if event.widget == event.widget.winfo_toplevel():
            if not optimiser.finishtracker.value: # noqa
                optimiser.nuke_order = True
            results_object = None

    solved.bind('<Destroy>', nuke_the_env)
    solved.mainloop()
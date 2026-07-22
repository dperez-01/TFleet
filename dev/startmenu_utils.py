'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        startmenu_utils.py

 Author:      Diego Pérez

 Created:     19/11/2024
 Copyright:   (c) perez 2024
-------------------------------------------------------------------------------
'''
from copy import deepcopy

# First of all, import settings manager to configure the applicaction
import settings

# Now, import language and assets
from pathlib import Path
if settings.LANGUAGE == 'English':
    import language.EN as lang
    import language.ES as other_lang  # Ensure compatibility between loaded files
    if settings.COLOUR_PALETTE == 'Dark':
        import colour.night_palette as colour
        OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\EN\night\startmenu")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\night\solved")
    elif settings.COLOUR_PALETTE == 'Light':
        import colour.day_palette as colour
        OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\EN\day\startmenu")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\day\solved")
    elif settings.COLOUR_PALETTE == 'Blue':
        import colour.blue_palette as colour
        OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\EN\blue\startmenu")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\blue\solved")

elif settings.LANGUAGE == 'Castellano':
    import language.ES as lang
    import language.EN as other_lang  # Ensure compatibility between loaded files
    if settings.COLOUR_PALETTE == 'Dark':
        import colour.night_palette as colour
        OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\ES\night\startmenu")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\night\solved")
    elif settings.COLOUR_PALETTE == 'Light':
        import colour.day_palette as colour
        OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\ES\day\startmenu")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\day\solved")
    elif settings.COLOUR_PALETTE == 'Blue':
        import colour.blue_palette as colour
        OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\ES\blue\startmenu")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\blue\solved")

# Continue with optimiser
import HEURISTIC_handler as optimiser_handler
import HEURISTIC_matrix_builder as builder

import ast
import ctypes.wintypes
import traceback
import json
import webbrowser

from tkinter import Toplevel, messagebox, filedialog, PhotoImage, Button, Frame, Label
from tkinter.ttk import Combobox

# App imports
import win_nodes
import win_services
import win_iniservices
import win_depottransfers
import win_sleepers
import win_linkers
from canvasclass import FullCanvas
from help_manager import open_help
import startmenu_blocker as window_blocker

def relative_to_assets(path: str) -> Path:
    return OUTPUT_PATH1 / Path(path)
def relative_to_solved(path: str) -> Path:
    return OUTPUT_PATH2 / Path(path)

def _load_json_with_lang_replacements(filepath):
    # read raw text
    with open(filepath, 'r', encoding='utf-8') as fh:
        raw = fh.read()

    # Generic language replacements
    raw = raw.replace(other_lang.DEPOT_MAINTENANCE, lang.DEPOT_MAINTENANCE)
    raw = raw.replace(other_lang.DEPOT_OVERNIGHT, lang.DEPOT_OVERNIGHT)

    # Initial day replacement
    for i in range(8):
        raw = raw.replace(other_lang.CURRENT_PLUS_WEEK[i], lang.CURRENT_PLUS_WEEK[i])

    # parse JSON from replaced text
    return json.loads(raw)

def merger_chooser(popup: Toplevel, combobox: Combobox, values: list, elements_ref: list, filedata: dict, filename: str):
    day = values.index(combobox.get())
    elements_ref.append([filedata, day, filename])
    popup.destroy()

def merger(winmaster):
    elements = []
    last_selected_file = lang.utils_notyet
    last_selected_day = lang.utils_notyet
    while True:
        add_more = messagebox.askyesnocancel(lang.utils_addmore, lang.utils_lastfile + last_selected_file + lang.utils_lastday + last_selected_day)
        if add_more == None:
            return
        elif not add_more:
            break
        else:
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            here = ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, buf)

            filename = filedialog.askopenfilename(initialdir=here, defaultextension='.FSsolved', filetypes=[("FleetScheduler solution", ".FSsolved"), ("JSON file", ".json"), ("All files", ".*")])
            if filename is None or filename == '':
                continue

            try:
                filedata = _load_json_with_lang_replacements(filename)

            except:
                error = traceback.format_exc()
                messagebox.showerror(lang.utils_errorsolved, lang.utils_errorsolveddesc + str(error))
                return

            popup = Toplevel(winmaster, bg=colour.WINDOW_BACKGROUNDS)
            popup.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
            popup.title(lang.utils_chooseday)
            popup.attributes('-topmost', True)
            popup.overrideredirect(True)

            border = Frame(popup, bg=colour.WINDOW_BACKGROUNDS, highlightthickness=2, highlightbackground=colour.TITLES_FOREGROUND, highlightcolor=colour.TITLES_FOREGROUND)
            border.pack(fill='both', expand=True)

            Label(border, font=('futura', 10), text=lang.utils_monolastfile, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND, highlightthickness=0).grid(row=0, column=0, sticky='w', padx=(20, 10), pady=(20, 0))
            Label(border, font=('futura', 10), text=last_selected_file, bg=colour.WINDOW_BACKGROUNDS, fg=colour.MERGER_FILES, highlightthickness=0).grid(row=1, column=0, sticky='w', padx=(20, 10))

            Label(border, font=('futura', 10), text=lang.utils_monolastday, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND, highlightthickness=0).grid(row=2, column=0, sticky='w', padx=(20, 10))
            Label(border, font=('futura', 10), text=last_selected_day, bg=colour.WINDOW_BACKGROUNDS, fg=colour.MERGER_FILES, highlightthickness=0).grid(row=3, column=0, sticky='w', padx=(20, 10))
            Frame(border, bg='#000000', height=3).grid(row=4, column=0, sticky='ew')

            cut_filename = filename.split('/')[-1]
            Label(border, font=('futura', 10), text=lang.utils_selectinglastday, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND, highlightthickness=0).grid(row=5, column=0, sticky='w', padx=(20, 10))
            Label(border, font=('futura', 10), text=cut_filename, bg=colour.WINDOW_BACKGROUNDS, fg=colour.MERGER_FILES, highlightthickness=0).grid(row=6, column=0, sticky='w', padx=(20, 10))

            picker = Combobox(border, values=filedata['str_week'], font=('futura', 13), width=10, state='readonly')
            picker.set(filedata['str_week'][0])
            picker.bind("<<ComboboxSelected>>", lambda e: border.focus_set())
            picker.grid(row=7, column=0, padx=(20, 10), pady=(10, 20), sticky='w')

            btn = Button(border, image=PhotoImage(file=relative_to_assets('pick_day.png')), borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS, command=lambda: merger_chooser(popup, picker, filedata['str_week'], elements, filedata, cut_filename))
            btn.image = PhotoImage(file=relative_to_assets('pick_day.png'))
            btn.configure(image=btn.image)
            btn.grid(row=0, rowspan=8, column=1, padx=(10, 20), pady=20)

            popup.update()
            screen_width = popup.winfo_screenwidth()
            screen_height = popup.winfo_screenheight()
            x = (screen_width - popup.winfo_reqwidth()) // 2
            y = (screen_height - popup.winfo_reqheight()) // 2
            popup.geometry(f"+{x}+{y}")

            popup.wait_window(popup)
            last_selected_file = cut_filename
            last_selected_day = filedata['str_week'][elements[-1][1]]

    # Begin some checking and construction of a new solution
    iterated_sols = 0
    services_sorted_train = {}
    transfers_sorted_train = {}
    maintenances_sorted_train = {}
    extra_rows_services = []
    extra_rows_maintenance = []
    extra_rows_transfers = []
    x_ref_base = 0  # A reference for x_values needs to be kept between files
    for i in range(len(elements)):
        assets = elements[i][0]

        iterated_sols += 1

        if iterated_sols > 1:  # Check with last one
            if (not assets['str_week'][0] in latest_cutday):  # noqa
                ask = messagebox.askyesno(lang.utils_minorerror, lang.utils_merge1 + latest_filename + lang.utils_notday + elements[i][2] + lang.utils_continue1)  # noqa
                if not ask:
                    return

            if latest_basenodes != assets['basenodes']:  # noqa
                ask = messagebox.askyesno(lang.utils_fatalerror, lang.utils_merge2 + elements[i][2] + lang.utils_mergeand + latest_filename + lang.utils_continue2)  # noqa
                if not ask:
                    return

            if latest_depot != assets['depot']:  # noqa
                ask = messagebox.askyesno(lang.utils_fatalerror, lang.utils_merge3 + elements[i][2] + lang.utils_mergeand + latest_filename + lang.utils_continue2)  # noqa
                if not ask:
                    return

            if lastest_transfers != assets['basetransfers']:  # noqa
                ask = messagebox.askyesno(lang.utils_minorerror, lang.utils_merge4 + elements[i][2] + lang.utils_mergeand + latest_filename + lang.utils_continue2)  # noqa
                if not ask:
                    return

            if latest_sleepers != assets['basesleepers']:  # noqa
                ask = messagebox.askyesno(lang.utils_minorerror, lang.utils_merge5 + elements[i][2] + lang.utils_mergeand + latest_filename + lang.utils_continue2)  # noqa
                if not ask:
                    return

            try:
                if latest_linkers != assets['baselinkers']:  # noqa
                    ask = messagebox.askyesno(lang.utils_minorerror, lang.utils_merge8 + elements[i][2] + lang.utils_mergeand + latest_filename + lang.utils_continue2)  # noqa
                    if not ask:
                        return
            except KeyError:
                pass

            if latest_baseservices != assets['baseservices']:  # noqa
                ask = messagebox.askyesno(lang.utils_minorerror, lang.utils_merge6 + elements[i][2] + lang.utils_mergeand + latest_filename + lang.utils_continue2)  # noqa
                if not ask:
                    return

            if latest_shortenings != assets['shortenings']:  # noqa
                ask = messagebox.askyesno(lang.utils_minorerror, lang_utils_merge7 + elements[i][2] + lang.utils_mergeand + latest_filename + lang.utils_continue2)  # noqa
                if not ask:
                    return

        else:
            starting_day = assets['starting_day']  # Expected to be different

        latest_filename = elements[i][2]
        latest_cutday = assets['str_week'][elements[i][1]]  # Can be used with the first element of str_week to see if schedule fits properly

        latest_services = assets['services']  # Expected to be different
        latest_maintenances = assets['maintenances']  # Expected to be different
        latest_transfers = assets['transfers'] # Expected to be different
        latest_baseservices = assets['baseservices']  # Checked, relaxed requirement
        latest_basenodes = assets['basenodes']  # Checked, strict requirement
        latest_shortenings = assets['shortenings']  # Checked, relaxed requirement
        latest_numtrains = assets['numtrains']  # Checked, strict requirement
        latest_trainid = assets['trainid']  # Checked, relaxed requirement
        latest_km_limit = assets['km_limit']  # Expected to be different
        latest_depot = assets['depot']  # Checked, strict requirement
        latest_maintenance_name = assets['maintenance_name']  # Expected to be different
        latest_maintenance_duration = assets['maintenance_duration']  # Expected to be different
        lastest_transfers = assets['basetransfers']  # Checked, relaxed requirement
        latest_sleepers = assets['basesleepers']  # Checked, relaxed requirement
        try:
            latest_linkers = assets['baselinkers']  # Checked, relaxed requirement
        except KeyError:
            latest_linkers = {}

        # Prepare trains
        trains_yref = []
        for train in latest_trainid.values():
            if train not in services_sorted_train:
                services_sorted_train[train] = []
                transfers_sorted_train[train] = []
                maintenances_sorted_train[train] = []

            # A referential object is needed to understand relation between y-axis and IDs
            trains_yref.insert(0, train)

        # Cut x-value
        last_hour = 24 * elements[i][1]

        # Define iniservices
        if iterated_sols == 1: # First time
            for s in range(latest_numtrains):
                train = trains_yref[int(latest_services['s' + str(s + 1)][0][1])]
                services_sorted_train[train].append(latest_services['s' + str(s + 1)])
                services_sorted_train[train][-1][0][0] += x_ref_base


        for s in range(latest_numtrains, len(latest_services)): # Always consider "if a service is being cut, it will be used from the previous file; if not, the iniservice of the current file is fictional and should not be included"
            if latest_services['s' + str(s + 1)][0][0] > last_hour:
                continue
            else:
                try:
                    train = trains_yref[int(latest_services['s' + str(s + 1)][0][1])]
                    services_sorted_train[train].append(latest_services['s' + str(s + 1)])
                    services_sorted_train[train][-1][0][0] += x_ref_base
                except IndexError:
                    extra_rows_services.append(latest_services['s' + str(s + 1)])
                    extra_rows_services[-1][0][0] += x_ref_base

        for t in range(len(latest_transfers)):
            if latest_transfers['t' + str(t + 1)][0][0] > last_hour:
                continue
            else:
                try:
                    train = trains_yref[int(latest_transfers['t' + str(t + 1)][0][1])]
                    transfers_sorted_train[train].append(latest_transfers['t' + str(t + 1)])
                    transfers_sorted_train[train][-1][0][0] += x_ref_base
                except IndexError:
                    extra_rows_transfers.append(latest_transfers['t' + str(t + 1)])
                    extra_rows_transfers[-1][0][0] += x_ref_base

        for m in range(len(latest_maintenances)):
            if latest_maintenances['m' + str(m + 1)][0][0] > last_hour:
                continue
            else:
                try:
                    train = trains_yref[int(latest_maintenances['m' + str(m + 1)][0][1])]
                    maintenances_sorted_train[train].append(latest_maintenances['m' + str(m + 1)])
                    maintenances_sorted_train[train][-1][0][0] += x_ref_base
                except IndexError:
                    extra_rows_maintenance.append(latest_maintenances['m' + str(m + 1)])
                    extra_rows_maintenance[-1][0][0] += x_ref_base

        x_ref_base += last_hour

    # All data has been explored. All trains, and data from last file is stored. Proceed with building the solution according to .FSSolved "standard"
    # Sort trains
    aux_sorter = []  # Would not be necessary if we use a list rather than a dict
    for train in services_sorted_train:
        aux_sorter.append(train)

    # As trainIDs were sorted, this needs to be sorted too.
    # TODO Warning! This is not taking into account that numtrains might not be a constant (because of using latest_XXX, mainly). A dict approach might be used, similar as "if train not in services_sorted_train"; however, in this case we will OVERRIDE ALWAYS
    maintenance_duration = [x for _, x in sorted(zip(aux_sorter, latest_maintenance_duration))]  # noqa
    maintenance_name = [x for _, x in sorted(zip(aux_sorter, latest_maintenance_name))]  # noqa
    aux_sorter = sorted(aux_sorter)

    # Trainids
    trainid = {}
    numtrains = len(aux_sorter)
    refypos = numtrains - 1
    for i in range(len(aux_sorter)):
        trainid['train' + str(i + 1)] = aux_sorter[i]

    # Sort services and maintenances
    services_list = []
    for train in services_sorted_train:
        for s in range(len(services_sorted_train[train])):
            services_sorted_train[train][s][0][1] = refypos - aux_sorter.index(train)
            services_list.append(services_sorted_train[train][s])

    services_list = sorted(services_list, key=lambda item: item[0][0])
    services = {}
    for s in range(len(services_list)):
        services['s' + str(s + 1)] = services_list[s]
    for s in range(len(extra_rows_services)):
        services['s' + str(len(services) + 1)] = extra_rows_services[s]

    transfers_list = []
    for train in transfers_sorted_train:
        for t in range(len(transfers_sorted_train[train])):
            transfers_sorted_train[train][t][0][1] = refypos - aux_sorter.index(train)
            transfers_list.append(transfers_sorted_train[train][t])

    transfers_list = sorted(transfers_list, key=lambda item: item[0][0])
    transfers = {}
    for t in range(len(transfers_list)):
        transfers['t' + str(t + 1)] = transfers_list[t]
    for t in range(len(extra_rows_transfers)):
        transfers['t' + str(len(transfers) + 1)] = extra_rows_transfers[t]

    maintenances_list = []
    for train in maintenances_sorted_train:
        for m in range(len(maintenances_sorted_train[train])):
            maintenances_sorted_train[train][m][0][1] = refypos - aux_sorter.index(train)
            maintenances_list.append(maintenances_sorted_train[train][m])

    maintenances_list = sorted(maintenances_list, key=lambda item: item[0][0])
    maintenances = {}
    for m in range(len(maintenances_list)):
        maintenances['m' + str(m + 1)] = maintenances_list[m]
    for m in range(len(extra_rows_maintenance)):
        maintenances['m' + str(len(maintenances) + 1)] = extra_rows_maintenance[m]

    # Plot
    solved = Toplevel(winmaster)
    solved.geometry("1440x810+50+50")
    solved.configure(bg="#FFFFFF")
    solved.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
    solved.title(lang.utils_solvedtitle)
    solved_icon = PhotoImage(file=relative_to_solved("icon1.png"))
    solved.iconphoto(False, solved_icon)
    solved.lift()

    results_object = FullCanvas(init_mode='existing_data', parentwindow=solved, basenodes=latest_basenodes, baseshortenings=latest_shortenings, baseservices=latest_baseservices, basetransfers=lastest_transfers, basesleepers=latest_sleepers, baselinkers=latest_linkers, numtrains=numtrains, starting_day=starting_day, trainid=trainid, km_limit=latest_km_limit, depot=latest_depot, maintenance_duration=maintenance_duration, maintenance_name=maintenance_name, s_collection=services, m_collection=maintenances, t_collection=transfers)  # noqa TODO se necesita meter la t_colelctions

    solved.mainloop()  # TODO por qué necesita un mainloop si es una TopLevel?

def save_file():
    if window_blocker.IS_OPEN:
        messagebox.showinfo(lang.generic_windowopen, lang.generic_pleaseclose)
        return

    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    here = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    file = filedialog.asksaveasfile(initialfile='untitled.cfg', initialdir=here, defaultextension='.cfg', filetypes=[("Config. file", ".cfg"), ("Text file", ".txt"), ("All files", ".*")])
    if file is None:
        return
    try:

        file.writelines([
            str(win_iniservices.km_limit),
            "\n" + str(win_iniservices.next_mname),
            "\n" + str(win_iniservices.next_m_duration),
            "\n" + str(win_iniservices.trainid),
            "\n" + str(win_nodes.nodeslist),
            "\n" + str(win_nodes.shortenings),
            "\n" + str(win_nodes.depotnodes),
            "\n" + str(win_services.services),
            "\n" + str(win_services.WEEKDAY),
            "\n" + str(win_iniservices.iniservices),
            "\n" + str(win_nodes.NODES_ARE_NEW),
            "\n" + str(win_depottransfers.transfers),
            "\n" + str(win_sleepers.sleepers),
            "\n" + str(win_linkers.linkers)
            ])
        file.close()
        if settings.SAVELOAD_CONFIRMATION:
            messagebox.showinfo(lang.utils_success, lang.utils_configsaved + str(file))

    except:
        error = traceback.format_exc()
        messagebox.showerror(lang.utils_errorsave, lang.utils_errorsavedesc + str(error))
        file.close()

def load_file():
    if window_blocker.IS_OPEN:
        messagebox.showinfo(lang.generic_windowopen, lang.generic_pleaseclose)
        return

    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    here = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    file = filedialog.askopenfilename(initialdir=here, defaultextension='.cfg', filetypes=[("Config. file", ".cfg"), ("Text file", ".txt"), ("All files", ".*")])
    if file is None or file == '':
        return

    file = open(file, 'r')
    assets = file.readlines()

    # Generic language replacements
    for i in range(len(assets)):
        assets[i] = assets[i].replace(other_lang.DEPOT_MAINTENANCE, lang.DEPOT_MAINTENANCE)
        assets[i] = assets[i].replace(other_lang.DEPOT_OVERNIGHT, lang.DEPOT_OVERNIGHT)

    # Initial day replacement
    for i in range(8):
        assets[8] = assets[8].replace(other_lang.CURRENT_PLUS_WEEK[i], lang.CURRENT_PLUS_WEEK[i])

    try:
        win_iniservices.km_limit = ast.literal_eval(assets[0])
        win_iniservices.next_mname = ast.literal_eval(assets[1])
        win_iniservices.next_m_duration = ast.literal_eval(assets[2])
        win_iniservices.trainid = ast.literal_eval(assets[3])
        win_nodes.nodeslist = ast.literal_eval(assets[4])
        win_nodes.shortenings = ast.literal_eval(assets[5])
        win_nodes.depotnodes = ast.literal_eval(assets[6])
        win_services.services = ast.literal_eval(assets[7])
        win_services.WEEKDAY = assets[8]
        if '\n' in win_services.WEEKDAY:
            win_services.WEEKDAY = win_services.WEEKDAY.replace('\n', '')
        win_iniservices.iniservices = ast.literal_eval(assets[9])
        win_nodes.NODES_ARE_NEW = ast.literal_eval(assets[10])
        win_depottransfers.transfers = ast.literal_eval(assets[11])
        win_sleepers.sleepers = ast.literal_eval(assets[12])
        win_linkers.linkers = ast.literal_eval(assets[13])

        file.close()
        if settings.SAVELOAD_CONFIRMATION:
            messagebox.showinfo(lang.utils_success, lang.utils_configloaded)

    except:
        error = traceback.format_exc()
        messagebox.showerror(lang.utils_errorload, lang.utils_errorloaddesc + str(error))
        file.close()

    return

def load_solution(winmaster):
    CSIDL_PERSONAL = 5  # My Documents
    SHGFP_TYPE_CURRENT = 0  # Get current, not default value
    buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
    here = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

    file = filedialog.askopenfilename(initialdir=here, defaultextension='.FSsolved', filetypes=[("FleetScheduler solution", ".FSsolved"), ("JSON file", ".json"), ("All files", ".*")])
    if file is None or file == '':
        return

    try:
        assets = _load_json_with_lang_replacements(file)

    except:
        error = traceback.format_exc()
        messagebox.showerror(lang.utils_errorsolved, lang.utils_errorsolveddesc + str(error))
        return

    solved = Toplevel(winmaster)
    solved.geometry("1440x810+50+50")
    solved.configure(bg="pink")
    solved.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
    solved.title(lang.utils_solvedtitle)
    solved_icon = PhotoImage(file=relative_to_solved("icon1.png"))
    solved.iconphoto(False, solved_icon)
    solved.lift()

    for i in range(8):
        assets['starting_day'] = assets['starting_day'].replace(other_lang.CURRENT_PLUS_WEEK[i], lang.CURRENT_PLUS_WEEK[i])

    try:
        baselinkers = assets['baselinkers']
    except:
        baselinkers = {}

    results_object = FullCanvas(init_mode='existing_data', parentwindow=solved, basenodes=assets['basenodes'], baseshortenings=assets['shortenings'], baseservices=assets['baseservices'], baselinkers=baselinkers, basetransfers=assets['basetransfers'], basesleepers=assets['basesleepers'], numtrains=assets['numtrains'], starting_day=assets['starting_day'], trainid=assets['trainid'], km_limit=assets['km_limit'], depot=assets['depot'], maintenance_duration=assets['maintenance_duration'], maintenance_name=assets['maintenance_name'], s_collection=assets['services'], m_collection=assets['maintenances'], t_collection=assets['transfers'])

    solved.mainloop() # TODO por qué necesita un mainloop si es una TopLevel?

def calculate(winmaster, intv): # TODO create a flag that prevents this button from working in case the user has to restart the application to apply setting changes
    if window_blocker.IS_OPEN:
        messagebox.showinfo(lang.generic_windowopen, lang.generic_pleaseclose)
        return

    try:
        numtrains = len(win_iniservices.trainid)
        trainids = {'train' + str(i+1):win_iniservices.trainid[i] for i in range(numtrains)}
    except:
        return messagebox.showerror(lang.utils_faterr, lang.utils_error1 + traceback.format_exc())

    if '??' in win_iniservices.next_mname or '??' in win_iniservices.next_m_duration:
        return messagebox.showerror(lang.utils_errfound, lang.utils_error2)

    try:
        days_to_solve = int(intv.get())
    except:
        return messagebox.showerror(lang.utils_errfound, lang.utils_error3)

    if days_to_solve < 1 or days_to_solve > 7:
        return messagebox.showerror(lang.utils_errfound, lang.utils_error4)

    try:
        utils, error = builder.build_matrices(daystosolve=days_to_solve, realservices=win_services.services, iniservices=deepcopy(win_iniservices.iniservices), depotnodes=win_nodes.depotnodes, numtrains=numtrains, weekday=win_services.WEEKDAY, next_m_duration=win_iniservices.next_m_duration, transfers=win_depottransfers.transfers, reallinkers=win_linkers.linkers, km_limit=win_iniservices.km_limit)
        if utils is None:
            return messagebox.showerror(error['title'], error['content'])

    except:
        return messagebox.showerror(lang.utils_faterr, lang.utils_error5 + traceback.format_exc())

    optimiser_handler.log_and_solve(winmaster, numtrains, trainids, win_nodes.nodeslist, win_nodes.shortenings, win_services.services, win_iniservices.iniservices, win_iniservices.next_m_duration, win_iniservices.next_mname, win_iniservices.km_limit, win_nodes.depotnodes, win_linkers.linkers, win_depottransfers.transfers, win_sleepers.sleepers, *utils)

def multicuts_calculate(winmaster): # TODO create a flag that prevents this button from working in case the user has to restart the application to apply setting changes
    if window_blocker.IS_OPEN:
        messagebox.showinfo(lang.generic_windowopen, lang.generic_pleaseclose)
        return
    
    try:
        numtrains = len(win_iniservices.trainid)
        trainids = {'train' + str(i+1):win_iniservices.trainid[i] for i in range(numtrains)}
    except:
        return messagebox.showerror(lang.utils_faterr, lang.utils_error1 + traceback.format_exc())

    if '??' in win_iniservices.next_mname or '??' in win_iniservices.next_m_duration:
        return messagebox.showerror(lang.utils_errfound, lang.utils_error2)

    i = 0
    for key in win_iniservices.iniservices:
        if win_iniservices.iniservices[key]['forced'] != '':
            if win_iniservices.iniservices[key]['forced'] not in win_services.services:
                return messagebox.showerror(lang.utils_errfound, 'Train ' + win_iniservices.trainid[i] + lang.utils_errorforced + win_iniservices.iniservices[key]['forced'] + lang.utils_notexists)
                

        if win_iniservices.iniservices[key]['bans'][0] != '':
            for banned in win_iniservices.iniservices[key]['bans']:
                if banned not in win_services.services:
                    return messagebox.showerror(lang.utils_errfound, 'Train ' + win_iniservices.trainid[i] + lang.utils_errorbanned + banned + lang.utils_notexists)

        i += 1

    optimiser_handler.autocut_log_and_solve(winmaster, numtrains, trainids, win_nodes.nodeslist, win_nodes.shortenings, win_services.WEEKDAY, win_iniservices.iniservices, win_services.services, win_iniservices.next_m_duration, win_iniservices.next_mname, win_iniservices.km_limit, win_nodes.depotnodes, win_depottransfers.transfers, win_sleepers.sleepers, win_linkers.linkers)

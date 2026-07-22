'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        settings_manager.py

 Author:      Diego Pérez

 Created:     15/05/2024
 Copyright:   (c) perez 2024
-------------------------------------------------------------------------------
'''
import sys
# TODO leer JSON y coger de ahí los valores para las variables de abajo, en lugar de introducirlos a mano
# TODO hacer la pantalla que le corresponde

from tkinter import Toplevel, Button, Label, Entry, messagebox, PhotoImage, Frame, Checkbutton, BooleanVar, OptionMenu, StringVar
from tkwidgets import ImagedOptionMenu, ColorEntry, ScrollableFrame

import json
import traceback
import settings

from pathlib import Path
from help_manager import open_help
import startmenu_blocker as window_blocker

settingspath = Path(__file__).parent / Path(r".\settings")
def relative_to_settings(path: str) -> Path:
    return settingspath / Path(path)

def import_from_JSON():
    file = open(relative_to_settings('settings.json'), 'r')
    try:
        assets = json.load(file)
        file.close()

        settings.LANGUAGE = assets['LANGUAGE']
        # OPTIMISER = assets['OPTIMISER']
        settings.MAINTENANCE_COLOR = assets['MAINTENANCE_COLOR']
        settings.EXTRA_ROWS = assets['EXTRA_ROWS']
        settings.MDURATION_TO_EXCEL = assets['MDURATION_TO_EXCEL']
        settings.SAVELOAD_CONFIRMATION = assets['SAVELOAD_CONFIRMATION']
        settings.HEURISTIC_STEPS = assets['HEURISTIC_STEPS']
        settings.HEURISTIC_ITERS_PER_STEP = assets['HEURISTIC_ITERS_PER_STEP']
        settings.HEURISTIC_SOLVE_ABOVE_ALL = assets['HEURISTIC_SOLVE_ABOVE_ALL']
        # GUROBI_MIPFOCUS = assets['GUROBI_MIPFOCUS']
        # GUROBI_PRESOLVE = assets['GUROBI_PRESOLVE']
        # GUROBI_METHOD = assets['GUROBI_METHOD']
        settings.GAP_MINUTES = assets['GAP_MINUTES']
        settings.GAP_HOUR = settings.GAP_MINUTES / 60
        settings.AVOIDANCE_MARGIN = assets['AVOIDANCE_MARGIN']
        settings.CRITICAL_MARGIN = assets['CRITICAL_MARGIN']
        settings.DEFAULT_INTERVENTION = assets['DEFAULT_INTERVENTION']
        settings.DEFAULT_INTERVENTION_KM = assets['DEFAULT_INTERVENTION_KM']
        settings.DEFAULT_INTERVENTION_TIME = assets['DEFAULT_INTERVENTION_TIME']
        settings.HEURISTIC_DAYS_PER_CUT = assets['HEURISTIC_DAYS_PER_CUT']
        settings.HEURISTIC_NUMBER_OF_CUTS = assets['HEURISTIC_NUMBER_OF_CUTS']
        settings.TOLERANCE_TO_LINK_STEP_AND_MAINT = assets['TOLERANCE_TO_LINK_STEP_AND_MAINT']
        settings.COLOUR_PALETTE = assets['COLOUR_PALETTE']
        settings.DISP_COLOUR_PALETTE = assets['COLOUR_PALETTE']

    except:
        error = traceback.format_exc()
        messagebox.showerror('Error when looking for settings file', 'An error occurred when looking for settings file. Did you delete or modify it?\n' + str(error))
        file.close()
        sys.exit()

def settings_window(winmaster):
    if window_blocker.IS_OPEN:
        messagebox.showinfo("A window is already open", "Please, close the existing window before opening another one.")
        return

    if settings.LANGUAGE == 'English':
        import language.EN as lang
        if settings.COLOUR_PALETTE == 'Dark':
            import colour.night_palette as colour
            settings_assets = Path(__file__).parent / Path(r".\assets\EN\night\settings")
            edition_assets = Path(__file__).parent / Path(r".\assets\EN\night\edition")

        elif settings.COLOUR_PALETTE == 'Light':
            import colour.day_palette as colour
            settings_assets = Path(__file__).parent / Path(r".\assets\EN\day\settings")
            edition_assets = Path(__file__).parent / Path(r".\assets\EN\day\edition")

        else: # COLOUR_PALETTE == 'Blue':
            import colour.blue_palette as colour
            settings_assets = Path(__file__).parent / Path(r".\assets\EN\blue\settings")
            edition_assets = Path(__file__).parent / Path(r".\assets\EN\blue\edition")

    elif settings.LANGUAGE == 'Castellano':
        import language.ES as lang
        if settings.COLOUR_PALETTE == 'Dark':
            import colour.night_palette as colour
            settings_assets = Path(__file__).parent / Path(r".\assets\ES\night\settings")
            edition_assets = Path(__file__).parent / Path(r".\assets\ES\night\edition")

        elif settings.COLOUR_PALETTE == 'Light':
            import colour.day_palette as colour
            settings_assets = Path(__file__).parent / Path(r".\assets\ES\day\settings")
            edition_assets = Path(__file__).parent / Path(r".\assets\ES\day\edition")

        else:  # COLOUR_PALETTE == 'Blue':
            import colour.blue_palette as colour
            settings_assets = Path(__file__).parent / Path(r".\assets\ES\blue\settings")
            edition_assets = Path(__file__).parent / Path(r".\assets\ES\blue\edition")

    def relative_to_settings_assets(path: str) -> Path:
        return settings_assets / Path(path)

    def relative_to_edition(path: str) -> Path:
        return edition_assets / Path(path)

    win = Toplevel(winmaster)
    win.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
    win.bind("<Destroy>", lambda e: window_blocker.window_destruction_protocol())
    window_blocker.IS_OPEN = True
    win.geometry('900x900+0+0')
    win.minsize(width=900, height=450)
    win.configure(bg=colour.WINDOW_BACKGROUNDS)
    win.title('Settings')
    win_icon = PhotoImage(file=relative_to_settings_assets("icon2.png"))
    win.iconphoto(False, win_icon)

    def export_to_JSON():
        changed = False

        # Collect & Compare
        language = language_chooser.get()
        if language != settings.LANGUAGE:
            changed = True

        chosen_colour = colour_var.get()
        if chosen_colour != settings.COLOUR_PALETTE:
            changed = True

        display_colour = display_var.get()
        if display_colour != settings.DISP_COLOUR_PALETTE:
            changed = True

        # optimiser = optimiser_chooser.get()
        # if optimiser != OPTIMISER:
        #     changed = True

        mcolor = maint_color.get()
        if mcolor != settings.MAINTENANCE_COLOR:
            changed = True

        erows = int(extra_rows.get())
        if erows != settings.EXTRA_ROWS:
            changed = True

        mdur = maint_dur_bool.get()
        if mdur != settings.MDURATION_TO_EXCEL:
            changed = True

        saveload_conf = saveload_confirmation_bool.get()
        if saveload_conf != settings.SAVELOAD_CONFIRMATION:
            changed = True

        hsteps = int(h_steps.get())
        if hsteps != settings.HEURISTIC_STEPS:
            changed = True

        hiters = int(h_iters_per_step.get())
        if hiters != settings.HEURISTIC_ITERS_PER_STEP:
            changed = True

        hinfinite = h_infinite_bool.get()
        if hinfinite != settings.HEURISTIC_SOLVE_ABOVE_ALL:
            changed = True

        # gmf = int(g_mipfocus.get())
        # if gmf != GUROBI_MIPFOCUS:
        #     changed = True

        # gp = int(g_presolve.get())
        # if gp != GUROBI_PRESOLVE:
        #     changed = True

        # gm = int(g_method.get())
        # if gm != GUROBI_METHOD:
        #     changed = True

        gap = int(timegap.get())
        if gap != settings.GAP_MINUTES:
            changed = True

        av_margin = int(h_avoidance_margin.get())
        if av_margin != settings.AVOIDANCE_MARGIN:
            changed = True

        cr_margin = int(h_critical_margin.get())
        if cr_margin != settings.CRITICAL_MARGIN:
            changed = True

        var_def_int_name = def_int_name.get()
        if var_def_int_name != settings.DEFAULT_INTERVENTION:
            changed = True

        var_def_int_km = int(def_int_km.get())
        if var_def_int_km != settings.DEFAULT_INTERVENTION_KM:
            changed = True

        var_def_int_dur = float(def_int_dur.get())
        if var_def_int_dur != settings.DEFAULT_INTERVENTION_TIME:
            changed = True

        var_days_per_cut = int(days_per_cut.get())
        if var_days_per_cut != settings.HEURISTIC_DAYS_PER_CUT:
            changed = True

        var_number_of_cuts = int(number_of_cuts.get())
        if var_number_of_cuts != settings.HEURISTIC_NUMBER_OF_CUTS:
            changed = True

        if cr_margin < av_margin:
            messagebox.showerror('Compulsory maintenance margin less than optional maintenance margin', 'The compulsory maintenance margin cannot be less than the optional maintenance margin, it needs to at least the same. Please, correct this before saving settings.')
            return

        if changed:
            if erows < 1:
                erows = 1
                messagebox.showinfo('Extra rows must be at least 1', 'The number of extra rows must be at least 1. It has been set to 1.')
            exportable = {
                'LANGUAGE': language,
                # 'OPTIMISER': optimiser,
                'MAINTENANCE_COLOR': mcolor,
                'EXTRA_ROWS': erows,
                'MDURATION_TO_EXCEL': mdur,
                'SAVELOAD_CONFIRMATION': saveload_conf,
                'HEURISTIC_STEPS': hsteps,
                'HEURISTIC_ITERS_PER_STEP': hiters,
                'HEURISTIC_SOLVE_ABOVE_ALL': hinfinite,
                # 'GUROBI_MIPFOCUS': gmf,
                # 'GUROBI_PRESOLVE': gp,
                # 'GUROBI_METHOD': gm,
                'GAP_MINUTES': gap,
                'AVOIDANCE_MARGIN': av_margin,
                'CRITICAL_MARGIN': cr_margin,
                'DEFAULT_INTERVENTION': var_def_int_name,
                'DEFAULT_INTERVENTION_KM': var_def_int_km,
                'DEFAULT_INTERVENTION_TIME': var_def_int_dur,
                'HEURISTIC_DAYS_PER_CUT': var_days_per_cut,
                'HEURISTIC_NUMBER_OF_CUTS': var_number_of_cuts,
                'COLOUR_PALETTE': chosen_colour,
                'DISP_COLOUR_PALETTE': display_colour
            }

            file = open(relative_to_settings('settings.json'), 'w')
            json.dump(exportable, file, indent=6) # TODO eso del indent no se que tal queda
            file.close()

            messagebox.showinfo(lang.ss1, lang.ss2)
            win.destroy()

    save_button = Button(win, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS, command=export_to_JSON)
    save_button.image = PhotoImage(file=relative_to_edition('save.png'))
    save_button.configure(image=save_button.image)
    save_button.pack(side='bottom')

    scrollable = ScrollableFrame(win, x_scroll=False, bg=colour.TITLES_BACKGROUND, bd=0, packside='top')

    scrollable.columnconfigure(0, weight=1, minsize=450, uniform='uniform')
    scrollable.columnconfigure(1, weight=1, minsize=450, uniform='uniform')

    # TODO poner encabezados de seccion. tipo "Ajustes generales", "Ajustes de gráficos". Con líneas anchas arriba y abajo pero no a los lados en los rotulos así como un cambio de color se mejoraría el Look and feel q no tengo por no haber imagenes
    Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=0, column=0, columnspan=2, sticky='news')
    Label(scrollable, bd=2, text=lang.ss3, font=('futura', 26), justify='center', relief='flat', highlightthickness=0, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).grid(row=1, column=0, columnspan=2, ipady=25, sticky='news')
    scrollable.rowconfigure(1, weight=1, minsize=60, uniform='uniform')
    Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=2, column=0, columnspan=2, sticky='news')

    Label(scrollable, bd=2, text=lang.ss4, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=3, column=0, padx=20, pady=10, sticky='news')
    language_chooser = ImagedOptionMenu(scrollable, settings.LANGUAGE, {"English":PhotoImage(file=relative_to_settings_assets('EN.png')), "Castellano": PhotoImage(file=relative_to_settings_assets('ES.png'))})
    language_chooser.grid(row=3, column=1, padx=30, pady=10, sticky='ew')
    language_chooser.configure(width=120, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT, activebackground=colour.FRAME_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, font=('futura', 13))
    language_chooser['menu'].configure(activebackground=colour.FRAME_BACKGROUND, activeforeground=colour.INPUT_FOREGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
    scrollable.rowconfigure(3, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss5, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=0, padx=20, pady=10, sticky='news')
    colour_var = StringVar(scrollable, value=settings.COLOUR_PALETTE)
    colour_chooser = OptionMenu(scrollable, colour_var, *['Light', 'Dark', 'Blue'])
    colour_chooser.grid(row=4, column=1, padx=30, pady=10, sticky='ew')
    colour_chooser.configure(width=120, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT, activebackground=colour.FRAME_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, font=('futura', 13))
    colour_chooser['menu'].configure(activebackground=colour.FRAME_BACKGROUND, activeforeground=colour.INPUT_FOREGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
    scrollable.rowconfigure(4, weight=1, minsize=60, uniform='uniform')

    # Label(scrollable, bd=2, text='Optimiser', font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=0, padx=20, pady=10, sticky='news')
    # optimiser_chooser = ImagedOptionMenu(scrollable, OPTIMISER, {"GUROBI":PhotoImage(file=relative_to_settings_assets('gurobi.png')), "Heuristic": PhotoImage(file=relative_to_settings_assets('heuristic.png'))})
    # optimiser_chooser.grid(row=4, column=1, padx=30, pady=10, sticky='ew')
    # optimiser_chooser.configure(width=120, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT, activebackground=colour.FRAME_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, font=('futura', 13))
    # optimiser_chooser['menu'].configure(activebackground=colour.FRAME_BACKGROUND, activeforeground=colour.INPUT_FOREGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)

    Label(scrollable, bd=2, text=lang.ss6, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=5, column=0, padx=20, pady=10, sticky='news')
    saveload_confirmation_bool = BooleanVar(scrollable, value=settings.SAVELOAD_CONFIRMATION)
    auxlabel2 = Label(scrollable, bg=colour.TITLES_BACKGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    auxlabel2.grid(row=5, column=1, padx=30, ipadx=10, pady=10, sticky='ew')
    saveload_confirmation_button = Checkbutton(auxlabel2, text=lang.ss19, variable=saveload_confirmation_bool, onvalue=True, offvalue=False, font=('futura', 13), bd=0, selectcolor=colour.INPUT_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
    saveload_confirmation_button.pack(fill='both', expand=True)
    scrollable.rowconfigure(5, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss7, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=6, column=0, padx=20, pady=10, sticky='news')
    timegap = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    timegap.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    timegap.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    timegap.insert(0, settings.GAP_MINUTES)
    timegap.grid(row=6, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(6, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss8, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=7, column=0, padx=20, pady=10, sticky='news')
    def_int_name = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    def_int_name.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    def_int_name.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    def_int_name.insert(0, settings.DEFAULT_INTERVENTION)
    def_int_name.grid(row=7, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(7, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss9, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=8, column=0, padx=20, pady=10, sticky='news')
    def_int_km = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    def_int_km.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    def_int_km.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    def_int_km.insert(0, settings.DEFAULT_INTERVENTION_KM)
    def_int_km.grid(row=8, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(8, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss10, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=9, column=0, padx=20, pady=10, sticky='news')
    def_int_dur = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    def_int_dur.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    def_int_dur.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    def_int_dur.insert(0, settings.DEFAULT_INTERVENTION_TIME)
    def_int_dur.grid(row=9, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(9, weight=1, minsize=60, uniform='uniform')

    Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=10, column=0, columnspan=2, sticky='news')
    Label(scrollable, bd=2, text=lang.ss11, font=('futura', 26), justify='center', relief='flat', highlightthickness=0, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).grid(row=11, column=0, columnspan=2, ipady=25, sticky='news')
    scrollable.rowconfigure(11, weight=1, minsize=60, uniform='uniform')
    Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=12, column=0, columnspan=2, sticky='news')

    Label(scrollable, bd=2, text=lang.ss12, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=13, column=0, padx=20, pady=10, sticky='news')
    display_var = StringVar(scrollable, value=settings.DISP_COLOUR_PALETTE)
    display_chooser = OptionMenu(scrollable, display_var, *['Light', 'Dark'])
    display_chooser.grid(row=13, column=1, padx=30, pady=10, sticky='ew')
    display_chooser.configure(width=120, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT, activebackground=colour.FRAME_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, font=('futura', 13))
    display_chooser['menu'].configure(activebackground=colour.FRAME_BACKGROUND, activeforeground=colour.INPUT_FOREGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
    scrollable.rowconfigure(13, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss13, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=14, column=0, padx=20, pady=10, sticky='news')
    maint_color = ColorEntry(scrollable, base_color=settings.MAINTENANCE_COLOR, fg=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT, font=('futura', 13))
    maint_color.grid(row=14, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(14, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss14, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=15, column=0, padx=20, pady=10, sticky='news')
    extra_rows = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    extra_rows.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    extra_rows.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    extra_rows.insert(0, settings.EXTRA_ROWS)
    extra_rows.grid(row=15, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(15, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss15, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=16, column=0, padx=20, pady=10, sticky='news')
    maint_dur_bool = BooleanVar(scrollable, value=settings.MDURATION_TO_EXCEL)
    auxlabel = Label(scrollable, bg=colour.TITLES_BACKGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    auxlabel.grid(row=16, column=1, padx=30, ipadx=10, pady=10, sticky='ew')
    maint_dur = Checkbutton(auxlabel, text=lang.ss18, variable=maint_dur_bool, onvalue=True, offvalue=False, font=('futura', 13), bd=0, selectcolor=colour.INPUT_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
    maint_dur.pack(fill='both', expand=True)
    scrollable.rowconfigure(16, weight=1, minsize=60, uniform='uniform')

    Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=17, column=0, columnspan=2, sticky='news')
    Label(scrollable, bd=2, text=lang.ss16, font=('futura', 26), justify='center', relief='flat', highlightthickness=0, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).grid(row=18, column=0, columnspan=2, ipady=25, sticky='news')
    scrollable.rowconfigure(18, weight=1, minsize=60, uniform='uniform')
    Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=19, column=0, columnspan=2, sticky='news')

    Label(scrollable, bd=2, text=lang.ss17, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=20, column=0, padx=20, pady=10, sticky='news')
    h_steps = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    h_steps.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    h_steps.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    h_steps.insert(0, settings.HEURISTIC_STEPS)
    h_steps.grid(row=20, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(20, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss20, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=21, column=0, padx=20, pady=10, sticky='news')
    h_iters_per_step = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    h_iters_per_step.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    h_iters_per_step.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    h_iters_per_step.insert(0, settings.HEURISTIC_ITERS_PER_STEP)
    h_iters_per_step.grid(row=21, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(21, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss21, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=22, column=0, padx=20, pady=10, sticky='news')
    h_infinite_bool = BooleanVar(scrollable, value=settings.HEURISTIC_SOLVE_ABOVE_ALL)
    auxlabel3 = Label(scrollable, bg=colour.TITLES_BACKGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    auxlabel3.grid(row=22, column=1, padx=30, ipadx=10, pady=10, sticky='ew')
    hinfinite_button = Checkbutton(auxlabel3, text=lang.ss22, variable=h_infinite_bool, onvalue=True, offvalue=False, font=('futura', 13), bd=0, selectcolor=colour.INPUT_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
    hinfinite_button.pack(fill='both', expand=True)
    scrollable.rowconfigure(22, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss23, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=23, column=0, padx=20, pady=10, sticky='news')
    h_avoidance_margin = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    h_avoidance_margin.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    h_avoidance_margin.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    h_avoidance_margin.insert(0, settings.AVOIDANCE_MARGIN)
    h_avoidance_margin.grid(row=23, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(23, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss24, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=24, column=0, padx=20, pady=10, sticky='news')
    h_critical_margin = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    h_critical_margin.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    h_critical_margin.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    h_critical_margin.insert(0, settings.CRITICAL_MARGIN)
    h_critical_margin.grid(row=24, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(24, weight=1, minsize=60, uniform='uniform')


    Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=25, column=0, columnspan=2, sticky='news')
    Label(scrollable, bd=2, text=lang.ss26, font=('futura', 26), justify='center', relief='flat', highlightthickness=0, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).grid(row=26, column=0, columnspan=2, ipady=25, sticky='news')
    scrollable.rowconfigure(27, weight=1, minsize=60, uniform='uniform')
    Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=27, column=0, columnspan=2, sticky='news')

    Label(scrollable, bd=2, text=lang.ss27, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=28, column=0, padx=20, pady=10, sticky='news')
    number_of_cuts = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    number_of_cuts.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    number_of_cuts.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    number_of_cuts.insert(0, settings.HEURISTIC_NUMBER_OF_CUTS)
    number_of_cuts.grid(row=28, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(28, weight=1, minsize=60, uniform='uniform')

    Label(scrollable, bd=2, text=lang.ss28, font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=29, column=0, padx=20, pady=10, sticky='news')
    days_per_cut = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    days_per_cut.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    days_per_cut.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    days_per_cut.insert(0, settings.HEURISTIC_DAYS_PER_CUT)
    days_per_cut.grid(row=29, column=1, padx=30, pady=10, sticky='ew')
    scrollable.rowconfigure(29, weight=1, minsize=60, uniform='uniform')

    # Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=21, column=0, columnspan=2, sticky='news')
    # Label(scrollable, bd=2, text='Gurobi Optimiser Parameters (Advanced)', font=('futura', 26), justify='center', relief='flat', highlightthickness=0, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).grid(row=22, column=0, columnspan=2, ipady=25, sticky='news')
    # Frame(scrollable, height=4, bg='#000000', highlightthickness=0, bd=0).grid(row=23, column=0, columnspan=2, sticky='news')
    #
    # Label(scrollable, bd=2, text='MIP strategy (1 - 3)', font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=24, column=0, padx=20, pady=10, sticky='news')
    # g_mipfocus = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    # g_mipfocus.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    # g_mipfocus.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    # g_mipfocus.insert(0, GUROBI_MIPFOCUS)
    # g_mipfocus.grid(row=24, column=1, padx=30, pady=10, sticky='ew')
    #
    # Label(scrollable, bd=2, text='Presolve method (0 - 2)', font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=25, column=0, padx=20, pady=10, sticky='news')
    # g_presolve = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    # g_presolve.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    # g_presolve.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    # g_presolve.insert(0, GUROBI_PRESOLVE)
    # g_presolve.grid(row=25, column=1, padx=30, pady=10, sticky='ew')
    #
    # Label(scrollable, bd=2, text='Root relaxation method (1 - 3)', font=('futura', 13), justify='left', relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=26, column=0, padx=20, pady=10, sticky='news')
    # g_method = Entry(scrollable, font=('futura', 13), bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, bd=0, highlightcolor=colour.HIGHLIGHT, highlightthickness=4, highlightbackground=colour.HIGHLIGHT)
    # g_method.bind('<FocusIn>', lambda event: event.widget.configure(bg=colour.FRAME_BACKGROUND))
    # g_method.bind('<FocusOut>', lambda event: event.widget.configure(bg=colour.INPUT_BACKGROUND))
    # g_method.insert(0, GUROBI_METHOD)
    # g_method.grid(row=26, column=1, padx=30, pady=10, sticky='ew')

    scrollable.updateScrollRegion()
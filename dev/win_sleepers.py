'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        win_depottransfers.py

 Author:      Diego Pérez

 Created:     23/12/2024
 Copyright:   (c) perez 2024
-------------------------------------------------------------------------------
'''
import traceback
from tkinter import Toplevel, Entry, Button, Frame, Label, PhotoImage, messagebox
import ast
from copy import deepcopy
import datetime

import win_nodes as nodes
from tkwidgets import ScrollableFrame, ColorEntry, AutocompleteCombobox

import settings

# Now, import language and assets
from pathlib import Path
if settings.LANGUAGE == 'English':
    import language.EN as lang
    if settings.COLOUR_PALETTE == 'Dark':
        import colour.night_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\night\edition")
    elif settings.COLOUR_PALETTE == 'Light':
        import colour.day_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\day\edition")
    elif settings.COLOUR_PALETTE == 'Blue':
        import colour.blue_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\blue\edition")

elif settings.LANGUAGE == 'Castellano':
    import language.ES as lang
    if settings.COLOUR_PALETTE == 'Dark':
        import colour.night_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\night\edition")
    elif settings.COLOUR_PALETTE == 'Light':
        import colour.day_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\day\edition")
    elif settings.COLOUR_PALETTE == 'Blue':
        import colour.blue_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\blue\edition")

from help_manager import open_help
import startmenu_blocker as window_blocker

def relative_to_services(path: str) -> Path:
    return OUTPUT_PATH / Path(path)

sleepers = {}

class transfers_ScrollableFrame(ScrollableFrame):
    def addNewLabel(self, depot):
        self.entries[depot] = []

        # Depot
        depots = [depot + ' < ' + other if other != depot else depot for other in self.depots]
        self.entries[depot].append(AutocompleteCombobox(master=self, completevalues=depots))
        self.entries[depot][0].grid(row=self.i, column=0, padx=10, sticky='ew')
        self.entries[depot][0].bind("<<ComboboxSelected>>", lambda e: self.on_value_change(depot))
        # self.entries[depot].append(Label(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.TITLES_FOREGROUND))
        # self.entries[depot][0].grid(row=self.i, column=0, padx=10, sticky='ew')

        # To id
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][1].grid(row=self.i, column=1, padx=10, sticky='ew')

        # From id
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][2].grid(row=self.i, column=2, padx=10, sticky='ew')

        # Duration
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][3].grid(row=self.i, column=3, padx=10, sticky='ew')

        # Kilometers
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][4].grid(row=self.i, column=4, padx=10, sticky='ew')

        # Night block time
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][5].grid(row=self.i, column=5, padx=10, sticky='ew')

        # Early morning block time
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][6].grid(row=self.i, column=6, padx=10, sticky='ew')

        # Week capacity
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][7].grid(row=self.i, column=7, sticky='ew')

        self.entries[depot].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][8].grid(row=self.i, column=8, sticky='ew')

        self.entries[depot].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][9].grid(row=self.i, column=9, sticky='ew')

        self.entries[depot].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][10].grid(row=self.i, column=10, sticky='ew')

        self.entries[depot].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][11].grid(row=self.i, column=11, sticky='ew')

        self.entries[depot].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][12].grid(row=self.i, column=12, sticky='ew')

        self.entries[depot].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[depot][13].grid(row=self.i, column=13, sticky='ew')

        # Color
        self.entries[depot].append(ColorEntry(self, base_color=colour.INPUT_BACKGROUND, bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716"))
        self.entries[depot][14].grid(row=self.i, column=14, padx=10, sticky='nsew')

        self.i += 1

        # Adding a spacer
        self.falselabels.append(Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1))
        self.falselabels[-1].grid(row=self.i, column=0, sticky='w')

        self.i += 1

    def on_value_change(self, depot):
        current_value = self.entries[depot][0].get()

        if ' < ' in current_value:
            for el in self.entries[depot]:
                if el is self.entries[depot][0] or el is self.entries[depot][1] or el is self.entries[depot][2] or el is self.entries[depot][3] or el is self.entries[depot][4] or el is self.entries[depot][5] or el is self.entries[depot][6]:
                    continue # These remain editable
                el.configure(state='disabled')

        else:
            for el in self.entries[depot]:
                el.configure(state='normal')


    def __init__(self, winmaster, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.i = 2
        self.entries = {}
        self.falselabels = []
        self.depots = [depot for depot in nodes.depotnodes if nodes.depotnodes[depot]]

        # Define headers
        Label(self, bd=2, text=lang.gui_depot, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='news')
        self.columnconfigure(0, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_to_id, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='news')
        self.columnconfigure(1, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_from_id, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='news')
        self.columnconfigure(2, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='news')
        self.columnconfigure(3, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_kilometers, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=4, ipady=10, sticky='news')
        self.columnconfigure(4, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_nightlimit, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=5, ipady=10, sticky='news')
        self.columnconfigure(5, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_morning_limit, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=6, ipady=10, sticky='news')
        self.columnconfigure(6, weight=16, minsize=130)

        Label(self, bd=2, text=lang.MON, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=7, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.TUE, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=8, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.WED, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=9, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.THU, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=10, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.FRI, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=11, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.SAT, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=12, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.SUN, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=13, ipady=10, sticky='news')

        self.columnconfigure(7, weight=1, uniform='weekdays')
        self.columnconfigure(8, weight=1, uniform='weekdays')
        self.columnconfigure(9, weight=1, uniform='weekdays')
        self.columnconfigure(10, weight=1, uniform='weekdays')
        self.columnconfigure(11, weight=1, uniform='weekdays')
        self.columnconfigure(12, weight=1, uniform='weekdays')
        self.columnconfigure(13, weight=1, uniform='weekdays')

        Label(self, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=14, ipady=10, sticky='news')
        self.columnconfigure(14, weight=16, minsize=130)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, sticky='w')

        for depot in nodes.depotnodes:
            if nodes.depotnodes[depot]:
                self.addNewLabel(depot)
                if depot in sleepers:
                    self.entries[depot][0].set(sleepers[depot]['location'])
                    # try:
                    # To id
                    self.entries[depot][1].insert(0, sleepers[depot]['id_to'])

                    # To id
                    self.entries[depot][2].insert(0, sleepers[depot]['id_from'])

                    # Duration
                    self.entries[depot][3].insert(0, sleepers[depot]['duration'])

                    # Kilometers
                    self.entries[depot][4].insert(0, sleepers[depot]['kilometers'])

                    # Night block time
                    self.entries[depot][5].insert(0, sleepers[depot]['nightblock'])

                    # Early morning block time
                    self.entries[depot][6].insert(0, sleepers[depot]['morningblock'])

                    # Week data
                    self.entries[depot][7].insert(0, sleepers[depot]['week'][0])
                    self.entries[depot][8].insert(0, sleepers[depot]['week'][1])
                    self.entries[depot][9].insert(0, sleepers[depot]['week'][2])
                    self.entries[depot][10].insert(0, sleepers[depot]['week'][3])
                    self.entries[depot][11].insert(0, sleepers[depot]['week'][4])
                    self.entries[depot][12].insert(0, sleepers[depot]['week'][5])
                    self.entries[depot][13].insert(0, sleepers[depot]['week'][6])

                    # Color
                    self.entries[depot][14].set(sleepers[depot]['color'])

                else:
                    self.entries[depot][0].set(depot)

                # except:
                #     print('Some kind of error (that may be ignored) occurred when trying to load sleeper data for depot ' + depot)
                #     print(traceback.format_exc())

        self.update()

    def define_transfers(self):
        global sleepers
        forward_rules = {}
        new_sleepers = {}
        for depot in self.depots:
            depot_ = self.entries[depot][0].get() # String

            if ' < ' in depot_:
                forwards = True
                forward_rules[depot] = depot_.split(' < ')[1]
            else:
                forwards = False
                forward_rules[depot] = depot

            new_sleepers[depot] = {'location': depot_}
            try:
                to_key = self.entries[depot][1].get()  # String
                from_key = self.entries[depot][2].get()  # String

            except:
                messagebox.showerror(lang.error_saving, lang.sleeperror1 + depot + '.' + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                if not forwards:
                    new_sleepers[depot]['duration'] = ast.literal_eval(self.entries[depot][3].get())
                else:
                    new_sleepers[depot]['duration'] = self.entries[depot][3].get()
            except:
                messagebox.showerror(lang.error_saving, lang.sleeperror2 + depot + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                if not forwards:
                    new_sleepers[depot]['kilometers'] = ast.literal_eval(self.entries[depot][4].get())
                else:
                    new_sleepers[depot]['kilometers'] = self.entries[depot][4].get()
            except:
                messagebox.showerror(lang.error_saving, lang.sleeperror3 + depot + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                if not forwards:
                    new_sleepers[depot]['week'] = [ast.literal_eval(item.get()) if item.get() != '' else item.get() for item in self.entries[depot][7:14]]
                else:
                    new_sleepers[depot]['week'] = [item.get() for item in self.entries[depot][7:14]]
            except:
                messagebox.showerror(lang.error_saving, lang.sleeperror4 + depot + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_sleepers[depot]['id_to'] = to_key
                new_sleepers[depot]['id_from'] = from_key
                new_sleepers[depot]['color'] = self.entries[depot][14].get()
                nodes.NODES_ARE_NEW[depot] = False
            except:
                messagebox.showerror(lang.error_saving, lang.sleeperror5 + depot + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            # Try to catch a typical error
            try:
                new_sleepers[depot]['nightblock'] = self.entries[depot][5].get()
                new_sleepers[depot]['morningblock'] = self.entries[depot][6].get()
                datetime.datetime.strptime(new_sleepers[depot]['nightblock'], '%H:%M').time()  # datetime.time
                datetime.datetime.strptime(new_sleepers[depot]['morningblock'], '%H:%M').time()  # datetime.time
            except:
                messagebox.showerror(lang.error_saving, lang.sleeperror6 + depot + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

        # Check forward rules consistency
        for depot in forward_rules:
            if depot != forward_rules[depot]:
                target_depot = forward_rules[depot]
                if forward_rules[target_depot] != target_depot:
                    messagebox.showerror(lang.error_saving, 'Depot ' + depot + lang.sleeperror7 + forward_rules[depot] + lang.sleeperror8 + traceback.format_exc())
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return

        sleepers = deepcopy(new_sleepers)
        self.root.destroy()

def sleeperswin(winmaster):
    if len(nodes.nodeslist) == 0: # Undefined nodes, show error
        messagebox.showerror(lang.generic_nonodes, lang.generic_createnodes)

    else: # Defined nodes
        if window_blocker.IS_OPEN:
            messagebox.showinfo(lang.generic_windowopen, lang.generic_pleaseclose)
            return

        win = Toplevel(winmaster)
        win.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        win.bind("<Destroy>", lambda e: window_blocker.window_destruction_protocol())
        window_blocker.IS_OPEN = True
        win.configure(background=colour.WINDOW_BACKGROUNDS)
        win.geometry('1600x600')
        win.minsize(width=1600, height=100)
        win.title(lang.sleepers_title)
        win_icon = PhotoImage(file=relative_to_services("icon2.png"))
        win.iconphoto(False, win_icon)

        btn = Button(win, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS)
        btn.image = PhotoImage(file=relative_to_services('save.png'))
        btn.configure(image=btn.image)

        btn.pack(anchor='center', padx=20, pady=10)

        # Initialize a Scrollable frame:
        Scrollable = transfers_ScrollableFrame(win, bg=colour.FRAME_BACKGROUND, bd=0, x_scroll=False)

        # Command already defined, reconfiguring
        btn.configure(command=Scrollable.define_transfers)

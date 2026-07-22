'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        win_services.py

 Author:      perez

 Created:     15/10/2023
 Copyright:   (c) perez 2023
-------------------------------------------------------------------------------
'''
from copy import deepcopy
import traceback
from tkinter import Toplevel, Entry, Button, Frame, Label, PhotoImage, messagebox
from tkinter.ttk import Combobox, Style
import ast
import datetime
from tkwidgets import ScrollableFrame, AutocompleteCombobox, ColorEntry

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

combostyle = Style()
combostyle.theme_use('clam')
combostyle.configure("Custom.TCombobox", foreground=colour.INPUT_FOREGROUND,  # Text color
                     background=colour.AUX_INPUT_BACKGROUND,  # Arrow background
                     fieldbackground=colour.INPUT_BACKGROUND,  # Entry field background
                     arrowcolor=colour.INPUT_FOREGROUND,  # Dropdown arrow color
                     selectbackground=colour.AUX_INPUT_BACKGROUND,  # Background color when an item is selected (in dropdown)
                     selectforeground=colour.INPUT_FOREGROUND,  # Text color when selected
                     bordercolor=colour.HIGHLIGHT,  # Border around the entry field
                     # lightcolor="purple",             # Top-left edge (highlight)
                     # darkcolor="purple",              # Bottom-right edge (shadow)
                     relief="flat"  # Optional: makes edges flat or raised
                     )

def relative_to_services(path: str) -> Path:
    return OUTPUT_PATH / Path(path)

WEEKDAY = 'Current'
services = {}

def _parse_time_or_min(tstr):
    try:
        return datetime.datetime.strptime(tstr, '%H:%M').time()
    except Exception:
        return datetime.time(0, 0, 1)

def _parse_number_or_min(nstr):
    try:
        return float(nstr)
    except Exception:
        return 0

class Service_ScrollableFrame(ScrollableFrame):
    def addNewLabel(self):
        self.entries.append([])

        # Service id
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][0].grid(row=self.i, column=0, padx=10, sticky='ew')

        # From
        self.entries[-1].append(AutocompleteCombobox(master=self, completevalues=self.nodeslist))
        self.entries[-1][1].grid(row=self.i, column=1, padx=10, sticky='ew')

        # To
        self.entries[-1].append(AutocompleteCombobox(master=self, completevalues=self.nodeslist))
        self.entries[-1][2].grid(row=self.i, column=2, padx=10, sticky='ew')

        # Kilometers
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][3].grid(row=self.i, column=3, padx=10)

        # Departure time
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][4].grid(row=self.i, column=4, padx=10)

        # Arrival time
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][5].grid(row=self.i, column=5, padx=(10, 0))

        # Arrival extra day
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][6].grid(row=self.i, column=6, padx=(0, 10))

        # Forced service
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][7].grid(row=self.i, column=7, padx=10)

        # Bans
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][8].grid(row=self.i, column=8, padx=10)

        # Day 1
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][9].grid(row=self.i, column=9, sticky='ew')

        # Day 2
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][10].grid(row=self.i, column=10, sticky='ew')

        # Day 3
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][11].grid(row=self.i, column=11, sticky='ew')

        # Day 4
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][12].grid(row=self.i, column=12, sticky='ew')

        # Day 5
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][13].grid(row=self.i, column=13, sticky='ew')

        # Day 6
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][14].grid(row=self.i, column=14, sticky='ew')

        # Day 7
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][15].grid(row=self.i, column=15, sticky='ew')

        # Color
        self.entries[-1].append(ColorEntry(self, base_color=colour.INPUT_BACKGROUND, bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716"))
        self.entries[-1][16].grid(row=self.i, column=16, padx=10, sticky='ew')

        # Basket
        self.basket.append(Label(self, text='\U0001F5D1', bd=2, highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, relief='flat', bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, width=3))
        self.basket[-1].bind("<Button-1>", self.deleterow)
        self.basket[-1].grid(row=self.i, column=17, padx=10, sticky='ew')

        self.i += 1

        # Adding a spacer
        self.falselabels.append(Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1))
        self.falselabels[-1].grid(row=self.i, column=0, sticky='w')

        self.i += 1

        # Update the scroll region after new widgets are added
        self.updateScrollRegion()

    def deleterow(self, event):
        widget = event.widget
        self.deleter = messagebox.askyesno(lang.generic_deletion, lang.generic_confirmdeletion)
        if self.deleter: # Delete
            index = self.basket.index(widget)
            self.destroy_row(index)

    def destroy_row(self, index):
        for item in self.entries[index]:
            item.grid_forget()
        del self.entries[index]

        self.falselabels[index].grid_forget()
        self.basket[index].grid_forget()

        del self.falselabels[index]
        del self.basket[index]

        self.updateScrollRegion()
        self.root.lift()

    def super_sorter(self, case: int):
        data = [[self.entries[i][j].get() for j in range(len(self.entries[i]))] for i in range(len(self.entries))]
        print(data)
        if case == 0:  # Sort by service id
            data.sort(key=lambda x: x[0])
        elif case == 1:  # Sort by origin
            data.sort(key=lambda x: x[1])
        elif case == 2:  # Sort by destiny
            data.sort(key=lambda x: x[2])
        elif case == 3:  # Sort by kilometers
            data.sort(key=lambda x: _parse_number_or_min(x[3]))
        elif case == 4:  # Sort by departure time
            data.sort(key=lambda x: _parse_time_or_min(x[4]))
        elif case == 5:  # Sort by arrival time
            data.sort(key=lambda x: _parse_time_or_min(x[5]))

        for i in range(len(self.entries)):
            for j in range(len(self.entries[i])):
                if type(self.entries[i][j]) is Entry:
                    self.entries[i][j].delete(0, 'end')
                    self.entries[i][j].insert(0, data[i][j])
                elif type(self.entries[i][j]) is AutocompleteCombobox:
                    self.entries[i][j].set(data[i][j])
                elif type(self.entries[i][j]) is ColorEntry:
                    self.entries[i][j].set(data[i][j])

        self.updateScrollRegion()
        print('¡Panenke', data)
        self.root.lift()

    def __init__(self, winmaster, nodeslist, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.i = 2
        self.entries = []
        self.nodeslist = nodeslist
        self.falselabels = []
        self.basket = []

        # Define headers
        service_label = Label(self, bd=2, text=lang.gui_servid, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        service_label.grid(row=0, column=0, ipady=10, sticky='news')
        service_label.bind("<Button-1>", lambda e: self.super_sorter(0))
        self.columnconfigure(0, weight=16, minsize=130)

        from_label = Label(self, bd=2, text=lang.gui_fromarrow, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        from_label.grid(row=0, column=1, ipady=10, sticky='news')
        from_label.bind("<Button-1>", lambda e: self.super_sorter(1))
        self.columnconfigure(1, weight=16, minsize=130)

        to_label = Label(self, bd=2, text=lang.gui_toarrow, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        to_label.grid(row=0, column=2, ipady=10, sticky='news')
        to_label.bind("<Button-1>", lambda e: self.super_sorter(2))
        self.columnconfigure(2, weight=16, minsize=130)

        km_label = Label(self, bd=2, text=lang.gui_kmarrow, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        km_label.grid(row=0, column=3, ipady=10, sticky='news')
        km_label.bind("<Button-1>", lambda e: self.super_sorter(3))
        self.columnconfigure(3, weight=16, minsize=130)

        departure_label = Label(self, bd=2, text=lang.gui_departurearr, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        departure_label.grid(row=0, column=4, ipady=10, sticky='news')
        departure_label.bind("<Button-1>", lambda e: self.super_sorter(4))
        self.columnconfigure(4, weight=16, minsize=150)

        arrival_label = Label(self, bd=2, text=lang.gui_arrarr, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        arrival_label.grid(row=0, column=5, columnspan=2, ipady=10, sticky='news')
        arrival_label.bind("<Button-1>", lambda e: self.super_sorter(5))
        self.columnconfigure(5, weight=16, minsize=150)
        self.columnconfigure(6, weight=1, uniform='weekdays', minsize=40)

        Label(self, bd=2, text=lang.gui_forced, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=7, ipady=10, sticky='news')
        self.columnconfigure(7, weight=16, minsize=150)

        Label(self, bd=2, text=lang.gui_bans, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=8, ipady=10, sticky='news')
        self.columnconfigure(8, weight=16, minsize=150)

        Label(self, bd=2, text=lang.MON, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=9, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.TUE, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=10, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.WED, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=11, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.THU, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=12, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.FRI, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=13, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.SAT, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=14, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.SUN, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=15, ipady=10, sticky='news')

        self.columnconfigure(9, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(10, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(11, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(12, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(13, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(14, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(15, weight=1, uniform='weekdays', minsize=40)

        Label(self, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=16, ipady=10, sticky='news')
        self.columnconfigure(16, weight=16, minsize=80)

        Label(self, bd=2, text=' ', font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=17, ipady=10, sticky='news')
        self.columnconfigure(17, weight=1)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, sticky='w')

        self.update()

        if len(services) == 0: # Nodes defined, not services; standard window
            self.addNewLabel()

        else: # Nodes and services defined; load data to window
            [self.addNewLabel() for _ in range(len(services))]  # Create a new label for each service
            i=0
            for service in services:
                # Service id
                self.entries[i][0].insert(0, service)
                # From
                self.entries[i][1].set(services[service]['origin'])
                # To
                self.entries[i][2].set(services[service]['destiny'])
                # Kilometers
                self.entries[i][3].insert(0, str(services[service]['kilometers']))
                # Departure time
                self.entries[i][4].insert(0, services[service]['str_departure-time'])
                # Arrival time
                self.entries[i][5].insert(0, services[service]['str_arrival-time'])
                # Arrival extra day
                self.entries[i][6].insert(0, services[service]['arrival_extra_days'])
                # Forced service
                self.entries[i][7].insert(0, str(services[service]['forced']))
                # Bans
                self.entries[i][8].insert(0, str(services[service]['bans']).translate({ord(i): None for i in "[]'"}))
                # Day 1
                self.entries[i][9].insert(0, str(services[service]['week'][0]))
                # Day 2
                self.entries[i][10].insert(0, str(services[service]['week'][1]))
                # Day 3
                self.entries[i][11].insert(0, str(services[service]['week'][2]))
                # Day 4
                self.entries[i][12].insert(0, str(services[service]['week'][3]))
                # Day 5
                self.entries[i][13].insert(0, str(services[service]['week'][4]))
                # Day 6
                self.entries[i][14].insert(0, str(services[service]['week'][5]))
                # Day 7
                self.entries[i][15].insert(0, str(services[service]['week'][6]))
                # Color
                self.entries[i][16].set(services[service]['color'])

                i += 1
                # if not i % 5:
                #     self.update()

            self.update()

    def collect_data(self, weekday_entry):
        global WEEKDAY
        WEEKDAY = weekday_entry.get()
        self.define_services()

    def define_services(self):
        global services
        new_services = {}
        repeated_ids = []

        for row in range(len(self.entries)):
            try:
                key = self.entries[row][0].get()  # String
                new_services[key] = {}
                if ',' in key:
                    messagebox.showerror(lang.error_saving, 'ID ' + key + lang.serverror15)
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return

                if key in repeated_ids:
                    messagebox.showerror(lang.error_saving, 'ID ' + str(key) + lang.serverror1 + str(repeated_ids.index(key) + 1) + ' & ' + str(row + 1) + '.')
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return
                else:
                    repeated_ids.append(key)
            except:
                messagebox.showerror(lang.error_saving, lang.serverror2 + str(row + 1) + '.' + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return


            new_services[key]['origin'] = self.entries[row][1].get()  # String
            if new_services[key]['origin'] not in self.nodeslist:
                messagebox.showerror(lang.error_saving, lang.serverror3 + new_services[key]['origin'] + lang.serverror4 + key + lang.serverror5)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            new_services[key]['destiny'] = self.entries[row][2].get()  # String
            if new_services[key]['destiny'] not in self.nodeslist:
                messagebox.showerror(lang.error_saving, lang.serverror6 + new_services[key]['destiny'] + lang.serverror4 + key + lang.serverror5)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_services[key]['forced'] = self.entries[row][7].get()  # String
                new_services[key]['bans'] = self.entries[row][8].get().replace(", ", ",").replace(" ,", ",").split(",") # List
                new_services[key]['color'] = self.entries[row][16].get()
            except:
                messagebox.showerror(lang.error_saving, lang.serverror7 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_services[key]['kilometers'] = ast.literal_eval(self.entries[row][3].get())  # int/float
            except:
                messagebox.showerror(lang.error_saving, lang.serverror8 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                days = []  # list of ints
                days.append(ast.literal_eval(self.entries[row][9].get())) if self.entries[row][9].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][10].get())) if self.entries[row][10].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][11].get())) if self.entries[row][11].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][12].get())) if self.entries[row][12].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][13].get())) if self.entries[row][13].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][14].get())) if self.entries[row][14].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][15].get())) if self.entries[row][15].get() != '' else days.append('')
                new_services[key]['week'] = deepcopy(days)
            except:
                messagebox.showerror(lang.error_saving, lang.serverror9 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            # Try to catch a typical error
            try:
                new_services[key]['str_departure-time'] = self.entries[row][4].get()  # String
                new_services[key]['str_arrival-time'] = self.entries[row][5].get()  # String
                new_services[key]['arrival_extra_days'] = '' if self.entries[row][6].get() == '' else int(self.entries[row][6].get())
                datetime.datetime.strptime(new_services[key]['str_departure-time'], '%H:%M').time()  # datetime.time
                datetime.datetime.strptime(new_services[key]['str_arrival-time'], '%H:%M').time()  # datetime.time
            except:
                messagebox.showerror(lang.error_saving, lang.serverror10 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

        # Check that stated forced and bans constraints are matching other existing services
        for key in new_services:
            if new_services[key]['forced'] != '':
                if new_services[key]['forced'] not in new_services:
                    messagebox.showerror(lang.error_saving, lang.serverror11 + key + lang.serverror12 + new_services[key]['forced'] + lang.serverror14)
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return

            if new_services[key]['bans'][0] != '':
                for banned in new_services[key]['bans']:
                    if banned not in new_services:
                        messagebox.showerror(lang.error_saving, lang.serverror11 + key + lang.serverror13 + banned + lang.serverror14)
                        self.root.attributes('-topmost', True)
                        self.root.attributes('-topmost', False)
                        return

        services = deepcopy(new_services)
        self.root.destroy()


def serviceswin(winmaster, nodeslist):
    global WEEKDAY
    if len(nodeslist) == 0: # Undefined nodes, show error
        messagebox.showerror(lang.generic_nonodes, lang.generic_createnodes)

    else: # Defined nodes
        if window_blocker.IS_OPEN:
            messagebox.showinfo(lang.generic_windowopen, lang.generic_pleaseclose)
            return

        root = Toplevel(winmaster)
        root.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        root.bind("<Destroy>", lambda e: window_blocker.window_destruction_protocol())
        window_blocker.IS_OPEN = True
        root.configure(background=colour.WINDOW_BACKGROUNDS)
        root.geometry('1600x600')
        root.minsize(width=1600, height=100)
        root.title(lang.services_title)
        root_icon = PhotoImage(file=relative_to_services("icon2.png"))
        root.iconphoto(False, root_icon)

        topframe = Frame(master=root, background=colour.WINDOW_BACKGROUNDS)

        dayframe = Frame(master=topframe, background=colour.WINDOW_BACKGROUNDS)
        lbl = Label(dayframe, bd=2, text=lang.service_starting_day, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND)
        picker = Combobox(dayframe, values=lang.CURRENT_PLUS_WEEK, font=('futura', 13), width=10, style="Custom.TCombobox", state='readonly')
        picker.bind("<<ComboboxSelected>>", lambda e: picker.selection_clear())
        picker.set(WEEKDAY)

        lbl.grid(row=0, column=0, padx=20, pady=10)
        picker.grid(row=0, column=1, padx=20, pady=10)
        dayframe.pack(side='left')

        buttonframe = Frame(master=topframe, background=colour.WINDOW_BACKGROUNDS)
        btn = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS)
        btn.image = PhotoImage(file=relative_to_services('addrow.png'))
        btn.configure(image=btn.image)
        btn2 = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS)
        btn2.image = PhotoImage(file=relative_to_services('save.png'))
        btn2.configure(image=btn2.image)

        btn.grid(row=0, column=0, padx=20, pady=10)
        btn2.grid(row=0, column=1, padx=20, pady=10)
        buttonframe.place(relx=0.5, rely=0.5, anchor='center')

        topframe.pack(side='top', fill='x')

        # Initialize a Scrollable frame:
        Scrollable = Service_ScrollableFrame(root, nodeslist, bg=colour.FRAME_BACKGROUND, bd=0, x_scroll=False)

        # Commands 1 to 3 already defined, reconfiguring
        btn.configure(command=Scrollable.addNewLabel)
        btn2.configure(command=lambda: Scrollable.collect_data(picker))

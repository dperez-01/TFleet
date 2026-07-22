'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        win_linkers.py

 Author:      Diego Pérez

 Created:     12/03/2026
 Copyright:   (c) perez 2026
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


def relative_to_linkers(path: str) -> Path:
    return OUTPUT_PATH / Path(path)

linkers = {}

class Linkers_ScrollableFrame(ScrollableFrame):
    def addNewLabel(self):
        self.entries.append([])

        # Service id
        self.entries[-1].append(Entry(self, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][0].grid(row=self.i, column=0, padx=10, sticky='ew')

        # From
        self.entries[-1].append(AutocompleteCombobox(master=self, completevalues=self.nodeslist))
        self.entries[-1][1].grid(row=self.i, column=1, padx=10, sticky='ew')

        # To
        self.entries[-1].append(AutocompleteCombobox(master=self, completevalues=self.nodeslist))
        self.entries[-1][2].grid(row=self.i, column=2, padx=10, sticky='ew')

        # Kilometers
        self.entries[-1].append(Entry(self, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][3].grid(row=self.i, column=3, padx=10)

        # Duration (min)
        self.entries[-1].append(Entry(self, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][4].grid(row=self.i, column=4, padx=10)

        # Window opening time
        self.entries[-1].append(Entry(self, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][5].grid(row=self.i, column=5, padx=10)

        # Window ending time
        self.entries[-1].append(Entry(self, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][6].grid(row=self.i, column=6, padx=(10, 0))

        # Window ending time extra day
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][7].grid(row=self.i, column=7, padx=(0, 10))

        # Strict links
        self.entries[-1].append(Entry(self, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        # self.entries[-1][8].grid(row=self.i, column=8, padx=10)

        # Avoid linking
        self.entries[-1].append(Entry(self, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        # self.entries[-1][9].grid(row=self.i, column=9, padx=10)

        # Day 1
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][10].grid(row=self.i, column=10, sticky='ew')

        # Day 2
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][11].grid(row=self.i, column=11, sticky='ew')

        # Day 3
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][12].grid(row=self.i, column=12, sticky='ew')

        # Day 4
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][13].grid(row=self.i, column=13, sticky='ew')

        # Day 5
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][14].grid(row=self.i, column=14, sticky='ew')

        # Day 6
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][15].grid(row=self.i, column=15, sticky='ew')

        # Day 7
        self.entries[-1].append(Entry(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][16].grid(row=self.i, column=16, sticky='ew')

        # Color
        self.entries[-1].append(ColorEntry(self, base_color=colour.INPUT_BACKGROUND, bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716"))
        self.entries[-1][17].grid(row=self.i, column=17, padx=10, sticky='ew')

        # Basket
        self.basket.append(Label(self, text='\U0001F5D1', bd=2, highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, relief='flat', bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, width=3))
        self.basket[-1].bind("<Button-1>", self.deleterow)
        self.basket[-1].grid(row=self.i, column=18, padx=10, sticky='ew')

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

    def __init__(self, winmaster, nodeslist, serviceslist, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.i = 2
        self.entries = []
        self.nodeslist = nodeslist
        self.serviceslist = serviceslist
        self.falselabels = []
        self.basket = []

        # Define headers
        service_label = Label(self, bd=2, text=lang.gui_servid, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        service_label.grid(row=0, column=0, ipady=10, sticky='news')
        self.columnconfigure(0, weight=16)

        from_label = Label(self, bd=2, text=lang.gui_fromsimple, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        from_label.grid(row=0, column=1, ipady=10, sticky='news')
        self.columnconfigure(1, weight=16)

        to_label = Label(self, bd=2, text=lang.gui_tosimple, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        to_label.grid(row=0, column=2, ipady=10, sticky='news')
        self.columnconfigure(2, weight=16)

        km_label = Label(self, bd=2, text=lang.gui_kilometers, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        km_label.grid(row=0, column=3, ipady=10, sticky='news')
        self.columnconfigure(3, weight=16)

        duration_label = Label(self, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        duration_label.grid(row=0, column=4, ipady=10, sticky='news')
        self.columnconfigure(4, weight=16)

        departure_label = Label(self, bd=2, text=lang.gui_windowopening, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        departure_label.grid(row=0, column=5, ipady=10, sticky='news')
        self.columnconfigure(5, weight=16)

        arrival_label = Label(self, bd=2, text=lang.gui_windowclosing, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND)
        arrival_label.grid(row=0, column=6, columnspan=2, ipady=10, sticky='news')
        self.columnconfigure(6, weight=16)
        self.columnconfigure(7, weight=1, uniform='weekdays', minsize=40)

        # Label(self, bd=2, text=lang.gui_strictallow, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=8, ipady=10, sticky='news')
        # self.columnconfigure(8, weight=16)

        # Label(self, bd=2, text=lang.gui_strictban, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=9, ipady=10, sticky='news')
        # self.columnconfigure(9, weight=16)

        Label(self, bd=2, text=lang.MON, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=10, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.TUE, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=11, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.WED, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=12, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.THU, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=13, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.FRI, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=14, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.SAT, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=15, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.SUN, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=16, ipady=10, sticky='news')

        self.columnconfigure(10, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(11, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(12, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(13, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(14, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(15, weight=1, uniform='weekdays', minsize=40)
        self.columnconfigure(16, weight=1, uniform='weekdays', minsize=40)

        Label(self, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=17, ipady=10, sticky='news')
        self.columnconfigure(17, weight=16, minsize=80)

        Label(self, bd=2, text=' ', font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=18, ipady=10, sticky='news')
        self.columnconfigure(18, weight=1)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, columnspan=18, sticky='w')

        self.update()

        if len(linkers) == 0: # Nodes defined, not services; standard window
            self.addNewLabel()

        else: # Nodes and services defined; load data to window
            [self.addNewLabel() for _ in range(len(linkers))]  # Create a new label for each service
            i=0
            for link in linkers:
                # Service id
                self.entries[i][0].insert(0, link)
                # From
                self.entries[i][1].set(linkers[link]['origin'])
                # To
                self.entries[i][2].set(linkers[link]['destiny'])
                # Kilometers
                self.entries[i][3].insert(0, str(linkers[link]['kilometers']))
                # Duration (min)
                self.entries[i][4].insert(0, linkers[link]['duration'])
                # Window opening time
                self.entries[i][5].insert(0, linkers[link]['str_opening-time'])
                # Window ending time
                self.entries[i][6].insert(0, linkers[link]['str_ending-time'])
                # Window ending extra day
                self.entries[i][7].insert(0, linkers[link]['ending_extra_days'])
                # Strictly link
                # self.entries[i][8].insert(0, str(linkers[link]['forced']).translate({ord(i): None for i in "[]'"}))
                # Bans
                # self.entries[i][9].insert(0, str(linkers[link]['bans']).translate({ord(i): None for i in "[]'"}))
                # Day 1
                self.entries[i][10].insert(0, str(linkers[link]['week'][0]))
                # Day 2
                self.entries[i][11].insert(0, str(linkers[link]['week'][1]))
                # Day 3
                self.entries[i][12].insert(0, str(linkers[link]['week'][2]))
                # Day 4
                self.entries[i][13].insert(0, str(linkers[link]['week'][3]))
                # Day 5
                self.entries[i][14].insert(0, str(linkers[link]['week'][4]))
                # Day 6
                self.entries[i][15].insert(0, str(linkers[link]['week'][5]))
                # Day 7
                self.entries[i][16].insert(0, str(linkers[link]['week'][6]))
                # Color
                self.entries[i][17].set(linkers[link]['color'])

                i += 1
                # if not i % 5:
                #     self.update()

            self.update()

    def define_linkers(self): # TODO hay que poner strings correctos, que esta usando los de otras pantallas por aceleraración del desarrollo, pero hay que cambiarlos
        global linkers
        new_linkers = {}
        repeated_ids = []

        for row in range(len(self.entries)):
            try:
                key = self.entries[row][0].get()  # String
                new_linkers[key] = {}
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


            new_linkers[key]['origin'] = self.entries[row][1].get()  # String
            if new_linkers[key]['origin'] not in self.nodeslist:
                messagebox.showerror(lang.error_saving, lang.serverror3 + new_linkers[key]['origin'] + lang.serverror4 + key + lang.serverror5)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            new_linkers[key]['destiny'] = self.entries[row][2].get()  # String
            if new_linkers[key]['destiny'] not in self.nodeslist:
                messagebox.showerror(lang.error_saving, lang.serverror6 + new_linkers[key]['destiny'] + lang.serverror4 + key + lang.serverror5)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_linkers[key]['forced'] = self.entries[row][8].get()  # String
                new_linkers[key]['bans'] = self.entries[row][9].get().replace(", ", ",").replace(" ,", ",").split(",") # List
                new_linkers[key]['color'] = self.entries[row][17].get()
            except:
                messagebox.showerror(lang.error_saving, lang.serverror7 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_linkers[key]['kilometers'] = ast.literal_eval(self.entries[row][3].get())  # int/float
            except:
                messagebox.showerror(lang.error_saving, lang.serverror8 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_linkers[key]['duration'] = ast.literal_eval(self.entries[row][4].get())
            except:
                messagebox.showerror(lang.error_saving, lang.error_transfers2 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                days = []  # list of ints
                days.append(ast.literal_eval(self.entries[row][10].get())) if self.entries[row][10].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][11].get())) if self.entries[row][11].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][12].get())) if self.entries[row][12].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][13].get())) if self.entries[row][13].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][14].get())) if self.entries[row][14].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][15].get())) if self.entries[row][15].get() != '' else days.append('')
                days.append(ast.literal_eval(self.entries[row][16].get())) if self.entries[row][16].get() != '' else days.append('')
                new_linkers[key]['week'] = deepcopy(days)
            except:
                messagebox.showerror(lang.error_saving, lang.serverror9 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            # Try to catch a typical error
            try:
                new_linkers[key]['str_opening-time'] = self.entries[row][5].get()  # String
                new_linkers[key]['str_ending-time'] = self.entries[row][6].get()  # String
                new_linkers[key]['ending_extra_days'] = '' if self.entries[row][7].get() == '' else int(self.entries[row][7].get())
                datetime.datetime.strptime(new_linkers[key]['str_opening-time'], '%H:%M').time()  # datetime.time
                datetime.datetime.strptime(new_linkers[key]['str_ending-time'], '%H:%M').time()  # datetime.time
            except:
                messagebox.showerror(lang.error_saving, lang.serverror10 + key + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

        # Check that stated forced and bans constraints are matching other existing services
        # for key in new_linkers:
        #     if new_linkers[key]['forced'] != '':
        #         if new_linkers[key]['forced'] not in new_linkers:
        #             messagebox.showerror(lang.error_saving, lang.serverror11 + key + lang.serverror12 + new_linkers[key]['forced'] + lang.serverror14)
        #             self.root.attributes('-topmost', True)
        #             self.root.attributes('-topmost', False)
        #             return
        #
        #     if new_linkers[key]['bans'][0] != '':
        #         for banned in new_linkers[key]['bans']:
        #             if banned not in new_linkers:
        #                 messagebox.showerror(lang.error_saving, lang.serverror11 + key + lang.serverror13 + banned + lang.serverror14)
        #                 self.root.attributes('-topmost', True)
        #                 self.root.attributes('-topmost', False)
        #                 return

        linkers = deepcopy(new_linkers)
        self.root.destroy()

def linkerswin(winmaster, nodeslist, serviceslist):
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
        root_icon = PhotoImage(file=relative_to_linkers("icon2.png"))
        root.iconphoto(False, root_icon)

        buttonframe = Frame(master=root, background=colour.WINDOW_BACKGROUNDS)

        btn = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND)
        btn.image = PhotoImage(file=relative_to_linkers('addrow.png'))
        btn.configure(image=btn.image)

        btn2 = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND)
        btn2.image = PhotoImage(file=relative_to_linkers('save.png'))
        btn2.configure(image=btn2.image)

        btn.grid(row=0, column=0, padx=20, pady=10)
        btn2.grid(row=0, column=1, padx=20, pady=10)

        buttonframe.pack(anchor='center')

        # Initialize a Scrollable frame:
        Scrollable = Linkers_ScrollableFrame(root, nodeslist, serviceslist, bg=colour.FRAME_BACKGROUND, bd=0, x_scroll=False)

        # Commands 1 to 3 already defined, reconfiguring
        btn.configure(command=Scrollable.addNewLabel)
        btn2.configure(command=lambda: Scrollable.define_linkers())


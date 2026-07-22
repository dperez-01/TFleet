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
import datetime
from copy import deepcopy

import win_nodes as nodes
from tkwidgets import ScrollableFrame, ColorEntry, AutocompleteCombobox
from pathlib import Path

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

transfers = {}

def relative_to_services(path: str) -> Path:
    return OUTPUT_PATH / Path(path)

class transfers_ScrollableFrame(ScrollableFrame):
    def addNewLabel(self, depot):
        self.entries[depot] = []

        # Depot
        depots = [depot + ' < ' + other if other != depot else depot for other in self.depots]
        self.entries[depot].append(AutocompleteCombobox(master=self, completevalues=depots))
        self.entries[depot][0].grid(row=self.i, column=0, padx=10, sticky='ew')
        self.entries[depot][0].bind("<<ComboboxSelected>>", lambda e: self.on_value_change(depot))
        # self.entries[depot].append(Label(self, bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        # self.entries[depot][0].grid(row=self.i, column=0, padx=10, sticky='ew')

        # To id
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[depot][1].grid(row=self.i, column=1, padx=10, sticky='ew')

        # From id
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[depot][2].grid(row=self.i, column=2, padx=10, sticky='ew')

        # Duration
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[depot][3].grid(row=self.i, column=3, padx=10, sticky='ew')

        # Kilometers
        self.entries[depot].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[depot][4].grid(row=self.i, column=4, padx=10, sticky='ew')

        # Gap start time
        self.gapframes[depot] = [Frame(self, bg=colour.FRAME_BACKGROUND, bd=0), [], 0]
        self.gapframes[depot][0].grid(row=self.i, column=5, padx=10, sticky='ew')
        self.gapframes[depot][0].columnconfigure(0, weight=1)

        # Week capacity
        self.capacityframes[depot] = [Frame(self, bg=colour.FRAME_BACKGROUND, bd=0), [], 0]
        self.capacityframes[depot][0].grid(row=self.i, column=6, columnspan=7, sticky='nsew')
        self.capacityframes[depot][0].columnconfigure(0, weight=1, uniform='weekdays')
        self.capacityframes[depot][0].columnconfigure(1, weight=1, uniform='weekdays')
        self.capacityframes[depot][0].columnconfigure(2, weight=1, uniform='weekdays')
        self.capacityframes[depot][0].columnconfigure(3, weight=1, uniform='weekdays')
        self.capacityframes[depot][0].columnconfigure(4, weight=1, uniform='weekdays')
        self.capacityframes[depot][0].columnconfigure(5, weight=1, uniform='weekdays')
        self.capacityframes[depot][0].columnconfigure(6, weight=1, uniform='weekdays')

        # Color
        self.entries[depot].append(ColorEntry(self, base_color=colour.INPUT_BACKGROUND, bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716"))
        self.entries[depot][5].grid(row=self.i, column=13, padx=10, sticky='nsew')

        # Substraction button
        self.minus[depot] = Label(self, fg='#ff0026', text=' - ', bd=2, highlightthickness=0, relief='flat', bg=colour.FRAME_BACKGROUND, font=('futura', 13, 'bold'), width=3)
        self.minus[depot].bind("<Button-1>", lambda e: self.delete_subrow(depot))
        self.minus[depot].grid(row=self.i, column=14, sticky='ns')

        # Add row button
        self.plus[depot] = Label(self, fg='#00ff44', text=' + ', bd=2, highlightthickness=0, relief='flat', bg=colour.FRAME_BACKGROUND, font=('futura', 13, 'bold'), width=3)
        subrow_creator = self.define_create_subrow_command(depot)
        self.plus[depot].bind("<Button-1>", lambda e: subrow_creator())
        self.plus[depot].grid(row=self.i, column=15, sticky='ns')

        self.i += 1

        # Adding a spacer
        self.falselabels.append(Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1))
        self.falselabels[-1].grid(row=self.i, column=0, sticky='w')

        self.i += 1
    def define_create_subrow_command(self, depot):
        def create_subrow():
            if len(self.gapframes[depot][1]) == 0:
                self.gapframes[depot][1].append(Entry(self.gapframes[depot][0], bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, disabledbackground=colour.INPUT_BACKGROUND, disabledforeground=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            else:
                self.gapframes[depot][1].append(Entry(self.gapframes[depot][0], bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            self.gapframes[depot][1][-1].grid(row=len(self.gapframes[depot][1]) - 1, column=0, sticky='ew')

            self.capacityframes[depot][1].append([])
            # Day 1
            self.capacityframes[depot][1][-1].append(Entry(self.capacityframes[depot][0], bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            self.capacityframes[depot][1][-1][0].grid(row=len(self.capacityframes[depot][1]) - 1, column=0, sticky='ew')

            # Day 2
            self.capacityframes[depot][1][-1].append(Entry(self.capacityframes[depot][0], bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            self.capacityframes[depot][1][-1][1].grid(row=len(self.capacityframes[depot][1]) - 1, column=1, sticky='ew')

            # Day 3
            self.capacityframes[depot][1][-1].append(Entry(self.capacityframes[depot][0], bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            self.capacityframes[depot][1][-1][2].grid(row=len(self.capacityframes[depot][1]) - 1, column=2, sticky='ew')

            # Day 4
            self.capacityframes[depot][1][-1].append(Entry(self.capacityframes[depot][0], bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            self.capacityframes[depot][1][-1][3].grid(row=len(self.capacityframes[depot][1]) - 1, column=3, sticky='ew')

            # Day 5
            self.capacityframes[depot][1][-1].append(Entry(self.capacityframes[depot][0], bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            self.capacityframes[depot][1][-1][4].grid(row=len(self.capacityframes[depot][1]) - 1, column=4, sticky='ew')

            # Day 6
            self.capacityframes[depot][1][-1].append(Entry(self.capacityframes[depot][0], bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            self.capacityframes[depot][1][-1][5].grid(row=len(self.capacityframes[depot][1]) - 1, column=5, sticky='ew')

            # Day 7
            self.capacityframes[depot][1][-1].append(Entry(self.capacityframes[depot][0], bd=2, font='futura', width=2, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
            self.capacityframes[depot][1][-1][6].grid(row=len(self.capacityframes[depot][1]) - 1, column=6, sticky='ew')

            self.capacityframes[depot][2] += 1

            # Update the scroll region after new widgets are added
            self.updateScrollRegion()

        return create_subrow

    def delete_subrow(self, depot):
        self.deleter = messagebox.askyesno(lang.generic_deletion, lang.generic_confirmdeletion)
        if self.deleter: # Delete
            self.destroy_subrow(depot)

    def destroy_subrow(self, depot):
        self.gapframes[depot][1][-1].grid_forget()

        self.capacityframes[depot][2] -= 1
        for item in self.capacityframes[depot][1][-1]:
            item.grid_forget()

        del self.gapframes[depot][1][-1]
        del self.capacityframes[depot][1][-1]

        # Update the scroll region after new widgets are added
        self.updateScrollRegion()
        self.root.lift()

    def on_value_change(self, depot):
        current_value = self.entries[depot][0].get()

        if ' < ' in current_value:
            # "Entries" should always be editable. Only the other kind of entry elements are disabled
            # for el in self.entries[depot]:
            #     if el is self.entries[depot][0] or el is self.entries[depot][1] or el is self.entries[depot][2] or el is self.entries[depot][3]:
            #         continue # These remain editable
            #     el.configure(state='disabled')

            for l in self.capacityframes[depot][1]:
                for el in l:
                    el.configure(state='disabled')

            for el in self.gapframes[depot][1]:
                el.configure(state='disabled')

        else:
            for el in self.entries[depot]:
                el.configure(state='normal')

            for l in self.capacityframes[depot][1]:
                for el in l:
                   el.configure(state='normal')

            for el in self.gapframes[depot][1]:
                el.configure(state='normal')
            self.gapframes[depot][1][0].config(state="disabled") # Its the first one, 0:00.

    def __init__(self, winmaster, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.i = 2
        self.entries = {}
        self.gapframes = {}
        self.capacityframes = {}
        self.falselabels = []
        self.minus = {}
        self.plus = {}
        self.depots = [depot for depot in nodes.depotnodes if nodes.depotnodes[depot]]

        # Define headers
        Label(self, bd=2, text=lang.gui_depot, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='ew')
        self.columnconfigure(0, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_to_id, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='ew')
        self.columnconfigure(1, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_from_id, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='ew')
        self.columnconfigure(2, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='ew')
        self.columnconfigure(3, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_kilometers, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=4, ipady=10, sticky='ew')
        self.columnconfigure(4, weight=16, minsize=130)

        Label(self, bd=2, text=lang.gui_gap_starttime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=5, ipady=10, sticky='ew')
        self.columnconfigure(5, weight=16, minsize=130)

        Label(self, bd=2, text=lang.MON, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=6, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.TUE, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=7, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.WED, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=8, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.THU, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=9, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.FRI, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=10, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.SAT, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=11, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.SUN, font=('futura', 11), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=12, ipady=10, sticky='news')

        self.columnconfigure(6, weight=1, uniform='weekdays')
        self.columnconfigure(7, weight=1, uniform='weekdays')
        self.columnconfigure(8, weight=1, uniform='weekdays')
        self.columnconfigure(9, weight=1, uniform='weekdays')
        self.columnconfigure(10, weight=1, uniform='weekdays')
        self.columnconfigure(11, weight=1, uniform='weekdays')
        self.columnconfigure(12, weight=1, uniform='weekdays')

        Label(self, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=13, ipady=10, sticky='ew')
        self.columnconfigure(13, weight=11, minsize=80)

        Label(self, bd=2, text=' ', font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=14, columnspan=2, ipady=10, sticky='ew')
        self.columnconfigure(14, weight=1)
        self.columnconfigure(15, weight=1)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, sticky='w')

        k = 0
        for depot in nodes.depotnodes:
            if nodes.depotnodes[depot]:
                self.addNewLabel(depot)
                if depot in transfers:
                    self.entries[depot][0].set(transfers[depot]['location'])

                    # Transfer to depot id
                    self.entries[depot][1].insert(0, transfers[depot]['id_to'])

                    # Transfer from depot id
                    self.entries[depot][2].insert(0, transfers[depot]['id_from'])

                    # Duration
                    self.entries[depot][3].insert(0, transfers[depot]['duration'])

                    # Kilometers
                    self.entries[depot][4].insert(0, transfers[depot]['kilometers'])

                    # Color
                    self.entries[depot][5].set(transfers[depot]['color'])

                    sr = 0
                    subrow_creator = self.define_create_subrow_command(depot)
                    for start, _, week_data in transfers[depot]['partitions']:
                        subrow_creator()
                        self.gapframes[depot][1][sr].insert(0, start)
                        sd = 0
                        for cap in week_data:
                            self.capacityframes[depot][1][sr][sd].insert(0, cap)
                            sd += 1
                        sr += 1
                    self.gapframes[depot][1][0].config(state="disabled")

                    # Check if entries need to be disabled
                    self.on_value_change(depot)

                else:
                    self.entries[depot][0].set(depot)
                    subrow_creator = self.define_create_subrow_command(depot)
                    subrow_creator()
                    self.gapframes[depot][1][0].insert(0, '0:00')
                    self.gapframes[depot][1][0].config(state="disabled")

                k += 1

        self.update()

    def define_transfers(self):
        global transfers
        forward_rules = {}
        new_transfers = {}
        for depot in self.depots:
            depot_ = self.entries[depot][0].get() # String

            if ' < ' in depot_:
                forwards = True
                forward_rules[depot] = depot_.split(' < ')[1]
            else:
                forwards = False
                forward_rules[depot] = depot

            new_transfers[depot] = {'location': depot_}
            try:
                to_key = self.entries[depot][1].get()  # String
                from_key = self.entries[depot][2].get()  # String

            except:
                messagebox.showerror(lang.error_saving, lang.error_transfers1 + depot + '.' + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_transfers[depot]['duration'] = ast.literal_eval(self.entries[depot][3].get())
            except:
                messagebox.showerror(lang.error_saving, lang.error_transfers2 + depot + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_transfers[depot]['kilometers'] = ast.literal_eval(self.entries[depot][4].get())
            except:
                messagebox.showerror(lang.error_saving, lang.error_transfers3 + depot + '\n' + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            new_transfers[depot]['partitions'] = []
            for subrow in range(len(self.gapframes[depot][1])):
                new_transfers[depot]['partitions'].append([]) # Will contain 0: 'Start', 1: 'End', 2: [Capacities]
                new_transfers[depot]['partitions'][-1].append(self.gapframes[depot][1][subrow].get())
                try:
                    datetime.datetime.strptime(new_transfers[depot]['partitions'][-1][0], '%H:%M').time()  # datetime.time
                except:
                    messagebox.showerror(lang.error_saving, lang.error_transfers4 + depot + lang.error_transfers4_1)
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return

                new_transfers[depot]['partitions'][-1].append(None)
                new_transfers[depot]['partitions'][-1].append([])

            for subrow in range(len(self.gapframes[depot][1])):
                for subcol in range(len(self.capacityframes[depot][1][subrow])):
                    item = self.capacityframes[depot][1][subrow][subcol].get()
                    if item != '' and item != '->':  # Then it's a number or an invalid string
                        try:
                            if not forwards:
                                item = ast.literal_eval(item)
                            else:
                                item = item
                        except:
                            messagebox.showerror(lang.error_saving, lang.error_transfers5 + depot + lang.error_transfers5_1 + str(new_transfers[depot]['partitions'][subrow][0]) + lang.error_transfers5_2 + lang.FULL_WEEK[subcol] + lang.error_transfers5_3)
                            self.root.attributes('-topmost', True)
                            self.root.attributes('-topmost', False)
                            return
                    new_transfers[depot]['partitions'][subrow][2].append(item)

            for subrow in range(len(self.gapframes[depot][1]) - 1):
                new_transfers[depot]['partitions'][subrow][1] = new_transfers[depot]['partitions'][subrow + 1][0]
            new_transfers[depot]['partitions'][-1][1] = '0:00'

            try:
                new_transfers[depot]['id_to'] = to_key
                new_transfers[depot]['id_from'] = from_key
                new_transfers[depot]['color'] = self.entries[depot][5].get()
                nodes.NODES_ARE_NEW[depot] = False
            except:
                messagebox.showerror(lang.error_saving, lang.error_transfers6 + depot + lang.error_transfers6_1 + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

        # Check forward rules consistency
        for depot in forward_rules:
            if depot != forward_rules[depot]:
                target_depot = forward_rules[depot]
                if forward_rules[target_depot] != target_depot:
                    messagebox.showerror(lang.error_saving, 'Depot ' + depot + lang.error_transfers7 + forward_rules[depot] + lang.error_transfers7_1 + traceback.format_exc())
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return

        transfers = deepcopy(new_transfers)
        self.root.destroy()

def transferswin(winmaster):
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
        win.title(lang.transfers_title)
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

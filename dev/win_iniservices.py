'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        win_iniservices.py

 Author:      perez

 Created:     25/10/2023
 Copyright:   (c) perez 2023
-------------------------------------------------------------------------------
'''
from tkinter import Toplevel, PhotoImage, Button, Entry, Label, Frame, messagebox, filedialog, Checkbutton, BooleanVar

from tkwidgets import ScrollableFrame, AutocompleteCombobox, ColorEntry, ToolTip
from datetime import datetime, date, time, timedelta
import openpyxl as xlsx
import ast
import ctypes.wintypes
from copy import deepcopy
import traceback

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

iniservices = {}

trainid = []
km_limit = []
next_mname = []
next_m_duration = []

class Iniservice_ScrollableFrame(ScrollableFrame):
    def addNewLabel(self):
        self.entries.append([])

        # Train ID
        self.entries[-1].append(Entry(self, bd=2, width=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=0, padx=10, sticky='ew')

        # Initial degradation
        self.entries[-1].append(Entry(self, bd=2, width=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=1, padx=10, sticky='ew')

        # Maint. km limit
        self.entries[-1].append(Entry(self, bd=2, width=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=2, padx=10, sticky='ew')

        # Next maint. name
        self.entries[-1].append(Entry(self, bd=2, width=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=3, padx=10, sticky='ew')

        # Next maint. duration
        self.entries[-1].append(Entry(self, bd=2, width=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=4, padx=10, sticky='ew')

        # Location
        self.entries[-1].append(AutocompleteCombobox(master=self, completevalues=self.nodeslist))
        self.entries[-1][-1].grid(row=self.i, column=5, padx=10, sticky='ew')

        # Service id
        self.entries[-1].append(Entry(self, bd=2, width=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=6, padx=10, sticky='ew')

        # Unblock-time
        self.entries[-1].append(Entry(self, bd=2, width=6, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=7, padx=10, sticky='ew')

        # Forced
        self.entries[-1].append(Entry(self, bd=2, width=6, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=8, padx=10, sticky='ew')

        # Bans
        self.entries[-1].append(Entry(self, bd=2, width=6, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=9, padx=10, sticky='ew')

        # Color
        self.entries[-1].append(ColorEntry(self, base_color='#6d6d6d', bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716"))
        self.entries[-1][-1].grid(row=self.i, column=10, padx=10, sticky='ew')

        # Basket
        self.basket.append(Label(self, text='\U0001F5D1', bd=2, highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, relief='flat', bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, width=3))
        self.basket[-1].bind("<Button-1>", self.deleterow)
        self.basket[-1].grid(row=self.i, column=11, padx=10, sticky='ew')

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
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
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

        # self.i -= 2
        self.updateScrollRegion()
        self.root.lift()

    def __init__(self, winmaster, nodeslist, depotnodes, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.i = 2
        self.entries = []
        for node in depotnodes:
            if depotnodes[node]:
                nodeslist.append(node + lang.DEPOT_MAINTENANCE)
                nodeslist.append(node + lang.DEPOT_OVERNIGHT)
        self.nodeslist = sorted(nodeslist)
        self.falselabels = []
        self.basket = []

        # Define headers
        Label(self, bd=2, text=lang.gui_trainid, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_inideg, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_kmlimit, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_mname, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_mdur, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=4, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_loc, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=5, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_locinfo, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=6, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_availst, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=7, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_forced, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=8, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_bans, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=9, ipady=10, sticky='news')
        Label(self, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=10, ipady=10, sticky='news')
        Label(self, bd=2, text=' ', font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=11, ipady=10, sticky='news')

        self.columnconfigure(0, weight=4)
        self.columnconfigure(1, weight=4)
        self.columnconfigure(2, weight=4)
        self.columnconfigure(3, weight=4)
        self.columnconfigure(4, weight=4)
        self.columnconfigure(5, weight=4)
        self.columnconfigure(6, weight=4)
        self.columnconfigure(7, weight=2)
        self.columnconfigure(8, weight=2)
        self.columnconfigure(9, weight=2)
        self.columnconfigure(10, weight=1, minsize=90)
        self.columnconfigure(11, weight=1)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, sticky='news')

        if len(iniservices) == 0:
            self.addNewLabel()

        else:
            for row in range(len(iniservices)):
                self.addNewLabel()

                # Train ID
                self.entries[-1][0].insert(0, trainid[row])

                # Initial degradation
                self.entries[-1][1].insert(0, str(iniservices['iniservice' + str(row+1)]['kilometers']))

                # Maint. km limit
                self.entries[-1][2].insert(0, str(km_limit[row]))

                # Next maint. name
                self.entries[-1][3].insert(0, next_mname[row])

                # Next maint. duration
                self.entries[-1][4].insert(0, str(next_m_duration[row]))

                # Location
                self.entries[-1][5].set(iniservices['iniservice' + str(row+1)]['origin'])

                # Location extra information
                self.entries[-1][6].insert(0, iniservices['iniservice' + str(row+1)]['AUXid'])

                # Unblock-time
                self.entries[-1][7].insert(0, iniservices['iniservice' + str(row+1)]['arrival-time'])

                # Condition
                self.entries[-1][8].insert(0, iniservices['iniservice' + str(row+1)]['forced'])

                # Bans
                self.entries[-1][9].insert(0, str(iniservices['iniservice' + str(row+1)]['bans']).translate({ord(i): None for i in "[]'"}))

                # Color
                self.entries[-1][10].set(iniservices['iniservice' + str(row+1)]['color'])

            self.update()

    def define_services(self, called_from_sap=False):
        global iniservices, trainid, km_limit, next_mname, next_m_duration
        new_iniservices = {}

        new_km_limit = []
        new_next_mname = []
        new_next_m_duration = []

        repeated_ids = []
        new_trainid = []
        for row in range(len(self.entries)):
            try:
                train = self.entries[row][0].get()  # String
                if train in repeated_ids:
                    messagebox.showerror(lang.error_saving, 'ID ' + str(train) + lang.inierror1 + str(repeated_ids.index(train) + 1) + ' & ' + str(row + 1) + '.')
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return
                else:
                    new_trainid.append(train)
                    repeated_ids.append(train)
            except:
                messagebox.showerror(lang.error_saving, lang.inierror2 + str(row + 1) + '.')
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return


        sorter = [x for _, x in sorted(zip(new_trainid, list(range(len(new_trainid)))))]
        new_trainid = sorted(new_trainid)

        idx = -1
        for row in sorter:
            idx += 1
            id = self.entries[row][6].get()  # String
            train = self.entries[row][0].get()  # String

            try:
                current_km = ast.literal_eval(self.entries[row][1].get())  # Numerical
            except:
                messagebox.showerror(lang.error_saving, lang.inierror_train + str(train) + lang.inierror3)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                mname = self.entries[row][3].get()
                mduration = self.entries[row][4].get()
                if mname == '??' or mduration == '??':
                    messagebox.showerror(lang.error_saving, lang.inierror4 + str(train) + '.')
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return
                if mname == '':
                    messagebox.showerror(lang.error_saving, lang.inierror_train + str(train) + lang.inierror5)
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return
            except:
                messagebox.showerror(lang.error_saving, lang.inierror_train + str(train) + lang.inierror6)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                mduration = ast.literal_eval(mduration)
            except:
                messagebox.showerror(lang.error_saving, lang.inierror_train + str(train) + lang.inierror7)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                new_km_limit.append(ast.literal_eval(self.entries[row][2].get()))  # Numerical
            except:
                messagebox.showerror(lang.error_saving, lang.inierror_train + str(train) + lang.inierror8)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            new_next_mname.append(mname)  # String
            new_next_m_duration.append(mduration)  # Numerical

            location = self.entries[row][5].get()  # String
            if location not in self.nodeslist:
                messagebox.showerror(lang.error_saving, lang.inierror9 + str(location) + lang.inierror9_1 + str(train) + lang.inierror9_2)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                lock = '' if self.entries[row][7].get() == '' else ast.literal_eval(self.entries[row][7].get())
            except:
                messagebox.showerror(lang.error_saving, lang.inierror_train + str(train) + lang.inierror10)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                color = self.entries[row][10].get()  # String

                new_iniservices['iniservice' + str(idx+1)] = {}
                new_iniservices['iniservice' + str(idx+1)]['id'] = location + ' ' +  id if len(id) > 0 else location
                new_iniservices['iniservice' + str(idx+1)]['AUXid'] = id
                new_iniservices['iniservice' + str(idx+1)]['origin'] = location
                new_iniservices['iniservice' + str(idx+1)]['destiny'] = location
                new_iniservices['iniservice' + str(idx+1)]['kilometers'] = current_km
                new_iniservices['iniservice' + str(idx+1)]['departure-time'] = 0
                new_iniservices['iniservice' + str(idx+1)]['arrival-time'] = lock
                new_iniservices['iniservice' + str(idx+1)]['str_departure-time'] = '00:00'
                lock2 = 0.1 if lock == '' else lock # TODO no se si q tal con poner 0.1, lo suyo es poner un parametro ajustable y que sea 3 de serie; Y aparte cambiar en los matrix builder
                new_iniservices['iniservice' + str(idx+1)]['str_arrival-time'] = (datetime.combine(date.today(), time()) + timedelta(hours=round(lock2, 8))).strftime('%H:%M')
                new_iniservices['iniservice' + str(idx+1)]['color'] = color
                new_iniservices['iniservice' + str(idx+1)]['forced'] = self.entries[row][8].get()  # String
                new_iniservices['iniservice' + str(idx+1)]['bans'] = self.entries[row][9].get().replace(", ", ",").replace(" ,", ",").split(",")  # List
            except:
                messagebox.showerror(lang.error_saving, lang.inierror11 + str(train) + lang.inierror11_1 + traceback.format_exc())
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return


        iniservices = deepcopy(new_iniservices)
        trainid = deepcopy(new_trainid)
        km_limit = deepcopy(new_km_limit)
        next_mname = deepcopy(new_next_mname)
        next_m_duration = deepcopy(new_next_m_duration)

        if not called_from_sap:
            self.root.destroy()

    def import_excel(self):
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        here = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

        file = filedialog.askopenfilename(initialdir=here, defaultextension='.xlsx', filetypes=[("Excel file", ".xlsx"), ("All files", ".*")])
        if file is None or file == '':
            return

        # self.define_services(called_from_sap=True)

        wb = xlsx.load_workbook(file)
        ws = wb.active
        data = {}

        has_trainid = False
        has_nextmaint = False
        has_currkm = False
        has_maxmargin = False
        has_um = False
        for i in ws.columns:
            if not isinstance(i[0].value, str):
                continue

            elif i[0].value.lower() == 'Composición'.lower():
                has_trainid = True
                data['trainid'] = [x.value for x in i[1:]]

            elif i[0].value.lower() == 'Interv.'.lower():
                has_nextmaint = True
                data['maint'] = [x.value for x in i[1:]]

            elif i[0].value.lower() == 'Val Desde Int.'.lower():
                for j in ws.columns:
                    if j[0].value == 'U.M.':
                        has_currkm = True
                        has_um = True
                        data['inikm'] = [x.value for x in i[1:]]
                        data['um'] = [x.value for x in j[1:]]
                        break

            elif i[0].value.lower() == 'Margen Max.'.lower():
                for j in ws.columns:
                    if j[0].value == 'U.M.':
                        has_maxmargin = True
                        has_um = True
                        data['margin'] = [x.value for x in i[1:]]
                        data['um'] = [x.value for x in j[1:]]
                        break

        if not has_trainid:
            messagebox.showerror('Error', lang.inierror12)
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)
            return

        if not has_nextmaint and not has_currkm and not has_maxmargin and not has_um:
            messagebox.showerror('Error', lang.inierror13)
            self.root.attributes('-topmost', True)
            self.root.attributes('-topmost', False)
            return

        for other_key in data:
            if other_key != 'trainid':
                data[other_key] = [x for _, x in sorted(zip(data['trainid'], data[other_key]), key=lambda item: item[0])]

        data['trainid'] = sorted(data['trainid'])

        to_kill = []
        for i in range(len(data['trainid'])):
            if data['um'][i] != 'KM':
                to_kill.append(i)

        for i in reversed(to_kill):
            data['trainid'].pop(i)
            data['maint'].pop(i)
            data['inikm'].pop(i)
            data['margin'].pop(i)
        del data['um']

        merged = {}
        for i in range(len(data['trainid'])):
            if not data['trainid'][i] in merged:
                merged[data['trainid'][i]] = {'maint': [], 'inikm': [], 'margin': []}
            merged[data['trainid'][i]]['maint'].append(data['maint'][i])
            merged[data['trainid'][i]]['inikm'].append(data['inikm'][i])
            merged[data['trainid'][i]]['margin'].append(data['margin'][i])

        final = {}
        for trainid in merged:
            final[trainid] = {}
            periods = [merged[trainid]['margin'][i] + merged[trainid]['inikm'][i] for i in range(len(merged[trainid]['margin']))]
            most_frequent = min(periods)
            most_frequent_index = periods.index(most_frequent) # Sets use of inikm from most frequent period

            margins = [merged[trainid]['margin'][i] for i in range(len(merged[trainid]['margin']))]
            lowest_margin = min(margins)
            margin_index = margins.index(lowest_margin) # Sets the lowest margin

            maint_index = margin_index
            # Example: IS each 8000km and 500km to IS, but 4000km to another one. So then in 500 we do the other one
            other_indexes = [i for i in range(len(merged[trainid]['margin'])) if merged[trainid]['margin'][i] <= most_frequent and i != most_frequent_index]
            if len(other_indexes) > 0:
                all_margins = [merged[trainid]['margin'][i] + merged[trainid]['inikm'][i] for i in other_indexes]
                maint_index = other_indexes[all_margins.index(max(all_margins))]
            final[trainid]['maint'] = merged[trainid]['maint'][maint_index]
            final[trainid]['inikm'] = merged[trainid]['inikm'][most_frequent_index]
            final[trainid]['margin'] = merged[trainid]['margin'][margin_index]

        new = 0
        updated = 0
        existing = len(self.entries)
        something = self.entries[0][0].get() # Is the first row just a generic empty row (like the one generated when first opening an empty scenario)?

        for trainid in final:
            for row in range(existing):
                if trainid == self.entries[row][0].get():
                    updated += 1

                    # Train ID
                    self.entries[row][0].delete(0, 'end')
                    self.entries[row][0].insert(0, trainid)

                    # Initial degradation
                    self.entries[row][1].delete(0, 'end')
                    if final[trainid]['inikm'] >= 0:
                        self.entries[row][1].insert(0, str(final[trainid]['inikm']))
                    else:
                        self.entries[row][1].insert(0, '0')

                    # Maint. km limit
                    self.entries[row][2].delete(0, 'end')
                    self.entries[row][2].insert(0, str(final[trainid]['inikm'] + final[trainid]['margin']))

                    # Next maint. name
                    self.entries[row][3].delete(0, 'end')
                    self.entries[row][3].insert(0, final[trainid]['maint'])
                    break

            else:
                new += 1
                self.addNewLabel()
                # Train ID
                self.entries[-1][0].insert(0, trainid)

                # Initial degradation
                if final[trainid]['inikm'] >= 0:
                    self.entries[-1][1].insert(0, str(final[trainid]['inikm']))
                else:
                    self.entries[-1][1].insert(0, '0')

                # Maint. km limit
                self.entries[-1][2].insert(0, str(final[trainid]['inikm'] + final[trainid]['margin']))

                # Next maint. name
                self.entries[-1][3].insert(0, final[trainid]['maint'])


        if existing <= 1 and something == '' and updated == 0 and new > 0:
            self.destroy_row(0)
        self.root.lift()
        messagebox.showinfo(lang.iniservice_excel1, lang.iniservice_excel2 + str(new) + lang.iniservice_excel3 + str(updated) + lang.iniservice_excel4)
        self.root.lift()

def iniserviceswin(winmaster, nodeslist, depotnodes):
    global iniservices

    if len(nodeslist) == 0:
        messagebox.showerror(lang.generic_nonodes, lang.generic_createnodes)

    else:
        if window_blocker.IS_OPEN:
            messagebox.showinfo(lang.generic_windowopen, lang.generic_pleaseclose)
            return

        win = Toplevel(winmaster)
        win.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        win.bind("<Destroy>", lambda e: window_blocker.window_destruction_protocol())
        window_blocker.IS_OPEN = True
        win.geometry('1600x600')
        win.minsize(width=1600, height=100)
        win.configure(bg=colour.WINDOW_BACKGROUNDS)
        win.title(lang.iniservice_title)
        win_icon = PhotoImage(file=relative_to_services("icon2.png"))
        win.iconphoto(False, win_icon)

        topframe = Frame(master=win, background=colour.WINDOW_BACKGROUNDS)

        excelframe = Frame(master=topframe, background=colour.WINDOW_BACKGROUNDS)
        btn_excel = Button(excelframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS)
        btn_excel.image = PhotoImage(file=relative_to_services('excel_importer.png'))
        btn_excel.configure(image=btn_excel.image)

        btn_excel.pack(padx=20, pady=3)
        ToolTip(btn_excel, lang.iniservice_tt)
        excelframe.pack(side='left')

        buttonframe = Frame(master=topframe, background=colour.WINDOW_BACKGROUNDS)

        btn = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND)  # Additional garbage collection is required TODO: why?
        btn.image = PhotoImage(file=relative_to_services('addrow.png'))
        btn.configure(image=btn.image)

        btn2 = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND)
        btn2.image = PhotoImage(file=relative_to_services('save.png'))
        btn2.configure(image=btn2.image)

        btn.grid(row=0, column=0, padx=20, pady=10)
        btn2.grid(row=0, column=1, padx=20, pady=10)
        buttonframe.place(relx=0.5, rely=0.5, anchor='center')

        topframe.pack(side='top', fill='x')


        # Initialize a Scrollable frame:
        Scrollable = Iniservice_ScrollableFrame(win, nodeslist, depotnodes, bg=colour.FRAME_BACKGROUND, x_scroll=False, bd=0)

        # Commands 1 to 3 already defined, reconfiguring
        btn.configure(command=Scrollable.addNewLabel)
        btn2.configure(command=Scrollable.define_services)
        btn_excel.configure(command=Scrollable.import_excel)
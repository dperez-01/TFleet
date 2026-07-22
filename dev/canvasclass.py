'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        canvasclass.py

 Author:      perez

 Created:     08/10/2023
 Copyright:   (c) perez 2023
-------------------------------------------------------------------------------
'''
import ast

# First of all, import settings manager to configure the applicaction
import settings

# Now, import language and assets
from pathlib import Path
if settings.LANGUAGE == 'English':
    import language.EN as lang
    if settings.COLOUR_PALETTE == 'Dark':
        import colour.night_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\night\edition")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\night\NavigationToolbarAssets")
    elif settings.COLOUR_PALETTE == 'Light':
        import colour.day_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\day\edition")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\day\NavigationToolbarAssets")
    elif settings.COLOUR_PALETTE == 'Blue':
        import colour.blue_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\EN\blue\edition")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\blue\NavigationToolbarAssets")

elif settings.LANGUAGE == 'Castellano':
    import language.ES as lang
    if settings.COLOUR_PALETTE == 'Dark':
        import colour.night_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\night\edition")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\night\NavigationToolbarAssets")
    elif settings.COLOUR_PALETTE == 'Light':
        import colour.day_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\day\edition")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\day\NavigationToolbarAssets")
    elif settings.COLOUR_PALETTE == 'Blue':
        import colour.blue_palette as colour
        OUTPUT_PATH = Path(__file__).parent / Path(r".\assets\ES\blue\edition")
        OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\blue\NavigationToolbarAssets")


import matplotlib.pyplot as plt
if settings.DISP_COLOUR_PALETTE == 'Dark':
    import colour.night_palette as dispcolour
    plt.style.use('dark_background')
elif settings.DISP_COLOUR_PALETTE == 'Light':
    import colour.day_palette as dispcolour
    plt.style.use('default')

import json

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.patches import Polygon as PolyFather
from matplotlib.patches import Rectangle
from decimal import Decimal

from tkinter import Button, messagebox, Label, Toplevel, PhotoImage, filedialog, Frame, Entry, Checkbutton, BooleanVar
from tkinter.ttk import Combobox, Style
from tkwidgets import AutocompleteCombobox, CustomCalendar, ColorEntry, ToolTip, FancyCheckButton, ScrollableFrame

from copy import deepcopy
from datetime import datetime, timedelta, time, date
from abc import ABCMeta, abstractmethod
import xlsxwriter as xlsx
import ctypes.wintypes
import numpy as np
from math import ceil
import traceback

import win_services as newservices
import win_iniservices as newiniservices
import win_nodes as newnodes
import win_depottransfers as newdepottransfers
import win_sleepers as newsleepers
import win_linkers as newlinkers
import boxes_library as win_library
from help_manager import open_help


def relative_to_navtoolbarassets(path: str) -> Path:
    return OUTPUT_PATH2 / Path(path)

def relative_to_edition(path: str) -> Path:
    return OUTPUT_PATH / Path(path)


import json
from collections import deque
import numpy as np

def is_json_native(obj):
    # quick check for types json handles natively
    return obj is None or isinstance(obj, (str, bool, int, float))

def path_to_str(path):
    # path is a list of tokens (keys or indices)
    s = "root"
    for p in path:
        if isinstance(p, int):
            s += f"[{p}]"
        else:
            s += f"[{repr(p)}]"
    return s

def find_non_jsonables(obj, max_find=50, max_depth=200):
    """
    Yield tuples (path_list, obj, type(obj)) for items that are not JSON-serializable.
    Stops after max_find findings.
    """
    found = 0
    stack = deque()
    stack.append(([], obj, 0))  # (path, current_obj, depth)

    while stack:
        path, cur, depth = stack.pop()
        if found >= max_find:
            return

        if depth > max_depth:
            # prevent runaway recursion
            continue

        # fast accept for native json scalars
        if is_json_native(cur):
            continue

        # common JSON container types: iterate them
        if isinstance(cur, dict):
            for k, v in cur.items():
                stack.append((path + [k], v, depth + 1))
            continue
        if isinstance(cur, (list, tuple, set)):
            # convert set to a list iteration (path will show a non-index key)
            if isinstance(cur, set):
                for i, v in enumerate(cur):
                    stack.append((path + [f"<set_item_{i}>"], v, depth + 1))
            else:
                for i, v in enumerate(cur):
                    stack.append((path + [i], v, depth + 1))
            continue

        # handle numpy types fast
        if isinstance(cur, np.generic):
            # numpy scalar (e.g. np.int32, np.float64)
            yield (path, cur, type(cur))
            found += 1
            continue
        if isinstance(cur, np.ndarray):
            yield (path, cur, type(cur))
            found += 1
            continue

        # Some other common containers which json can't handle:
        # e.g. bytes, bytearray, complex, custom objects, pandas types, etc.
        if isinstance(cur, (bytes, bytearray, complex)):
            yield (path, cur, type(cur))
            found += 1
            continue

        # Last attempt: try json.dumps on the object directly (may be expensive for large objects).
        try:
            json.dumps(cur)
            # OK
            continue
        except Exception:
            yield (path, cur, type(cur))
            found += 1
            continue




combostyle = Style()
combostyle.theme_use('clam')
combostyle.configure("Simple.TCombobox", foreground=colour.INPUT_FOREGROUND,  # Text color
                     background=colour.INPUT_BACKGROUND,  # Arrow background
                     fieldbackground=colour.INPUT_BACKGROUND,  # Entry field background
                     arrowcolor=colour.INPUT_FOREGROUND,  # Dropdown arrow color
                     selectbackground=colour.AUX_INPUT_BACKGROUND,  # Background color when an item is selected (in dropdown)
                     selectforeground=colour.INPUT_FOREGROUND,  # Text color when selected
                     bordercolor=colour.HIGHLIGHT,  # Border around the entry field
                     # lightcolor="purple",             # Top-left edge (highlight)
                     # darkcolor="purple",              # Bottom-right edge (shadow)
                     relief="flat"  # Optional: makes edges flat or raised
                     )

combostyle.map("Simple.TCombobox",
    fieldbackground=[("readonly", colour.INPUT_BACKGROUND)],
    background=[("readonly", colour.INPUT_BACKGROUND)],
    foreground=[("readonly", colour.INPUT_FOREGROUND)],
    arrowcolor=[("readonly", colour.INPUT_FOREGROUND)]
)

class MaintenancesScrollableFrame(ScrollableFrame):
    def addNewLabel(self, index: int):
        self.entries[index] = []

        self.labels.append(Label(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.labels[-1].grid(row=self.i, column=0, padx=10, sticky='ew')

        lab = Label(self, bd=2, text=lang.cc1, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
        lab.grid(row=self.i, column=1, padx=10, sticky='ew')
        lab.bind('<Button-1>', lambda e: self.write_predetermined_maintenance(index))

        self.entries[index].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[index][0].grid(row=self.i, column=2, padx=10, sticky='ew')

        self.entries[index].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[index][1].grid(row=self.i, column=3, padx=10, sticky='ew')

        self.entries[index].append(Entry(self, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[index][2].grid(row=self.i, column=4, padx=10, sticky='ew')

        self.i += 1

        # Adding a spacer
        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=self.i, column=0, sticky='w')
        self.i += 1

    def write_predetermined_maintenance(self, index):
        self.entries[index][0].delete(0, 'end')
        self.entries[index][0].insert(0, settings.DEFAULT_INTERVENTION_KM)
        self.entries[index][1].delete(0, 'end')
        self.entries[index][1].insert(0, settings.DEFAULT_INTERVENTION)
        self.entries[index][2].delete(0, 'end')
        self.entries[index][2].insert(0, settings.DEFAULT_INTERVENTION_TIME)

    def all_are_predetermined(self):
        for i in self.entries:
            self.write_predetermined_maintenance(i)

    def __init__(self, winmaster, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.i = 2
        self.entries = {}
        self.labels = []

        Label(self, bd=2, text=lang.gui_trainid, font=('futura', 12), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='news')
        self.columnconfigure(0, weight=1, minsize=130)
        Label(self, bd=2, text=lang.cc2, font=('futura', 12), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='news')
        self.columnconfigure(1, weight=3, minsize=350)
        Label(self, bd=2, text=lang.cc3, font=('futura', 12), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='news')
        self.columnconfigure(2, weight=1, minsize=130)
        Label(self, bd=2, text=lang.cc4, font=('futura', 12), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='news')
        self.columnconfigure(3, weight=1, minsize=130)
        Label(self, bd=2, text=lang.cc5, font=('futura', 12), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=4, ipady=10, sticky='news')
        self.columnconfigure(4, weight=1, minsize=130)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, sticky='w')

        for index in range(len(newiniservices.iniservices)):
            if newiniservices.next_mname[index] == '??': # TODO what's the problem with index??
                self.addNewLabel(index)
                self.labels[-1].configure(text=newiniservices.trainid[index])
                self.entries[index][0].insert(0, str(newiniservices.km_limit[index]))

    def define_maintenances(self):
        for index in self.entries:
            kmlimit = self.entries[index][0].get()
            maintname = self.entries[index][1].get()
            maintduration = self.entries[index][2].get()

            if kmlimit == '' or maintname == '' or maintduration == '':
                continue

            try:
                kmlimit = ast.literal_eval(kmlimit)
            except:
                messagebox.showerror(lang.error_saving, lang.inierror_train + str(newiniservices.trainid[index]) + lang.cc6)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            try:
                maintduration = ast.literal_eval(maintduration)
            except:
                messagebox.showerror(lang.error_saving, lang.inierror_train + str(newiniservices.trainid[index]) + lang.inierror7)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            newiniservices.km_limit[index] = kmlimit  # Numerical
            newiniservices.next_mname[index] = maintname  # String
            newiniservices.next_m_duration[index] = maintduration  # Numerical

        self.root.destroy()

class SummaryScrollableFrame(ScrollableFrame):
    def addNewLabel(self, train, left, right):
        self.entries.append([])

        self.entries[-1].append(Label(self, text=train, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[-1][0].grid(row=self.i, column=0, padx=10, sticky='ew')

        self.entries[-1].append(Label(self, text=left, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[-1][1].grid(row=self.i, column=1, padx=10, sticky='ew')

        self.entries[-1].append(Label(self, text=right, bd=2, font='futura', width=6, relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[-1][2].grid(row=self.i, column=2, padx=10, sticky='ew')

        self.i += 1

        # Adding a spacer
        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=self.i, column=0, sticky='w')
        self.i += 1

    def __init__(self, winmaster, summary, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.i = 2
        self.entries = []

        Label(self, bd=2, text=lang.gui_trainid, font=('futura', 12), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='news')
        self.columnconfigure(0, weight=1, minsize=200)
        Label(self, bd=2, text=lang.cc7, font=('futura', 12), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='news')
        self.columnconfigure(1, weight=1, minsize=200)
        Label(self, bd=2, text=lang.cc8, font=('futura', 12), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='news')
        self.columnconfigure(2, weight=1, minsize=200)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, sticky='w')

        for train in summary:
            self.addNewLabel(train, summary[train][0], summary[train][1])

def hour_string_to_excel_position(string):
    hour, minute = string.split(':')
    res = 6 * int(hour) + int(int(minute) / 10)
    if res > 1 and minute == '00':
        return res - 1
    else:
        return res

def util_sleepers_creation(basesleepers, starting_day, tmax):
    util_sleepers = deepcopy(basesleepers)

    days = lang.FULL_WEEK
    current = datetime.now().isoweekday() - 1 if starting_day == lang.CURRENT else days.index(starting_day)

    for depot in util_sleepers:
        mb = datetime.strptime(util_sleepers[depot]['morningblock'], '%H:%M').time()  # datetime.time
        nb = datetime.strptime(util_sleepers[depot]['nightblock'], '%H:%M').time()  # datetime.time

        util_sleepers[depot]['morningblock'] = mb.hour + mb.minute / 60
        util_sleepers[depot]['nightblock'] = nb.hour + nb.minute / 60

        if util_sleepers[depot]['nightblock'] < util_sleepers[depot]['morningblock']:
            util_sleepers[depot]['nightblock'] += 24

        if basesleepers[depot]['location'] != depot:
            forwarded_depot = basesleepers[depot]['location'].split(' < ')[1]
            util_sleepers[depot]['forward_capacity'] = forwarded_depot
        else:
            util_sleepers[depot]['forward_capacity'] = depot
            util_sleepers[depot]['week'] = util_sleepers[depot]['week'][current:] + util_sleepers[depot]['week'][:current]
            if ceil(tmax / 24) > 7:
                for i in range(ceil(tmax / 24) - 7):
                    util_sleepers[depot]['week'].append(util_sleepers[depot]['week'][i])


    return util_sleepers

# TODO leftovers of the autoadjuster for time fields
scheduler = False
def on_change(strvar, *args):
    global scheduler
    # cancel scheduler upon content change
    if scheduler:
        strvar.after_cancel(scheduler)
    # create new scheduler to execute show one second later
    # change 1000 (ms) to whatever value you want
    scheduler = strvar.after(10000, live_time_parser(*args))

def live_time_parser(departure, departure_day, arrival, arrival_day, duration, str_week, exiting): # TODO ojo con lo de "Live-update" porque todavía no es que estñe muy implementado. Hay q abrir ticket en SO?
    departure_time = departure.get()
    if departure_time != '':
        try:
            t = datetime.strptime(departure_time, '%H:%M').time()
            str_departure_day = departure_day.get()
            numerical_departure = 24 * str_week.index(str_departure_day) + t.hour + t.minute / 60
        except:
            departure_time = ''
        # start = 24 * self.str_week.index(new_dep_day) + t.hour + t.minute / 60
        # end = 24 * self.str_week.index(new_arr_day) + t.hour + t.minute / 60


    arrival_time = arrival.get()
    if arrival_time != '':
        try:
            t = datetime.strptime(arrival_time, '%H:%M').time()
            str_arrival_day = arrival_day.get()
            numerical_arrival = 24 * str_week.index(str_arrival_day) + t.hour + t.minute / 60
        except:
            arrival_time = ''

    duration_time = duration.get()
    if duration_time != '':
        try:
            numerical_duration = float(duration_time)
        except:
            duration_time = ''

    # Exiting codes:
    # 1 -> Departure time
    # 2 -> Arrival time
    # 3 -> Duration
    if exiting == 1: # Prioritises combination of departure and arrival
        if departure_time != '' and arrival_time != '':
            duration.delete(0, 'end')
            value = numerical_arrival - numerical_departure # noqa
            duration.insert(0, value)
            departure.configure(bg=colour.INPUT_BACKGROUND)
            arrival.configure(bg=colour.INPUT_BACKGROUND)
            duration.configure(bg=colour.INPUT_BACKGROUND) if value > 0 else duration.configure(bg='#ffd28f')

        elif departure_time != '' and duration_time != '':
            arrival.delete(0, 'end')
            h, m = departure_time.split(':')
            st = datetime.combine(date.today(), time(int(h), int(m)))
            end = st + timedelta(hours=round(float(numerical_duration), 32)) # noqa
            arrival.insert(0, (end).strftime('%H:%M'))
            departure.configure(bg=colour.INPUT_BACKGROUND)
            duration.configure(bg=colour.INPUT_BACKGROUND) if numerical_duration > 0 else duration.configure(bg='#ffd28f')

            dif = (end.date() - st.date()).days
            new = str_week.index(str_departure_day) + dif # noqa
            if new > len(str_week):
                new = -1
                arrival.configure(bg='#ffd28f')
            else:
                arrival.configure(bg=colour.INPUT_BACKGROUND)

            arrival_day.set(str_week[new])

    elif exiting == 2: # Prioritises combination of departure and arrival
        if departure_time != '' and arrival_time != '':
            duration.delete(0, 'end')
            value = numerical_arrival - numerical_departure # noqa
            duration.insert(0, value) # noqa
            departure.configure(bg=colour.INPUT_BACKGROUND)
            arrival.configure(bg=colour.INPUT_BACKGROUND)
            duration.configure(bg=colour.INPUT_BACKGROUND) if value > 0 else duration.configure(bg='#ffd28f')

        elif arrival_time != '' and duration_time != '':
            departure.delete(0, 'end')
            h, m = arrival_time.split(':')
            end = datetime.combine(date.today(), time(int(h), int(m)))
            st = end - timedelta(hours=round(float(numerical_duration), 32)) # noqa
            departure.insert(0, (datetime.combine(date.today(), time(int(h), int(m))) - timedelta(hours=round(float(numerical_duration), 32))).strftime('%H:%M')) # noqa
            arrival.configure(bg=colour.INPUT_BACKGROUND)
            duration.configure(bg=colour.INPUT_BACKGROUND) if numerical_duration > 0 else duration.configure(bg='#ffd28f')

            dif = (end.date() - st.date()).days
            new = str_week.index(str_arrival_day) - dif  # noqa
            if new < 0:
                new = 0
                departure.configure(bg='#ffd28f')
            else:
                departure.configure(bg=colour.INPUT_BACKGROUND)

            departure_day.set(str_week[new])

    elif exiting == 3: # Prioritises combination of departure and duration
        if departure_time != '' and duration_time != '':
            arrival.delete(0, 'end')
            h, m = departure_time.split(':')
            st = datetime.combine(date.today(), time(int(h), int(m)))
            end = st + timedelta(hours=round(float(numerical_duration), 32)) # noqa
            arrival.insert(0, (end).strftime('%H:%M'))
            departure.configure(bg=colour.INPUT_BACKGROUND)
            duration.configure(bg=colour.INPUT_BACKGROUND) if numerical_duration > 0 else duration.configure(bg='#ffd28f')

            dif = (end.date() - st.date()).days
            new = str_week.index(str_departure_day) + dif # noqa
            if new > len(str_week):
                new = -1
                arrival.configure(bg='#ffd28f')
            else:
                arrival.configure(bg=colour.INPUT_BACKGROUND)
            arrival_day.set(str_week[new])

        elif arrival_time != '' and duration_time != '':
            departure.delete(0, 'end')
            h, m = arrival_time.split(':')
            end = datetime.combine(date.today(), time(int(h), int(m)))
            st = end - timedelta(hours=round(float(numerical_duration), 32)) # noqa
            departure.insert(0, (datetime.combine(date.today(), time(int(h), int(m))) - timedelta(hours=round(float(numerical_duration), 32))).strftime('%H:%M')) # noqa
            arrival.configure(bg=colour.INPUT_BACKGROUND)
            duration.configure(bg=colour.INPUT_BACKGROUND) if numerical_duration > 0 else duration.configure(bg='#ffd28f')

            dif = (end.date() - st.date()).days
            new = str_week.index(str_arrival_day) - dif  # noqa
            if new < 0:
                new = 0
                departure.configure(bg='#ffd28f')
            else:
                departure.configure(bg=colour.INPUT_BACKGROUND)
            departure_day.set(str_week[new])

class Polygon:
    __metaclass__ = ABCMeta

    _lock = None  # only one can be animated at a time

    @abstractmethod
    def compute_edges(self):
        raise NotImplementedError("Implemented in child classes")

    def __init__(self, parent, ax, bottomleft, height, width, text, origin, destiny, conditioned_successor, banned_successors, departure_time, arrival_time, hmovement, ticket, id_, type_, mtext=None, kmservice=None, kmlimit=None, **kwargs):
        self.parent = parent

        self.ax = ax
        self.bottomleft = bottomleft
        self.height = height
        self.width = width
        self.polygon = PolyFather(self.compute_edges(), **kwargs) # Always stores a polygon, but retriggering the function causes movement
        self.msg = text
        self.mmsg = mtext
        self.km = kmservice
        self.kmlimit = kmlimit
        if ticket == 'S' or 'M':
            self.text = self.ax.text(self.polygon.xy[0][0] + self.width/2, self.polygon.xy[0][1] + self.height + 0.15, self.msg, ha='center', va='center', fontsize=self.parent.masterfontsize, fontfamily='monospace')
        else:
            self.text = self.ax.text(self.polygon.xy[0][0] + self.width/2, self.polygon.xy[0][1] + self.height + 0.35, self.msg, ha='center', va='center', fontsize=self.parent.masterfontsize, fontfamily='monospace')
        self.mtext = self.mmsg if self.mmsg == None else self.ax.text(self.polygon.xy[0][0] + self.width/2, self.polygon.xy[0][1] + self.height/2, self.mmsg, ha='center', va='center', fontsize=self.parent.masterfontsize, fontfamily='monospace', color=dispcolour.DISP_TEXTSMAINT)
        self.origin = origin
        self.destiny = destiny
        self.conditioned_successor = conditioned_successor
        self.banned_successors = deepcopy(banned_successors)
        self.departure_time = departure_time
        self.arrival_time = arrival_time
        self.press = None
        self.background = None
        self.hmovement = hmovement
        self.ticket = ticket
        self.hatched = False
        self.selected = False
        self.controlpress = 0, 0
        self.id_ = id_
        self.type_ = type_

    def connect(self):
        'connect to all the events we need'
        self.cidpress = self.polygon.figure.canvas.mpl_connect('button_press_event', self.on_press) # TODO averiguarse un evento de selección en area?
        self.cidrelease = self.polygon.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.polygon.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def on_press(self, event):
        'on button press we will see if the mouse is over us and store some data'
        if event.inaxes != self.polygon.axes or self.parent.click_to_create or self.parent.click_to_summarise:
            return
        if Polygon._lock is not None:
            return
        contains, attrd = self.polygon.contains(event)
        if not contains:
            return

        # Single addition to selection
        if event.button == 1 and event.key == 'control':
            self.parent.highlighter.active = False
            Polygon._lock = self
            self.controlpress = event.x, event.y
            return

        # Edition mode
        if event.button == 3:
            self.parent.summon_properties_window(item=self)
            return

        # After this point, only left button (alone) must work
        if event.button != 1:
            return

        self.parent.highlighter.active = False
        Polygon._lock = self
        if self.selected:
            self.press = 0, 0, 0
            self.group_event = event.xdata, event.ydata
            self.group_press = [(item, deepcopy(item.polygon.xy)) for item in self.parent.highlighter.selection]

            canvas = self.polygon.figure.canvas
            axes = self.polygon.axes
            for item in self.parent.highlighter.selection:
                # Destroy text
                item.text.remove()
                if not item.mtext == None:
                    item.mtext.remove()

                # draw everything but the selected polygon and store the pixel buffer
                item.polygon.set_animated(True)

            canvas.draw()
            self.background = canvas.copy_from_bbox(self.polygon.axes.bbox)

            # now redraw just the polygon
            for item in self.parent.highlighter.selection:
                axes.draw_artist(item.polygon)

            # and blit just the redrawn area
            canvas.blit(axes.bbox)

        # Normal mode
        else:
            self.press = deepcopy(self.polygon.xy), event.xdata, event.ydata

            # Destroy text
            self.text.remove()
            if not self.mtext == None:
                self.mtext.remove()

            # draw everything but the selected polygon and store the pixel buffer
            canvas = self.polygon.figure.canvas
            axes = self.polygon.axes
            self.polygon.set_animated(True)
            canvas.draw() # TODO COULD USE DRAW_IDLE()?
            self.background = canvas.copy_from_bbox(self.polygon.axes.bbox)

            # now redraw just the polygon
            axes.draw_artist(self.polygon)

            # and blit just the redrawn area
            canvas.blit(axes.bbox)

    def on_motion(self, event):
        'on motion, we will move the rect if the mouse is over us'
        if Polygon._lock is not self:
            return
        if event.inaxes != self.polygon.axes:
            return
        if self.press is None:
            return

        if self.selected:
            canvas = self.polygon.figure.canvas # TODO this two actions are performed in several functions accross the class, with the canvas and axes always being the same. They can be attributes form init, and we gain 0.00000001 seconds
            axes = self.polygon.axes
            for item, xy in self.group_press:
                dx = event.xdata - self.group_event[0]
                dy = event.ydata - self.group_event[1]
                for i in range(len(item.polygon.xy)): # TODO la longitud es siempre 4, puedo ganarme 0.00000000001 segundos. Cambialo que es una ganancia estupenda
                    # X-motion
                    if item.hmovement and (item.parent.horzban.get() or event.key == 'h' or event.key == 'H'):
                        item.polygon.xy[i][0] = xy[i][0] + dx  # noqa

                    # Y-motion
                    item.polygon.xy[i][1] = xy[i][1] + int(dy)

                item.bottomleft = [item.polygon.xy[0][0], item.polygon.xy[0][1]]

            # restore the background region
            canvas.restore_region(self.background)

            # redraw just the current polygon
            for item, _ in self.group_press:
                axes.draw_artist(item.polygon)

            # blit just the redrawn area
            canvas.blit(axes.bbox)

        else:
            xy, xpress, ypress = self.press

            # Displacements
            if self.hmovement and (self.parent.horzban.get() or event.key == 'h' or event.key == 'H'):
                dx = event.xdata - xpress
            dy = event.ydata - ypress

            for i in range(len(self.polygon.xy)):
                # X-motion
                if self.hmovement and (self.parent.horzban.get() or event.button == 2 or event.key == 'h' or event.key == 'H'):
                    self.polygon.xy[i][0] = xy[i][0] + dx # noqa

                # Y-motion
                self.polygon.xy[i][1] = xy[i][1] + int(dy)

            self.bottomleft = [self.polygon.xy[0][0], self.polygon.xy[0][1]]

            canvas = self.polygon.figure.canvas
            axes = self.polygon.axes
            # restore the background region
            canvas.restore_region(self.background)

            # redraw just the current polygon
            axes.draw_artist(self.polygon)

            # blit just the redrawn area
            canvas.blit(axes.bbox)

    # noinspection PyUnusedLocal
    def on_release(self, event):
        'on release, we reset the press data'

        if Polygon._lock is not self or Polygon._lock == None:
            return

        # Single addition to selection
        if (event.button == 1 and event.key == 'control') or self.press is None:
            self.parent.highlighter.active = True
            Polygon._lock = None
            if event.x == self.controlpress[0] and event.y == self.controlpress[1]:
                if self.selected:
                    self.clear_selected()
                    self.parent.highlighter.selection.remove(self)
                else:
                    self.set_selected()
                    self.parent.highlighter.selection.append(self)
            return

        # self.parent.highlighter.selector.set_active(True)
        self.parent.highlighter.active = True

        if self.selected:
            undo_history = []

            for item, xy in self.group_press:
                # Prepare undo registry
                if item.ticket == 'S':
                    undo_history.append(['S', item.parent.s_collection.index(item), xy])
                    item.text = item.ax.text(item.polygon.xy[0][0] + item.width / 2, item.polygon.xy[0][1] + item.height + 0.15, item.msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
                if item.ticket == 'M':
                    undo_history.append(['M', item.parent.m_collection.index(item), xy])
                    item.text = item.ax.text(item.polygon.xy[0][0] + item.width / 2, item.polygon.xy[0][1] + item.height + 0.15, item.msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
                if item.ticket == 'T':
                    undo_history.append(['T', item.parent.t_collection.index(item), xy])
                    item.text = item.ax.text(item.polygon.xy[0][0] + item.width / 2, item.polygon.xy[0][1] + item.height + 0.35, item.msg, ha='center', va='center', fontsize=8, fontfamily='monospace')

                # New text
                if not item.mtext == None:
                    item.mtext = item.ax.text(item.polygon.xy[0][0] + item.width / 2, item.polygon.xy[0][1] + item.height / 2, item.mmsg, ha='center', va='center', fontsize=8, fontfamily='monospace', color=dispcolour.DISP_TEXTSMAINT)

                # turn off the polygon animation property and reset the background
                item.polygon.set_animated(False)

            self.parent.modify_undo_history(['move', undo_history])

        else:
            # Prepare undo registry
            if self.ticket == 'S':
                self.parent.modify_undo_history(['move', [['S', self.parent.s_collection.index(self), self.press[0]]]])
                self.text = self.ax.text(self.polygon.xy[0][0] + self.width / 2, self.polygon.xy[0][1] + self.height + 0.15, self.msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
            if self.ticket == 'M':
                self.parent.modify_undo_history(['move', [['M', self.parent.m_collection.index(self), self.press[0]]]])
                self.text = self.ax.text(self.polygon.xy[0][0] + self.width / 2, self.polygon.xy[0][1] + self.height + 0.15, self.msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
            if self.ticket == 'T':
                self.parent.modify_undo_history(['move', [['T', self.parent.t_collection.index(self), self.press[0]]]])
                self.text = self.ax.text(self.polygon.xy[0][0] + self.width / 2, self.polygon.xy[0][1] + self.height + 0.35, self.msg, ha='center', va='center', fontsize=8, fontfamily='monospace')

            if not self.mtext == None:
                self.mtext = self.ax.text(self.polygon.xy[0][0] + self.width / 2, self.polygon.xy[0][1] + self.height / 2, self.mmsg, ha='center', va='center', fontsize=8, fontfamily='monospace', color=dispcolour.DISP_TEXTSMAINT)

            # turn off the polygon animation property and reset the background
            self.polygon.set_animated(False)

        self.press = None

        # Redo gets wiped one way or the other
        self.parent.modify_redo_history(wiping=True)

        self.background = None
        # redraw the full figure
        self.polygon.figure.canvas.draw()  # TODO valdría draw_idle()?

        # if self.ticket == 'S':
        #     self.parent.modify_undo_history(['move', [['S', self.parent.s_collection.index(self), self.press[0]]]])
        #     self.parent.modify_redo_history(wiping=True)
        # if self.ticket == 'M':
        #     self.parent.modify_undo_history(['move', [['M', self.parent.m_collection.index(self), self.press[0]]]])
        #     self.parent.modify_redo_history(wiping=True)
        # if self.ticket == 'T':
        #     self.parent.modify_undo_history(['move', [['T', self.parent.t_collection.index(self), self.press[0]]]])
        #     self.parent.modify_redo_history(wiping=True)

        Polygon._lock = None

        # logger.debug("Release polygon (%s, %d) at (%f, %f)", self.type_,
        #              self.id_, self.bottomleft[0], self.bottomleft[1])
        self.parent.update_plot(showstatus=False)

    def set_selected(self):
        'Classifies the polygon as selected'
        self.polygon.set_edgecolor('#f0bd26')  # or any valid color
        self.selected = True
        self.polygon.figure.canvas.draw_idle()  # Refresh the canvas to show the change

    def soft_set_selected(self):
        'Classifies the polygon as selected, but does not trigger the re-rendering. Re-rendering is intended to be called by the Highlighter class once all the affected polygons have been processed'
        self.polygon.set_edgecolor('#f0bd26')  # or any valid color
        self.selected = True

    def clear_selected(self):
        'Classifies the polygon as not selected'
        self.selected = False
        self.polygon.set_edgecolor(dispcolour.DISP_BOXBORDER)
        self.polygon.figure.canvas.draw_idle()  # Refresh the canvas to show the change

    def soft_clear_selected(self):
        'Classifies the polygon as not selected, but does not trigger the re-rendering. Re-rendering is intended to be called by the Highlighter class once all the affected polygons have been processed'
        self.selected = False
        self.polygon.set_edgecolor(dispcolour.DISP_BOXBORDER)

    def mmsg_replacement(self, new_mmsg):
        self.mmsg = new_mmsg
        if not self.mtext == None:
            self.mtext.remove()
        self.mtext = self.ax.text(self.polygon.xy[0][0] + self.width/2, self.polygon.xy[0][1] + self.height/2, self.mmsg, ha='center', va='center', fontsize=8, fontfamily='monospace', color=dispcolour.DISP_TEXTSMAINT)

    def disconnect(self): # TODO no estoy haciendo uso de esto, pero quiza me sea interesante utilzairlo cuando vaya a eliminar cosas con mi toolbox
        'disconnect all the stored connection ids'
        self.polygon.figure.canvas.mpl_disconnect(self.cidpress)
        self.polygon.figure.canvas.mpl_disconnect(self.cidrelease)
        self.polygon.figure.canvas.mpl_disconnect(self.cidmotion)

class ScheduleBox(Polygon):
    _id = 0

    def compute_edges(self):
        return [
            [ # BOTTOM - LEFT
                self.bottomleft[0],
                self.bottomleft[1]
            ],
            [ # TOP - LEFT
                self.bottomleft[0],
                self.bottomleft[1] + self.height
            ],
            [ # TOP - RIGHT
                self.bottomleft[0] + self.width,
                self.bottomleft[1] + self.height
            ],
            [ # BOTTOM - RIGHT
                self.bottomleft[0] + self.width,
                self.bottomleft[1]
            ]
        ]

    def __init__(self, parent, ax, bottomleft, height, width, name, ticket, origin=None, destiny=None, conditioned_successor='', banned_successors=[], departure_time=None, arrival_time=None, mtext=None, kmservice=None, hmovement=False, kmlimit=None, **kwargs):
        Polygon.__init__(self, parent, ax, bottomleft, height, width, name, origin, destiny, conditioned_successor, banned_successors, departure_time, arrival_time, hmovement, ticket, ScheduleBox._id, "launcher", mtext=mtext, kmservice=kmservice, kmlimit=kmlimit, **kwargs)
        ScheduleBox._id += 1

class FastAreaSelector:
    def __init__(self, ax, parent):
        self.ax = ax
        self.parent = parent
        self.press_event = None
        self.selection = []
        self.rect = None
        self.background = None
        self.canvas = ax.figure.canvas
        self.active = True
        self.connect()

    def on_press(self, event):
        if event.inaxes != self.ax or not self.active or event.button != 1:
            return

        if not (getattr(event, 'key', None) == 'control' or getattr(event, 'key', None) == 'control'):
            if len(self.selection) > 0:
                self.clear_highlights()

        self.press_event = event
        # Create the rectangle patch
        self.rect = Rectangle((event.xdata, event.ydata), 0, 0, facecolor='yellow', edgecolor='yellow', alpha=0.2, fill=True)
        self.ax.add_patch(self.rect)
        self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def on_motion(self, event):
        if self.press_event is None or event.inaxes != self.ax: return
        x0, y0 = self.press_event.xdata, self.press_event.ydata
        x1, y1 = event.xdata, event.ydata
        self.rect.set_xy((min(x0, x1), min(y0, y1)))
        self.rect.set_width(abs(x1 - x0))
        self.rect.set_height(abs(y1 - y0))
        self.canvas.restore_region(self.background)
        self.ax.draw_artist(self.rect)
        self.canvas.blit(self.ax.bbox)

    def on_release(self, event):
        if self.press_event is None or event.button != 1:
            return
        if self.press_event.x == event.x and self.press_event.y == event.y:
            if len(self.selection) > 0:
                self.clear_highlights()
                self.press_event = None
                self.active = True
                return

        x0, y0 = self.rect.xy
        x1 = x0 + self.rect.get_width()
        y1 = y0 + self.rect.get_height()
        self.background = None
        self.onselect(x0, x1, y0, y1)
        self.rect.remove()
        self.rect = None
        self.press_event = None
        self.active = True

    def onselect(self, x0, x1, y0, y1):
        epsilon = 0.08  # More or less 5 minutes
        new_selection = []
        new_selection += [service for service in self.parent.s_collection if service.polygon.xy[0][0] >= x0 - epsilon and service.polygon.xy[2][0] <= x1 + epsilon and service.polygon.xy[0][1] >= y0 - epsilon and service.polygon.xy[2][1] <= y1 + epsilon]
        new_selection += [maint for maint in self.parent.m_collection if maint.polygon.xy[0][0] >= x0 - epsilon and maint.polygon.xy[2][0] <= x1 + epsilon and maint.polygon.xy[0][1] >= y0 - epsilon and maint.polygon.xy[2][1] <= y1 + epsilon]
        new_selection += [transfer for transfer in self.parent.t_collection if transfer.polygon.xy[0][0] >= x0 - epsilon and transfer.polygon.xy[2][0] <= x1 + epsilon and transfer.polygon.xy[0][1] >= y0 - epsilon and transfer.polygon.xy[2][1] <= y1 + epsilon]
        self.selection += new_selection
        for item in self.selection:
            item.soft_set_selected()
        self.canvas.draw_idle()

    def clear_highlights(self):
        for item in self.selection:
            item.soft_clear_selected()
        self.selection = []
        # self.canvas.draw_idle()

    def connect(self):
        self.cid_press = self.canvas.mpl_connect('button_press_event', self.on_press)
        self.cid_release = self.canvas.mpl_connect('button_release_event', self.on_release)
        self.cid_motion = self.canvas.mpl_connect('motion_notify_event', self.on_motion)

    def disconnect(self):
        self.canvas.mpl_disconnect(self.cid_press)
        self.canvas.mpl_disconnect(self.cid_release)
        self.canvas.mpl_disconnect(self.cid_motion)
        # self.rect.remove()

class ZoomPan:
    def __init__(self, ax, factor):
        self.ax = ax
        self.cur_xlim = None
        self.xpress = None
        self.factor = factor
        self.default_xlim = self.ax.get_xlim()

        self.fig = self.ax.get_figure()  # get the figure of interest
        self.cidScroll = self.fig.canvas.mpl_connect('scroll_event', self.zoom)
        self.cidBP = self.fig.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidBR = self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidBM = self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)
        self.cidKey = self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)  # Add key event

    def zoom(self, event):
        if event.inaxes != self.ax:
            return
        if event.button != 'up' and event.button != 'down':
            return

        cur_xlim = self.ax.get_xlim()
        if event.button == 'up':
            # deal with zoom in
            scale_factor = 1 / self.factor
        else: # event.button == 'down':
            # deal with zoom out
            scale_factor = self.factor

        # Prevent the home button from breaking after zooming
        self.ax.figure.canvas.toolbar.push_current()

        # new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
        # relx = (cur_xlim[1] - event.xdata)/(cur_xlim[1] - cur_xlim[0])
        # self.ax.set_xlim([(event.xdata - new_width) * (1-relx), (event.xdata + new_width) * relx])

        width = cur_xlim[1] - cur_xlim[0]
        new_width = width * scale_factor
        # Keep mouse position at same relative location
        left = event.xdata - (event.xdata - cur_xlim[0]) * (new_width / width)
        right = event.xdata + (cur_xlim[1] - event.xdata) * (new_width / width)

        # Prevent zooming out beyond default
        if left < self.default_xlim[0] or right > self.default_xlim[1]:
            left, right = self.default_xlim

        self.ax.set_xlim([left, right])

        self.ax.figure.canvas.draw()

    def on_key_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.key == 'right':
            cur_xlim = self.ax.get_xlim()
            max_pan = self.default_xlim[1] - cur_xlim[1]
            actual_pan = min(12, max_pan)
            new_left = cur_xlim[0] + actual_pan
            new_right = cur_xlim[1] + actual_pan
        elif event.key == 'left':
            cur_xlim = self.ax.get_xlim()
            max_pan = cur_xlim[0] - self.default_xlim[0]
            actual_pan = min(12, max_pan)
            new_left = cur_xlim[0] - actual_pan
            new_right = cur_xlim[1] - actual_pan
        else:
            return
        self.ax.set_xlim([new_left, new_right])
        self.ax.figure.canvas.draw()

    def on_press(self, event):
        if event.inaxes != self.ax:
            return
        if event.button != 2:
            return

        self.cur_xlim = self.ax.get_xlim()
        # self.cur_ylim = self.ax.get_ylim()
        self.xpress = event.xdata

    def on_motion(self, event):
        if self.xpress is None:
            return
        if event.inaxes != self.ax:
            return
        if event.button != 2:
            return

        dx = event.xdata - self.xpress
        new_left = self.cur_xlim[0] - dx
        new_right = self.cur_xlim[1] - dx

        # Clamp to default limits
        if new_left < self.default_xlim[0]:
            new_left = self.default_xlim[0]
            new_right = new_left + (self.cur_xlim[1] - self.cur_xlim[0])
        if new_right > self.default_xlim[1]:
            new_right = self.default_xlim[1]
            new_left = new_right - (self.cur_xlim[1] - self.cur_xlim[0])

        self.ax.set_xlim([new_left, new_right])
        self.ax.figure.canvas.draw()

        # self.cur_xlim -= dx
        # self.ax.set_xlim(self.cur_xlim)
        # self.ax.figure.canvas.draw()

    # # Faster panning
    # def on_motion(self, event):
    #     if self.xpress is None:
    #         return
    #     if event.inaxes != self.ax:
    #         return
    #     if event.button != 2:
    #         return
    #
    #     # Use the center of the axes for Y to keep Y axis fixed
    #     center_y = (self.ax.bbox.y0 + self.ax.bbox.y1) / 2
    #     self.ax._pan_start = SimpleNamespace(lim=self.ax.viewLim.frozen(), trans=self.ax.transData.frozen(), trans_inverse=self.ax.transData.inverted().frozen(), bbox=self.ax.bbox.frozen(), x=event.x, y=center_y)
    #     self.ax.drag_pan(3, event.key, event.x, center_y)
    #     self.fig.canvas.draw_idle()

    def on_release(self, event):
        if event.button != 2:
            return
        if self.xpress is None:
            return
        self.xpress = None
        self.ax.figure.canvas.draw()

class FullCanvas():
    def __init__(self, init_mode, parentwindow, basenodes, baseshortenings, baseservices, baselinkers, basetransfers, basesleepers, numtrains, starting_day, trainid, km_limit, depot, maintenance_duration, maintenance_name, solution_x=None, departure_time=None, duration_service=None, conditioned_successor=None, banned_successors=None, origins=None, destinies=None, table_conversion=None, km_service=None, dict_color=None, str_departures=None, str_arrivals=None, solution_maintenance=None, solution_linkers=None, info_linkers=None, iniservices=None, s_collection=None, m_collection=None, t_collection=None, multiple_next_m_name=None, multiple_next_m_duration=None, multiple_km_limit=None):
        # Parents
        self.parent = parentwindow

        # State definers
        self.click_to_create = False
        self.click_to_summarise = False

        # Base-data
        self.baseservices = deepcopy(baseservices)
        self.basenodes = deepcopy(basenodes)
        self.basenodes_without_extras = deepcopy(basenodes)
        self.shortenings = deepcopy(baseshortenings)
        self.shortenings_without_extras = deepcopy(baseshortenings)
        self.baselinkers = deepcopy(baselinkers)
        self.basetransfers = deepcopy(basetransfers)
        self.basesleepers = deepcopy(basesleepers)

        # Data
        self.numtrains = numtrains
        self.refypos = numtrains - 1
        self.starting_day = starting_day # Note: This is a string, not a number
        self.trainid = deepcopy(trainid) # TODO this and other data are stupidly stored as dictionaries. Since deprecation of several behaviors, this is no longer needed. Change to list.
        self.km_limit = deepcopy(km_limit)
        self.depot_without_extras = deepcopy(depot)
        self.depot = deepcopy(depot)
        self.maintenance_name = deepcopy(maintenance_name)
        self.maintenance_duration = deepcopy(maintenance_duration)

        # Real depot considerations
        for station in self.depot_without_extras:
            if self.depot[station]:
                self.depot[station] = False
                self.depot[station + lang.DEPOT_MAINTENANCE] = True
                self.depot[station + lang.DEPOT_OVERNIGHT] = False
                self.basenodes.append(station + lang.DEPOT_MAINTENANCE)
                self.basenodes.append(station + lang.DEPOT_OVERNIGHT)
                self.shortenings[station + lang.DEPOT_MAINTENANCE] = self.shortenings[station]
                self.shortenings[station + lang.DEPOT_OVERNIGHT] = self.shortenings[station]

        # Customisation
        self.nightstarttime = 0  # From 0 to 23
        self.nightendtime = 6  # From 0 to 23

        # Other elements
        self.action_list_undo = [] # Used for undo
        self.action_list_redo = [] # Used for redo

        # First construction - Basics
        self.deletionmode = BooleanVar(master=parentwindow, value=False)
        self.editionmode = BooleanVar(master=parentwindow, value=False)
        self.horzban = BooleanVar(master=parentwindow, value=False)
        self.propwindow = None # Used for properties window
        self.chooserw = None # Used for both new day cuts and excel exportation

        # First construction - New graph
        if init_mode == 'standard':
            # self.base_s_collection, self.base_m_collection, self.base_t_collection = self.collection_construction(solution_x, departure_time, duration_service, table_conversion, km_service, origins, destinies, conditioned_successor, banned_successors, str_departures, str_arrivals, dict_color, solution_maintenance, maintenance_duration, maintenance_name, solution_linkers, info_linkers, basetransfers, basesleepers, iniservices, comes_from_multicuts, multiple_next_m_name, multiple_next_m_duration, multiple_km_limit)
            if multiple_next_m_name is None:
                solution_maintenance = np.array(solution_maintenance).reshape(-1, 1)
                multiple_next_m_name = np.array(maintenance_name).reshape(-1, 1)
                multiple_next_m_duration = np.array(maintenance_duration).reshape(-1, 1)
                multiple_km_limit = np.array(km_limit).reshape(-1, 1)

            self.base_s_collection, self.base_m_collection, self.base_t_collection = self.collection_construction(solution_x, departure_time, duration_service, table_conversion, km_service, origins, destinies, conditioned_successor, banned_successors, str_departures, str_arrivals, dict_color, solution_maintenance, solution_linkers, info_linkers, basetransfers, basesleepers, iniservices, multiple_next_m_name, multiple_next_m_duration, multiple_km_limit)
            self.canvas_construction(self.base_s_collection, self.base_m_collection, self.base_t_collection)
            self.canvas_customisation(create_toolbar=True)
            self.update_plot(showstatus=False)

        # First construction - Loading previous graph
        if init_mode == 'existing_data':
            self.base_s_collection, self.base_m_collection, self.base_t_collection = s_collection, m_collection, t_collection
            self.canvas_construction(s_collection, m_collection, t_collection)
            self.canvas_customisation(create_toolbar=True)
            self.update_plot(showstatus=False)

        # Fix viewing
        self.parent.update()
        self._last_size = self.parent.wm_geometry()
        self.parent.bind('<Configure>', self.on_parent_resize)
        self.parent.state('zoomed')

    def on_parent_resize(self, event):
        if event.widget == self.parent:
            current_geom = self.parent.wm_geometry()
            if current_geom != self._last_size:
                self._last_size = current_geom
                self.apply_tight_layout_once()

    def apply_tight_layout_once(self, pad=.5, h_pad=None, w_pad=None, rect=None):
        """
        Apply a tight layout adjustment to a figure *once*,
        and prevent it from re-triggering on interactive updates.

        Parameters
        ----------
        fig : matplotlib.figure.Figure
            The figure to adjust.
        pad, h_pad, w_pad, rect : float or None
            Same parameters as Figure.tight_layout.
        """
        # Perform a manual tight_layout calculation
        self.parent.update()
        self.fig.tight_layout(pad=pad, h_pad=h_pad, w_pad=w_pad, rect=rect)

        # Disconnect automatic layout managers to prevent future updates
        self.fig.set_tight_layout(False) # noqa
        self.fig.set_constrained_layout(False) # noqa

        # Freeze subplot parameters so that resizing or zooming won’t retrigger layout
        self.fig.subplots_adjust(left=self.fig.subplotpars.left, right=self.fig.subplotpars.right, bottom=self.fig.subplotpars.bottom, top=self.fig.subplotpars.top, wspace=self.fig.subplotpars.wspace, hspace=self.fig.subplotpars.hspace)
        self.canvasp.draw_idle()

    def reset_view(self):
        for _ in range(len(self.action_list_undo)):
            self.undo_action()

    def collection_construction(self, solution_x, departure_time, duration_service, table_conversion, km_service, origins, destinies, conditioned_successors, banned_successors, str_departures, str_arrivals, dict_color, solution_maintenance, solution_linkers, info_linkers, transfers, sleepers, iniservices, multiple_next_m_name=None, multiple_next_m_duration=None, multiple_km_limit=None):
        base_s_collection = {}
        base_t_collection = {}
        for s in range(len(solution_x)):
            base_s_collection['s' + str(s + 1)] = [
                [departure_time[s], self.refypos - solution_x[s].index(max(solution_x[s]))], # 0
                duration_service[s], # 1
                table_conversion[s], # 2
                km_service[s], # 3
                origins[s], # 4
                destinies[s], # 5
                conditioned_successors[s], # 6
                str_departures[s], # 7
                str_arrivals[s], # 8
                dict_color[s], # noqa 9
                banned_successors[s] # 10
            ]

        for s in range(self.numtrains):
            if '-Depot' in iniservices['iniservice' + str(s+1)]['destiny']:
                depot = base_s_collection['s' + str(s + 1)][4]
                base_s_collection['s' + str(s + 1)][4] += lang.DEPOT_MAINTENANCE if lang.CHECK_MAINTENANCE in iniservices['iniservice' + str(s+1)]['destiny'] else lang.DEPOT_OVERNIGHT
                base_s_collection['s' + str(s + 1)][5] += lang.DEPOT_MAINTENANCE if lang.CHECK_MAINTENANCE in iniservices['iniservice' + str(s+1)]['destiny'] else lang.DEPOT_OVERNIGHT

                next_service = min([i for i in base_s_collection if base_s_collection[i][0][1] == self.refypos - s and base_s_collection['s' + str(s + 1)][0][0] < base_s_collection[i][0][0]], key=lambda item: base_s_collection[item][0][0], default=None)
                if next_service is None: # Not usual; train blocked in depot beyond horizon, so next service does not exist
                    next_service_departure = duration_service[s]
                    if lang.CHECK_MAINTENANCE in iniservices['iniservice' + str(s + 1)]['destiny']:
                        next_service_departure += transfers[depot]['duration'] / 60
                    elif lang.CHECK_OVERNIGHT in iniservices['iniservice' + str(s + 1)]['destiny']:
                        next_service_departure += sleepers[depot]['duration'] / 60
                else: # General case
                    next_service_departure = base_s_collection[next_service][0][0]

                l = len(base_t_collection)
                # TODO CASO RARO, aunque algo negligente mas por parte del usuario q mia si llega a ser relevante. Su corrección es además dura: Si un tren estuviera al inicio en depot mantenimiento, y la aplicación decidiera que va a mantenimiento del tiron, no hay que ponerle ni paso de entrada ni de salida. Bastaría con el paso de salida que se añade aquí en la comprobación de los iniservices, pero hay que asegurarse que a ese mantenimiento no se le añaden luego sus pasos correspondientes en la sección genérica, pues ya tenemos lo que queremos
                # TODO el usuario debería o poner que aun no esta en depot, o poner que esta en depot pero ya bloqueado, con su nota de mtto.
                if lang.CHECK_MAINTENANCE in iniservices['iniservice' + str(s+1)]['destiny']:
                    real_depot = depot
                    if ' < ' in transfers[depot]['location']:
                        real_depot = transfers[depot]['location'].split(' < ')[1]

                    base_t_collection['l' + str(l + 1)] = [[next_service_departure - transfers[depot]['duration'] / 60, self.refypos - s],  # 0
                                                           transfers[depot]['duration'] / 60,  # 1
                                                           transfers[depot]['id_from'],  # 2
                                                           transfers[depot]['kilometers'],  # 3
                                                           depot + lang.DEPOT_MAINTENANCE,  # 4
                                                           depot,  # 5
                                                           transfers[depot]['color'],  # 6
                                                           real_depot, # 7 Extra-auxiliar for linkers; real location
                                                           True,  # 8 Extra-auxiliar for linkers; indicator for maintenance
                                                           next_service_departure,  # 9 Extra-auxiliar for linkers; parameter
                                                           'l',  # -1
                                                           ]  # Service with bans and successors as empty

                elif lang.CHECK_OVERNIGHT in iniservices['iniservice' + str(s+1)]['destiny']:
                    real_depot = depot
                    if ' < ' in sleepers[depot]['location']:
                        real_depot = sleepers[depot]['location'].split(' < ')[1]

                    base_t_collection['l' + str(l + 1)] = [[next_service_departure - sleepers[depot]['duration'] / 60, self.refypos - s],  # 0
                                                           sleepers[depot]['duration'] / 60,  # 1
                                                           sleepers[depot]['id_from'],  # 2
                                                           sleepers[depot]['kilometers'],  # 3
                                                           depot + lang.DEPOT_OVERNIGHT,  # 4
                                                           depot,  # 5
                                                           sleepers[depot]['color'],  # 6
                                                           real_depot,  # 7 Extra-auxiliar for linkers; location
                                                           False,   # 8 Extra-auxiliar for linkers; indicator for overnight
                                                           next_service_departure,  # 9 Extra-auxiliar for linkers; parameter
                                                           'l',  # -1
                                                           ]  # Service with bans and successors as empty

        rows, cols = np.where(solution_linkers >= 0)
        append_to_t_collection = []
        maintenance_transfer_defined = np.zeros(solution_maintenance.shape, dtype=bool)
        # TODO los transfer de arriba podrían querer tener otras ubicaciones de destino, pues podría darse el caso de que fueran pasos. Aunque luego abajo se les hace referencia, a ver que les pasa
        for i in range(rows.size):
            train_idx = rows[i]
            service_idx = cols[i]
            print('SERV', service_idx, base_s_collection['s' + str(service_idx + 1)][0][1], base_s_collection['s' + str(service_idx + 1)][0][0], base_s_collection['s' + str(service_idx + 1)][2])
            linker_idx = solution_linkers[train_idx, service_idx]

            earliest_linker_departure = max(departure_time[service_idx] + duration_service[service_idx], info_linkers[linker_idx]['opening-time'])
            depot = destinies[service_idx]
            real_depot = transfers[depot]['location'].split(' < ')[1] if ' < ' in transfers[depot]['location'] else transfers[depot]['location']
            dependency = True if ' < ' in transfers[depot]['location'] else False
            # Next service will always exist, as a linker is never placed after the last service of a train
            next_service = min([x for x in base_s_collection if base_s_collection[x][0][1] == self.refypos - train_idx and departure_time[service_idx] < base_s_collection[x][0][0]], key=lambda item: base_s_collection[item][0][0], default=None)
            next_service_departure = base_s_collection[next_service][0][0]
            next_location = base_s_collection[next_service][4]

            for j in range(solution_maintenance[train_idx].size):
                if solution_maintenance[train_idx, j] > 0 and departure_time[service_idx] <= solution_maintenance[train_idx, j] <= next_service_departure:
                    # If left depot is a master depot. Right will not be considered, since the capacity and kilometers evaluation of that depot is not evaluated unless some dependency exists
                    if not dependency:
                        # Right depot depends on left. Create t/s_collection with: "TO" as usual (transfers[depot]), "FROM" uses transfer[next_location] with transfer[depot]'s depot as origin.
                        if ' < ' in transfers[next_location]['location'] and transfers[next_location]['location'].split(' < ')[1] == depot:
                            # Possible to do maintenance before the linker.  USES LINKER ID in "FROM"
                            if solution_maintenance[train_idx, j] + multiple_next_m_duration[train_idx, j] + (transfers[depot]['duration'] / 60) <= info_linkers[linker_idx]['ending-time']:
                                id_from = info_linkers[linker_idx]['id']
                                color_from = info_linkers[linker_idx]['color']
                                from_departure_time = min(info_linkers[linker_idx]['ending-time'], next_service_departure - transfers[next_location]['duration'] / 60)

                            #  Skip linker ID
                            else:
                                id_from = transfers[next_location]['id_from']
                                color_from = transfers[next_location]['color']
                                from_departure_time = next_service_departure - transfers[next_location]['duration'] / 60

                            append_to_t_collection.append([[departure_time[service_idx] + duration_service[service_idx], self.refypos - train_idx],  # 0
                                                           transfers[depot]['duration'] / 60,  # 1
                                                           transfers[depot]['id_to'],  # 2
                                                           transfers[depot]['kilometers'],  # 3
                                                           depot,  # 4
                                                           depot + lang.DEPOT_MAINTENANCE,  # 5
                                                           transfers[depot]['color'],  # 6
                                                           'l',  # -1
                                                           ])

                            append_to_t_collection.append([[from_departure_time, self.refypos - train_idx],  # 0
                                                           transfers[next_location]['duration'] / 60,  # 1
                                                           id_from,  # 2
                                                           transfers[next_location]['kilometers'],  # 3
                                                           depot + lang.DEPOT_MAINTENANCE,  # 4
                                                           next_location,  # 5
                                                           color_from,  # 6
                                                           'l',  # -1
                                                           ])

                            # Avoids duplication of transfers
                            maintenance_transfer_defined[train_idx, j] = 1
                            break


                        # Right location cannot be considered for maintenance (No depot, or depot constraints not evaluated). Create t/s_collection with: "TO" as usual (transfers[depot]), "FROM" uses the sum of KMs and DURATION of transfers[depot] and the info_linkers
                        else:
                            # Inside bounds? -> Using LINKER ID
                            if solution_maintenance[train_idx, j] + multiple_next_m_duration[train_idx, j] + 2 * (transfers[depot]['duration'] / 60) <= info_linkers[linker_idx]['ending-time']:
                                id_from = info_linkers[linker_idx]['id']
                                color_from = info_linkers[linker_idx]['color']
                                from_departure_time = min(next_service_departure - info_linkers[linker_idx]['duration'] - (transfers[depot]['duration'] / 60), info_linkers[linker_idx]['ending-time'])

                            # Out of bounds? -> No LINKER ID
                            else:
                                id_from = transfers[depot]['id_from'] + ' - ' + next_location
                                color_from = transfers[depot]['color']
                                from_departure_time = next_service_departure - info_linkers[linker_idx]['duration'] - (transfers[depot]['duration'] / 60)

                            append_to_t_collection.append([[departure_time[service_idx] + duration_service[service_idx], self.refypos - train_idx],  # 0
                                                           transfers[depot]['duration'] / 60,  # 1
                                                           transfers[depot]['id_to'],  # 2
                                                           transfers[depot]['kilometers'],  # 3
                                                           depot,  # 4
                                                           depot + lang.DEPOT_MAINTENANCE,  # 5
                                                           transfers[depot]['color'],  # 6
                                                           'l',  # -1
                                                           ])

                            append_to_t_collection.append([[from_departure_time, self.refypos - train_idx],  # 0
                                                           (transfers[depot]['duration'] / 60) + info_linkers[linker_idx]['duration'],  # 1
                                                           id_from,  # 2
                                                           transfers[depot]['kilometers'] + info_linkers[linker_idx]['kilometers'],  # 3
                                                           depot + lang.DEPOT_MAINTENANCE,  # 4
                                                           next_location,  # 5
                                                           color_from,  # 6
                                                           'l',  # -1
                                                           ])

                            # Avoids duplication of transfers
                            maintenance_transfer_defined[train_idx, j] = 1
                            break

                    else: # Left depot is dependent
                        # left depot is dependent on the right. Create t/s_collection with: "TO" using transfers[depot] parameters with transfers[next_locations] depot's as destiny and "FROM" as usual (transfers[next_location]).
                        if real_depot == next_location:
                            # The linker can be done as early as possible and the mainteance after it.  USES LINKER ID in "TO"
                            if earliest_linker_departure + transfers[depot]['duration'] / 60 + transfers[next_location]['duration'] / 60 + multiple_next_m_duration[train_idx, j] <= next_service_departure:
                                id_to = info_linkers[linker_idx]['id']
                                color_to = info_linkers[linker_idx]['color']
                                to_departure_time = earliest_linker_departure
                                solution_maintenance[train_idx, j] = earliest_linker_departure + transfers[depot]['duration'] / 60

                            # left depot is dependent on the right, but the linker's earliest time would make maintenance infeasible (linker is too late). The latest, with maintenance before makes no sense.  Skip linker ID
                            else:
                                id_to = transfers[depot]['id']
                                color_to = transfers[depot]['color']
                                to_departure_time = departure_time[service_idx] + duration_service[service_idx]

                            append_to_t_collection.append([[to_departure_time, self.refypos - train_idx],  # 0
                                                           transfers[depot]['duration'] / 60,  # 1
                                                           id_to,  # 2
                                                           transfers[depot]['kilometers'],  # 3
                                                           depot,  # 4
                                                           next_location + lang.DEPOT_MAINTENANCE,  # 5
                                                           color_to,  # 6
                                                           'l',  # -1
                                                           ])

                            append_to_t_collection.append([[next_service_departure - (transfers[next_location]['duration'] / 60), self.refypos - train_idx],  # 0
                                                           (transfers[next_location]['duration'] / 60),  # 1
                                                           transfers[next_location]['id_from'],  # 2
                                                           transfers[next_location]['kilometers'],  # 3
                                                           next_location + lang.DEPOT_MAINTENANCE,  # 4
                                                           next_location,  # 5
                                                           transfers[next_location]['color'],  # 6
                                                           'l',  # -1
                                                           ])

                            # Avoids duplication of transfers
                            maintenance_transfer_defined[train_idx, j] = 1
                            break

                        # Right lcoation cannot be considered for maintenance. Linker does not depend on right, and its capacity and transfer's kms are not being considered so we won't do maintenance there. Create t/s_collection with: "TO" as usual (transfers[depot]), "FROM" uses the sum of KMs and DURATION of transfers[depot] and the info_linkers
                        else: # TODO the equivalent to this else statement in the upper major block is identical, so an if, elif and else trio would reduce the amount of elements
                            # Inside bounds? -> Using LINKER ID
                            if solution_maintenance[train_idx, j] + multiple_next_m_duration[train_idx, j] + 2 * transfers[depot]['duration'] / 60 <= info_linkers[linker_idx]['ending-time']:
                                id_from = info_linkers[linker_idx]['id']
                                color_from = info_linkers[linker_idx]['color']
                                from_departure_time = min(next_service_departure - info_linkers[linker_idx]['duration'] - (transfers[depot]['duration'] / 60), info_linkers[linker_idx]['ending-time'])

                            # Out of bounds? -> No LINKER ID
                            else:
                                id_from = transfers[depot]['id_from'] + ' - ' + next_location
                                color_from = transfers[depot]['color']
                                from_departure_time = next_service_departure - (transfers[depot]['duration'] / 60) - info_linkers[linker_idx]['duration']

                            append_to_t_collection.append([[departure_time[service_idx] + duration_service[service_idx], self.refypos - train_idx],  # 0
                                                           transfers[depot]['duration'] / 60,  # 1
                                                           transfers[depot]['id_to'],  # 2
                                                           transfers[depot]['kilometers'],  # 3
                                                           depot,  # 4
                                                           depot + lang.DEPOT_MAINTENANCE,  # 5
                                                           transfers[depot]['color'],  # 6
                                                           'l',  # -1
                                                           ])

                            append_to_t_collection.append([[from_departure_time, self.refypos - train_idx],  # 0
                                                           (transfers[depot]['duration'] / 60) + info_linkers[linker_idx]['duration'],  # 1
                                                           id_from,  # 2
                                                           transfers[depot]['kilometers'] + info_linkers[linker_idx]['kilometers'],  # 3
                                                           depot + lang.DEPOT_MAINTENANCE,  # 4
                                                           next_location,  # 5
                                                           color_from,  # 6
                                                           'l',  # -1
                                                           ])

                            # Avoids duplication of transfers
                            maintenance_transfer_defined[train_idx, j] = 1
                            break

            else: # No maintenance invloved within the linker's gap, just create as normal
                if service_idx < self.numtrains:  # If iniservice, a depot transfer might already have been defined, so it should be considered.
                    print('Service match (natural index)', service_idx, base_s_collection['s' + str(service_idx+1)])
                    for transfer in base_t_collection:
                        if base_t_collection[transfer][0][1] == self.refypos - train_idx:
                            print('Transfer match (inversed index, natural index)', self.refypos - train_idx, train_idx)
                            # Using a forwarded depot. is the linker also going to forwarder? Then, change transfer/sleeper parameters and skip.
                            if base_t_collection[transfer][7] != base_t_collection[transfer][5] and base_t_collection[transfer][7] == info_linkers[linker_idx]['destiny']:
                                print('Debug verifier 1', base_t_collection[transfer][7], info_linkers[linker_idx]['destiny'])
                                ref = transfers if base_t_collection[transfer][8] else sleepers
                                real_depot = base_t_collection[transfer][7]

                                if earliest_linker_departure + (ref[real_depot]['duration'] / 60) <= next_service_departure and earliest_linker_departure <= info_linkers[linker_idx]['ending-time']:
                                    linker_start = earliest_linker_departure
                                    linker_id = info_linkers[linker_idx]['id']
                                else:
                                    linker_start = next_service_departure - ref[real_depot]['duration'] / 60
                                    linker_id = ref[real_depot]['id_from']

                                base_t_collection[transfer] = [[linker_start, self.refypos - train_idx],  # 0
                                                               ref[real_depot]['duration'] / 60,  # 1
                                                               linker_id,  # 2
                                                               ref[real_depot]['kilometers'],  # 3
                                                               base_t_collection[transfer][4],  # 4
                                                               info_linkers[linker_idx]['destiny'],  # 5
                                                               info_linkers[linker_idx]['color'],  # 6
                                                               't',  # -1
                                                               ]
                            # No forwarded depot. Aggregate durations, kms and IDs
                            else:
                                ref = transfers if base_t_collection[transfer][8] else sleepers
                                if earliest_linker_departure + info_linkers[linker_idx]['duration'] <= next_service_departure and earliest_linker_departure <= info_linkers[linker_idx]['ending-time']:
                                    linker_start = earliest_linker_departure
                                    linker_id = info_linkers[linker_idx]['id']
                                else:
                                    linker_start = next_service_departure - (ref[depot]['duration'] / 60) - info_linkers[linker_idx]['duration']
                                    linker_id = base_t_collection[transfer][2]

                                base_t_collection[transfer][0][0] = linker_start
                                base_t_collection[transfer][1] = info_linkers[linker_idx]['duration'] + (ref[depot]['duration'] / 60)
                                base_t_collection[transfer][2] = linker_id
                                base_t_collection[transfer][3] = info_linkers[linker_idx]['kilometers'] + ref[depot]['kilometers']
                                base_t_collection[transfer][5] = info_linkers[linker_idx]['destiny']
                                base_t_collection[transfer][6] = info_linkers[linker_idx]['color']
                                base_t_collection[transfer][-1] = 't'

                            # Only up to one transfer exists per train, as the others are being created ina  different variable
                            break

                    else: # Iniservice, but no transfers or overnights
                        append_to_t_collection.append([[earliest_linker_departure, self.refypos - train_idx],  # 0
                                                       info_linkers[linker_idx]['duration'],  # 1
                                                       info_linkers[linker_idx]['id'],  # 2
                                                       info_linkers[linker_idx]['kilometers'],  # 3
                                                       info_linkers[linker_idx]['origin'],  # 4
                                                       info_linkers[linker_idx]['destiny'],  # 5
                                                       info_linkers[linker_idx]['color'],  # 6
                                                       't',  # -1
                                                       ])

                # No iniservice, and no maintenance. Just create linker
                else:
                    append_to_t_collection.append([[earliest_linker_departure, self.refypos - train_idx],  # 0
                                                                   info_linkers[linker_idx]['duration'],  # 1
                                                                   info_linkers[linker_idx]['id'],  # 2
                                                                   info_linkers[linker_idx]['kilometers'],  # 3
                                                                   info_linkers[linker_idx]['origin'],  # 4
                                                                   info_linkers[linker_idx]['destiny'],  # 5
                                                                   info_linkers[linker_idx]['color'],  # 6
                                                                   't', # -1
                                                                   ])




        auxs = {}
        s = 0
        for serv in sorted(base_s_collection.items(), key=lambda item: item[1][0][0]):
            s += 1
            auxs['s' + str(s)] = serv[1]
        base_s_collection = deepcopy(auxs)

        for el in append_to_t_collection:
            base_t_collection['l' + str(len(base_t_collection) + 1)] = el
        auxs = {}

        l = 0
        for el in sorted(base_t_collection.items(), key=lambda item: item[1][0][0]):
            l += 1
            base_name = 'l' if 'l' == el[1][-1] else 't'
            auxs[base_name + str(l)] = el[1]
        base_t_collection = deepcopy(auxs)

        base_m_collection = {}
        m = 0
        train_accu_km = [0] * self.numtrains
        prev_maint_finish = [0] * self.numtrains
        st_collection = dict(sorted((base_s_collection | base_t_collection).items(), key=lambda item: item[1][0][0]))
        for t in range(solution_maintenance.shape[0]):
            for j in range(solution_maintenance.shape[1]):
                if solution_maintenance[t, j]:
                    for service in [service for service in st_collection if st_collection[service][0][1] == self.refypos - t]:
                        if solution_maintenance[t, j] >= st_collection[service][0][0] and st_collection[service][0][0] >= prev_maint_finish[t]:
                            train_accu_km[t] += st_collection[service][3]
                    m += 1
                    base_m_collection['m' + str(m)] = [
                    [solution_maintenance[t, j], self.refypos - t], # 0
                    multiple_next_m_duration[t, j], # 1
                    multiple_next_m_name[t, j], # 2
                    'Km: ' + str(train_accu_km[t]), # 3
                    train_accu_km[t], # 4
                    multiple_km_limit[t, j] # 5
                    ]
                    train_accu_km[t] = 0
                    prev_maint_finish[t] = solution_maintenance[t, j] + multiple_next_m_duration[t, j]

                    if maintenance_transfer_defined[t, j]:
                        continue

                    # Which depot?
                    depot = None
                    depot_serv = None
                    for service in base_s_collection:
                        if base_s_collection[service][0][1] == self.refypos - t:
                            if base_s_collection[service][0][0] <= solution_maintenance[t, j]:
                                depot = base_s_collection[service][5]
                                # depot = base_s_collection[service][5] if not lang.DEPOT_MAINTENANCE in base_s_collection[service][5] else base_s_collection[service][5].replace(lang.DEPOT_MAINTENANCE, '')
                                # depot = base_s_collection[service][5] if not lang.DEPOT_OVERNIGHT in base_s_collection[service][5] else base_s_collection[service][5].replace(lang.DEPOT_MAINTENANCE, '')
                                depot_serv = service
                            else:
                                break

                    # Transfers
                    if not '-Depot' in depot :
                        l = len(base_t_collection)
                        # Transfer to depot for maintenance
                        base_t_collection['l' + str(l + 1)] = [[base_s_collection[depot_serv][0][0] + base_s_collection[depot_serv][1], self.refypos - t],  # 0
                           transfers[depot]['duration'] / 60,  # 1
                           transfers[depot]['id_to'],  # 2
                           transfers[depot]['kilometers'],  # 3
                           depot,  # 4
                           depot + lang.DEPOT_MAINTENANCE,  # 5
                           transfers[depot]['color'],  # 6
                       ]  # Service with bans and successors as empty

                    else: # Make sure that the previous element is finishing in the correct depot (the maintenance subdepot)
                        depot = depot if not lang.DEPOT_MAINTENANCE in depot else depot.replace(lang.DEPOT_MAINTENANCE, '')
                        depot = depot if not lang.DEPOT_OVERNIGHT in depot else depot.replace(lang.DEPOT_OVERNIGHT, '')
                        base_s_collection[depot_serv][5] = depot + lang.DEPOT_MAINTENANCE

                    # Transfer from depot after maintenance
                    services_to_search = [serv for serv in sorted(base_s_collection, key=lambda item: base_s_collection[item][0][0]) if base_s_collection[serv][0][1] == self.refypos - t and base_s_collection[serv][0][0] >= solution_maintenance[t, j]]
                    if len(services_to_search) > 0:
                        next_serv = min(services_to_search, key=lambda item: base_s_collection[item][0][0])
                        numerical_base = base_s_collection[next_serv][0][0] - transfers[depot]['duration'] / 60
                    else:
                        numerical_base = solution_maintenance[t, j] + multiple_next_m_duration[t, j]

                    depot = depot if not lang.DEPOT_OVERNIGHT in depot else depot.replace(lang.DEPOT_OVERNIGHT, '')
                    l = len(base_t_collection)
                    base_t_collection['l' + str(l + 1)] = [[numerical_base, self.refypos - t],  # 0
                       transfers[depot]['duration'] / 60,  # 1
                       transfers[depot]['id_from'],  # 2
                       transfers[depot]['kilometers'],  # 3
                       depot + lang.DEPOT_MAINTENANCE,  # 4
                       depot,  # 5
                       transfers[depot]['color'],  # 6
                   ]  # Service with bans and successors as empty

        tmax = max([departure_time[i] + duration_service[i] for i in range(self.numtrains, len(departure_time))] + [solution_maintenance[t, j] + multiple_next_m_duration[t, j] for t in range(solution_maintenance.shape[0]) for j in range(solution_maintenance.shape[1]) if solution_maintenance[t, j] > 0])

        # Sleepers
        checked_depots = []
        util_sleepers = util_sleepers_creation(sleepers, self.starting_day, tmax)
        for depot in util_sleepers:
            if depot in checked_depots:
                continue

            current_depots = []
            target_capacity_depot = None
            for other_depot in util_sleepers:
                if other_depot == depot:
                    if other_depot not in current_depots:
                        current_depots.append(other_depot)
                        checked_depots.append(other_depot)
                    if target_capacity_depot is None:
                        target_capacity_depot = other_depot

                elif depot == util_sleepers[other_depot]['forward_capacity']:
                    if other_depot not in current_depots:
                        current_depots.append(other_depot)
                        checked_depots.append(other_depot)
                    target_capacity_depot = depot

                elif other_depot == util_sleepers[depot]['forward_capacity']:
                    if other_depot not in current_depots:
                        current_depots.append(other_depot)
                        checked_depots.append(other_depot)
                    target_capacity_depot = other_depot

            for day in range(ceil(tmax / 24)):
                st_collection = dict(sorted((base_s_collection | base_t_collection).items(), key=lambda item: item[1][0][0]))
                # last_service = [None] * self.numtrains
                successor_service = [None] * self.numtrains
                last_location = [None] * self.numtrains
                when_to_go = [None] * self.numtrains
                eligible_sleeper = [True] * self.numtrains

                for t in range(self.numtrains):
                    for service in st_collection:
                        if t == st_collection[service][0][1]:
                            if st_collection[service][0][0] < (day + 1) * 24:
                                last_location[t] = st_collection[service][5] if 'l' not in service else (st_collection[service][5] if '-Depot' in st_collection[service][5] else st_collection[service][4]) # A linker with premature leaving but no services after? Stay in depot
                                when_to_go[t] = st_collection[service][0][0] + st_collection[service][1]
                                if when_to_go[t] > util_sleepers[target_capacity_depot]['nightblock'] + day * 24:
                                    eligible_sleeper[t] = False
                            elif st_collection[service][0][0] >= (day + 1) * 24:
                                break

                    if last_location[t] in {c + suf for c in current_depots for suf in (lang.DEPOT_MAINTENANCE, lang.DEPOT_OVERNIGHT)}:
                        eligible_sleeper[t] = False

                    if last_location[t] not in current_depots:
                        eligible_sleeper[t] = False

                    if not eligible_sleeper[t]:
                        continue

                    checker_next_service = {}
                    for service in st_collection:
                        if t == st_collection[service][0][1] and st_collection[service][0][0] > when_to_go[t]:
                            checker_next_service[service] = st_collection[service]
                    if len(checker_next_service) > 0:
                        next_service = min(checker_next_service, key=lambda item: checker_next_service[item][0][0])
                        if st_collection[next_service][0][0] < (day + 1) * 24 + util_sleepers[target_capacity_depot]['morningblock'] or 'l' in next_service:
                            eligible_sleeper[t] = False
                        else:
                            successor_service[t] = next_service
                    else:
                        eligible_sleeper[t] = False

                # Final step: sort eligible sleepers by their when_to_go and add them until reaching capacity, respecting km coounters for maintenance
                suffixes = (lang.DEPOT_MAINTENANCE, lang.DEPOT_OVERNIGHT)
                depot_positions = {c + s for c in current_depots for s in suffixes}
                occupations = sum([1 if item in depot_positions else 0 for item in last_location])
                sorted_indices = [i for i, _ in sorted([(i, when_to_go[i]) for i, val in enumerate(eligible_sleeper) if val], key=lambda x: x[1])]

                # liberations = []
                # for t in range(self.numtrains):
                #     if '-Depot' not in last_location[t]:
                #         for transfer in base_t_collection:
                #             if base_t_collection[transfer][0][1] == t and base_t_collection[transfer][5] == depot:
                #                 if base_t_collection[transfer][0][0] <= (day + 1) * 24:

                while occupations < util_sleepers[target_capacity_depot]['week'][day] and len(sorted_indices) > 0:
                    occupations += 1
                    train = sorted_indices.pop(0)
                    position: str = last_location[train]

                    next_maint = min([m for m in base_m_collection if base_m_collection[m][0][1] == train and base_m_collection[m][0][0] > when_to_go[train]], key=lambda item: base_m_collection[item][0][0], default=False)
                    if next_maint:
                        topline = base_m_collection[next_maint][0][0]
                        prev_maint = max([m for m in base_m_collection if base_m_collection[m][0][1] == train and base_m_collection[m][0][0] < when_to_go[train]], key=lambda item: base_m_collection[item][0][0], default=False)

                        if not prev_maint:
                            baseline = 0
                        else:
                            baseline = base_m_collection[prev_maint][0][0]

                        real_km = sum([st_collection[serv][3] for serv in st_collection if baseline <= st_collection[serv][0][0] < topline and st_collection[serv][0][1] == train])
                        if real_km + 2 * int(util_sleepers[position]['kilometers']) >= base_m_collection[next_maint][5]:
                            occupations -= 1
                            continue

                    # Transfers
                    l = len(base_t_collection)
                    # Transfer to depot for sleeping
                    base_t_collection['l' + str(l + 1)] = [[when_to_go[train], train],  # 0
                                                           float(util_sleepers[position]['duration']) / 60,  # 1
                                                           util_sleepers[position]['id_to'],  # 2
                                                           int(util_sleepers[position]['kilometers']),  # 3
                                                           position,  # 4
                                                           position + lang.DEPOT_OVERNIGHT,  # 5
                                                           util_sleepers[position]['color'],  # 6
                                                           ]  # Service with bans and successors as empty

                    # Transfer from depot after sleeping
                    if successor_service[train] != None:
                        base_t_collection['l' + str(l + 2)] = [[st_collection[successor_service[train]][0][0] - float(util_sleepers[position]['duration']) / 60, train],  # 0
                                                               float(util_sleepers[position]['duration']) / 60,  # 1
                                                               util_sleepers[position]['id_from'],  # 2
                                                               int(util_sleepers[position]['kilometers']),  # 3
                                                               position + lang.DEPOT_OVERNIGHT,  # 4
                                                               position,  # 5
                                                               util_sleepers[position]['color'],  # 6
                                                               ]  # Service with bans and successors as empty

        return base_s_collection, base_m_collection, base_t_collection

    def format_coord(self, x, y):
        if self.nightstarttime > 0 and int(x/24) == 0 and self.nightendtime > int(x/24):
            emojicode = '\U0001F319' # noqa
        if self.nightstarttime + 24*int(x/24) <= 24*int(x/24) + int(x%24) < self.nightendtime + 24*int(x/24): # Moon
            emojicode = '\U0001F319'
        else: # Sun
            emojicode = '\u2600'

        minutes = '0' + str(int((x % 24 % 1) * 60)) if int((x % 24 % 1) * 60) < 10 else str(int((x % 24 % 1) * 60))
        time = emojicode + str(int(x % 24)) + ':' + minutes
        train = self.trainid['train' + str(int(self.numtrains - int(y)))] if y < self.numtrains else ''
        return lang.cc9 + str(time) + lang.cc10 + str(train)

    def canvas_construction(self, s_collection, m_collection, t_collection):
        self.fig = Figure()

        self.ax = self.fig.add_subplot(1, 1, 1)
        self.s_collection = []
        self.m_collection = []
        self.t_collection = []

        # get last hour, will be used for fontsize and str_week purposes
        max_services = max([s_collection[service][0][0] + s_collection[service][1] for service in s_collection]) if len(s_collection) > 0 else 0
        max_maints = max([m_collection[maint][0][0] + m_collection[maint][1] for maint in m_collection]) if len(m_collection) > 0 else 0
        self.last_hour = int(ceil(max(max_services,  max_maints)))
        if self.last_hour <= 192:
            self.masterfontsize = 8
        elif 192 < self.last_hour <= 250:
            self.masterfontsize = 7
        else:
            self.masterfontsize = 6

        for service in s_collection:
            self.s_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=s_collection[service][0], height=0.5, width=s_collection[service][1], name=s_collection[service][2], ticket='S', origin=s_collection[service][4], destiny=s_collection[service][5], conditioned_successor=s_collection[service][6], banned_successors=s_collection[service][10], departure_time=s_collection[service][7], arrival_time=s_collection[service][8], kmservice=s_collection[service][3], facecolor=s_collection[service][9], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.6))
            self.ax.add_patch(self.s_collection[-1].polygon)
            self.s_collection[-1].connect()

        for maint in m_collection:
            self.m_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=m_collection[maint][0], height=0.5, width=m_collection[maint][1], name=m_collection[maint][2], ticket='M', hmovement=True, mtext=m_collection[maint][3], kmservice=m_collection[maint][4], kmlimit=m_collection[maint][5], facecolor=settings.MAINTENANCE_COLOR, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.5))
            self.ax.add_patch(self.m_collection[-1].polygon)
            self.m_collection[-1].connect()

        for transfer in t_collection:
            self.t_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=t_collection[transfer][0], height=0.5, width=t_collection[transfer][1], name=t_collection[transfer][2], ticket='T', hmovement=True, origin=t_collection[transfer][4], destiny=t_collection[transfer][5], conditioned_successor='', banned_successors=[], kmservice=t_collection[transfer][3], facecolor=t_collection[transfer][6], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.7))
            self.ax.add_patch(self.t_collection[-1].polygon)
            self.t_collection[-1].connect()

    def __str_week_creation__(self):
        self.str_week = lang.FULL_WEEK
        current = datetime.now().isoweekday() - 1 if self.starting_day == lang.CURRENT else self.str_week.index(self.starting_day)

        self.str_week = self.str_week[current:] + self.str_week[:current]

        if self.last_hour >= 168:
            base = 2
            suffix = ' #' + str(base)
            i = 0
            for _ in range(int(self.last_hour / 24) + 1 - 7):
                if i == 7:
                    i = 0
                    base += 1
                    suffix = ' #' + str(base)

                self.str_week.append(self.str_week[i] + suffix)
                i += 1

    def canvas_customisation(self, create_toolbar=False): # TODO creo que ahora mismo muchas de las llamadas que se hacen a esta funcion son innecesarias, y bastaría con un canvas.draw() o canvas.draw_idle()
        # Create str_week
        self.__str_week_creation__()

        # set xlim and ylim
        self.ax.set_xlim(0, self.last_hour)
        self.ax.set_ylim(0, self.numtrains + settings.EXTRA_ROWS)
        self.ax.set_facecolor(dispcolour.DISP_BACKGROUND)

        # define xticks (time-lapses) # TODO add to configuration tab in startmenu? May need to check the "night color-change"
        multiple = 6 # 6 because of 3 * 2, using * 2 to reduce the amount of labels # TODO add to configuration tab in startmenu? May need to check the "night color-change"
        tick_labels = []
        for i in range(self.last_hour):
            if not i % multiple:
                tick_labels.append(str(int(i % 24)) + ':00')
            elif not i % 3:
                tick_labels.append('')

        self.ax.set_xticks(list(range(0, self.last_hour, 3)), labels=tick_labels, fontsize=8)
        self.ax.set_xticks(list(range(0, self.last_hour, 1)), minor=True)

        # Also, clear distinction between days
        self.ax.vlines(list(range(0, self.last_hour, 24)), 0, self.numtrains + settings.EXTRA_ROWS, linewidth=2, colors=dispcolour.DISP_VERTTHICKLINE, zorder=2.01)

        try: # TODO Is keyword create_toolbar a valid workaround to avoid using try/except blocks?
            for day in self.days_text: # noqa
                day.remove()
            del self.days_text # noqa
        except:
            pass

        day = -1
        self.days_text = []
        for i in range(0, self.last_hour, 24):
            day += 1
            self.days_text.append(self.ax.text(i, self.numtrains + settings.EXTRA_ROWS + 0.2, self.str_week[day], fontsize=8, fontfamily='monospace', color=dispcolour.DISP_TEXTS))

        # Ticks config
        self.ax.yaxis.tick_right()
        self.ax.yaxis.set_ticks_position('both')

        # Grid config
        self.ax.grid(axis='y', alpha=1, color=dispcolour.DISP_VERTMIDLINE)
        self.ax.grid(axis='x', which='minor', alpha=0.3, color=dispcolour.DISP_VERTTHINLINE)
        self.ax.grid(axis='x', which='major', alpha=1, color=dispcolour.DISP_VERTMIDLINE)

        # iterator = -1
        # daycolor = ['#ff8800', '#fff200', '#11d400', '#00fffb', '#9000ff', '#ff00a6', '#d62418']
        axis_unit_numtrains = self.numtrains / (self.numtrains + settings.EXTRA_ROWS)
        for i in range(0, int(self.last_hour), 24):
            # iterator = iterator + 1 if iterator < 6 else 0
            self.ax.axvspan(i, i + self.nightendtime, 0, axis_unit_numtrains, facecolor=dispcolour.DISP_NIGHTBACKGROUND, alpha=0.4, zorder=-100)
            self.ax.axvspan(i, i + self.nightendtime, axis_unit_numtrains, 1, facecolor=dispcolour.DISP_TOPNIGHTBACKGROUND, alpha=0.4, zorder=-100)
            if self.nightstarttime > 0:
                self.ax.axvspan(i + self.nightstarttime, i + 24, 0, axis_unit_numtrains, facecolor=dispcolour.DISP_NIGHTBACKGROUND, alpha=0.4, zorder=-100)
                self.ax.axvspan(i + self.nightstarttime, i + 24, axis_unit_numtrains, 1, facecolor=dispcolour.DISP_TOPNIGHTBACKGROUND, alpha=0.4, zorder=-100)

        self.ax.axhspan(self.numtrains, self.numtrains + settings.EXTRA_ROWS, facecolor=dispcolour.DISP_TOPDAYBACKGROUND, alpha=0.4, zorder=-101)
        # Customise coords label
        self.ax.format_coord = self.format_coord

        # Try best fitting
        # self.fig.set_tight_layout(True) # noqa
        # self.fig.set_constrained_layout(True) # noqa

        # Objeto con la FIGURA
        if create_toolbar:
            self.canvasp = FigureCanvasTkAgg(self.fig, master=self.parent)
            self.create_toolbar()
            self.canvasp._tkcanvas.pack(fill='both', expand=True)
            # self.canvasp._tkcanvas.place(relx=0.5, rely=0.5, anchor='center', relwidth=1, relheight=.95)
            self.highlighter = FastAreaSelector(self.ax, self)
            self.zoomandpan = ZoomPan(self.ax, factor=1.25)
        else:
            self.toolbar.update() # TODO will the live coordinates label work? Is this enough?

    def create_toolbar(self):
        # Barra de herramientas
        self.toolbar = NavigationToolbar2Tk(self.canvasp, self.parent)
        self.toolbar.children['!button4'].pack_forget()

        # self.toolbar.children['!checkbutton1'].pack_forget() Does not work, due to MPL bugs. Then, we have to...:
        for key in self.toolbar.children:
            if '!checkbutton' in key: # First checkbutton encountered; destroy and exit
                self.toolbar.children[key].pack_forget()
                break

        self.toolbar.children['!frame'].pack_forget()
        self.toolbar.children['!frame2'].pack_forget()

        self.horzbanbutton = Checkbutton(master=self.toolbar, variable=self.horzban, indicatoron=False, offrelief='flat', overrelief='groove', borderwidth=1)
        self.horzbanbutton.image = PhotoImage(file=relative_to_navtoolbarassets('horzbanbutton.png'))
        self.horzbanbutton.configure(image=self.horzbanbutton.image)
        self.horzbanbutton.pack(side="left", padx=2)
        ToolTip(self.horzbanbutton, lang.cc11)

        self.resetbutton = Button(master=self.toolbar, command=self.reset_view, relief='flat', overrelief='groove', borderwidth=1)
        self.resetbutton.image = PhotoImage(file=relative_to_navtoolbarassets('restartbutton.png'))
        self.resetbutton.configure(image=self.resetbutton.image, state='disabled') # Needs extra garbage collection and an image of 30x30
        self.resetbutton.pack(side="left", padx=2)
        ToolTip(self.resetbutton, lang.cc12)
        # Will be enabled by the registry modifier. Left for reference
        # self.parent.bind("<Control-Alt-R>", lambda event: self.reset_view())
        # self.parent.bind("<Control-Alt-r>", lambda event: self.reset_view())

        self.undobutton = Button(master=self.toolbar, command=self.undo_action, relief='flat', overrelief='groove', borderwidth=1)
        self.undobutton.image = PhotoImage(file=relative_to_navtoolbarassets('undobutton.png'))
        self.undobutton.configure(image=self.undobutton.image, state='disabled') # Needs extra garbage collection and an image of 30x30
        self.undobutton.pack(side="left", padx=2)
        ToolTip(self.undobutton, lang.cc13)
        # Will be enabled by the registry modifier. Left for reference
        # self.parent.bind("<Control-Z>", lambda event: self.undo_action())
        # self.parent.bind("<Control-z>", lambda event: self.undo_action())

        self.redobutton = Button(master=self.toolbar, command=self.redo_action, relief='flat', overrelief='groove', borderwidth=1)
        self.redobutton.image = PhotoImage(file=relative_to_navtoolbarassets('redobutton.png'))
        self.redobutton.configure(image=self.redobutton.image, state='disabled') # Needs extra garbage collection and an image of 30x30
        self.redobutton.pack(side="left", padx=2)
        ToolTip(self.redobutton, lang.cc14)
        # Will be enabled by the registry modifier. Left for reference
        # self.parent.bind("<Control-Y>", lambda event: self.redo_action())
        # self.parent.bind("<Control-y>", lambda event: self.redo_action())

        # self.updatebutton = Button(master=self.toolbar, command=self.update_plot, relief='flat', overrelief='groove', borderwidth=1)
        # self.updatebutton.image = PhotoImage(file=relative_to_navtoolbarassets('kmbutton.png'))
        # self.updatebutton.configure(image=self.updatebutton.image) # Needs extra garbage collection and an image of 30x30
        # self.updatebutton.pack(side="left", padx=2)
        # ToolTip(self.updatebutton, 'UpdateKm (Ctrl + U)\nUpdates km counters over maintenance boxes and at the end of the horizon')
        # self.parent.bind("<Control-U>", lambda event: self.update_plot())
        # self.parent.bind("<Control-u>", lambda event: self.update_plot())

        self.toolbar._Spacer()

        self.savedatabutton = Button(master=self.toolbar, command=self.store_solution, relief='flat', overrelief='groove', borderwidth=1)
        self.savedatabutton.image = PhotoImage(file=relative_to_navtoolbarassets('savedata.png'))
        self.savedatabutton.configure(image=self.savedatabutton.image) # Needs extra garbage collection and an image of 30x30
        self.savedatabutton.pack(side="left", padx=2)
        ToolTip(self.savedatabutton, lang.cc15)
        self.parent.bind("<Control-S>", lambda event: self.store_solution())
        self.parent.bind("<Control-s>", lambda event: self.store_solution())

        # self.resultsexportbutton = Button(master=self.toolbar, command=self.exportresults, relief='flat', overrelief='groove', borderwidth=1)
        # self.resultsexportbutton.image = PhotoImage(file=relative_to_navtoolbarassets('resultsexportbutton.png'))
        # self.resultsexportbutton.configure(image=self.resultsexportbutton.image) # Needs extra garbage collection and an image of 30x30
        # self.resultsexportbutton.pack(side="left", padx=2)
        # ToolTip(self.resultsexportbutton, 'Results exportation (Ctrl + I)\nExports linear programming results to excel')
        # self.parent.bind("<Control-I>", lambda event: self.exportresults())
        # self.parent.bind("<Control-i>", lambda event: self.exportresults())

        self.excelformatbutton = Button(master=self.toolbar, command=self.pre_excelformatting, relief='flat', overrelief='groove', borderwidth=1)
        self.excelformatbutton.image = PhotoImage(file=relative_to_navtoolbarassets('excelformatbutton.png'))
        self.excelformatbutton.configure(image=self.excelformatbutton.image) # Needs extra garbage collection and an image of 30x30
        self.excelformatbutton.pack(side="left", padx=2)
        ToolTip(self.excelformatbutton, lang.cc16)
        self.parent.bind("<Control-E>", lambda event: self.pre_excelformatting())
        self.parent.bind("<Control-e>", lambda event: self.pre_excelformatting())

        self.daycutbutton = Button(master=self.toolbar, command=self.new_day_generation_starter, relief='flat', overrelief='groove', borderwidth=1)
        self.daycutbutton.image = PhotoImage(file=relative_to_navtoolbarassets('cutbutton.png'))
        self.daycutbutton.configure(image=self.daycutbutton.image)
        self.daycutbutton.pack(side="left", padx=2)
        ToolTip(self.daycutbutton, lang.cc17)
        self.parent.bind("<Control-K>", lambda event: self.new_day_generation_starter())
        self.parent.bind("<Control-k>", lambda event: self.new_day_generation_starter())

        self.summarybutton = Button(master=self.toolbar, command=self.day_summariser_handler, relief='flat', overrelief='groove', borderwidth=1)
        self.summarybutton.image = PhotoImage(file=relative_to_navtoolbarassets('summarybutton.png'))
        self.summarybutton.configure(image=self.summarybutton.image)
        self.summarybutton.pack(side="left", padx=2)
        ToolTip(self.summarybutton, lang.cc18)
        self.parent.bind("<Control-L>", lambda event: self.day_summariser_handler())
        self.parent.bind("<Control-l>", lambda event: self.day_summariser_handler())

        self.toolbar._Spacer()

        # self.editionbutton = Checkbutton(master=self.toolbar, variable=self.editionmode, command=self.edit_manager, indicatoron=False, offrelief='flat', overrelief='groove', borderwidth=1)
        # self.editionbutton.image = PhotoImage(file=relative_to_navtoolbarassets('editpropertiesbutton.png'))
        # self.editionbutton.configure(image=self.editionbutton.image)
        # self.editionbutton.pack(side="left", padx=2)
        # ToolTip(self.editionbutton, 'Toggle box edition mode (or Right-Click over box)\nWhen in edition mode, click over a box to edit its properties')

        self.librarybutton = Button(master=self.toolbar, command=lambda: win_library.librarywin(self.parent, self), relief='flat', overrelief='groove', borderwidth=1)
        self.librarybutton.image = PhotoImage(file=relative_to_navtoolbarassets('librarybutton.png'))
        self.librarybutton.configure(image=self.librarybutton.image)
        self.librarybutton.pack(side="left", padx=2)
        ToolTip(self.librarybutton, lang.cc19)
        self.parent.bind("<Control-N>", lambda event: win_library.librarywin(self.parent, self))
        self.parent.bind("<Control-n>", lambda event: win_library.librarywin(self.parent, self))


        self.createservicebutton = Button(master=self.toolbar, command=lambda: self.summon_properties_window(alternative_ticket='S'), relief='flat', overrelief='groove', borderwidth=1)
        self.createservicebutton.image = PhotoImage(file=relative_to_navtoolbarassets('createservicebutton.png'))
        self.createservicebutton.configure(image=self.createservicebutton.image)
        self.createservicebutton.pack(side="left", padx=2)
        ToolTip(self.createservicebutton, lang.cc20)
        self.parent.bind("<Control-Q>", lambda event: self.summon_properties_window(alternative_ticket='S'))
        self.parent.bind("<Control-q>", lambda event: self.summon_properties_window(alternative_ticket='S'))

        self.createmaintenancebutton = Button(master=self.toolbar, command=lambda: self.summon_properties_window(alternative_ticket='M'), relief='flat', overrelief='groove', borderwidth=1)
        self.createmaintenancebutton.image = PhotoImage(file=relative_to_navtoolbarassets('createmaintenancebutton.png'))
        self.createmaintenancebutton.configure(image=self.createmaintenancebutton.image)
        self.createmaintenancebutton.pack(side="left", padx=2)
        ToolTip(self.createmaintenancebutton, lang.cc21)
        self.parent.bind("<Control-A>", lambda event: self.summon_properties_window(alternative_ticket='M'))
        self.parent.bind("<Control-a>", lambda event: self.summon_properties_window(alternative_ticket='M'))

        self.createtransferbutton = Button(master=self.toolbar, command=lambda: self.summon_properties_window(alternative_ticket='T'), relief='flat', overrelief='groove', borderwidth=1)
        self.createtransferbutton.image = PhotoImage(file=relative_to_navtoolbarassets('createtransferbutton.png'))
        self.createtransferbutton.configure(image=self.createtransferbutton.image)
        self.createtransferbutton.pack(side="left", padx=2)
        ToolTip(self.createtransferbutton, lang.cc22)
        self.parent.bind("<Control-T>", lambda event: self.summon_properties_window(alternative_ticket='T'))
        self.parent.bind("<Control-t>", lambda event: self.summon_properties_window(alternative_ticket='T'))

        self.basketbutton = Button(master=self.toolbar, command=self.delete_manager, relief='flat', overrelief='groove', borderwidth=1, text='\U0001F5D1')
        self.basketbutton.pack(side="left", padx=2)
        self.parent.bind("<Delete>", lambda event: self.delete_manager())
        self.parent.bind("<BackSpace>", lambda event: self.delete_manager())
        ToolTip(self.basketbutton, lang.cc23)

        self.toolbar.update()

    def modify_undo_history(self, item=None, deleting=False):
        if deleting:
            self.action_list_undo.pop(-1)
            if len(self.action_list_undo) == 0:
                self.undobutton.configure(state='disabled')
                self.parent.unbind("<Control-Z>")
                self.parent.unbind("<Control-z>")
                self.resetbutton.configure(state='disabled')
                self.parent.unbind("<Control-Alt-R>")
                self.parent.unbind("<Control-Alt-r>")
            return

        self.action_list_undo.append(item)
        self.undobutton.configure(state='normal')
        self.parent.bind("<Control-Z>", lambda event: self.undo_action())
        self.parent.bind("<Control-z>", lambda event: self.undo_action())
        self.resetbutton.configure(state='normal')
        self.parent.bind("<Control-Alt-R>", lambda event: self.reset_view())
        self.parent.bind("<Control-Alt-r>", lambda event: self.reset_view())

    def modify_redo_history(self, item=None, deleting=False, wiping=False):
        if wiping:
            self.action_list_redo = []
            self.redobutton.configure(state='disabled')
            self.parent.unbind("<Control-Y>")
            self.parent.unbind("<Control-y>")
            return

        if deleting:
            self.action_list_redo.pop(-1)
            if len(self.action_list_redo) == 0:
                self.redobutton.configure(state='disabled')
                self.parent.unbind("<Control-Y>")
                self.parent.unbind("<Control-y>")
            return

        self.action_list_redo.append(item)
        self.redobutton.configure(state='normal')
        self.parent.bind("<Control-Y>", lambda event: self.redo_action())
        self.parent.bind("<Control-y>", lambda event: self.redo_action())

    def undo_action(self):
        if len(self.action_list_undo) > 0:
            self.undobutton.configure(state='disabled')
            self.parent.unbind("<Control-Z>")
            self.parent.unbind("<Control-z>")
            self.resetbutton.configure(state='disabled')
            self.parent.unbind("<Control-Alt-R>")
            self.parent.unbind("<Control-Alt-r>")

            if self.action_list_undo[-1][0] == 'create': # ['create', type_of_element, created_index]
                # Needs to target the element in the created_index, in its corresponding type_of_element list, and disconnect+delete it
                created_index = self.action_list_undo[-1][2]

                if self.action_list_undo[-1][1] == 'S':
                    elements_to_restore = {'bottomleft': self.s_collection[created_index].bottomleft,
                                           'width': self.s_collection[created_index].width,
                                           'name': self.s_collection[created_index].msg,
                                           'origin': self.s_collection[created_index].origin,
                                           'destiny': self.s_collection[created_index].destiny,
                                           'conditioned_successor': self.s_collection[created_index].conditioned_successor,
                                           'banned_successors': self.s_collection[created_index].banned_successors,
                                           'departure_time': self.s_collection[created_index].departure_time,
                                           'arrival_time': self.s_collection[created_index].arrival_time,
                                           'kmservice': self.s_collection[created_index].km,
                                           'facecolor': self.s_collection[created_index].polygon._original_facecolor}
                    self.modify_redo_history(['create', 'S', created_index, elements_to_restore]) # ['create', type_of_element, insertion_index, {element_to_restore}]

                    self.s_collection[created_index].disconnect()
                    self.s_collection[created_index].text.remove()
                    self.s_collection[created_index].polygon.remove()

                    del self.s_collection[created_index]
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                elif self.action_list_undo[-1][1] == 'M':
                    elements_to_restore = {'bottomleft': self.m_collection[created_index].bottomleft,
                                           'width': self.m_collection[created_index].width,
                                           'name': self.m_collection[created_index].msg,
                                           'mtext': self.m_collection[created_index].mmsg,
                                           'kmlimit': self.m_collection[created_index].kmlimit,
                                           'departure_time': self.m_collection[created_index].departure_time,
                                           'arrival_time': self.m_collection[created_index].arrival_time,}
                    self.modify_redo_history(['create', 'M', created_index, elements_to_restore]) # ['create', type_of_element, insertion_index, {element_to_restore}]

                    self.m_collection[created_index].disconnect()
                    self.m_collection[created_index].text.remove()
                    self.m_collection[created_index].mtext.remove()
                    self.m_collection[created_index].polygon.remove()

                    del self.m_collection[created_index]
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                elif self.action_list_undo[-1][1] == 'T':
                    elements_to_restore = {'bottomleft': self.t_collection[created_index].bottomleft,
                                           'width': self.t_collection[created_index].width,
                                           'name': self.t_collection[created_index].msg,
                                           'origin': self.t_collection[created_index].origin,
                                           'destiny': self.t_collection[created_index].destiny,
                                           'departure_time': self.t_collection[created_index].departure_time,
                                           'arrival_time': self.t_collection[created_index].arrival_time,
                                           'kmservice': self.t_collection[created_index].km,
                                           'facecolor': self.t_collection[created_index].polygon._original_facecolor}
                    self.modify_redo_history(['create', 'T', created_index, elements_to_restore]) # ['create', type_of_element, insertion_index, {element_to_restore}]

                    self.t_collection[created_index].disconnect()
                    self.t_collection[created_index].text.remove()
                    self.t_collection[created_index].polygon.remove()

                    del self.t_collection[created_index]
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

            elif self.action_list_undo[-1][0] == 'edit': # ['edit', type_of_element, edited_index, {previous_elements}]
                edited_index = self.action_list_undo[-1][2]

                if self.action_list_undo[-1][1] == 'S':
                    elements_to_restore = {'bottomleft': self.s_collection[edited_index].bottomleft,
                                           'width': self.s_collection[edited_index].width,
                                           'name': self.s_collection[edited_index].msg,
                                           'origin': self.s_collection[edited_index].origin,
                                           'destiny': self.s_collection[edited_index].destiny,
                                           'conditioned_successor': self.s_collection[edited_index].conditioned_successor,
                                           'banned_successors': self.s_collection[edited_index].banned_successors,
                                           'departure_time': self.s_collection[edited_index].departure_time,
                                           'arrival_time': self.s_collection[edited_index].arrival_time,
                                           'kmservice': self.s_collection[edited_index].km,
                                           'facecolor': self.s_collection[edited_index].polygon._original_facecolor}
                    self.modify_redo_history(['edit', 'S', edited_index, elements_to_restore]) # ['edit', type_of_element, insertion_index, {element_to_restore}]

                    self.s_collection[edited_index].disconnect()
                    self.s_collection[edited_index].text.remove()
                    self.s_collection[edited_index].polygon.remove()

                    self.s_collection[edited_index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_undo[-1][3]['bottomleft'], height=0.5, width=self.action_list_undo[-1][3]['width'], name=self.action_list_undo[-1][3]['name'], ticket='S', origin=self.action_list_undo[-1][3]['origin'], destiny=self.action_list_undo[-1][3]['destiny'], conditioned_successor=self.action_list_undo[-1][3]['conditioned_successor'], banned_successors=self.action_list_undo[-1][3]['banned_successors'], departure_time=self.action_list_undo[-1][3]['departure_time'], arrival_time=self.action_list_undo[-1][3]['arrival_time'], kmservice=self.action_list_undo[-1][3]['kmservice'], facecolor=self.action_list_undo[-1][3]['facecolor'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.6)
                    self.ax.add_patch(self.s_collection[edited_index].polygon)
                    self.s_collection[edited_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                elif self.action_list_undo[-1][1] == 'M':
                    elements_to_restore = {'bottomleft': self.m_collection[edited_index].bottomleft,
                                           'width': self.m_collection[edited_index].width,
                                           'name': self.m_collection[edited_index].msg,
                                           'mtext': self.m_collection[edited_index].mmsg,
                                           'kmlimit': self.m_collection[edited_index].kmlimit,
                                           'departure_time': self.m_collection[edited_index].departure_time,
                                           'arrival_time': self.m_collection[edited_index].arrival_time,}
                    self.modify_redo_history(['edit', 'M', edited_index, elements_to_restore]) # ['create', type_of_element, insertion_index, {element_to_restore}]

                    self.m_collection[edited_index].disconnect()
                    self.m_collection[edited_index].text.remove()
                    self.m_collection[edited_index].mtext.remove()
                    self.m_collection[edited_index].polygon.remove()

                    self.m_collection[edited_index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_undo[-1][3]['bottomleft'], height=0.5, width=self.action_list_undo[-1][3]['width'], name=self.action_list_undo[-1][3]['name'], ticket='M', origin=None, destiny=None, hmovement=True, mtext=lang.cc32, kmservice=0, departure_time=self.action_list_undo[-1][3]['departure_time'], arrival_time=self.action_list_undo[-1][3]['arrival_time'], kmlimit=self.action_list_undo[-1][3]['kmlimit'], facecolor=settings.MAINTENANCE_COLOR, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.5)
                    self.ax.add_patch(self.m_collection[edited_index].polygon)
                    self.m_collection[edited_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                elif self.action_list_undo[-1][1] == 'T':
                    elements_to_restore = {'bottomleft': self.t_collection[edited_index].bottomleft,
                                           'width': self.t_collection[edited_index].width,
                                           'name': self.t_collection[edited_index].msg,
                                           'origin': self.t_collection[edited_index].origin,
                                           'destiny': self.t_collection[edited_index].destiny,
                                           'departure_time': self.t_collection[edited_index].departure_time,
                                           'arrival_time': self.t_collection[edited_index].arrival_time,
                                           'kmservice': self.t_collection[edited_index].km,
                                           'facecolor': self.t_collection[edited_index].polygon._original_facecolor}
                    self.modify_redo_history(['edit', 'T', edited_index, elements_to_restore]) # ['create', type_of_element, insertion_index, {element_to_restore}]

                    self.t_collection[edited_index].disconnect()
                    self.t_collection[edited_index].text.remove()
                    self.t_collection[edited_index].polygon.remove()

                    self.t_collection[edited_index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_undo[-1][3]['bottomleft'], height=0.5, width=self.action_list_undo[-1][3]['width'], name=self.action_list_undo[-1][3]['name'], ticket='T', origin=self.action_list_undo[-1][3]['origin'], destiny=self.action_list_undo[-1][3]['destiny'], conditioned_successor='', banned_successors=[], departure_time=self.action_list_undo[-1][3]['departure_time'], arrival_time=self.action_list_undo[-1][3]['arrival_time'], kmservice=self.action_list_undo[-1][3]['kmservice'], facecolor=self.action_list_undo[-1][3]['facecolor'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.7)
                    self.ax.add_patch(self.t_collection[edited_index].polygon)
                    self.t_collection[edited_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

            elif self.action_list_undo[-1][0] == 'delete': # ['delete', [[type_of_element, restoration_index, {element_to_restore}] ... for each moved element]]
                new_redo_history = []
                for element in self.action_list_undo[-1][1]: # element = [type_of_element, deletion_index, {element_to_restore}]
                    restoration_index = element[1]

                    if element[0] == 'S':
                        self.s_collection.insert(restoration_index, ScheduleBox(parent=self, ax=self.ax, bottomleft=element[2]['bottomleft'], height=0.5, width=element[2]['width'], name=element[2]['name'], ticket='S', origin=element[2]['origin'], destiny=element[2]['destiny'], conditioned_successor=element[2]['conditioned_successor'], banned_successors=element[2]['banned_successors'], departure_time=element[2]['departure_time'], arrival_time=element[2]['arrival_time'], kmservice=element[2]['kmservice'], facecolor=element[2]['facecolor'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.6))
                        self.ax.add_patch(self.s_collection[restoration_index].polygon)
                        self.s_collection[restoration_index].connect()

                        new_redo_history.insert(0, ['S', restoration_index])

                    elif element[0] == 'M':
                        self.m_collection.insert(restoration_index, ScheduleBox(parent=self, ax=self.ax, bottomleft=element[2]['bottomleft'], height=0.5, width=element[2]['width'], name=element[2]['name'], ticket='M', origin=None, destiny=None, hmovement=True, mtext=lang.cc32, kmservice=0, departure_time=element[2]['departure_time'], arrival_time=element[2]['arrival_time'], kmlimit=element[2]['kmlimit'], facecolor=settings.MAINTENANCE_COLOR, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.5))
                        self.ax.add_patch(self.m_collection[restoration_index].polygon)
                        self.m_collection[restoration_index].connect()

                        new_redo_history.insert(0, ['M', restoration_index])

                    elif element[0] == 'T':
                        self.t_collection.insert(restoration_index, ScheduleBox(parent=self, ax=self.ax, bottomleft=element[2]['bottomleft'], height=0.5, width=element[2]['width'], name=element[2]['name'], ticket='T', origin=element[2]['origin'], destiny=element[2]['destiny'], conditioned_successor='', banned_successors=[], departure_time=element[2]['departure_time'], arrival_time=element[2]['arrival_time'], kmservice=element[2]['kmservice'], facecolor=element[2]['facecolor'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.7))
                        self.ax.add_patch(self.t_collection[restoration_index].polygon)
                        self.t_collection[restoration_index].connect()

                        new_redo_history.insert(0, ['T', restoration_index])

                self.canvas_customisation()
                self.update_plot(showstatus=False)
                self.modify_redo_history(['delete', new_redo_history]) # ['delete', [[type_of_element, deletion_index] ... for each deleted element]]

            elif self.action_list_undo[-1][0] == 'move': # ['move', [[type_of_element, created_index, former_polygon_xy] ... for each moved element]]
                new_redo_history = ['move', []]
                for element in self.action_list_undo[-1][1]: # element = [type_of_element, created_index, former_polygon_xy]
                    if element[0] == 'S':
                        new_redo_history[1].append([element[0], element[1], deepcopy(self.s_collection[element[1]].polygon.xy)])
                        self.s_collection[element[1]].text.remove()
                        self.s_collection[element[1]].polygon.xy = element[2]
                        self.s_collection[element[1]].bottomleft = element[2][0][0], element[2][0][1]
                        self.s_collection[element[1]].text = self.ax.text(self.s_collection[element[1]].polygon.xy[0][0] + self.s_collection[element[1]].width/2, self.s_collection[element[1]].polygon.xy[0][1] + self.s_collection[element[1]].height + 0.2, self.s_collection[element[1]].msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
                        self.canvasp.draw()
                        self.update_plot(showstatus=False)

                    elif element[0] == 'M':
                        new_redo_history[1].append([element[0], element[1], deepcopy(self.m_collection[element[1]].polygon.xy)])
                        self.m_collection[element[1]].text.remove()
                        self.m_collection[element[1]].mtext.remove()
                        self.m_collection[element[1]].polygon.xy = element[2]
                        self.m_collection[element[1]].bottomleft = element[2][0][0], element[2][0][1]
                        self.m_collection[element[1]].text = self.ax.text(self.m_collection[element[1]].polygon.xy[0][0] + self.m_collection[element[1]].width/2, self.m_collection[element[1]].polygon.xy[0][1] + self.m_collection[element[1]].height + 0.2, self.m_collection[element[1]].msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
                        self.m_collection[element[1]].mtext = self.ax.text(self.m_collection[element[1]].polygon.xy[0][0] + self.m_collection[element[1]].width / 2, self.m_collection[element[1]].polygon.xy[0][1] + self.m_collection[element[1]].height / 2, self.m_collection[element[1]].mmsg, ha='center', va='center', fontsize=8, fontfamily='monospace', color=dispcolour.DISP_TEXTSMAINT)
                        self.canvasp.draw()
                        self.update_plot(showstatus=False)

                    elif element[0] == 'T':
                        new_redo_history[1].append([element[0], element[1], deepcopy(self.t_collection[element[1]].polygon.xy)])
                        self.t_collection[element[1]].text.remove()
                        self.t_collection[element[1]].polygon.xy = element[2]
                        self.t_collection[element[1]].bottomleft = element[2][0][0], element[2][0][1]
                        self.t_collection[element[1]].text = self.ax.text(self.t_collection[element[1]].polygon.xy[0][0] + self.t_collection[element[1]].width/2, self.t_collection[element[1]].polygon.xy[0][1] + self.t_collection[element[1]].height + 0.2, self.t_collection[element[1]].msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
                        self.canvasp.draw()
                        self.update_plot(showstatus=False)

                self.modify_redo_history(new_redo_history)

            self.undobutton.configure(state='normal')
            self.parent.bind("<Control-Z>", lambda event: self.undo_action())
            self.parent.bind("<Control-z>", lambda event: self.undo_action())
            self.resetbutton.configure(state='normal')
            self.parent.bind("<Control-Alt-R>", lambda event: self.reset_view())
            self.parent.bind("<Control-Alt-r>", lambda event: self.reset_view())
            self.modify_undo_history(deleting=True)
            return

    def redo_action(self):
        if len(self.action_list_redo) > 0:
            self.redobutton.configure(state='disabled')
            self.parent.unbind("<Control-Y>")
            self.parent.unbind("<Control-y>")
            if self.action_list_redo[-1][0] == 'create': # ['create', type_of_element, insertion_index, {element_to_restore}]
                insertion_index = self.action_list_redo[-1][2]

                if self.action_list_redo[-1][1] == 'S':
                    self.s_collection.insert(insertion_index, ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_redo[-1][3]['bottomleft'], height=0.5, width=self.action_list_redo[-1][3]['width'], name=self.action_list_redo[-1][3]['name'], ticket='S', origin=self.action_list_redo[-1][3]['origin'], destiny=self.action_list_redo[-1][3]['destiny'], conditioned_successor=self.action_list_redo[-1][3]['conditioned_successor'], banned_successors=self.action_list_redo[-1][3]['banned_successors'], departure_time=self.action_list_redo[-1][3]['departure_time'], arrival_time=self.action_list_redo[-1][3]['arrival_time'], kmservice=self.action_list_redo[-1][3]['kmservice'], facecolor=self.action_list_redo[-1][3]['facecolor'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.6))
                    self.ax.add_patch(self.s_collection[insertion_index].polygon)
                    self.s_collection[insertion_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                    self.modify_undo_history(['create', 'S', insertion_index])

                elif self.action_list_redo[-1][1] == 'M':
                    self.m_collection.insert(insertion_index, ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_redo[-1][3]['bottomleft'], height=0.5, width=self.action_list_redo[-1][3]['width'], name=self.action_list_redo[-1][3]['name'], ticket='M', origin=None, destiny=None, hmovement=True, mtext=lang.cc32, kmservice=0, departure_time=self.action_list_redo[-1][3]['departure_time'], arrival_time=self.action_list_redo[-1][3]['arrival_time'], kmlimit=self.action_list_redo[-1][3]['kmlimit'], facecolor=settings.MAINTENANCE_COLOR, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.5))
                    self.ax.add_patch(self.m_collection[insertion_index].polygon)
                    self.m_collection[insertion_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                    self.modify_undo_history(['create', 'M', insertion_index])

                elif self.action_list_redo[-1][1] == 'T':
                    self.t_collection.insert(insertion_index, ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_redo[-1][3]['bottomleft'], height=0.5, width=self.action_list_redo[-1][3]['width'], name=self.action_list_redo[-1][3]['name'], ticket='T', origin=self.action_list_redo[-1][3]['origin'], destiny=self.action_list_redo[-1][3]['destiny'], conditioned_successor='', banned_successors=[], departure_time=self.action_list_redo[-1][3]['departure_time'], arrival_time=self.action_list_redo[-1][3]['arrival_time'], kmservice=self.action_list_redo[-1][3]['kmservice'], facecolor=self.action_list_redo[-1][3]['facecolor'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.7))
                    self.ax.add_patch(self.t_collection[insertion_index].polygon)
                    self.t_collection[insertion_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                    self.modify_undo_history(['create', 'T', insertion_index])

            elif self.action_list_redo[-1][0] == 'edit': # ['edit', type_of_element, insertion_index, {element_to_restore}]
                edited_index = self.action_list_redo[-1][2]

                if self.action_list_redo[-1][1] == 'S':
                    elements_to_restore = {'bottomleft': self.s_collection[edited_index].bottomleft,
                                           'width': self.s_collection[edited_index].width,
                                           'name': self.s_collection[edited_index].msg,
                                           'origin': self.s_collection[edited_index].origin,
                                           'destiny': self.s_collection[edited_index].destiny,
                                           'conditioned_successor': self.s_collection[edited_index].conditioned_successor,
                                           'banned_successors': self.s_collection[edited_index].banned_successors,
                                           'departure_time': self.s_collection[edited_index].departure_time,
                                           'arrival_time': self.s_collection[edited_index].arrival_time,
                                           'kmservice': self.s_collection[edited_index].km,
                                           'facecolor': self.s_collection[edited_index].polygon._original_facecolor}
                    self.modify_undo_history(['edit', 'S', edited_index, elements_to_restore]) # ['edit', type_of_element, insertion_index, {element_to_restore}]

                    self.s_collection[edited_index].disconnect()
                    self.s_collection[edited_index].text.remove()
                    self.s_collection[edited_index].polygon.remove()

                    self.s_collection[edited_index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_redo[-1][3]['bottomleft'], height=0.5, width=self.action_list_redo[-1][3]['width'], name=self.action_list_redo[-1][3]['name'], ticket='S', origin=self.action_list_redo[-1][3]['origin'], destiny=self.action_list_redo[-1][3]['destiny'], conditioned_successor=self.action_list_redo[-1][3]['conditioned_successor'], banned_successors=self.action_list_redo[-1][3]['banned_successors'], departure_time=self.action_list_redo[-1][3]['departure_time'], arrival_time=self.action_list_redo[-1][3]['arrival_time'], kmservice=self.action_list_redo[-1][3]['kmservice'], facecolor=self.action_list_redo[-1][3]['facecolor'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.6)
                    self.ax.add_patch(self.s_collection[edited_index].polygon)
                    self.s_collection[edited_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                elif self.action_list_redo[-1][1] == 'M':
                    elements_to_restore = {'bottomleft': self.m_collection[edited_index].bottomleft,
                                           'width': self.m_collection[edited_index].width,
                                           'name': self.m_collection[edited_index].msg,
                                           'mtext': self.m_collection[edited_index].mmsg,
                                           'kmlimit': self.m_collection[edited_index].kmlimit,
                                           'departure_time': self.m_collection[edited_index].departure_time,
                                           'arrival_time': self.m_collection[edited_index].arrival_time,}
                    self.modify_undo_history(['edit', 'M', edited_index, elements_to_restore]) # ['edit', type_of_element, insertion_index, {element_to_restore}]

                    self.m_collection[edited_index].disconnect()
                    self.m_collection[edited_index].text.remove()
                    self.m_collection[edited_index].mtext.remove()
                    self.m_collection[edited_index].polygon.remove()

                    self.m_collection[edited_index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_redo[-1][3]['bottomleft'], height=0.5, width=self.action_list_redo[-1][3]['width'], name=self.action_list_redo[-1][3]['name'], ticket='M', origin=None, destiny=None, hmovement=True, mtext=lang.cc32, kmservice=0, departure_time=self.action_list_redo[-1][3]['departure_time'], arrival_time=self.action_list_redo[-1][3]['arrival_time'], kmlimit=self.action_list_redo[-1][3]['kmlimit'], facecolor=settings.MAINTENANCE_COLOR, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.5)
                    self.ax.add_patch(self.m_collection[edited_index].polygon)
                    self.m_collection[edited_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

                elif self.action_list_redo[-1][1] == 'T':
                    elements_to_restore = {'bottomleft': self.t_collection[edited_index].bottomleft,
                                           'width': self.t_collection[edited_index].width,
                                           'name': self.t_collection[edited_index].msg,
                                           'origin': self.t_collection[edited_index].origin,
                                           'destiny': self.t_collection[edited_index].destiny,
                                           'departure_time': self.t_collection[edited_index].departure_time,
                                           'arrival_time': self.t_collection[edited_index].arrival_time,
                                           'kmservice': self.t_collection[edited_index].km,
                                           'facecolor': self.t_collection[edited_index].polygon._original_facecolor}
                    self.modify_undo_history(['edit', 'T', edited_index, elements_to_restore]) # ['edit', type_of_element, insertion_index, {element_to_restore}]

                    self.t_collection[edited_index].disconnect()
                    self.t_collection[edited_index].text.remove()
                    self.t_collection[edited_index].polygon.remove()

                    self.t_collection[edited_index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=self.action_list_redo[-1][3]['bottomleft'], height=0.5, width=self.action_list_redo[-1][3]['width'], name=self.action_list_redo[-1][3]['name'], ticket='T', origin=self.action_list_redo[-1][3]['origin'], destiny=self.action_list_redo[-1][3]['destiny'], conditioned_successor='', banned_successors=[], departure_time=self.action_list_redo[-1][3]['departure_time'], arrival_time=self.action_list_redo[-1][3]['arrival_time'], kmservice=self.action_list_redo[-1][3]['kmservice'], facecolor=self.action_list_redo[-1][3]['facecolor'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.7)
                    self.ax.add_patch(self.t_collection[edited_index].polygon)
                    self.t_collection[edited_index].connect()
                    self.canvas_customisation()
                    self.update_plot(showstatus=False)

            elif self.action_list_redo[-1][0] == 'delete': # ['delete', type_of_element, deletion_index]
                redo_history = []
                for element in self.action_list_redo[-1][1]:
                    deletion_index = element[1]

                    if element[0] == 'S':
                        elements_to_restore = {'bottomleft': self.s_collection[deletion_index].bottomleft,
                                               'width': self.s_collection[deletion_index].width,
                                               'name': self.s_collection[deletion_index].msg,
                                               'origin': self.s_collection[deletion_index].origin,
                                               'destiny': self.s_collection[deletion_index].destiny,
                                               'conditioned_successor': self.s_collection[deletion_index].conditioned_successor,
                                               'banned_successors': self.s_collection[deletion_index].banned_successors,
                                               'departure_time': self.s_collection[deletion_index].departure_time,
                                               'arrival_time': self.s_collection[deletion_index].arrival_time,
                                               'kmservice': self.s_collection[deletion_index].km,
                                               'facecolor': self.s_collection[deletion_index].polygon._original_facecolor}
                        redo_history.insert(0, ['S', deletion_index, elements_to_restore]) # ['create', type_of_element, insertion_index, {element_to_restore}]

                        self.s_collection[deletion_index].disconnect()
                        self.s_collection[deletion_index].text.remove()
                        self.s_collection[deletion_index].polygon.remove()

                        del self.s_collection[deletion_index]

                    elif element[0] == 'M':
                        elements_to_restore = {'bottomleft': self.m_collection[deletion_index].bottomleft,
                                               'width': self.m_collection[deletion_index].width,
                                               'name': self.m_collection[deletion_index].msg,
                                               'mtext': self.m_collection[deletion_index].mmsg,
                                               'kmlimit': self.m_collection[deletion_index].kmlimit,
                                               'departure_time': self.m_collection[deletion_index].departure_time,
                                               'arrival_time': self.m_collection[deletion_index].arrival_time,}
                        redo_history.insert(0, ['M', deletion_index, elements_to_restore]) # ['create', type_of_element, insertion_index, {element_to_restore}]

                        self.m_collection[deletion_index].disconnect()
                        self.m_collection[deletion_index].text.remove()
                        self.m_collection[deletion_index].mtext.remove()
                        self.m_collection[deletion_index].polygon.remove()

                        del self.m_collection[deletion_index]

                    elif element[0] == 'T':
                        elements_to_restore = {'bottomleft': self.t_collection[deletion_index].bottomleft,
                                               'width': self.t_collection[deletion_index].width,
                                               'name': self.t_collection[deletion_index].msg,
                                               'origin': self.t_collection[deletion_index].origin,
                                               'destiny': self.t_collection[deletion_index].destiny,
                                               'departure_time': self.t_collection[deletion_index].departure_time,
                                               'arrival_time': self.t_collection[deletion_index].arrival_time,
                                               'kmservice': self.t_collection[deletion_index].km,
                                               'facecolor': self.t_collection[deletion_index].polygon._original_facecolor}
                        redo_history.insert(0, ['T', deletion_index, elements_to_restore]) # ['create', type_of_element, insertion_index, {element_to_restore}]

                        self.t_collection[deletion_index].disconnect()
                        self.t_collection[deletion_index].text.remove()
                        self.t_collection[deletion_index].polygon.remove()

                        del self.t_collection[deletion_index]

                self.modify_undo_history(['delete', redo_history])  # ['delete', [[type_of_element, restoration_index, {element_to_restore}] ... for each deleted element]]
                self.canvas_customisation()
                self.update_plot(showstatus=False)

            elif self.action_list_redo[-1][0] == 'move': # ['move', [[type_of_element, created_index, former_polygon_xy] ... for each moved element]]
                new_undo_history = ['move', []]
                for element in self.action_list_redo[-1][1]: # element = [type_of_element, created_index, former_polygon_xy]
                    if element[0] == 'S':
                        new_undo_history[1].append([element[0], element[1], deepcopy(self.s_collection[element[1]].polygon.xy)])
                        self.s_collection[element[1]].text.remove()
                        self.s_collection[element[1]].polygon.xy = element[2]
                        self.s_collection[element[1]].bottomleft = element[2][0][0], element[2][0][1]
                        self.s_collection[element[1]].text = self.ax.text(self.s_collection[element[1]].polygon.xy[0][0] + self.s_collection[element[1]].width/2, self.s_collection[element[1]].polygon.xy[0][1] + self.s_collection[element[1]].height + 0.2, self.s_collection[element[1]].msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
                        self.canvasp.draw()
                        self.update_plot(showstatus=False)

                    elif element[0] == 'M':
                        new_undo_history[1].append([element[0], element[1], deepcopy(self.m_collection[element[1]].polygon.xy)])
                        self.m_collection[element[1]].text.remove()
                        self.m_collection[element[1]].mtext.remove()
                        self.m_collection[element[1]].polygon.xy = element[2]
                        self.m_collection[element[1]].bottomleft = element[2][0][0], element[2][0][1]
                        self.m_collection[element[1]].text = self.ax.text(self.m_collection[element[1]].polygon.xy[0][0] + self.m_collection[element[1]].width/2, self.m_collection[element[1]].polygon.xy[0][1] + self.m_collection[element[1]].height + 0.2, self.m_collection[element[1]].msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
                        self.m_collection[element[1]].mtext = self.ax.text(self.m_collection[element[1]].polygon.xy[0][0] + self.m_collection[element[1]].width / 2, self.m_collection[element[1]].polygon.xy[0][1] + self.m_collection[element[1]].height / 2, self.m_collection[element[1]].mmsg, ha='center', va='center', fontsize=8, fontfamily='monospace', color=dispcolour.DISP_TEXTSMAINT)
                        self.canvasp.draw()
                        self.update_plot(showstatus=False)

                    elif element[0] == 'T':
                        new_undo_history[1].append([element[0], element[1], deepcopy(self.t_collection[element[1]].polygon.xy)])
                        self.t_collection[element[1]].text.remove()
                        self.t_collection[element[1]].polygon.xy = element[2]
                        self.t_collection[element[1]].bottomleft = element[2][0][0], element[2][0][1]
                        self.t_collection[element[1]].text = self.ax.text(self.t_collection[element[1]].polygon.xy[0][0] + self.t_collection[element[1]].width/2, self.t_collection[element[1]].polygon.xy[0][1] + self.t_collection[element[1]].height + 0.2, self.t_collection[element[1]].msg, ha='center', va='center', fontsize=8, fontfamily='monospace')
                        self.canvasp.draw()
                        self.update_plot(showstatus=False)

                self.modify_undo_history(new_undo_history)

            self.redobutton.configure(state='normal')
            self.parent.bind("<Control-Y>", lambda event: self.redo_action())
            self.parent.bind("<Control-y>", lambda event: self.redo_action())
            self.modify_redo_history(deleting=True)

    def chooserw_nullification_protocol(self, event): # noqa
        self.chooserw = None

    def new_day_generation_starter(self):
        if self.chooserw != None:
            return

        self.update_plot(showstatus=False)

        self.chooserw = Toplevel(self.parent)
        self.chooserw.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.chooserw.configure(background=colour.WINDOW_BACKGROUNDS)
        self.chooserw.title(lang.cc24)
        root_icon = PhotoImage(file=relative_to_edition("icon2.png"))
        self.chooserw.iconphoto(False, root_icon)
        self.chooserw.resizable(False, False)
        self.chooserw.bind('<Destroy>', self.chooserw_nullification_protocol)
        self.chooserw.focus_set()
        self.chooserw.bind('<Escape>', lambda e: self.chooserw.destroy())


        Label(self.chooserw, bd=2, text=lang.cc25, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).pack(padx=20, pady=(10, 0))

        self.days_plus_one = deepcopy(self.str_week)
        self.days_plus_one[0] = lang.cc26

        self.picker = Combobox(self.chooserw, values=self.days_plus_one, font=('futura', 13), width=10, style="Simple.TCombobox", state='readonly')
        self.picker.bind("<<ComboboxSelected>>", lambda e: self.chooserw.focus_set())
        self.picker.unbind('<MouseWheel>')
        self.picker.set(self.days_plus_one[1]) # This is the next day to the current run starting day
        self.picker.pack(padx=20, pady=(10, 0))

        btn = Button(master=self.chooserw, command=self.new_day_generation, relief='flat', background=colour.WINDOW_BACKGROUNDS)
        btn.image = PhotoImage(file=relative_to_edition('save.png'))
        btn.configure(image=btn.image) # Needs extra garbage collection and an image of 30x30
        btn.pack(padx=20, pady=(10, 20))

    def new_day_generation(self):
        newstartday = self.picker.get()
        self.chooserw.destroy()

        idx = self.days_plus_one.index(newstartday)
        referenced_hour = 24*idx if idx != 0 else 168

        newiniservices.iniservices = {}
        newiniservices.trainid = []
        newiniservices.km_limit = []
        newiniservices.next_mname = []
        newiniservices.next_m_duration = []
        ask_for_predetermined_maintenance = False

        for i in range(self.numtrains):
            train_y_pos = self.refypos - i
            latest_m = -1
            km = 0
            block = ''
            stuck_in_maintenance = False
            auxmaintname = self.maintenance_name[i]
            auxmaintduration = self.maintenance_duration[i]
            kmlimit = self.km_limit[i]
            name = ''
            banned = []
            forced = ''


            # TODO como realizar el corte con los linkers: lo primero es que al mirar los mantenimientos uno a uno, miramos cuántos se corresponde al gap que se está cortando.
            #  Recordar que los gaps son de intervalo cerrado por la izquierda, por lo que estará empezando a las 12 salvo que hubiera herencia mediante "->".
            #  Así sabemos cuantos elementos restar. Si se está cortando un mantenimiento, alteramos a true la nueva variable basura para la creación forzada de paso.
            #  En el proceso de creacion de las colecciones cuando se viene del calculo, hay que tocar para comprobar esto en lo que respecta a los iniservices, y en su caso alterar el nombre del lugar inicial a la version depot.
            for maint in sorted(self.m_collection, key=lambda item: item.polygon.xy[0][0]):
                if maint.polygon.xy[0][1] == train_y_pos:
                    if maint.polygon.xy[0][0] <= referenced_hour:
                        latest_m = maint.polygon.xy[0][0]
                        location = maint.destiny
                        if lang.DEPOT_MAINTENANCE in location:
                            location = location.replace(lang.DEPOT_MAINTENANCE, lang.DEPOT_OVERNIGHT)
                        auxmaintname = '??' # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.
                        auxmaintduration = '??' # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.

                        # El corte cae dentro del mtto
                        if maint.polygon.xy[3][0] > referenced_hour:
                            block = maint.polygon.xy[3][0] - referenced_hour
                            name = maint.msg
                            location = maint.destiny
                            auxmaintname = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.
                            auxmaintduration = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.
                            stuck_in_maintenance = True

                    else:
                        break

            for service in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]):
                if train_y_pos == service.polygon.xy[0][1]:
                    if service.polygon.xy[0][0] <= referenced_hour:
                        # Mantendra el último de todos los explorados que son válidos
                        banned = service.banned_successors
                        forced = service.conditioned_successor
                        if not stuck_in_maintenance:
                            # El departure time del servicio cuadra
                            if latest_m < service.polygon.xy[0][0]:
                                km += service.km
                                name = ''
                                location = service.destiny

                                # El corte cae dentro del servicio
                                if service.polygon.xy[3][0] > referenced_hour:
                                    block = service.polygon.xy[3][0] - referenced_hour
                                    name = service.msg
                                    if service.ticket == 'T':
                                        if lang.DEPOT_MAINTENANCE in service.destiny:
                                            maints_to_search = [maint for maint in sorted(self.m_collection, key=lambda item: item.polygon.xy[0][0]) if maint.polygon.xy[0][1] == train_y_pos and maint.polygon.xy[0][0] >= referenced_hour]
                                            if len(maints_to_search) > 0:
                                                maint = min(maints_to_search, key=lambda item: item.polygon.xy[0][0])
                                            else:
                                                break
                                            services_to_search = [serv for serv in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]) if serv.polygon.xy[0][1] == train_y_pos and serv.polygon.xy[0][0] >= service.polygon.xy[3][0]]
                                            if len(services_to_search) > 0:
                                                next_service = min(services_to_search, key=lambda item: item.polygon.xy[0][0])
                                                # Must include the maintenance
                                                if next_service.polygon.xy[0][0] >= maint.polygon.xy[0][0]:
                                                    km = 0
                                                    block = maint.polygon.xy[3][0] - referenced_hour
                                                    name = maint.msg
                                                    auxmaintname = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.
                                                    auxmaintduration = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.
                                            else:
                                                km = 0
                                                block = maint.polygon.xy[3][0] - referenced_hour
                                                name = maint.msg
                                                auxmaintname = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.
                                                auxmaintduration = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.

                                    break

                                # No cae dentro del servicio, pero el último es una T. Se mira si va a hacer un mantenimiento antes del proximo servicio.
                                if service.ticket == 'T' and lang.DEPOT_MAINTENANCE in service.destiny:
                                    maints_to_search = [maint for maint in sorted(self.m_collection, key=lambda item: item.polygon.xy[0][0]) if maint.polygon.xy[0][1] == train_y_pos and maint.polygon.xy[0][0] >= referenced_hour]
                                    if len(maints_to_search) > 0:
                                        maint = min(maints_to_search, key=lambda item: item.polygon.xy[0][0])
                                    else:
                                        continue
                                    services_to_search = [serv for serv in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]) if serv.polygon.xy[0][1] == train_y_pos and serv.polygon.xy[0][0] >= service.polygon.xy[3][0]]
                                    if len(services_to_search) > 0:
                                        next_service = min(services_to_search, key=lambda item: item.polygon.xy[0][0])
                                        # Must include the maintenance
                                        if next_service.polygon.xy[0][0] >= maint.polygon.xy[0][0]:
                                            km = 0
                                            block = maint.polygon.xy[3][0] - referenced_hour
                                            name = maint.msg
                                            auxmaintname = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.
                                            auxmaintduration = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.

                                    else:
                                        km = 0
                                        block = maint.polygon.xy[3][0] - referenced_hour
                                        name = maint.msg
                                        auxmaintname = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.
                                        auxmaintduration = '??'  # TODO se puede poner un ajuste para que se ponga el ?? por defecto o que se ponga el mimso nombre que ya hubiera.

            if auxmaintname == '??':
                ask_for_predetermined_maintenance = True
            newiniservices.trainid.append(self.trainid['train' + str(i+1)])  # String
            newiniservices.km_limit.append(kmlimit)  # Numerical
            newiniservices.next_mname.append(auxmaintname)  # String
            newiniservices.next_m_duration.append(auxmaintduration)  # Numerical (or str = '??')

            # Prevents location duplication when cutting iniservices
            if location + ' ' in name: # noqa
                name = name.replace(location + ' ', '')

            newiniservices.iniservices['iniservice' + str(i+1)] = {}
            newiniservices.iniservices['iniservice' + str(i+1)]['id'] = location + ' ' + name
            newiniservices.iniservices['iniservice' + str(i+1)]['AUXid'] = name # Esto debe ser vacio o el servicio que se está haciendo (en la ventana se corresponde con el campo de location info)
            newiniservices.iniservices['iniservice' + str(i+1)]['origin'] = location
            newiniservices.iniservices['iniservice' + str(i+1)]['destiny'] = location
            newiniservices.iniservices['iniservice' + str(i+1)]['kilometers'] = km
            newiniservices.iniservices['iniservice' + str(i+1)]['departure-time'] = 0
            newiniservices.iniservices['iniservice' + str(i+1)]['arrival-time'] = block
            newiniservices.iniservices['iniservice' + str(i+1)]['str_departure-time'] = '00:00'
            lock2 = 0.1 if block == '' else block # TODO no se si q tal con poner 0.1, lo suyo es poner un parametro ajustable y que sea 3 de serie; Y aparte cambiar en los matrix builder
            newiniservices.iniservices['iniservice' + str(i+1)]['str_arrival-time'] = (datetime.combine(date.today(), time()) + timedelta(hours=round(lock2, 8))).strftime('%H:%M')
            newiniservices.iniservices['iniservice' + str(i+1)]['color'] = '#6d6d6d'
            newiniservices.iniservices['iniservice' + str(i+1)]['forced'] = forced
            newiniservices.iniservices['iniservice' + str(i+1)]['bans'] = deepcopy(banned)

        # Need to prevent getting changes that were done outside; we will use base values
        newservices.services = deepcopy(self.baseservices)
        newservices.WEEKDAY = newstartday.split(' ')[0]

        newnodes.nodeslist = deepcopy(self.basenodes_without_extras)
        newnodes.shortenings = deepcopy(self.shortenings_without_extras)
        newnodes.depotnodes = deepcopy(self.depot_without_extras)
        newnodes.NODES_ARE_NEW = {node:False for node in newnodes.nodeslist}
        newdepottransfers.transfers = deepcopy(self.basetransfers)
        newsleepers.sleepers = deepcopy(self.basesleepers)
        newlinkers.linkers = deepcopy(self.baselinkers)

        if ask_for_predetermined_maintenance:
            self.chooserw = Toplevel(self.parent)
            self.chooserw.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
            self.chooserw.configure(background=colour.WINDOW_BACKGROUNDS)
            self.chooserw.geometry("900x600")
            self.chooserw.title(lang.cc27)
            root_icon = PhotoImage(file=relative_to_edition("icon2.png"))
            self.chooserw.iconphoto(False, root_icon)
            self.chooserw.resizable(False, False)
            self.chooserw.bind('<Destroy>', self.chooserw_nullification_protocol)
            self.chooserw.focus_set()
            self.chooserw.bind('<Escape>', lambda e: self.chooserw.destroy())

            buttonframe = Frame(master=self.chooserw, background=colour.WINDOW_BACKGROUNDS)

            save_button = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND)
            save_button.image = PhotoImage(file=relative_to_edition('save.png'))
            save_button.configure(image=save_button.image)

            predetermined_button = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND)
            predetermined_button.image = PhotoImage(file=relative_to_edition('predmaint.png'))
            predetermined_button.configure(image=predetermined_button.image)

            save_button.grid(row=0, column=0, padx=20, pady=10)
            predetermined_button.grid(row=0, column=1, padx=20, pady=10)

            buttonframe.pack(anchor='center')
            scrollframe = MaintenancesScrollableFrame(self.chooserw, bg=colour.FRAME_BACKGROUND, bd=0, x_scroll=False)

            save_button.configure(command=scrollframe.define_maintenances)
            predetermined_button.configure(command=scrollframe.all_are_predetermined)
            self.chooserw.wait_window(self.chooserw)

        create = messagebox.askyesno(lang.cc28, lang.cc29)
        if create:
            CSIDL_PERSONAL = 5  # My Documents
            SHGFP_TYPE_CURRENT = 0  # Get current, not default value
            buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
            here = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

            with filedialog.asksaveasfile(initialfile='untitled.cfg', initialdir=here, defaultextension='.cfg', filetypes=[("Config. file", ".cfg"), ("Text file", ".txt"), ("All files", ".*")]) as file:
                if file is None:
                    return

                file.writelines([str(newiniservices.km_limit), "\n" + str(newiniservices.next_mname), "\n" + str(newiniservices.next_m_duration), "\n" + str(newiniservices.trainid), "\n" + str(newnodes.nodeslist), "\n" + str(newnodes.shortenings), "\n" + str(newnodes.depotnodes), "\n" + str(newservices.services), "\n" + str(newservices.WEEKDAY), "\n" + str(newiniservices.iniservices), "\n" + str(newnodes.NODES_ARE_NEW), "\n" + str(newdepottransfers.transfers), "\n" + str(newsleepers.sleepers), "\n" + str(newlinkers.linkers)])
                # TODO try/except error catching needed
                file.close()

    def update_plot(self, showstatus=True):
        self.updatekm()
        self.check_maint_constraints()
        self.check_service_constraints()
        # self.fig.canvas.draw()
        self.canvasp.draw_idle()
        # self.figframe.update()
        # self.parent.update()

        if showstatus:
            messagebox.showinfo(lang.cc30, lang.cc31)
            self.parent.lift()

    def check_service_constraints(self): # TODO aplicar distintos patrones de hatching según se viole una u otra restricción
        last_service = [None] * self.numtrains
        last_absolute = [None] * self.numtrains
        for service in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]):
            checking_y = int(service.polygon.xy[0][1])
            status_ok = True

            if checking_y >= self.numtrains:
                continue # We are on auxiliar rows; skipping...

            # First service?
            if last_service[checking_y] == None:
                last_service[checking_y] = service
                last_absolute[checking_y] = service

            # Not iniservice
            else:
                # Using elif statements will speed up the process in some cases
                if last_absolute[checking_y].destiny == service.origin: # Position OK # noqa
                    if service.ticket == 'S':
                        if last_service[checking_y].conditioned_successor != '' and service.msg != last_service[checking_y].conditioned_successor:  # Conditional service must be met, but is NOT met # noqa
                            service.polygon.set_hatch('--')
                            service.hatched = True
                            last_service[checking_y].polygon.set_hatch('--')  # noqa
                            last_service[checking_y].hatched = True  # noqa
                            status_ok = False

                        elif service.msg in last_service[checking_y].banned_successors: # noqa service is a banned service after last service
                            service.polygon.set_hatch('xx')
                            service.hatched = True
                            last_service[checking_y].polygon.set_hatch('xx')  # noqa
                            last_service[checking_y].hatched = True  # noqa
                            status_ok = False

                        elif last_service[checking_y].polygon.xy[3][0] + settings.GAP_HOUR >= service.polygon.xy[0][0]: # noqa Service is not fullfilling minimum gap restrictions
                            service.polygon.set_hatch('||')
                            service.hatched = True
                            last_service[checking_y].polygon.set_hatch('||')  # noqa
                            last_service[checking_y].hatched = True  # noqa
                            status_ok = False

                else: # Position NOT OK
                    service.polygon.set_hatch('///')
                    service.hatched = True
                    status_ok = False

                if status_ok and service.hatched:
                    service.polygon.set_hatch('')
                    service.hatched = False

                # Update
                last_absolute[checking_y] = service
                if service.ticket == 'S':
                    last_service[checking_y] = service

    def check_maint_constraints(self):
        self.getmaintenancelocation()
        for maint in self.m_collection:
            ym = self.refypos - int(maint.polygon.xy[0][1])
            if ym >= 0: # Not the empty row(s)
                if not self.depot[maint.origin]:
                    maint.polygon.set_hatch('///')
                    maint.hatched = True
                    continue

                if maint.km > maint.kmlimit:
                    maint.polygon.set_hatch('///')
                    maint.hatched = True
                    continue

            # Ifs were not triggered; make sure there is no hatch
            if maint.hatched:
                maint.polygon.set_hatch('')
                maint.hatched = False

    def getmaintenancelocation(self): # TODO do the same here for the l_collection
        for maint in self.m_collection:
            ym = int(maint.polygon.xy[0][1])
            if ym < self.numtrains: # Not the empty row(s)
                xm = maint.polygon.xy[0][0]

                # Services bottom right corner <= Maintenance bottom left corner, x-position
                prev_services_arrivals = [[service.polygon.xy[0][0], service.destiny] for service in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]) if ym == service.polygon.xy[0][1] and service.polygon.xy[0][0] <= xm] # TODO cambiado de xy[3][0] a [0][0]

                destiny = max(prev_services_arrivals, key=lambda item: item[0])[1]
                maint.origin = maint.destiny = destiny

                dep = Decimal(str(maint.polygon.xy[0][0])) % 24
                arr = dep + Decimal(str(maint.width))

                maint.departure_time = (datetime.combine(date.today(), time()) + timedelta(hours=round(float(dep), 32))).strftime('%H:%M')
                maint.arrival_time = (datetime.combine(date.today(), time()) + timedelta(hours=round(float(arr), 32))).strftime('%H:%M')

            else:
                maint.origin = maint.destiny = None

        for transfer in self.t_collection:
            ym = int(transfer.polygon.xy[0][1])
            if ym < self.numtrains: # Not the empty row(s)
                dep = Decimal(str(transfer.polygon.xy[0][0])) % 24
                arr = dep + Decimal(str(transfer.width))

                transfer.departure_time = (datetime.combine(date.today(), time()) + timedelta(hours=round(float(dep), 32))).strftime('%H:%M')
                transfer.arrival_time = (datetime.combine(date.today(), time()) + timedelta(hours=round(float(arr), 32))).strftime('%H:%M')

    def updatekm(self):
        trains = {}
        kmtrain = {}

        for i in range(self.numtrains):
            trains['train' + str(i + 1)] = {'SERVICES': {}, 'MAINT': {}}
            kmtrain['train' + str(i + 1)] = []

        for service in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]):
            t = self.refypos - int(service.polygon.xy[0][1])
            if t >= 0:
                trains['train' + str(t + 1)]['SERVICES'][service] = [service.polygon.xy[0][0], service.km]

        # It is very important that maintenance keys are added in ascending order based on maintenance start time
        for maint in sorted(self.m_collection, key=lambda item: item.polygon.xy[0][0]):
            m = self.refypos - int(maint.polygon.xy[0][1])
            if m >= 0: # Not the empty row(s)
                trains['train' + str(m + 1)]['MAINT'][maint] = maint.polygon.xy[0][0]

        for i in range(self.numtrains):
            prevman = 0 # TODO dado q los servicios se borran al ser usados, el prevman no vale para nada? es así?

            for maint in trains['train' + str(i + 1)]['MAINT']:
                premaintenance = []
                auxdelete = []
                for service in trains['train' + str(i + 1)]['SERVICES']:
                    if prevman <= trains['train' + str(i + 1)]['SERVICES'][service][0] < trains['train' + str(i + 1)]['MAINT'][maint]:
                        premaintenance.append(trains['train' + str(i + 1)]['SERVICES'][service][1])
                        auxdelete.append(service)

                # Separate services in prior and postmaintenance
                [trains['train' + str(i + 1)]['SERVICES'].pop(service) for service in auxdelete]

                kmtrain['train' + str(i + 1)].append(sum(premaintenance))
                prevman = trains['train' + str(i + 1)]['MAINT'][maint]

            kmtrain['train' + str(i + 1)].append(sum([trains['train' + str(i + 1)]['SERVICES'][service][1] for service in trains['train' + str(i + 1)]['SERVICES']]))

        last_kmtrain_used = [-1 for _ in range(self.numtrains)]
        for maint in sorted(self.m_collection, key=lambda item: item.polygon.xy[0][0]):
            ym = self.refypos - int(maint.polygon.xy[0][1])
            if ym >= 0: # Not the empty row(s)
                last_kmtrain_used[ym] += 1
                mtext = 'Km: ' + str(kmtrain['train' + str(ym + 1)][last_kmtrain_used[ym]])
                maint.mmsg_replacement(mtext)
                maint.km = kmtrain['train' + str(ym + 1)][last_kmtrain_used[ym]]

            else:
                maint.mmsg_replacement(lang.cc32)
                maint.km = 0

        # define yticks
        yticks_pos = list(range(0, self.numtrains + settings.EXTRA_ROWS, 1))
        ytickslabel_pos = [i + 0.5 for i in range(self.numtrains + settings.EXTRA_ROWS)]
        yticks_labels = [self.trainid[tren] + '\n' + 'Km: ' + str(kmtrain[tren][-1]) for tren in kmtrain]
        yticks_labels.reverse()
        [yticks_labels.append('') for _ in range(settings.EXTRA_ROWS)]

        # Row delimitation
        self.ax.set_yticks(yticks_pos, '', fontsize=8, fontfamily='monospace')
        # Mid-row ticks, displaying names and info
        self.ax.set_yticks(ytickslabel_pos, yticks_labels, fontsize=8, fontfamily='monospace', minor=True)

    def delete_manager(self):
        if len(self.highlighter.selection) > 0:
            undo_history = []

            for item in self.highlighter.selection:
                if item.ticket == 'S':
                    deletion_index = self.s_collection.index(item)
                    elements_to_restore = {'bottomleft': item.bottomleft, 'width': item.width, 'name': item.msg, 'origin': item.origin, 'destiny': item.destiny, 'conditioned_successor': item.conditioned_successor, 'banned_successors': item.banned_successors, 'departure_time': item.departure_time, 'arrival_time': item.arrival_time, 'kmservice': item.km, 'facecolor': item.polygon._original_facecolor}

                    self.s_collection[deletion_index].disconnect()
                    self.s_collection[deletion_index].text.remove()
                    self.s_collection[deletion_index].polygon.remove()

                    del self.s_collection[deletion_index]
                    undo_history.insert(0, ['S', deletion_index, elements_to_restore])

                elif item.ticket == 'M':
                    deletion_index = self.m_collection.index(item)
                    elements_to_restore = {'bottomleft': item.bottomleft, 'width': item.width, 'name': item.msg, 'mtext': item.mmsg, 'kmlimit': item.kmlimit, 'departure_time': item.departure_time, 'arrival_time': item.arrival_time, }

                    self.m_collection[deletion_index].disconnect()
                    self.m_collection[deletion_index].text.remove()
                    self.m_collection[deletion_index].mtext.remove()
                    self.m_collection[deletion_index].polygon.remove()

                    del self.m_collection[deletion_index]
                    undo_history.insert(0, ['M', deletion_index, elements_to_restore])

                elif item.ticket == 'T':
                    deletion_index = self.t_collection.index(item)
                    elements_to_restore = {'bottomleft': item.bottomleft, 'width': item.width, 'name': item.msg, 'origin': item.origin, 'destiny': item.destiny, 'departure_time': item.departure_time, 'arrival_time': item.arrival_time, 'kmservice': item.km, 'facecolor': item.polygon._original_facecolor}

                    self.t_collection[deletion_index].disconnect()
                    self.t_collection[deletion_index].text.remove()
                    self.t_collection[deletion_index].polygon.remove()

                    del self.t_collection[deletion_index]
                    undo_history.insert(0, ['T', deletion_index, elements_to_restore])

            self.modify_undo_history(['delete', undo_history])

            # TODO verificar que esto es lo que hay que hacer. Verificar el tema de los limites de eje en canvas customisation. En el undo history también se llama a canvas customisation, y no se si es necesario del todo
            self.highlighter.selection = []
            self.modify_redo_history(wiping=True)
            self.canvas_customisation()
            self.update_plot(showstatus=False)

    def popup_nullification_protocol(self, event): # noqa
        self.propwindow = None

    def day_summariser_handler(self):
        if self.click_to_summarise: # On, needs to toggle off and unbind escape event
            self.click_to_summarise = False
            self.parent.unbind('<Escape>')
            self.canvasp.mpl_disconnect(self.click_to_summarise_mplevent)

        else: # Off, needs to toggle on and bind escape event
            self.click_to_summarise = True
            self.parent.bind('<Escape>', lambda e: self.day_summariser_handler())
            self.click_to_summarise_mplevent = self.canvasp.mpl_connect('button_press_event', lambda e: self.day_summariser(e))

    def day_summariser(self, event):
        if self.propwindow is not None:
            return

        x = event.xdata
        day = int(x / 24)
        left = 24 * day
        right = left + 24

        self.propwindow = Toplevel(self.parent)
        self.propwindow.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.propwindow.configure(background=colour.WINDOW_BACKGROUNDS)
        self.propwindow.title(lang.cc33 + self.str_week[day])
        self.propwindow.geometry("1000x600")
        wizard_icon = PhotoImage(file=relative_to_edition("icon2.png"))
        self.propwindow.iconphoto(False, wizard_icon)
        self.propwindow.bind("<Destroy>", self.popup_nullification_protocol)
        self.propwindow.focus_set()
        self.propwindow.bind('<Escape>', lambda e: self.propwindow.destroy())

        # start_position = []
        # end_position = []
        # for train in self.numtrains:
        #     last_time = 0
        #     leftiest = None
        #     for box in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]):
        #         if box.polygon.xy[0][0] >= last_time and box.polygon.xy[3][0] <= right and box.polygon.xy[0][1] == self.refypos - train:
        #             last_time = box.polygon.xy[0][0]
        #             last_box = box
        #
        #             if box.polygon.xy[0][0] >= left and leftiest is None:
        #                 leftiest = box

        # Precompute sorted list once
        all_boxes = sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0])

        # Group boxes by row and cache start/end times to avoid repeated attribute access
        boxes_by_row = {}
        for b in all_boxes:
            row = b.polygon.xy[0][1]
            s = float(b.polygon.xy[0][0])
            e = float(b.polygon.xy[2][0])
            boxes_by_row.setdefault(row, []).append((b, s, e))

        summary = {}
        for train in range(self.numtrains):
            row_y = self.refypos - train
            boxes = boxes_by_row[row_y]

            # START OF DAY (left)
            spanning_left = next((b for b, s, e in boxes if s < left < e), None)
            if spanning_left is not None:
                start_pos = spanning_left.destiny
            else:
                ended_before = [t for t in boxes if t[2] <= left]
                last = max(ended_before, key=lambda t: t[2])
                start_pos = last[0].destiny

            # END OF DAY (right)
            spanning_right = next((b for b, s, e in boxes if s < right < e), None)
            if spanning_right is not None:
                end_pos = spanning_right.destiny
            else:
                ended_before = [t for t in boxes if t[2] <= right]
                last = max(ended_before, key=lambda t: t[2])
                end_pos = last[0].destiny or ''

            summary[self.trainid['train' + str(train + 1)]] = start_pos, end_pos

        self.day_summariser_handler()
        scrollframe = SummaryScrollableFrame(self.propwindow, summary, bg=colour.FRAME_BACKGROUND, bd=0, x_scroll=False)

    def summon_properties_window(self, item=None, alternative_ticket=None):
        if item != None:
            if self.propwindow == None:
                if item.ticket == 'S':
                    self.s_properties_window(item, mode='Edit')

                elif item.ticket == 'M':
                    self.m_properties_window(item, mode='Edit')

                else: # It's a T
                    self.t_properties_window(item, mode='Edit')

            else:
                return

        else: # Item is none, comes from toolbar button
            if self.propwindow == None:
                if alternative_ticket == 'S':
                    self.s_properties_window(item, mode='New')

                elif alternative_ticket == 'M':
                    self.m_properties_window(item, mode='New')

                else:  # It's a T
                    self.t_properties_window(item, mode='New')

            else:
                return

    def s_properties_window(self, item, mode):
        self.propwindow = Toplevel(self.parent)
        self.propwindow.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.propwindow.configure(background=colour.WINDOW_BACKGROUNDS)
        if mode == 'Edit':
            self.propwindow.title(lang.cc34 + item.msg)
        else:
            self.propwindow.title(lang.cc35)

        wizard_icon = PhotoImage(file=relative_to_edition("icon2.png"))
        self.propwindow.iconphoto(False, wizard_icon)
        self.propwindow.bind("<Destroy>", self.popup_nullification_protocol)
        self.propwindow.focus_set()
        self.propwindow.bind('<Escape>', lambda e: self.propwindow.destroy())

        # Boton de guardado
        savebtn = Button(self.propwindow, command=lambda: self.s_edition(item, mode=mode), borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS)
        savebtn.image = PhotoImage(file=relative_to_edition('save.png'))
        savebtn.configure(image=savebtn.image)
        savebtn.pack(side='top', pady=10)

        # Entries frame
        entriesframe = Frame(master=self.propwindow, background=colour.FRAME_BACKGROUND)

        # Define entries
        entriesframe.columnconfigure(0, weight=1, uniform='equal')
        entriesframe.columnconfigure(1, weight=1, uniform='equal')
        entriesframe.columnconfigure(2, weight=1, uniform='equal')
        entriesframe.columnconfigure(3, weight=1, uniform='equal')

        Label(entriesframe, bd=2, text=lang.gui_servidb, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='ew')
        self.service_name = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_name.grid(row=1, column=0, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_kilometers, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='ew')
        self.service_km = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_km.grid(row=1, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_forced, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='ew')
        self.service_condition = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_condition.grid(row=1, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_bans, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='ew')
        self.service_bans = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_bans.grid(row=1, column=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_departuretime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=0, columnspan=2, ipady=10, sticky='ew')
        # First third
        self.service_dep_day = Combobox(entriesframe, values=self.str_week, font='futura', style="Simple.TCombobox", state='readonly')
        self.service_dep_day.grid(row=3, column=0, padx=20, pady=20, sticky='ew')
        # Second third
        self.service_departure = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_departure.grid(row=3, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_arrivaltime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=2, columnspan=2, ipady=10, sticky='ew')
        # Third third
        self.service_arr_day = Combobox(entriesframe, values=self.str_week, font='futura', style="Simple.TCombobox", state='readonly')
        self.service_arr_day.grid(row=3, column=2, padx=20, pady=20, sticky='ew')
        # Fourth third
        self.service_arrival = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_arrival.grid(row=3, column=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=0, ipady=10, sticky='ew')
        self.service_dur = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_dur.grid(row=5, column=0, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_fromsimple, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=1, ipady=10, sticky='ew')
        self.service_origin = AutocompleteCombobox(master=entriesframe, completevalues=self.basenodes)
        self.service_origin.grid(row=5, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_tosimple, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=2, ipady=10, sticky='ew')
        self.service_destiny = AutocompleteCombobox(master=entriesframe, completevalues=self.basenodes)
        self.service_destiny.grid(row=5, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=3, ipady=10, sticky='ew')
        if mode == 'Edit':
            self.service_color = ColorEntry(entriesframe, base_color=item.polygon._original_facecolor, bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716")
        else:
            self.service_color = ColorEntry(entriesframe, base_color='#d6d6d6', bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716")
        self.service_color.grid(row=5, column=3, padx=20, pady=20, sticky='ew')

        if mode == 'Edit':
            self.service_name.insert(0, item.msg)
            self.service_km.insert(0, str(item.km))
            self.service_condition.insert(0, item.conditioned_successor)
            self.service_bans.insert(0, str(item.banned_successors).translate({ord(i): None for i in "[]'"}))

            try:
                self.service_dep_day.set(self.str_week[int(item.polygon.xy[0][0]/24)])
            except IndexError:
                self.service_dep_day.set(self.str_week[0])
            try:
                self.service_arr_day.set(self.str_week[int(item.polygon.xy[3][0]/24)])
            except IndexError:
                self.service_arr_day.set(self.str_week[-1])

            self.service_departure.insert(0, item.departure_time)
            self.service_arrival.insert(0, item.arrival_time)
            self.service_dur.insert(0, item.width)
            self.service_origin.set(item.origin)
            self.service_destiny.set(item.destiny)

        # self.service_departure_SV.trace_add('write', lambda var, z, e: on_change(self.service_departure, self.service_departure, self.service_dep_day, self.service_arrival, self.service_arr_day, self.service_dur, self.str_week, 1))
        self.service_departure.bind('<FocusOut>', lambda e: live_time_parser(self.service_departure, self.service_dep_day, self.service_arrival, self.service_arr_day, self.service_dur, self.str_week, exiting=1))
        self.service_dep_day.bind('<<ComboboxSelected>>', lambda e: live_time_parser(self.service_departure, self.service_dep_day, self.service_arrival, self.service_arr_day, self.service_dur, self.str_week, exiting=1))
        self.service_arrival.bind('<FocusOut>', lambda e: live_time_parser(self.service_departure, self.service_dep_day, self.service_arrival, self.service_arr_day, self.service_dur, self.str_week, exiting=2))
        self.service_arr_day.bind('<<ComboboxSelected>>', lambda e: live_time_parser(self.service_departure, self.service_dep_day, self.service_arrival, self.service_arr_day, self.service_dur, self.str_week, exiting=2))
        self.service_dur.bind('<FocusOut>', lambda e: live_time_parser(self.service_departure, self.service_dep_day, self.service_arrival, self.service_arr_day, self.service_dur, self.str_week, exiting=3))

        entriesframe.pack(fill='both', expand=True)

    def s_edition(self, item, mode):
        something_changed = False

        # Get the data and check if something changed
        try:
            new_name = self.service_name.get()
        except:
            messagebox.showerror(lang.cc36,lang.cc37)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        new_dur = eval(self.service_dur.get())
        new_km = eval(self.service_km.get())
        new_condition = self.service_condition.get()
        new_bans = self.service_bans.get()
        new_dep_day = self.service_dep_day.get()
        new_departure = self.service_departure.get()
        new_arr_day = self.service_arr_day.get()
        new_arrival = self.service_arrival.get()
        new_origin = self.service_origin.get()
        new_destiny = self.service_destiny.get()
        new_color = self.service_color.get()

        # Some additional checking
        if new_dur <= 0:
            messagebox.showerror(lang.cc36, lang.cc38)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        try:
            t = datetime.strptime(new_departure, '%H:%M').time()
        except:
            messagebox.showerror(lang.cc39,lang.cc40)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return
        new_start = 24 * self.str_week.index(new_dep_day) + t.hour + t.minute / 60

        try:
            t = datetime.strptime(new_arrival, '%H:%M').time()
        except:
            messagebox.showerror(lang.cc39, lang.cc41)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return
        new_end = 24 * self.str_week.index(new_arr_day) + t.hour + t.minute / 60

        # Special checking: apply common sense to durations
        if self.service_departure.cget('bg') == '#ffd28f':
            new_start = new_end - new_dur
            something_changed = True

        elif self.service_arrival.cget('bg') == '#ffd28f':
            new_end = new_start + new_dur
            something_changed = True

        if mode == 'Edit':
            if new_name != item.msg:
                something_changed = True

            if new_km != item.km:
                something_changed = True

            if new_condition != item.conditioned_successor:
                something_changed = True

            if new_bans != item.banned_successors:
                something_changed = True

            if new_start != item.polygon.xy[0][0] / 24:
                something_changed = True

            if new_end != item.polygon.xy[3][0] / 24:
                something_changed = True

            if new_origin != item.origin:
                something_changed = True

            if new_destiny != item.destiny:
                something_changed = True

            if new_color != item.polygon._original_facecolor:
                something_changed = True

            # Create the box again
            if something_changed:
                # Get train
                y = item.polygon.xy[0][1]

                # Search substitution target
                index = self.s_collection.index(item)

                # Modify undo history
                elements_to_restore = {'bottomleft': item.bottomleft, 'width': item.width, 'name': item.msg, 'origin': item.origin, 'destiny': item.destiny, 'conditioned_successor': item.conditioned_successor, 'banned_successors': item.banned_successors, 'departure_time': item.departure_time, 'arrival_time': item.arrival_time, 'kmservice': item.km, 'facecolor': item.polygon._original_facecolor}
                self.modify_undo_history(['edit', 'S', index, elements_to_restore])  # ['edit', type_of_element, insertion_index, {element_to_restore}]
                self.modify_redo_history(wiping=True)

                # Kill target
                self.s_collection[index].disconnect()
                self.s_collection[index].text.remove()
                self.s_collection[index].polygon.remove()

                # Draw
                self.s_collection[index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=[new_start, y], height=0.5, width=new_end - new_start, name=new_name, ticket='S', origin=new_origin, destiny=new_destiny, conditioned_successor=new_condition, banned_successors=new_bans, departure_time=new_departure, arrival_time=new_arrival, kmservice=new_km, facecolor=new_color, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.6)
                self.ax.add_patch(self.s_collection[index].polygon)
                self.s_collection[index].connect()
                self.canvasp.draw_idle()
                self.canvas_customisation()

                # Update plot
                self.update_plot(showstatus=False)

        else:
            self.s_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=[new_start, self.numtrains], height=0.5, width=new_end - new_start, name=new_name, ticket='S', origin=new_origin, destiny=new_destiny, conditioned_successor=new_condition, banned_successors=new_bans, departure_time=new_departure, arrival_time=new_arrival, kmservice=new_km, facecolor=new_color, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.6))
            self.ax.add_patch(self.s_collection[-1].polygon)
            self.s_collection[-1].connect()
            self.canvasp.draw_idle()
            self.canvas_customisation()
            self.modify_undo_history(['create', 'S', len(self.s_collection) - 1])
            self.modify_redo_history(wiping=True)

        self.propwindow.destroy()

        self.parent.attributes('-topmost', True)
        self.parent.attributes('-topmost', False)

    def m_properties_window(self, item, mode):
        self.propwindow = Toplevel(self.parent)
        self.propwindow.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.propwindow.configure(background=colour.WINDOW_BACKGROUNDS)
        if mode == 'Edit':
            self.propwindow.title(lang.cc42 + item.msg)
        else:
            self.propwindow.title(lang.cc43)
        wizard_icon = PhotoImage(file=relative_to_edition("icon2.png"))
        self.propwindow.iconphoto(False, wizard_icon)
        self.propwindow.bind("<Destroy>", self.popup_nullification_protocol)
        self.propwindow.focus_set()
        self.propwindow.bind('<Escape>', lambda e: self.propwindow.destroy())

        # Boton de guardado
        savebtn = Button(self.propwindow, command=lambda: self.m_edition(item, mode=mode), borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS)
        savebtn.image = PhotoImage(file=relative_to_edition('save.png'))
        savebtn.configure(image=savebtn.image)
        savebtn.pack(side='top', pady=10)

        # Entries frame
        entriesframe = Frame(master=self.propwindow, background=colour.FRAME_BACKGROUND)

        # Define entries
        entriesframe.columnconfigure(0, weight=1, uniform='equal')
        entriesframe.columnconfigure(1, weight=1, uniform='equal')
        entriesframe.columnconfigure(2, weight=1, uniform='equal')
        entriesframe.columnconfigure(3, weight=1, uniform='equal')

        if mode == 'Edit':
            Label(entriesframe, bd=2, text=lang.gui_maintname, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='ew')
            self.maint_id = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
            self.maint_id.grid(row=1, column=0, padx=20, pady=20, sticky='ew')

            Label(entriesframe, bd=2, text=lang.gui_loc, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='ew')
            self.maint_loc = Label(entriesframe, text=item.origin, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
            self.maint_loc.grid(row=1, column=1, padx=20, pady=20, sticky='ew')

        else:
            Label(entriesframe, bd=2, text=lang.gui_maintname, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, columnspan=2, ipady=10, sticky='ew')
            self.maint_id = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
            self.maint_id.grid(row=1, column=0, columnspan=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_kmlimitb, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='ew')
        self.maint_kminfo = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_kminfo.grid(row=1, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='ew')
        self.maint_dur = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_dur.grid(row=1, column=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_starttime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=0, columnspan=2, ipady=10, sticky='ew')
        # First third
        self.maint_start_day = Combobox(entriesframe, values=self.str_week, font='futura', style="Simple.TCombobox", state='readonly')
        self.maint_start_day.grid(row=3, column=0, padx=20, pady=20, sticky='ew')
        # Second third
        self.maint_start = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_start.grid(row=3, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_finishtime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=2, columnspan=2, ipady=10, sticky='ew')
        # Third third
        self.maint_end_day = Combobox(entriesframe, values=self.str_week, font='futura', style="Simple.TCombobox", state='readonly')
        self.maint_end_day.grid(row=3, column=2, padx=20, pady=20, sticky='ew')
        # Fourth third
        self.maint_end = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_end.grid(row=3, column=3, padx=20, pady=20, sticky='ew')

        if mode == 'Edit':
            self.maint_id.insert(0, item.msg)
            self.maint_kminfo.insert(0, item.kmlimit)
            self.maint_dur.insert(0, item.width)

            try:
                self.maint_start_day.set(self.str_week[int(item.polygon.xy[0][0]/24)])
            except IndexError:
                self.maint_start_day.set(self.str_week[0])
            try:
                self.maint_end_day.set(self.str_week[int(item.polygon.xy[3][0]/24)])
            except IndexError:
                self.maint_end_day.set(self.str_week[-1])

            self.maint_start.insert(0, item.departure_time)
            self.maint_end.insert(0, item.arrival_time)

        self.maint_start.bind('<FocusOut>', lambda e: live_time_parser(self.maint_start, self.maint_start_day, self.maint_end, self.maint_end_day, self.maint_dur, self.str_week, exiting=1))
        self.maint_start_day.bind('<<ComboboxSelected>>', lambda e: live_time_parser(self.maint_start, self.maint_start_day, self.maint_end, self.maint_end_day, self.maint_dur, self.str_week, exiting=1))
        self.maint_end.bind('<FocusOut>', lambda e: live_time_parser(self.maint_start, self.maint_start_day, self.maint_end, self.maint_end_day, self.maint_dur, self.str_week, exiting=2))
        self.maint_end_day.bind('<<ComboboxSelected>>', lambda e: live_time_parser(self.maint_start, self.maint_start_day, self.maint_end, self.maint_end_day, self.maint_dur, self.str_week, exiting=2))
        self.maint_dur.bind('<FocusOut>', lambda e: live_time_parser(self.maint_start, self.maint_start_day, self.maint_end, self.maint_end_day, self.maint_dur, self.str_week, exiting=3))

        entriesframe.pack(fill='both', expand=True)

    def m_edition(self, item, mode):
        something_changed = False

        # Get the data and check if something changed
        try:
            new_id = self.maint_id.get()
        except:
            messagebox.showerror(lang.cc39, lang.cc44)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        try:
            new_kmlimit = int(self.maint_kminfo.get())
        except:
            messagebox.showerror(lang.cc39, lang.cc45)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        new_dur = eval(self.maint_dur.get())
        if new_dur <= 0:
            messagebox.showerror(lang.cc39, lang.cc38)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        new_start_day = self.maint_start_day.get()
        new_departure = self.maint_start.get()
        new_end_day = self.maint_end_day.get()
        new_arrival = self.maint_end.get()

        # Some additional checking
        try:
            t = datetime.strptime(new_departure, '%H:%M').time()
        except:
            messagebox.showerror(lang.cc39,lang.cc40)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return
        new_start = 24 * self.str_week.index(new_start_day) + t.hour + t.minute / 60

        try:
            t = datetime.strptime(new_arrival, '%H:%M').time()
        except:
            messagebox.showerror(lang.cc39, lang.cc41)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return
        new_end = 24 * self.str_week.index(new_end_day) + t.hour + t.minute / 60

        # Special checking: apply common sense to durations
        if self.maint_start.cget('bg') == '#ffd28f':
            new_start = new_end - new_dur
            something_changed = True

        elif self.maint_end.cget('bg') == '#ffd28f':
            new_end = new_start + new_dur
            something_changed = True

        if mode == 'Edit':
            if new_id != item.msg:
                something_changed = True

            if new_start != item.polygon.xy[0][0] / 24:
                something_changed = True

            if new_end != item.polygon.xy[3][0] / 24:
                something_changed = True

            if new_kmlimit != item.kmlimit:
                something_changed = True

            # Create the box again
            if something_changed:
                # Get train
                y = item.polygon.xy[0][1]

                # Get some other data
                loc = item.origin
                mtext = item.mmsg
                km = item.km

                # Search substitution target
                index = self.m_collection.index(item)

                # Modify undo history
                elements_to_restore = {'bottomleft': item.bottomleft, 'width': item.width, 'name': item.msg, 'mtext': item.mmsg, 'kmlimit': item.kmlimit, 'departure_time': item.departure_time, 'arrival_time': item.arrival_time, }
                self.modify_undo_history(['edit', 'M', index, elements_to_restore])  # ['edit', type_of_element, insertion_index, {element_to_restore}]
                self.modify_redo_history(wiping=True)

                # Kill target
                self.m_collection[index].disconnect()
                self.m_collection[index].text.remove()
                self.m_collection[index].mtext.remove()
                self.m_collection[index].polygon.remove()

                # Draw
                self.m_collection[index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=[new_start, y], height=0.5, width=new_end - new_start, name=new_id, ticket='M', origin=loc, destiny=loc, hmovement=True, mtext=mtext, kmservice=km, kmlimit=new_kmlimit, departure_time=new_departure, arrival_time=new_arrival, facecolor=settings.MAINTENANCE_COLOR, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.5)
                self.ax.add_patch(self.m_collection[index].polygon)
                self.m_collection[index].connect()
                self.canvasp.draw_idle()
                self.canvas_customisation()

                # Update plot
                self.update_plot(showstatus=False)

        else:
            self.m_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=[new_start, self.numtrains], height=0.5, width=new_end - new_start, name=new_id, ticket='M', origin=None, destiny=None, hmovement=True, mtext=lang.cc32, kmservice=0, kmlimit=new_kmlimit, departure_time=new_departure, arrival_time=new_arrival, facecolor=settings.MAINTENANCE_COLOR, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.5))
            self.ax.add_patch(self.m_collection[-1].polygon)
            self.m_collection[-1].connect()
            self.canvasp.draw_idle()
            self.canvas_customisation()
            self.modify_undo_history(['create', 'M', len(self.m_collection) - 1])
            self.modify_redo_history(wiping=True)

        self.propwindow.destroy()
        self.parent.attributes('-topmost', True)
        self.parent.attributes('-topmost', False)

    def t_properties_window(self, item, mode):
        self.propwindow = Toplevel(self.parent)
        self.propwindow.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.propwindow.configure(background=colour.WINDOW_BACKGROUNDS)
        if mode == 'Edit':
            self.propwindow.title(lang.cc46 + item.msg)
        else:
            self.propwindow.title(lang.cc47)

        wizard_icon = PhotoImage(file=relative_to_edition("icon2.png"))
        self.propwindow.iconphoto(False, wizard_icon)
        self.propwindow.bind("<Destroy>", self.popup_nullification_protocol)
        self.propwindow.focus_set()
        self.propwindow.bind('<Escape>', lambda e: self.propwindow.destroy())

        # Boton de guardado
        savebtn = Button(self.propwindow, command=lambda: self.t_edition(item, mode=mode), borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS)
        savebtn.image = PhotoImage(file=relative_to_edition('save.png'))
        savebtn.configure(image=savebtn.image)
        savebtn.pack(side='top', pady=10)

        # Entries frame
        entriesframe = Frame(master=self.propwindow, background=colour.FRAME_BACKGROUND)

        # Define entries
        entriesframe.columnconfigure(0, weight=1, uniform='equal')
        entriesframe.columnconfigure(1, weight=1, uniform='equal')
        entriesframe.columnconfigure(2, weight=1, uniform='equal')
        entriesframe.columnconfigure(3, weight=1, uniform='equal')

        Label(entriesframe, bd=2, text=lang.gui_servidb, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='ew')
        self.transfer_name = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_name.grid(row=1, column=0, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_kilometers, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='ew')
        self.transfer_km = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_km.grid(row=1, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_fromsimple, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='ew')
        self.transfer_origin = AutocompleteCombobox(master=entriesframe, completevalues=self.basenodes)
        self.transfer_origin.grid(row=1, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_tosimple, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='ew')
        self.transfer_destiny = AutocompleteCombobox(master=entriesframe, completevalues=self.basenodes)
        self.transfer_destiny.grid(row=1, column=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_departuretime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=0, columnspan=2, ipady=10, sticky='ew')
        # First third
        self.transfer_dep_day = Combobox(entriesframe, values=self.str_week, font='futura', style="Simple.TCombobox", state='readonly')
        self.transfer_dep_day.grid(row=3, column=0, padx=20, pady=20, sticky='ew')
        # Second third
        self.transfer_departure = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_departure.grid(row=3, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_arrivaltime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=2, columnspan=2, ipady=10, sticky='ew')
        # Third third
        self.transfer_arr_day = Combobox(entriesframe, values=self.str_week, font='futura', style="Simple.TCombobox", state='readonly')
        self.transfer_arr_day.grid(row=3, column=2, padx=20, pady=20, sticky='ew')
        # Fourth third
        self.transfer_arrival = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_arrival.grid(row=3, column=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=0, columnspan=2, ipady=10, sticky='ew')
        self.transfer_dur = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_dur.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky='ew')


        Label(entriesframe, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=2, columnspan=2, ipady=10, sticky='ew')
        if mode == 'Edit':
            self.transfer_color = ColorEntry(entriesframe, base_color=item.polygon._original_facecolor, bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716")
        else:
            self.transfer_color = ColorEntry(entriesframe, base_color='#d6d6d6', bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716")
        self.transfer_color.grid(row=5, column=2, columnspan=2, padx=20, pady=20, sticky='ew')

        if mode == 'Edit':
            self.transfer_name.insert(0, item.msg)
            self.transfer_km.insert(0, str(item.km))

            try:
                self.transfer_dep_day.set(self.str_week[int(item.polygon.xy[0][0]/24)])
            except IndexError:
                self.transfer_dep_day.set(self.str_week[0])
            try:
                self.transfer_arr_day.set(self.str_week[int(item.polygon.xy[3][0]/24)])
            except IndexError:
                self.transfer_arr_day.set(self.str_week[-1])

            self.transfer_departure.insert(0, item.departure_time)
            self.transfer_arrival.insert(0, item.arrival_time)
            self.transfer_dur.insert(0, item.width)
            self.transfer_origin.set(item.origin)
            self.transfer_destiny.set(item.destiny)

        # self.service_departure_SV.trace_add('write', lambda var, z, e: on_change(self.service_departure, self.service_departure, self.service_dep_day, self.service_arrival, self.service_arr_day, self.service_dur, self.str_week, 1))
        self.transfer_departure.bind('<FocusOut>', lambda e: live_time_parser(self.transfer_departure, self.transfer_dep_day, self.transfer_arrival, self.transfer_arr_day, self.transfer_dur, self.str_week, exiting=1))
        self.transfer_dep_day.bind('<<ComboboxSelected>>', lambda e: live_time_parser(self.transfer_departure, self.transfer_dep_day, self.transfer_arrival, self.transfer_arr_day, self.transfer_dur, self.str_week, exiting=1))
        self.transfer_arrival.bind('<FocusOut>', lambda e: live_time_parser(self.transfer_departure, self.transfer_dep_day, self.transfer_arrival, self.transfer_arr_day, self.transfer_dur, self.str_week, exiting=2))
        self.transfer_arr_day.bind('<<ComboboxSelected>>', lambda e: live_time_parser(self.transfer_departure, self.transfer_dep_day, self.transfer_arrival, self.transfer_arr_day, self.transfer_dur, self.str_week, exiting=2))
        self.transfer_dur.bind('<FocusOut>', lambda e: live_time_parser(self.transfer_departure, self.transfer_dep_day, self.transfer_arrival, self.transfer_arr_day, self.transfer_dur, self.str_week, exiting=3))

        entriesframe.pack(fill='both', expand=True)

    def t_edition(self, item, mode):
        something_changed = False

        # Get the data and check if something changed
        try:
            new_name = self.transfer_name.get()
        except:
            messagebox.showerror(lang.cc36,lang.cc37)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        new_dur = eval(self.transfer_dur.get())
        new_km = eval(self.transfer_km.get())
        new_dep_day = self.transfer_dep_day.get()
        new_departure = self.transfer_departure.get()
        new_arr_day = self.transfer_arr_day.get()
        new_arrival = self.transfer_arrival.get()
        new_color = self.transfer_color.get()

        new_origin = self.transfer_origin.get()
        new_destiny = self.transfer_destiny.get()

        # Some additional checking
        if new_dur <= 0:
            messagebox.showerror(lang.cc36, lang.cc38)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        try:
            t = datetime.strptime(new_departure, '%H:%M').time()
        except:
            messagebox.showerror(lang.cc39,lang.cc40)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return
        new_start = 24 * self.str_week.index(new_dep_day) + t.hour + t.minute / 60

        try:
            t = datetime.strptime(new_arrival, '%H:%M').time()
        except:
            messagebox.showerror(lang.cc39, lang.cc41)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return
        new_end = 24 * self.str_week.index(new_arr_day) + t.hour + t.minute / 60

        # Special checking: apply common sense to durations
        if self.transfer_departure.cget('bg') == '#ffd28f':
            new_start = new_end - new_dur
            something_changed = True

        elif self.transfer_arrival.cget('bg') == '#ffd28f':
            new_end = new_start + new_dur
            something_changed = True

        if mode == 'Edit':
            if new_name != item.msg:
                something_changed = True

            if new_km != item.km:
                something_changed = True

            if new_start != item.polygon.xy[0][0] / 24:
                something_changed = True

            if new_end != item.polygon.xy[3][0] / 24:
                something_changed = True

            if new_origin != item.origin:
                something_changed = True

            if new_destiny != item.destiny:
                something_changed = True

            if new_color != item.polygon._original_facecolor:
                something_changed = True

            # Create the box again
            if something_changed:
                # Get train
                y = item.polygon.xy[0][1]

                # Search substitution target
                index = self.t_collection.index(item)

                # Modify undo history
                elements_to_restore = {'bottomleft': item.bottomleft, 'width': item.width, 'name': item.msg, 'origin': item.origin, 'destiny': item.destiny, 'departure_time': item.departure_time, 'arrival_time': item.arrival_time, 'kmservice': item.km, 'facecolor': item.polygon._original_facecolor}
                self.modify_undo_history(['edit', 'T', index, elements_to_restore])  # ['edit', type_of_element, insertion_index, {element_to_restore}]
                self.modify_redo_history(wiping=True)

                # Kill target
                self.t_collection[index].disconnect()
                self.t_collection[index].text.remove()
                self.t_collection[index].polygon.remove()

                # Draw
                self.t_collection[index] = ScheduleBox(parent=self, ax=self.ax, bottomleft=[new_start, y], height=0.5, width=new_end - new_start, name=new_name, ticket='T', origin=new_origin, destiny=new_destiny, conditioned_successor='', banned_successors=[], departure_time=new_departure, arrival_time=new_arrival, kmservice=new_km, facecolor=new_color, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.7, hmovement=True)
                self.ax.add_patch(self.t_collection[index].polygon)
                self.t_collection[index].connect()
                self.canvasp.draw_idle()
                self.canvas_customisation()

                # Update plot
                self.update_plot(showstatus=False)

        else:
            self.t_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=[new_start, self.numtrains], height=0.5, width=new_end - new_start, name=new_name, ticket='T', origin=new_origin, destiny=new_destiny, conditioned_successor='', banned_successors=[], departure_time=new_departure, arrival_time=new_arrival, kmservice=new_km, facecolor=new_color, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.7, hmovement=True))
            self.ax.add_patch(self.t_collection[-1].polygon)
            self.t_collection[-1].connect()
            self.canvasp.draw_idle()
            self.canvas_customisation()
            self.modify_undo_history(['create', 'T', len(self.t_collection) - 1])
            self.modify_redo_history(wiping=True)

        self.propwindow.destroy()

        self.parent.attributes('-topmost', True)
        self.parent.attributes('-topmost', False)

    def click_to_create_handler(self, column=None, properties=None):
        if self.click_to_create: # On, needs to toggle off and unbind escape event
            self.click_to_create = False
            self.parent.unbind('<Escape>')
            self.canvasp.mpl_disconnect(self.click_to_create_mplevent)

        else: # Off, needs to toggle on and bind escape event
            self.click_to_create = True
            self.parent.bind('<Escape>', lambda e: self.click_to_create_handler())
            self.click_to_create_mplevent = self.canvasp.mpl_connect('button_press_event', lambda e: self.on_click_library_creator(e, column, properties))

    def create_library_box(self, event, index, library_window):
        keyword = event.widget['text']
        if index == 0:
            properties = win_library.library['S'][keyword]

        elif index == 1:
            properties = win_library.library['M'][keyword]

        else: # index == 2:
            properties = win_library.library['T'][keyword]

        properties['name'] = keyword

        # Remove window from screen
        library_window.destroy()

        # Toggle special mouse mode
        self.click_to_create_handler(index, properties) # Continues in on_click_library_creator

    def on_click_library_creator(self, event, column, properties):
        """Wait until click event, or escape to cancel"""
        if event.inaxes != self.ax or event.button != 1:
            return

        # read coords
        x, y = event.xdata, int(event.ydata)

        # process autoduration and autolocation
        if properties['extensible']:
            prevs = [item for item in self.s_collection + self.t_collection + self.m_collection if item.polygon.xy[0][1] == y and item.polygon.xy[3][0] <= x]
            if len(prevs) > 0:
                selected = max(prevs, key=lambda item: item.polygon.xy[3][0])
                start = selected.polygon.xy[3][0]
            else:
                start = 0

            posts = [item for item in self.s_collection + self.t_collection + self.m_collection if item.polygon.xy[0][1] == y and item.polygon.xy[0][0] >= x]
            if len(posts) > 0:
                selected = min(posts, key=lambda item: item.polygon.xy[0][0])
                end = selected.polygon.xy[0][0]
            else:
                selected = max(self.s_collection + self.t_collection + self.m_collection, key=lambda item: item.polygon.xy[3][0])
                end = selected.polygon.xy[3][0]

            departure = (datetime.combine(date.today(), time()) + timedelta(hours=round(float(start), 32))).strftime('%H:%M')
            arrival = (datetime.combine(date.today(), time()) + timedelta(hours=round(float(end), 32))).strftime('%H:%M')

        elif properties['autopush'] != 'No':
            if properties['autopush'] == '\u2190': # Left
                prevs = [item for item in self.s_collection + self.t_collection + self.m_collection if item.polygon.xy[0][1] == y and item.polygon.xy[3][0] <= x]
                if len(prevs) > 0:
                    selected = max(prevs, key=lambda item: item.polygon.xy[3][0])
                    start = selected.polygon.xy[3][0]
                else:
                    start = 0
                end = start + properties['duration']

            else: # Right
                posts = [item for item in self.s_collection + self.t_collection + self.m_collection if item.polygon.xy[0][1] == y and item.polygon.xy[0][0] >= x]
                if len(posts) > 0:
                    selected = min(posts, key=lambda item: item.polygon.xy[0][0])
                    end = selected.polygon.xy[0][0]
                else:
                    selected = max(self.s_collection + self.t_collection + self.m_collection, key=lambda item: item.polygon.xy[3][0])
                    end = selected.polygon.xy[3][0]
                start = end - properties['duration']

            departure = (datetime.combine(date.today(), time()) + timedelta(hours=round(float(start), 32))).strftime('%H:%M')
            arrival = (datetime.combine(date.today(), time()) + timedelta(hours=round(float(end), 32))).strftime('%H:%M')

        else:
            if properties['start'] is not None and properties['end'] is not None:
                start = properties['start'] + 24 * (x // 24)
                end = properties['end'] + 24 * (x // 24)
            else:
                start = x
                end = x + properties['duration']

            departure = properties['departure_time'] if properties['departure_time'] != '' else (datetime.combine(date.today(), time()) + timedelta(hours=round(float(start), 32))).strftime('%H:%M')
            arrival = properties['arrival_time'] if properties['arrival_time'] != '' else (datetime.combine(date.today(), time()) + timedelta(hours=round(float(end), 32))).strftime('%H:%M')

        if column == 0:
            if properties['autolocation']:
                prevs = [item for item in self.s_collection + self.t_collection + self.m_collection if item.polygon.xy[0][1] == y and item.polygon.xy[3][0] <= x]
                if len(prevs) > 0:
                    selected = max(prevs, key=lambda item: item.polygon.xy[3][0])
                    origin = selected.destiny
                else:
                    self.click_to_create_handler()
                    messagebox.showerror(lang.cc48, lang.cc49)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

                posts = [item for item in self.s_collection + self.t_collection + self.m_collection if item.polygon.xy[0][1] == y and item.polygon.xy[0][0] >= x]
                if len(posts) > 0:
                    selected = min(posts, key=lambda item: item.polygon.xy[0][0])
                    destiny = selected.origin
                else:
                    destiny = origin  # If no subsequent element, assume stationary element

            else:
                origin = properties['origin']
                destiny = properties['destiny']

        elif column == 1:
            origin = None
            destiny = None

        else: # elif column == 2:
            if properties['autolocation']:
                prevs = [item for item in self.s_collection + self.t_collection + self.m_collection if item.polygon.xy[0][1] == y and item.polygon.xy[3][0] <= x]
                if len(prevs) > 0:
                    selected = max(prevs, key=lambda item: item.polygon.xy[3][0])
                    origin = selected.destiny
                    if properties['transfertype']:
                        destiny = origin + lang.DEPOT_MAINTENANCE if 'Depot' not in origin else origin.partition('-Depot')[0]
                    else:
                        destiny = origin + lang.DEPOT_OVERNIGHT if 'Depot' not in origin else origin.partition('-Depot')[0]

                    if 'Depot' not in origin and not self.depot_without_extras[origin]:
                        self.click_to_create_handler()
                        messagebox.showerror(lang.cc48, lang.cc50)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                else:
                    self.click_to_create_handler()
                    messagebox.showerror(lang.cc48, lang.cc49)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

            else:
                if properties['transfertype']: # Maintenance transfer
                    origin = properties['depot'] if properties['to_from_depot'] == lang.gui_todepot else properties['depot'] + lang.DEPOT_MAINTENANCE
                    destiny = properties['depot'] if properties['to_from_depot'] == lang.gui_fromdepot else properties['depot'] + lang.DEPOT_MAINTENANCE
                else: # Overnight transfer
                    origin = properties['depot'] if properties['to_from_depot'] == lang.gui_todepot else properties['depot'] + lang.DEPOT_OVERNIGHT
                    destiny = properties['depot'] if properties['to_from_depot'] == lang.gui_fromdepot else properties['depot'] + lang.DEPOT_OVERNIGHT

        # create box and register
        if column == 0:
            self.s_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=[start, y], height=0.5, width=end - start, name=properties['name'], ticket='S', origin=origin, destiny=destiny, conditioned_successor=properties['forced'], banned_successors=properties['bans'], departure_time=departure, arrival_time=arrival, kmservice=properties['km'], facecolor=properties['color'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.6))
            self.ax.add_patch(self.s_collection[-1].polygon)
            self.s_collection[-1].connect()
            self.canvasp.draw_idle()
            self.canvas_customisation()
            self.modify_undo_history(['create', 'S', len(self.s_collection) - 1])
            self.modify_redo_history(wiping=True)

        elif column == 1:
            self.m_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=[start, y], height=0.5, width=end - start, name=properties['name'], ticket='M', origin=origin, destiny=destiny, hmovement=True, mtext=lang.cc32, kmservice=0, kmlimit=properties['kmlimit'], departure_time=departure, arrival_time=arrival, facecolor=settings.MAINTENANCE_COLOR, linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.5))
            self.ax.add_patch(self.m_collection[-1].polygon)
            self.m_collection[-1].connect()
            self.canvasp.draw_idle()
            self.canvas_customisation()
            self.modify_undo_history(['create', 'M', len(self.m_collection) - 1])
            self.modify_redo_history(wiping=True)

        elif column == 2:
            self.t_collection.append(ScheduleBox(parent=self, ax=self.ax, bottomleft=[start, y], height=0.5, width=end - start, name=properties['name'], ticket='T', origin=origin, destiny=destiny, conditioned_successor='', banned_successors=[], departure_time=departure, arrival_time=arrival, kmservice=properties['km'], facecolor=properties['color'], linewidth=1.5, edgecolor=dispcolour.DISP_BOXBORDER, zorder=2.7, hmovement=True))
            self.ax.add_patch(self.t_collection[-1].polygon)
            self.t_collection[-1].connect()
            self.canvasp.draw_idle()
            self.canvas_customisation()
            self.modify_undo_history(['create', 'T', len(self.t_collection) - 1])
            self.modify_redo_history(wiping=True)

        # turn off click-to-create mode (uses your existing toggler to unbind Escape)
        self.update_plot(showstatus=False)
        self.click_to_create_handler()

    def pre_excelformatting(self, showstatus=True):
        if self.chooserw != None:
            return

        self.update_plot(showstatus=False)

        self.chooserw = Toplevel(self.parent)
        self.chooserw.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.chooserw.configure(background=colour.WINDOW_BACKGROUNDS)
        self.chooserw.title(lang.cc24)
        root_icon = PhotoImage(file=relative_to_edition("icon2.png"))
        self.chooserw.iconphoto(False, root_icon)
        self.chooserw.resizable(False, False)
        self.chooserw.bind('<Destroy>', self.chooserw_nullification_protocol)
        self.chooserw.focus_set()
        self.chooserw.bind('<Escape>', lambda e: self.chooserw.destroy())


        Label(self.chooserw, bd=2, text=lang.cc25, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).pack(padx=20, pady=(10, 0))

        self.picker = CustomCalendar(master=self.chooserw, allowed_weekdays=[lang.FULL_WEEK.index(self.str_week[0])], firstweekday='monday', locale='en_US', date_pattern='dd/mm/yyyy', background=colour.WINDOW_BACKGROUNDS, foreground=colour.TITLES_FOREGROUND, bordercolor=colour.WINDOW_BACKGROUNDS, headersbackground=colour.WINDOW_BACKGROUNDS, headersforeground=colour.TITLES_FOREGROUND, selectbackground='#fcba03', selectforeground='#000000', weekendbackground='#FFFFFF', weekendforeground='#000000', othermonthbackground='#e0e0e0', othermonthforeground='#000000', othermonthwebackground='#e0e0e0ng', othermonthweforeground='#000000', normalbackground='#FFFFFF', normalforeground='#000000', disableddaybackground='#345270', disableddayforeground='#FFFFFF')
        self.picker.pack(padx=20, pady=(10, 0))

        btn = Button(master=self.chooserw, command=lambda: self.excelformatting(showstatus), relief='flat', background=colour.WINDOW_BACKGROUNDS)
        btn.image = PhotoImage(file=relative_to_edition('save.png'))
        btn.configure(image=btn.image) # Needs extra garbage collection and an image of 30x30
        btn.pack(padx=20, pady=(10, 20))
    
    def excelformatting(self, showstatus=True):
        today = self.picker.get_date() # noqa
        self.chooserw.destroy()

        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        here = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        # Poder elegir la ruta del archivo de manera intuitiva y amigable
        file = filedialog.asksaveasfile(initialfile='untitled.xlsx', initialdir=here, defaultextension='.xlsx', filetypes=[("Excel workbook", ".xlsx"), ("All files", ".*")])
        # No quiso crear archivo
        if file is None:
            return
        location = file.name
        file.close()

        try:
            workbook = xlsx.Workbook(location)
            format_topdates = workbook.add_format({'bold':True, 'font_name':'Arial Black', 'font_size':12, 'align':'center', 'valign':'vcenter', 'bg_color':'#ffff00', 'border':2})
            format_hourheader = workbook.add_format({'bold':True, 'font_name':'Arial', 'font_size':12, 'align':'center', 'valign':'vcenter', 'bg_color':'#ffff99', 'border':2})
            format_trainheader = workbook.add_format({'bold':True, 'font_name':'Arial Narrow', 'font_size':8, 'font_color':'#0000ff', 'align':'center', 'valign':'vcenter', 'border':2})
            format_trainid = workbook.add_format({'bold':True, 'font_name':'Arial', 'font_size':14, 'font_color':'#0000ff', 'align':'center', 'valign':'vcenter', 'bg_color':'#b8cce4', 'border':2})

            format_just100 = workbook.add_format({'font_name': 'Arial', 'font_size': 10})
            format_just85 = workbook.add_format({'font_name':'Arial', 'font_size':8.5})
            format_just80 = workbook.add_format({'font_name':'Arial', 'font_size':8})
            format_just70 = workbook.add_format({'font_name':'Arial', 'font_size':7})
            format_justbold100 = workbook.add_format({'bold': True, 'font_name': 'Arial', 'font_size': 10})
            format_justbold85 = workbook.add_format({'bold':True, 'font_name':'Arial', 'font_size':8.5})
            format_justbold80 = workbook.add_format({'bold':True, 'font_name':'Arial', 'font_size':8})

            format_softlow = workbook.add_format({'bottom':1})
            format_hardright = workbook.add_format({'right':2})
            format_softlow_hardright = workbook.add_format({'bottom':1, 'right':2})

            format_maintenance = workbook.add_format({'bold':True, 'font_name':'Arial', 'font_size':12, 'align':'center', 'valign':'vcenter', 'border':2, 'bg_color':settings.MAINTENANCE_COLOR})

            format_serviceid = workbook.add_format({'bold':True, 'font_name':'Arial', 'font_size':12, 'align':'center', 'valign':'vcenter', 'border':2})
            format_serviceinfo100 = workbook.add_format({'font_name':'Arial', 'font_size':10, 'align':'center', 'valign':'vcenter'})
            format_serviceinfo85 = workbook.add_format({'font_name':'Arial', 'font_size':8.5, 'align':'center', 'valign':'vcenter'})
            format_serviceinfo80 = workbook.add_format({'font_name':'Arial', 'font_size':8, 'align':'center', 'valign':'vcenter'})
            format_serviceinfo70 = workbook.add_format({'font_name':'Arial', 'font_size':7, 'align':'center', 'valign':'vcenter'})
            format_serviceinfo100_hardright = workbook.add_format({'font_name':'Arial', 'font_size':10, 'align':'center', 'valign':'vcenter', 'right':2})
            format_serviceinfo85_hardright = workbook.add_format({'font_name':'Arial', 'font_size':8.5, 'align':'center', 'valign':'vcenter', 'right':2})
            format_serviceinfo80_hardright = workbook.add_format({'font_name':'Arial', 'font_size':8, 'align':'center', 'valign':'vcenter', 'right':2})
            format_serviceinfo70_hardright = workbook.add_format({'font_name':'Arial', 'font_size':7, 'align':'center', 'valign':'vcenter', 'right':2})

            format_services = {}
            for service in self.s_collection + self.t_collection:
                if service.msg in format_services:
                    continue
                else:
                    format_services[service.msg] = workbook.add_format({'bg_color':service.polygon._original_facecolor, 'border':2}) # noqa

            days = len(self.str_week)
            today = datetime.strptime(today, '%d/%m/%Y')
            all_dates = [today + timedelta(hours=int(24*i)) for i in range(days)]
            all_dates = [date.strftime(format='%d/%m/%Y') for date in all_dates]

            # An auxiliar:
            latest_position = ['?' for _ in range(self.numtrains)]

            for day in range(days):
                occupied_slots = np.zeros(shape=(self.numtrains, 144), dtype=np.int8)
                sheet = workbook.add_worksheet(self.str_week[day])

                sheet.set_column(0, 0, 14)
                sheet.set_column(1, 1, 4)
                sheet.set_column(2, 145, 1.22)
                sheet.set_column(146, 146, 4)
                sheet.set_column(147, 148, 1.22)

                sheet.set_row(0, 11)
                sheet.set_row(1, 19.2)
                sheet.set_row(2, 32.4)

                # Date Header
                sheet.merge_range(1, 0, 1, 1, self.str_week[day], format_topdates)
                sheet.merge_range(1, 2, 1, 25, all_dates[day], format_topdates)

                # Train header
                sheet.merge_range(2, 0, 2, 1, '', format_trainheader)
                sheet.insert_image(2, 0, relative_to_navtoolbarassets('talgo_logo.png'))

                # Hours 1 - 24
                sheet.merge_range(2, 2, 2, 7, 0, format_hourheader) # 1
                sheet.merge_range(2, 8, 2, 13, 1, format_hourheader) # 2
                sheet.merge_range(2, 14, 2, 19, 2, format_hourheader) # 3
                sheet.merge_range(2, 20, 2, 25, 3, format_hourheader) # 4
                sheet.merge_range(2, 26, 2, 31, 4, format_hourheader) # 5
                sheet.merge_range(2, 32, 2, 37, 5, format_hourheader) # 6
                sheet.merge_range(2, 38, 2, 43, 6, format_hourheader) # 7
                sheet.merge_range(2, 44, 2, 49, 7, format_hourheader) # 8
                sheet.merge_range(2, 50, 2, 55, 8, format_hourheader) # 9
                sheet.merge_range(2, 56, 2, 61, 9, format_hourheader) # 10
                sheet.merge_range(2, 62, 2, 67, 10, format_hourheader) # 11
                sheet.merge_range(2, 68, 2, 73, 11, format_hourheader) # 12
                sheet.merge_range(2, 74, 2, 79, 12, format_hourheader) # 13
                sheet.merge_range(2, 80, 2, 85, 13, format_hourheader) # 14
                sheet.merge_range(2, 86, 2, 91, 14, format_hourheader) # 15
                sheet.merge_range(2, 92, 2, 97, 15, format_hourheader) # 16
                sheet.merge_range(2, 98, 2, 103, 16, format_hourheader) # 17
                sheet.merge_range(2, 104, 2, 109, 17, format_hourheader) # 18
                sheet.merge_range(2, 110, 2, 115, 18, format_hourheader) # 19
                sheet.merge_range(2, 116, 2, 121, 19, format_hourheader) # 20
                sheet.merge_range(2, 122, 2, 127, 20, format_hourheader) # 21
                sheet.merge_range(2, 128, 2, 133, 21, format_hourheader) # 22
                sheet.merge_range(2, 134, 2, 139, 22, format_hourheader) # 23
                sheet.merge_range(2, 140, 2, 145, 23, format_hourheader) # 24

                # Hard Right table border
                for row in range(3, self.numtrains * 4 + 3):
                    sheet.write_blank(row, 145, '', format_hardright)

                # Services & Maintenance
                row = 3
                for train in range(self.numtrains):
                    real_y = self.refypos - train

                    sheet.set_row(row, 9)
                    sheet.set_row(row+1, 16.2)
                    sheet.set_row(row+2, 10.8)
                    sheet.set_row(row+3, 4.5)

                    # Train ID
                    sheet.merge_range(row, 0, row+3, 0, self.trainid['train' + str(train+1)], format_trainid)

                    # First location (If day > 0)
                    if day > 0:
                        sheet.merge_range(row, 1, row + 3, 1, self.shortenings[latest_position[train]], format_serviceid)

                    # Format line
                    for col in range(2, 145):
                        sheet.write_blank(row+3, col, '', format_softlow)
                    sheet.write_blank(row+3, 145, '', format_softlow_hardright)

                    # Draw services
                    for service in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]):
                        # Proving validity of service
                        if service.polygon.xy[0][1] == real_y:

                            # Starting on a previous day, or at 0:00
                            if service.polygon.xy[0][0] <= 24 * day:
                                departure = 2
                                str_departure_time = '00:00'
                                # Finishes AFTER this day
                                if service.polygon.xy[3][0] >= 24 * (day + 1):
                                    arrival = 145
                                    str_arrival_time = '00:00'
                                # Finishes THIS day
                                elif 24 * (day + 1) > service.polygon.xy[3][0] > 24 * day:
                                    arrival = hour_string_to_excel_position(service.arrival_time) + 2 # 2 cells offset (headers)
                                    str_arrival_time = service.arrival_time
                                # (Other) Finished on a previous day, or today at 0:00
                                else:
                                    continue

                            # Starting this day (Not at 0:00)
                            elif 24 * (day + 1) > service.polygon.xy[0][0] > 24 * day:
                                departure = hour_string_to_excel_position(service.departure_time) + 2 # 2 cells offset (headers)
                                str_departure_time = service.departure_time
                                # Finishes AFTER this day
                                if service.polygon.xy[3][0] >= 24 * (day + 1):
                                    arrival = 145
                                    str_arrival_time = '00:00'
                                # Finishes THIS day
                                elif 24 * (day + 1) > service.polygon.xy[3][0] > 24 * day:
                                    arrival = hour_string_to_excel_position(service.arrival_time) + 2 # 2 cells offset (headers)
                                    str_arrival_time = service.arrival_time

                            elif service.polygon.xy[0][0] >= 24 * (day + 1):
                                break

                            # Check that there is no overlapping
                            while occupied_slots[train, departure-2] == 1: # noqa
                                departure += 1
                                if departure > 145:
                                    break

                            while occupied_slots[train, arrival-2] == 1: # noqa
                                arrival -= 1
                                if arrival < 2:
                                    break

                            if departure > arrival:
                                arrival = departure

                            occupied_slots[train, departure-2:arrival-1] = 1 # -2 (offset not considered in arrays); latest index is ignored when slicing in python, so -2+1 = -1 to make sure its included if needed; in other words, Here is -2 then is -1, because when slicing we dont get the last position

                            # First location (If it is day 0, and departure time 0)
                            if day == 0 and departure == 2:
                                sheet.merge_range(row, 1, row + 3, 1, self.shortenings[service.origin], format_serviceid)

                            # Avoided breaks and continues. The latest position according to services should be safe to save
                            latest_position[train] = service.destiny

                            # ID
                            if arrival != departure:
                                print('+++', service.polygon.xy[0][0], service.polygon.xy[0][1], service.msg, departure, arrival)
                                sheet.merge_range(row+1, departure, row+1, arrival, service.msg, format_serviceid)
                            else:
                                print('|||', service.polygon.xy[0][0], service.polygon.xy[0][1], service.msg, departure, arrival)
                                sheet.write(row+1, departure, service.msg, format_serviceid)

                            # Formating hour and location tag
                            if arrival - departure + 1 >= 9: # >= 9 cells or more, write all fontsize 10
                                if arrival != 145:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo100)
                                    if service.ticket == 'S': sheet.write_rich_string(row+2, departure, format_justbold100, self.shortenings[service.origin], format_just100, ' ' + str_departure_time + ' - ' + str_arrival_time + ' ', format_justbold100, self.shortenings[service.destiny], format_serviceinfo100) # noqa
                                else:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo100_hardright)
                                    if service.ticket == 'S': sheet.write_rich_string(row+2, departure, format_justbold100, self.shortenings[service.origin], format_just100, ' ' + str_departure_time + ' - ' + str_arrival_time + ' ', format_justbold100, self.shortenings[service.destiny], format_serviceinfo100_hardright)

                            elif 9 > arrival - departure + 1 >= 8: # >= 8 cells or more, write all fontsize 8.5
                                if arrival != 145:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo85)
                                    if service.ticket == 'S': sheet.write_rich_string(row+2, departure, format_justbold85, self.shortenings[service.origin], format_just85, ' ' + str_departure_time + ' - ' + str_arrival_time + ' ', format_justbold85, self.shortenings[service.destiny], format_serviceinfo85)
                                else:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo85_hardright)
                                    if service.ticket == 'S': sheet.write_rich_string(row+2, departure, format_justbold85, self.shortenings[service.origin], format_just85, ' ' + str_departure_time + ' - ' + str_arrival_time + ' ', format_justbold85, self.shortenings[service.destiny], format_serviceinfo85_hardright)

                            elif 8 > arrival - departure + 1 >= 7: # >= 7 cells, write all fontsize 8
                                if arrival != 145:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo80)
                                    if service.ticket == 'S': sheet.write_rich_string(row+2, departure, format_justbold80, self.shortenings[service.origin], format_just80, ' ' + str_departure_time + ' - ' + str_arrival_time + ' ', format_justbold80, self.shortenings[service.destiny], format_serviceinfo80)
                                else:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo80_hardright)
                                    if service.ticket == 'S': sheet.write_rich_string(row+2, departure, format_justbold80, self.shortenings[service.origin], format_just80, ' ' + str_departure_time + ' - ' + str_arrival_time + ' ', format_justbold80, self.shortenings[service.destiny], format_serviceinfo80_hardright)

                            elif 7 > arrival - departure + 1 >= 5: # >= 5 cells, write time fontsize 8
                                if arrival != 145:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo80)
                                    if service.ticket == 'S': sheet.write_string(row+2, departure, str_departure_time + ' - ' + str_arrival_time, format_just80)
                                else:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo80_hardright)
                                    if service.ticket == 'S': sheet.write_string(row+2, departure, str_departure_time + ' - ' + str_arrival_time, format_just80)

                            elif 5 > arrival - departure + 1 >= 4: # >= 4 cells, write time fontsize 7
                                if arrival != 145:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo70)
                                    if service.ticket == 'S': sheet.write_string(row+2, departure, str_departure_time + ' - ' + str_arrival_time, format_just70)
                                else:
                                    sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo70_hardright)
                                    if service.ticket == 'S': sheet.write_string(row+2, departure, str_departure_time + ' - ' + str_arrival_time, format_just70)

                            else: # Don't write, less than 4 cells
                                if arrival != 145:
                                    if arrival != departure:
                                        sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo70)
                                    else:
                                        sheet.write(row+2, departure, '', format_serviceinfo70)
                                else:
                                    if arrival != departure:
                                        sheet.merge_range(row+2, departure, row+2, arrival, '', format_serviceinfo70_hardright)
                                    else:
                                        sheet.write(row+2, departure, '', format_serviceinfo70_hardright)

                            # Service distinctive color
                            if arrival != departure:
                                sheet.merge_range(row + 3, departure, row + 3, arrival, '', format_services[service.msg])
                            else:
                                sheet.write(row+3, departure, '', format_services[service.msg])

                    for maint in sorted(self.m_collection, key=lambda item: item.polygon.xy[0][0]):
                        # Proving validity of service
                        if maint.polygon.xy[0][1] == real_y:
                            # Starting on a previous day, or at 0:00
                            if maint.polygon.xy[0][0] <= 24 * day:
                                departure = 2
                                # Finishes AFTER this day
                                if maint.polygon.xy[3][0] >= 24 * (day + 1):
                                    arrival = 145
                                # Finishes THIS day
                                elif 24 * (day + 1) > maint.polygon.xy[3][0] > 24 * day:
                                    arrival = hour_string_to_excel_position(maint.arrival_time) + 2 # 2 cells offset (headers)
                                # (Other) Finished on a previous day, or today at 0:00
                                else:
                                    continue

                            # Starting this day (Not at 0:00)
                            elif 24 * (day + 1) > maint.polygon.xy[0][0] > 24 * day:
                                departure = hour_string_to_excel_position(maint.departure_time) + 2 # 2 cells offset (headers)
                                # Finishes AFTER this day
                                if maint.polygon.xy[3][0] >= 24 * (day + 1):
                                    arrival = 145
                                # Finishes THIS day
                                elif 24 * (day + 1) > maint.polygon.xy[3][0] > 24 * day:
                                    arrival = hour_string_to_excel_position(maint.arrival_time) + 2 # 2 cells offset (headers)

                            elif maint.polygon.xy[0][0] >= 24 * (day + 1):
                                break

                            # Now, we must check that the required slots are free
                            desired_slice = occupied_slots[train, departure-2:arrival-1]
                            key_value = desired_slice.max()

                            # Special case: only takes a few minutes from and overlapping exists, at the beginning/end of the day. This can also happen later
                            if key_value == 1 and arrival == departure:
                                continue

                            # Check if there is overlapping with other boxes
                            _continue_flag = False
                            while key_value == 1:
                                # Overlapping at departure
                                if desired_slice.argmax() == 0:
                                    departure += 1
                                    desired_slice = np.delete(desired_slice, [0])
                                # Overlapping at arrival
                                else:
                                    arrival -= 1
                                    desired_slice = np.delete(desired_slice, [-1])

                                # New key value
                                if desired_slice.size == 0: # This happens when the maintenance overlaps with the transfer to depot at the beginning/end of the day (this usually doesnt span many cells), so we skip this' day representation; the maintenance will be painted at other time anyways.
                                    _continue_flag = True
                                    break
                                key_value = desired_slice.max()

                            if _continue_flag:
                                continue

                            # Maintenance name
                            if arrival != departure:
                                sheet.merge_range(row+1, departure, row+1, arrival, maint.msg, format_maintenance)
                            else:
                                sheet.write(row+1, departure, maint.msg, format_maintenance)

                            # Maintenance duration tag
                            if arrival - departure + 1 >= 5: # >= 5 cells, fontsize 10
                                if arrival != 145:
                                    sheet.merge_range(row + 2, departure, row + 2, arrival, str(maint.width) + ' Hours', format_serviceinfo100) if settings.MDURATION_TO_EXCEL else sheet.merge_range(row + 2, departure, row + 2, arrival, '', format_serviceinfo100)
                                else:
                                    sheet.merge_range(row + 2, departure, row + 2, arrival, str(maint.width) + ' Hours', format_serviceinfo100_hardright) if settings.MDURATION_TO_EXCEL else sheet.merge_range(row + 2, departure, row + 2, arrival, '', format_serviceinfo100_hardright)

                            else: # < 5 cells, fontsize 8.5
                                if arrival != 145:
                                    if arrival != departure:
                                        sheet.merge_range(row + 2, departure, row + 2, arrival, str(maint.width) + ' Hours', format_serviceinfo85) if settings.MDURATION_TO_EXCEL else sheet.merge_range(row + 2, departure, row + 2, arrival, '', format_serviceinfo85)
                                    else:
                                        sheet.write(row + 2, departure, str(maint.width) + ' Hours', format_serviceinfo85) if settings.MDURATION_TO_EXCEL else sheet.write(row + 2, departure, '', format_serviceinfo85)
                                else:
                                    if arrival != departure:
                                        sheet.merge_range(row + 2, departure, row + 2, arrival, str(maint.width) + ' Hours', format_serviceinfo85_hardright) if settings.MDURATION_TO_EXCEL else sheet.merge_range(row + 2, departure, row + 2, arrival, '', format_serviceinfo85_hardright)
                                    else:
                                        sheet.write(row + 2, departure, str(maint.width) + ' Hours', format_serviceinfo85_hardright) if settings.MDURATION_TO_EXCEL else sheet.write(row + 2, departure, '', format_serviceinfo85_hardright)

                            # Maintenance distinctive color
                            if arrival != departure:
                                sheet.merge_range(row + 3, departure, row + 3, arrival, '', format_maintenance)
                            else:
                                sheet.write(row+3, departure, '', format_maintenance)

                    # Specify latest location, after managing services
                    sheet.merge_range(row, 146, row+3, 146, self.shortenings[latest_position[train]], format_serviceid) # noqa
                    row += 4

                # Setup and visibility features
                sheet.ignore_errors({'number_stored_as_text': 'A:ES'})
                sheet.freeze_panes(3, 2)
                sheet.set_zoom(67)

                sheet.set_landscape()
                sheet.center_horizontally()
                sheet.set_paper(9)
                sheet.set_margins(0.1, 0, 0, 0)
                sheet.fit_to_pages(1, 0)

            workbook.close()

            if showstatus:
                messagebox.showinfo(lang.cc51, lang.cc52 + location)
                self.parent.lift()

        except:
            error = traceback.format_exc()
            messagebox.showerror(lang.cc53, lang.cc54 + str(error))
            self.parent.lift()

    # TODO this function has lacked maintenance for a long time
    def exportresults(self, showstatus=True):
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        here = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        # Poder elegir la ruta del archivo de manera intuitiva y amigable
        file = filedialog.asksaveasfile(initialfile='untitled.xlsx', initialdir=here, defaultextension='.xlsx', filetypes=[("Excel workbook", ".xlsx"), ("All files", ".*")])
        # No quiso crear archivo
        if file is None:
            return
        location = file.name

        file.close()

        self.update_plot(showstatus=False)

        workbook = xlsx.Workbook(location)

        format_lowerborder = workbook.add_format({'bottom':2})
        format_rightborder = workbook.add_format({'right':2})
        format_services = {}
        for service in self.s_collection + self.t_collection:
            if service.msg in format_services:
                continue
            else:
                format_services[service.msg] = workbook.add_format({'bg_color':service.polygon._original_facecolor, 'border':2}) # noqa


        clean_ids = [self.trainid[train] for train in self.trainid]
        clean_ids.reverse()

        # Service sheet
        services_sheet = workbook.add_worksheet('Services')
        services_sheet.write_column(0, 0, ['Name', 'Departure time', 'Origin', 'Arrival time', 'Destiny'], format_rightborder)
        services_sheet.write_column(5, 0, clean_ids, format_rightborder)
        col = 0
        for service in sorted(self.s_collection + self.t_collection, key=lambda item: item.polygon.xy[0][0]):
            col += 1

            time, train = service.polygon.xy[0][0], int(service.polygon.xy[0][1])

            dep_days = str(int(time/24))
            dep_time = dep_days + 'd ' + service.departure_time

            time += service.width

            arr_days = str(int(time / 24))
            arr_time = arr_days + 'd ' + service.arrival_time

            services_sheet.write(0, col, service.msg, format_services[service.msg])
            services_sheet.write(1, col, dep_time)
            services_sheet.write(2, col, service.origin)
            services_sheet.write(3, col, arr_time)
            services_sheet.write(4, col, service.destiny, format_lowerborder)

            train += 5
            for row in range(5, self.numtrains + 5):
                if train == row: # Done by this train
                    services_sheet.write(row, col, 1, format_services[service.msg])
                else: # Not done by this train
                    services_sheet.write(row, col, 0)

        services_sheet.freeze_panes(5, 1)

        # Maintenance sheet
        maintenance_sheet = workbook.add_worksheet('Maintenance')
        maintenance_sheet.write_row(0, 1, ['Name', 'Start', 'Finish', 'Location', 'Km'], format_lowerborder)
        row = 0
        for train in range(self.numtrains):
            for maint in sorted(self.m_collection, key=lambda item: item.polygon.xy[0][0]):
                time, ypos = maint.polygon.xy[0][0], self.refypos - int(maint.polygon.xy[0][1])
                if train == ypos:
                    row += 1

                    dep_days = str(int(time/24))
                    dep_time = dep_days + 'd ' + maint.departure_time

                    time += maint.width

                    arr_days = str(int(time / 24))
                    arr_time = arr_days + 'd ' + maint.arrival_time


                    maintenance_sheet.write(row, 0, self.trainid['train' + str(train + 1)], format_rightborder)
                    maintenance_sheet.write(row, 1, maint.msg)
                    maintenance_sheet.write(row, 2, dep_time)
                    maintenance_sheet.write(row, 3, arr_time)
                    maintenance_sheet.write(row, 4, maint.origin)
                    maintenance_sheet.write(row, 5, maint.mmsg)

        maintenance_sheet.freeze_panes(1, 1)

        workbook.close()

        if showstatus:
            messagebox.showinfo(lang.cc51, lang.cc55 + location)
            self.parent.lift()

    def store_solution(self):
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0  # Get current, not default value
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        here = ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)

        file = filedialog.asksaveasfile(initialfile='untitled.FSsolved', initialdir=here, defaultextension='.FSsolved', filetypes=[("FleetScheduler solution", ".FSsolved"), ("JSON file", ".json"), ("All files", ".*")])
        if file is None:
            self.parent.attributes('-topmost', True)
            self.parent.attributes('-topmost', False)
            return

        try:
            self.update_plot(showstatus=False)
            services = {}
            i = 0
            for service in sorted(self.s_collection, key=lambda item: item.polygon.xy[0][0]):
                i += 1
                services['s' + str(i)] = [
                    list(service.polygon.xy[0]), # 0
                    service.width, # 1
                    service.msg, # 2
                    service.km, # 3
                    service.origin, # 4
                    service.destiny, # 5
                    service.conditioned_successor, # 6
                    service.departure_time, # 7
                    service.arrival_time, # 8
                    service.polygon._original_facecolor, # noqa 9
                    service.banned_successors # 10
                ]

            maintenances = {}
            i = 0
            for maint in sorted(self.m_collection, key=lambda item: item.polygon.xy[0][0]):
                i += 1
                maintenances['m' + str(i)] = [
                    list(maint.polygon.xy[0]), # 0
                    float(maint.width), # 1
                    maint.msg, # 2
                    maint.mmsg, # 3
                    maint.km, # 4
                    int(maint.kmlimit) # 5
                ]
            transfers = {}
            i = 0
            for transfer in sorted(self.t_collection, key=lambda item: item.polygon.xy[0][0]):
                i += 1
                transfers['t' + str(i)] = [
                    list(transfer.polygon.xy[0]), # 0
                    transfer.width, # 1
                    transfer.msg, # 2
                    transfer.km, # 3
                    transfer.origin, # 4
                    transfer.destiny, # 5
                    transfer.polygon._original_facecolor # noqa 6
                ]

            exportable = {
                'services': services,
                'maintenances': maintenances,
                'transfers': transfers,
                'baseservices': self.baseservices,
                'basenodes': self.basenodes_without_extras,
                'shortenings': self.shortenings_without_extras,
                'numtrains': self.numtrains,
                'starting_day': self.starting_day,
                'str_week': self.str_week,
                'trainid': self.trainid,
                'km_limit': self.km_limit,
                'depot': self.depot_without_extras,
                'maintenance_name': self.maintenance_name,
                'maintenance_duration': self.maintenance_duration,
                'basetransfers': self.basetransfers,
                'basesleepers': self.basesleepers,
                'baselinkers': self.baselinkers
            }

            for path, val, typ in find_non_jsonables(exportable, max_find=100):
                print(path_to_str(path), "type=", typ, "repr=", repr(val)[:200])

            json.dump(exportable, file, indent=6) # TODO eso del indent no se que tal queda

        except:
            error = traceback.format_exc()
            messagebox.showerror(lang.error_saving, lang.cc56 + str(error))
            self.parent.attributes('-topmost', True)
            self.parent.attributes('-topmost', False)


        file.close()
        if settings.SAVELOAD_CONFIRMATION:
            messagebox.showinfo(lang.cc57, lang.cc58 + str(file))

        self.parent.attributes('-topmost', True)
        self.parent.attributes('-topmost', False)
        return
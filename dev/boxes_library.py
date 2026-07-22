'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        boxes_library.py

 Author:      Diego Pérez

 Created:     19/10/2025
 Copyright:   (c) perez 2025
-------------------------------------------------------------------------------
'''

from copy import deepcopy
import traceback
from tkinter import Toplevel, Entry, Button, Frame, Label, PhotoImage, messagebox
from tkinter.ttk import Combobox, Style
import ast
from datetime import datetime, timedelta, time, date
from tkwidgets import ScrollableFrame, AutocompleteCombobox, ColorEntry, FancyCheckButton
import json

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
combostyle.map('Custom.TCombobox',
              fieldbackground=[('disabled', '#eeeeee')],
              background=[('disabled', '#f0f0f0')],
              foreground=[('disabled', '#7a7a7a')],
              arrowcolor=[('disabled', '#7a7a7a')]
               )

library = {'S':{}, 'M':{}, 'T':{}}

def relative_to_services(path: str) -> Path:
    return OUTPUT_PATH / Path(path)

settingspath = Path(__file__).parent / Path(r".\settings")
def relative_to_settings(path: str) -> Path:
    return settingspath / Path(path)

# def live_time_parser(departure, extra_arrival, arrival, duration, exiting): # TODO ojo con lo de "Live-update" porque todavía no es que estñe muy implementado. Hay q abrir ticket en SO?
#     departure_time = departure.get()
#     if departure_time != '':
#         try:
#             t = datetime.strptime(departure_time, '%H:%M').time()
#             numerical_departure = t.hour + t.minute / 60
#         except:
#             departure_time = ''
#
#     arrival_time = arrival.get()
#     if arrival_time != '':
#         try:
#             t = datetime.strptime(arrival_time, '%H:%M').time()
#             try:
#                 extra_t = 24 * int(extra_arrival.get())
#             except:
#                 extra_t = 0
#             numerical_arrival = extra_t + t.hour + t.minute / 60
#         except:
#             arrival_time = ''
#
#     duration_time = duration.get()
#     if duration_time != '':
#         try:
#             numerical_duration = float(duration_time)
#         except:
#             duration_time = ''
#
#     # Exiting codes:
#     # 1 -> Departure time
#     # 2 -> Arrival time
#     # 3 -> Duration
#     if exiting == 1: # Combines departure and duration
#         if departure_time != '' and duration_time != '':
#             arrival.delete(0, 'end')
#             extra_arrival.delete(0, 'end')
#             h, m = departure_time.split(':')
#             st = datetime.combine(date.today(), time(int(h), int(m)))
#             end = st + timedelta(hours=round(float(numerical_duration), 32)) # noqa
#             dif = (end.date() - st.date()).days
#             extra_arrival.insert(0, str(dif))
#             arrival.insert(0, (end).strftime('%H:%M'))
#
#     elif exiting == 2: # Combines arrival and duration
#         if arrival_time != '' and duration_time != '':
#             departure.delete(0, 'end')
#             h, m = arrival_time.split(':')
#             end = datetime.combine(date.today(), time(int(h), int(m)))
#             st = end - timedelta(hours=round(float(numerical_duration), 32)) # noqa
#             departure.insert(0, (datetime.combine(date.today(), time(int(h), int(m))) - timedelta(hours=round(float(numerical_duration), 32))).strftime('%H:%M')) # noqa
#
#     elif exiting == 3: # Uses whatever combination possible, prioritising departure + duration
#         if departure_time != '' and duration_time != '':
#             arrival.delete(0, 'end')
#             extra_arrival.delete(0, 'end')
#             h, m = departure_time.split(':')
#             st = datetime.combine(date.today(), time(int(h), int(m)))
#             end = st + timedelta(hours=round(float(numerical_duration), 32)) # noqa
#             dif = (end.date() - st.date()).days
#             extra_arrival.insert(0, str(dif))
#             arrival.insert(0, (end).strftime('%H:%M'))
#
#         elif arrival_time != '' and duration_time != '':
#             departure.delete(0, 'end')
#             h, m = arrival_time.split(':')
#             end = datetime.combine(date.today(), time(int(h), int(m)))
#             st = end - timedelta(hours=round(float(numerical_duration), 32)) # noqa
#             departure.insert(0, (datetime.combine(date.today(), time(int(h), int(m))) - timedelta(hours=round(float(numerical_duration), 32))).strftime('%H:%M')) # noqa

class library_ScrollableFrame(ScrollableFrame):
    def addNewLabel(self, index): # noqa
        # New template indicator
        self.entries[index].append(Label(self, text='Undefined', bd=2, highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, relief='flat', bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)) # TODO append a new label that reperesents a new box template
        self.entries[index][-1].grid(row=len(self.entries[index]) * 2, column=index * 2, padx=10, sticky='ew')
        if self.parent is None:
            self.entries[index][-1].bind("<Button-1>", lambda e: self.summon_properties_window(e, index))
            self.entries[index][-1].bind("<Button-3>", lambda e: self.summon_properties_window(e, index))
        else:
            self.entries[index][-1].bind("<Button-3>", lambda e: self.summon_properties_window(e, index))
            self.entries[index][-1].bind("<Button-1>", lambda e: self.parent.create_library_box(e, index, self.root)) # TODO also depending on column

        # Basket
        self.basket[index].append(Label(self, text='\U0001F5D1', bd=2, highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, relief='flat', bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, width=3))
        self.basket[index][-1].bind("<Button-1>", lambda e: self.deleterow(e, index))
        self.basket[index][-1].grid(row=len(self.entries[index]) * 2, column=index * 2 + 1, padx=(5, 25), sticky='ew')

        # Adding a spacer
        self.falselabels[index].append(Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1))
        self.falselabels[index][-1].grid(row=len(self.entries[index]) * 2 + 1, column=index * 2, columnspan=2, sticky='ew')

        # Update the scroll region after new widgets are added
        self.updateScrollRegion()

    def deleterow(self, event, col_index):
        widget = event.widget
        self.deleter = messagebox.askyesno(lang.generic_deletion, lang.generic_confirmdeletion)
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)
        if self.deleter: # Delete
            index = self.basket[col_index].index(widget)
            self.destroy_row(index, col_index)

    def destroy_row(self, index, col_index): # TODO añadir la destruccion dentro de la librería, pushear cambios al JSON
        global library

        name = self.entries[col_index][index]['text']
        self.entries[col_index][index].grid_forget()
        del self.entries[col_index][index]

        self.falselabels[col_index][index].grid_forget()
        self.basket[col_index][index].grid_forget()

        del self.falselabels[col_index][index]
        del self.basket[col_index][index]

        if name != 'Undefined':
            if col_index == 0:
                del library['S'][name]
            elif col_index == 1:
                del library['M'][name]
            else: # elif col_index == 2:
                del library['T'][name]

            try:
                p = relative_to_settings('library.json')
                with p.open('w', encoding='utf-8') as f:
                    json.dump(library, f, indent=4)
            except:
                messagebox.showerror(lang.liberror17, lang.liberror18)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

        self.updateScrollRegion()
        self.root.lift()

    def __init__(self, winmaster, fullcanvas_parent, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.entries = [[] for _ in range(3)]
        self.falselabels = [[] for _ in range(3)]
        self.basket = [[] for _ in range(3)]
        self.parent = fullcanvas_parent
        self.propwindow = None

        # Define headers
        fakelabel1 = Label(self, text="", bg=colour.TITLES_BACKGROUND)
        btn1 = Button(fakelabel1, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND, command=lambda: self.addNewLabel(0))
        btn1.image = PhotoImage(file=relative_to_services('addrow.png'))
        btn1.configure(image=btn1.image)
        btn1.pack()

        fakelabel1.grid(row=0, column=0, columnspan=2, sticky='ew')
        self.columnconfigure(0, weight=8)
        self.columnconfigure(1, weight=1)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, columnspan=2, sticky='w')

        fakelabel2 = Label(self, text="", bg=colour.TITLES_BACKGROUND)
        btn2 = Button(fakelabel2, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND, command=lambda: self.addNewLabel(1))
        btn2.image = PhotoImage(file=relative_to_services('addrow.png'))
        btn2.configure(image=btn2.image)
        btn2.pack()

        fakelabel2.grid(row=0, column=2, columnspan=2, sticky='ew')
        self.columnconfigure(2, weight=8)
        self.columnconfigure(3, weight=1)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=2, columnspan=2, sticky='w')

        fakelabel3 = Label(self, text="", bg=colour.TITLES_BACKGROUND)
        btn3 = Button(fakelabel3, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND, command=lambda: self.addNewLabel(2))
        btn3.image = PhotoImage(file=relative_to_services('addrow.png'))
        btn3.configure(image=btn3.image)
        btn3.pack()

        fakelabel3.grid(row=0, column=4, columnspan=2, sticky='ew')
        self.columnconfigure(4, weight=8)
        self.columnconfigure(5, weight=1)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=4, columnspan=2, sticky='w')

        keys = ['S', 'M', 'T']
        for col in range(3):
            for element in library[keys[col]]:
                self.addNewLabel(col)
                self.entries[col][-1].configure(text=element)
                if col != 1:
                    self.entries[col][-1].configure(bg=library[keys[col]][element]['color'])
                else:
                    self.entries[col][-1].configure(bg=settings.MAINTENANCE_COLOR)
                self.entries[col][-1].configure(fg="#000716")

        self.update()

    def popup_nullification_protocol(self, event): # noqa
        self.propwindow = None

    def summon_properties_window(self, event, column):
        global library

        if self.propwindow == None:
            item = event.widget
            if column == 0:
                if item["text"] in library['S']:
                    self.s_properties_window(item, keyword=item["text"])
                else:
                    self.s_properties_window(item)

            elif column == 1:
                if item["text"] in library['M']:
                    self.m_properties_window(item, keyword=item["text"])
                else:
                    self.m_properties_window(item)

            else: # It's 2
                if item["text"] in library['T']:
                    self.t_properties_window(item, keyword=item["text"])
                else:
                    self.t_properties_window(item)

        else:
            return

    def time_autocheck_event(self, ticket):
        if ticket == 'S':
            if self.service_dur['state'] == 'normal':
                new_state = 'disabled'
                new_combostate = 'disabled'
            else:
                new_state = 'normal'
                new_combostate = 'readonly'

            self.service_dur.configure(state=new_state)
            self.service_departure.configure(state=new_state)
            self.service_arrival.configure(state=new_state)
            self.service_extra_arrival.configure(state=new_state)
            self.service_autopush.configure(state=new_combostate)

        elif ticket == 'M':
            if self.maint_dur['state'] == 'normal':
                new_state = 'disabled'
                new_combostate = 'disabled'
            else:
                new_state = 'normal'
                new_combostate = 'readonly'

            self.maint_dur.configure(state=new_state)
            self.maint_departure.configure(state=new_state)
            self.maint_arrival.configure(state=new_state)
            self.maint_extra_arrival.configure(state=new_state)
            self.maint_autopush.configure(state=new_combostate)

        else: # ticket == 'T'
            if self.transfer_dur['state'] == 'normal':
                new_state = 'disabled'
                new_combostate = 'disabled'
            else:
                new_state = 'normal'
                new_combostate = 'readonly'

            self.transfer_dur.configure(state=new_state)
            self.transfer_departure.configure(state=new_state)
            self.transfer_arrival.configure(state=new_state)
            self.transfer_extra_arrival.configure(state=new_state)
            self.transfer_autopush.configure(state=new_combostate)

        self.propwindow.focus_set()

    def location_autocheck_event(self, ticket):
        if ticket == 'S':
            if self.service_origin['state'] == 'normal':
                new_state = 'disabled'
            else:
                new_state = 'normal'

            self.service_origin.configure(state=new_state)
            self.service_destiny.configure(state=new_state)

        elif ticket == 'M': # Not possible in maintenances, not even needed
            return

        else: # ticket == 'T'
            if self.transfer_depot_location['state'] == 'normal':
                new_state = 'disabled'
                new_combostate = 'disabled'
            else:
                new_state = 'normal'
                new_combostate = 'readonly'

            self.transfer_depot_location.configure(state=new_state)
            self.transfer_from_or_to.configure(state=new_combostate)

        self.propwindow.focus_set()

    def push_autocheck_event(self, ticket):
        if ticket == 'S':
            self.service_autopush.selection_clear()
            if self.service_autopush.get() != 'No':
                new_state = 'disabled'
            else:
                new_state = 'normal'

            self.service_arrival.configure(state=new_state)
            self.service_extra_arrival.configure(state=new_state)
            self.service_departure.configure(state=new_state)
            self.service_extensible.checkbutton.configure(state=new_state)

        elif ticket == 'M':
            self.maint_autopush.selection_clear()
            if self.maint_autopush.get() != 'No':
                new_state = 'disabled'
            else:
                new_state = 'normal'

            self.maint_arrival.configure(state=new_state)
            self.maint_extra_arrival.configure(state=new_state)
            self.maint_departure.configure(state=new_state)
            self.maint_extensible.checkbutton.configure(state=new_state)

        else:  # ticket == 'T'
            self.transfer_autopush.selection_clear()
            if self.transfer_autopush.get() != 'No':
                new_state = 'disabled'
            else:
                new_state = 'normal'

            self.transfer_arrival.configure(state=new_state)
            self.transfer_extra_arrival.configure(state=new_state)
            self.transfer_departure.configure(state=new_state)
            self.transfer_extensible.checkbutton.configure(state=new_state)

    def s_properties_window(self, item, keyword=None):
        global library

        self.propwindow = Toplevel(self.root)
        self.propwindow.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.propwindow.configure(background=colour.WINDOW_BACKGROUNDS)
        self.propwindow.geometry("1600x600")
        if keyword is not None:
            self.propwindow.title(lang.libtit1 + keyword)
        else:
            self.propwindow.title(lang.libtit2)

        wizard_icon = PhotoImage(file=relative_to_services("icon2.png"))
        self.propwindow.iconphoto(False, wizard_icon)
        self.propwindow.bind("<Destroy>", self.popup_nullification_protocol)
        self.propwindow.focus_set()
        self.propwindow.bind('<Escape>', lambda e: self.propwindow.destroy())

        # Boton de guardado
        savebtn = Button(self.propwindow, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS, command=lambda: self.s_save_element(item, keyword))
        savebtn.image = PhotoImage(file=relative_to_services('save.png'))
        savebtn.configure(image=savebtn.image)
        savebtn.pack(side='top', pady=10)

        # Entries frame
        entriesframe = Frame(master=self.propwindow, background=colour.FRAME_BACKGROUND)

        # Define entries
        entriesframe.columnconfigure(0, weight=1, uniform='equal')
        entriesframe.columnconfigure(1, weight=1, uniform='equal')
        entriesframe.columnconfigure(2, weight=1, uniform='equal')
        entriesframe.columnconfigure(3, weight=1, uniform='equal')
        entriesframe.columnconfigure(4, weight=1, uniform='equal')
        entriesframe.columnconfigure(5, weight=1, uniform='equal')
        entriesframe.columnconfigure(6, weight=1, uniform='equal')
        entriesframe.columnconfigure(7, weight=1, uniform='equal')
        entriesframe.columnconfigure(8, weight=1, uniform='equal')
        entriesframe.columnconfigure(9, weight=1, uniform='equal')
        entriesframe.columnconfigure(10, weight=1, uniform='equal')
        entriesframe.columnconfigure(11, weight=1, uniform='equal')

        Label(entriesframe, bd=2, text=lang.gui_servidb, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, columnspan=3, ipady=10, sticky='news')
        self.service_name = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_name.grid(row=1, column=0, columnspan=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_kilometers, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, columnspan=3, ipady=10, sticky='news')
        self.service_km = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_km.grid(row=1, column=3, columnspan=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_forced, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=6, columnspan=3, ipady=10, sticky='news')
        self.service_condition = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_condition.grid(row=1, column=6, columnspan=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_bans, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=9, columnspan=3, ipady=10, sticky='news')
        self.service_bans = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_bans.grid(row=1, column=9, columnspan=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_autodur, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=0, columnspan=4, ipady=10, sticky='news')
        self.service_extensible = FancyCheckButton(entriesframe, False, command=lambda: self.time_autocheck_event(ticket='S'))
        self.service_extensible.grid(row=3, column=0, columnspan=4, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_autoloc, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=4, columnspan=4, ipady=10, sticky='news')
        self.service_autolocation = FancyCheckButton(entriesframe, False, command=lambda: self.location_autocheck_event(ticket='S'))
        self.service_autolocation.grid(row=3, column=4, columnspan=4, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_autopush, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=8, columnspan=4, ipady=10, sticky='news')
        self.service_autopush = Combobox(entriesframe, values=['No', '\u2190', '\u2192'], font=('futura', 13), style="Custom.TCombobox", state='readonly')
        self.service_autopush.bind('<<ComboboxSelected>>', lambda e: self.push_autocheck_event(ticket='S'))
        self.service_autopush.unbind_class("TCombobox", "<MouseWheel>")
        self.service_autopush.current(0)
        self.service_autopush.grid(row=3, column=8, columnspan=4, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_departuretime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=0, columnspan=4, ipady=10, sticky='news')
        self.service_departure = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_departure.grid(row=5, column=0, columnspan=4, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_extradays, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=4, columnspan=4, ipady=10, sticky='news')
        self.service_extra_arrival = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_extra_arrival.grid(row=5, column=4, columnspan=4, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_arrivaltime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=4, column=8, columnspan=4, ipady=10, sticky='news')
        self.service_arrival = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_arrival.grid(row=5, column=8, columnspan=4, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=6, column=0, columnspan=3, ipady=10, sticky='news')
        self.service_dur = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_dur.grid(row=7, column=0, columnspan=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_fromsimple, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=6, column=3, columnspan=3, ipady=10, sticky='news')
        self.service_origin = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_origin.grid(row=7, column=3, columnspan=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_tosimple, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=6, column=6, columnspan=3, ipady=10, sticky='news')
        self.service_destiny = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.service_destiny.grid(row=7, column=6, columnspan=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=6, column=9, columnspan=3, ipady=10, sticky='news')
        if keyword is not None:
            self.service_color = ColorEntry(entriesframe, base_color=library['S'][keyword]['color'], bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716")
        else:
            self.service_color = ColorEntry(entriesframe, base_color='#d6d6d6', bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716")
        self.service_color.grid(row=7, column=9, columnspan=3, padx=20, pady=20, sticky='ew')

        if keyword is not None:
            self.service_name.insert(0, keyword)
            self.service_km.insert(0, str(library['S'][keyword]['km']))
            self.service_condition.insert(0, library['S'][keyword]['forced'])
            self.service_bans.insert(0, str(library['S'][keyword]['bans']).translate({ord(i): None for i in "[]'"}))
            self.service_departure.insert(0, library['S'][keyword]['departure_time'])
            self.service_extra_arrival.insert(0, str(library['S'][keyword]['extra_days_arrival']))
            self.service_arrival.insert(0, library['S'][keyword]['arrival_time'])
            self.service_dur.insert(0, str(library['S'][keyword]['duration']))
            self.service_origin.insert(0, library['S'][keyword]['origin'])
            self.service_destiny.insert(0, library['S'][keyword]['destiny'])
            self.service_extensible.set(library['S'][keyword]['extensible'])
            self.service_autolocation.set(library['S'][keyword]['autolocation'])
            self.service_autopush.set(library['S'][keyword]['autopush'])

            if library['S'][keyword]['extensible']:
                self.service_dur.configure(state='disabled')
                self.service_departure.configure(state='disabled')
                self.service_extra_arrival.configure(state='disabled')
                self.service_arrival.configure(state='disabled')
                self.service_autopush.configure(state='disabled')

            if library['S'][keyword]['autolocation']:
                self.service_origin.configure(state='disabled')
                self.service_destiny.configure(state='disabled')

            if library['S'][keyword]['autopush'] != 'No':
                self.service_departure.configure(state='disabled')
                self.service_extra_arrival.configure(state='disabled')
                self.service_arrival.configure(state='disabled')
                self.service_extensible.checkbutton.configure(state='disabled')

        entriesframe.pack(fill='both', expand=True)

    def m_properties_window(self, item, keyword=None):
        global library

        self.propwindow = Toplevel(self.root)
        self.propwindow.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.propwindow.configure(background=colour.WINDOW_BACKGROUNDS)
        self.propwindow.geometry("1600x450")
        if keyword is not None:
            self.propwindow.title(lang.libtit3 + keyword)
        else:
            self.propwindow.title(lang.libtit4)
        wizard_icon = PhotoImage(file=relative_to_services("icon2.png"))
        self.propwindow.iconphoto(False, wizard_icon)
        self.propwindow.bind("<Destroy>", self.popup_nullification_protocol)
        self.propwindow.focus_set()
        self.propwindow.bind('<Escape>', lambda e: self.propwindow.destroy())

        # Boton de guardado
        savebtn = Button(self.propwindow, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS, command=lambda: self.m_save_element(item, keyword))
        savebtn.image = PhotoImage(file=relative_to_services('save.png'))
        savebtn.configure(image=savebtn.image)
        savebtn.pack(side='top', pady=10)

        # Entries frame
        entriesframe = Frame(master=self.propwindow, background=colour.FRAME_BACKGROUND)

        # Define entries
        entriesframe.columnconfigure(0, weight=1, uniform='equal')
        entriesframe.columnconfigure(1, weight=1, uniform='equal')
        entriesframe.columnconfigure(2, weight=1, uniform='equal')
        entriesframe.columnconfigure(3, weight=1, uniform='equal')

        Label(entriesframe, bd=2, text=lang.gui_maintname, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='news')
        self.maint_id = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_id.grid(row=1, column=0, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_kmlimitb, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='news')
        self.maint_kminfo = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_kminfo.grid(row=1, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_autopush, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='news')
        self.maint_autopush = Combobox(entriesframe, values=['No', '\u2190', '\u2192'], font=('futura', 13), style="Custom.TCombobox", state='readonly')
        self.maint_autopush.unbind_class("TCombobox", "<MouseWheel>")
        self.maint_autopush.bind('<<ComboboxSelected>>', lambda e: self.push_autocheck_event(ticket='M'))
        self.maint_autopush.unbind('<MouseWheel>')
        self.maint_autopush.current(0)
        self.maint_autopush.grid(row=1, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_autodur, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='news')
        self.maint_extensible = FancyCheckButton(entriesframe, False, command=lambda: self.time_autocheck_event(ticket='M'))
        self.maint_extensible.grid(row=1, column=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=0, ipady=10, sticky='news')
        self.maint_dur = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_dur.grid(row=3, column=0, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_starttime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=1, ipady=10, sticky='news')
        self.maint_departure = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_departure.grid(row=3, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_extradays, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=2, ipady=10, sticky='news')
        self.maint_extra_arrival = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_extra_arrival.grid(row=3, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_finishtime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=3, ipady=10, sticky='news')
        self.maint_arrival = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.maint_arrival.grid(row=3, column=3, padx=20, pady=20, sticky='ew')

        if keyword is not None:
            self.maint_id.insert(0, keyword)
            self.maint_kminfo.insert(0, str(library['M'][keyword]['kmlimit']))
            self.maint_dur.insert(0, str(library['M'][keyword]['duration']))
            self.maint_departure.insert(0, library['M'][keyword]['departure_time'])
            self.maint_arrival.insert(0, library['M'][keyword]['arrival_time'])
            self.maint_extra_arrival.insert(0, str(library['M'][keyword]['extra_days_arrival']))
            self.maint_extensible.set(library['M'][keyword]['extensible'])
            self.maint_autopush.set(library['M'][keyword]['autopush'])

            if library['M'][keyword]['extensible']:
                self.maint_dur.configure(state='disabled')
                self.maint_departure.configure(state='disabled')
                self.maint_arrival.configure(state='disabled')
                self.maint_extra_arrival.configure(state='disabled')
                self.maint_autopush.configure(state='disabled')

            if library['M'][keyword]['autopush'] != 'No':
                self.maint_departure.configure(state='disabled')
                self.maint_arrival.configure(state='disabled')
                self.maint_extra_arrival.configure(state='disabled')
                self.maint_extensible.checkbutton.configure(state='disabled')

        entriesframe.pack(fill='both', expand=True)

    def t_properties_window(self, item, keyword=None):
        global library

        self.propwindow = Toplevel(self.root)
        self.propwindow.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
        self.propwindow.configure(background=colour.WINDOW_BACKGROUNDS)
        self.propwindow.geometry("1600x450")
        if keyword is not None:
            self.propwindow.title(lang.libtit5 + keyword)
        else:
            self.propwindow.title(lang.libtit6)

        wizard_icon = PhotoImage(file=relative_to_services("icon2.png"))
        self.propwindow.iconphoto(False, wizard_icon)
        self.propwindow.bind("<Destroy>", self.popup_nullification_protocol)
        self.propwindow.focus_set()
        self.propwindow.bind('<Escape>', lambda e: self.propwindow.destroy())

        # Boton de guardado
        savebtn = Button(self.propwindow, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.WINDOW_BACKGROUNDS, command=lambda: self.t_save_element(item, keyword))
        savebtn.image = PhotoImage(file=relative_to_services('save.png'))
        savebtn.configure(image=savebtn.image)
        savebtn.pack(side='top', pady=10)

        # Entries frame
        entriesframe = Frame(master=self.propwindow, background=colour.FRAME_BACKGROUND)
        entriesframe2 = Frame(master=self.propwindow, background=colour.FRAME_BACKGROUND)
        # Define entries
        entriesframe.columnconfigure(0, weight=1, uniform='equal')
        entriesframe.columnconfigure(1, weight=1, uniform='equal')
        entriesframe.columnconfigure(2, weight=1, uniform='equal')
        entriesframe.columnconfigure(3, weight=1, uniform='equal')
        entriesframe.columnconfigure(4, weight=1, uniform='equal')
        entriesframe2.columnconfigure(0, weight=1, uniform='mono')
        entriesframe2.columnconfigure(1, weight=1, uniform='mono')
        entriesframe2.columnconfigure(2, weight=1, uniform='mono')
        entriesframe2.columnconfigure(3, weight=1, uniform='mono')

        Label(entriesframe, bd=2, text=lang.gui_servidb, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='news')
        self.transfer_name = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_name.grid(row=1, column=0, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_kilometers, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='news')
        self.transfer_km = Entry(entriesframe, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_km.grid(row=1, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_autodur, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='news')
        self.transfer_extensible = FancyCheckButton(entriesframe, False, command=lambda: self.time_autocheck_event(ticket='T'))
        self.transfer_extensible.grid(row=1, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_autoloc, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='news')
        self.transfer_autolocation = FancyCheckButton(entriesframe, False, command=lambda: self.location_autocheck_event(ticket='T'))
        self.transfer_autolocation.grid(row=1, column=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe, bd=2, text=lang.gui_autopush, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=4, ipady=10, sticky='news')
        self.transfer_autopush = Combobox(entriesframe, values=['No', '\u2190', '\u2192'], font=('futura', 13), style="Custom.TCombobox", state='readonly')
        self.transfer_autopush.bind('<<ComboboxSelected>>', lambda e: self.push_autocheck_event(ticket='T'))
        self.transfer_autopush.unbind_class("TCombobox", "<MouseWheel>")
        self.transfer_autopush.current(0)
        self.transfer_autopush.grid(row=1, column=4, padx=20, pady=20, sticky='ew')

        Label(entriesframe2, bd=2, text=lang.gui_duration, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, ipady=10, sticky='news')
        self.transfer_dur = Entry(entriesframe2, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_dur.grid(row=1, column=0, padx=20, pady=20, sticky='ew')

        Label(entriesframe2, bd=2, text=lang.gui_departuretime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, ipady=10, sticky='news')
        self.transfer_departure = Entry(entriesframe2, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_departure.grid(row=1, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe2, bd=2, text=lang.gui_extradays, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, ipady=10, sticky='news')
        self.transfer_extra_arrival = Entry(entriesframe2, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_extra_arrival.grid(row=1, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe2, bd=2, text=lang.gui_arrivaltime, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, ipady=10, sticky='news')
        self.transfer_arrival = Entry(entriesframe2, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_arrival.grid(row=1, column=3, padx=20, pady=20, sticky='ew')

        Label(entriesframe2, bd=2, text=lang.gui_depot, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=0, ipady=10, sticky='news')
        self.transfer_depot_location = Entry(entriesframe2, bd=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND)
        self.transfer_depot_location.grid(row=3, column=0, padx=20, pady=20, sticky='ew')

        Label(entriesframe2, bd=2, text=lang.gui_fromto, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=1, ipady=10, sticky='news')
        self.transfer_from_or_to = Combobox(entriesframe2, values=['To Depot', 'From Depot'], font='futura', style="Custom.TCombobox", state='readonly')
        self.transfer_from_or_to.grid(row=3, column=1, padx=20, pady=20, sticky='ew')

        Label(entriesframe2, bd=2, text=lang.gui_maintq, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=2, ipady=10, sticky='news')
        self.maintenance_or_overnight = FancyCheckButton(entriesframe2, False)
        self.maintenance_or_overnight.grid(row=3, column=2, padx=20, pady=20, sticky='ew')

        Label(entriesframe2, bd=2, text=lang.gui_colour, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=2, column=3, ipady=10, sticky='news')
        if keyword is not None:
            self.transfer_color = ColorEntry(entriesframe2, base_color=library['T'][keyword]['color'], bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716")
        else:
            self.transfer_color = ColorEntry(entriesframe2, base_color='#d6d6d6', bd=2, font='futura', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, fg="#000716")
        self.transfer_color.grid(row=3, column=3, padx=20, pady=20, sticky='ew')

        if keyword is not None:
            self.transfer_name.insert(0, keyword)
            self.transfer_km.insert(0, str(library['T'][keyword]['km']))
            self.transfer_departure.insert(0, library['T'][keyword]['departure_time'])
            self.transfer_arrival.insert(0, library['T'][keyword]['arrival_time'])

            self.transfer_dur.insert(0, str(library['T'][keyword]['duration']))
            self.maintenance_or_overnight.set(library['T'][keyword]['transfertype'])
            self.transfer_depot_location.insert(0, library['T'][keyword]['depot'])
            self.transfer_from_or_to.set(library['T'][keyword]['to_from_depot'])
            self.transfer_extensible.set(library['T'][keyword]['extensible'])
            self.transfer_autolocation.set(library['T'][keyword]['autolocation'])
            self.transfer_autopush.set(library['T'][keyword]['autopush'])

            if library['T'][keyword]['extensible']:
                self.transfer_dur.configure(state='disabled')
                self.transfer_departure.configure(state='disabled')
                self.transfer_arrival.configure(state='disabled')
                self.transfer_extra_arrival.configure(state='disabled')
                self.transfer_autopush.configure(state='disabled')

            if library['T'][keyword]['autolocation']:
                self.transfer_depot_location.configure(state='disabled')
                self.transfer_from_or_to.configure(state='disabled')

            if library['T'][keyword]['autopush'] != 'No':
                self.transfer_departure.configure(state='disabled')
                self.transfer_arrival.configure(state='disabled')
                self.transfer_extra_arrival.configure(state='disabled')
                self.transfer_extensible.checkbutton.configure(state='disabled')

        entriesframe.pack(fill='both', expand=True)
        entriesframe2.pack(fill='both', expand=True)

    def s_save_element(self, item, keyword):
        global library

        something_changed = False

        # Get the data and check if something changed
        try:
            new_name = self.service_name.get()
            if new_name == '':
                messagebox.showerror(lang.error_saving, lang.liberror13)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return
        except:
            messagebox.showerror('Error', lang.liberror12)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        new_dur = self.service_dur.get()
        new_km = self.service_km.get()
        new_condition = self.service_condition.get()
        new_bans = self.service_bans.get().replace(", ", ",").replace(" ,", ",").split(",")
        new_departure = self.service_departure.get()
        new_extra_arrival = self.service_extra_arrival.get()
        new_arrival = self.service_arrival.get()
        new_origin = self.service_origin.get()
        new_destiny = self.service_destiny.get()
        new_color = self.service_color.get()
        new_extensible = self.service_extensible.get()
        new_autolocation = self.service_autolocation.get()
        new_autopush = self.service_autopush.get()

        try:
            new_km = eval(new_km)
        except:
            messagebox.showerror(lang.error_saving, lang.liberror11)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        # Some additional checking
        if new_extensible:
            new_start = None
            new_end = None

        elif new_autopush != 'No':
            new_start = None
            new_end = None
            if new_dur != '':
                try:
                    new_dur = float(new_dur)
                    if new_dur < 0:
                        messagebox.showerror(lang.error_saving, lang.liberror10)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror9)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

            else:
                messagebox.showerror(lang.error_saving, lang.liberror5)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return
        
        else:
            if new_dur != '':
                try:
                    new_dur = float(new_dur)
                    if new_dur < 0:
                        messagebox.showerror(lang.error_saving, lang.liberror10)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror9)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

            if new_departure != '':
                try:
                    t = datetime.strptime(new_departure, '%H:%M').time()
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror8)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_start = t.hour + t.minute / 60
            else:
                new_start = None

            if new_arrival != '':
                try:
                    t = datetime.strptime(new_arrival, '%H:%M').time()
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror7)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                if new_extra_arrival != '' and new_dur != '': # Note that new_extra_arrival makes NO SENSE with an existing duration
                    try:
                        extra_days = int(new_extra_arrival)
                    except:
                        messagebox.showerror(lang.error_saving, lang.liberror6)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                else:
                    extra_days = 0
                new_end = (extra_days * 24) + t.hour + t.minute / 60

            else:
                new_end = None

            # Actual new_start and new_end values, with duration always having preference unless both are stated?
            if new_start is None and new_end is None and new_dur == '':
                messagebox.showerror(lang.error_saving, lang.liberror5)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return
            elif new_start is None and new_end is None and new_dur != '':
                new_start = None
                new_end = None
            elif new_start is not None and new_end is None:
                if new_dur == '':
                    messagebox.showerror(lang.error_saving, lang.liberror5)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_end = new_start + new_dur
            elif new_start is None and new_end is not None:
                if new_dur == '':
                    messagebox.showerror(lang.error_saving, lang.liberror5)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_start = new_end - new_dur

        if not new_autolocation:
            if new_origin == '' or new_destiny == '':
                messagebox.showerror(lang.error_saving, lang.liberror16)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

            if lang.CHECK_DEPOT in new_origin.lower() or lang.CHECK_DEPOT in new_destiny.lower() or lang.CHECK_MAINTENANCE in new_origin.lower() or lang.CHECK_MAINTENANCE in new_destiny.lower() or lang.CHECK_OVERNIGHT in new_origin.lower() or lang.CHECK_OVERNIGHT in new_destiny.lower():
                messagebox.showerror(lang.error_saving, lang.liberror3)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

        if keyword is not None:
            if new_name != keyword:
                something_changed = True

            if new_extensible != library['S'][keyword]['extensible']:
                something_changed = True

            if new_autolocation != library['S'][keyword]['autolocation']:
                something_changed = True

            if new_km != library['S'][keyword]['km']:
                something_changed = True

            if new_condition != library['S'][keyword]['forced']:
                something_changed = True

            if new_bans != library['S'][keyword]['bans']:
                something_changed = True

            if new_departure != library['S'][keyword]['departure_time']:
                something_changed = True

            if new_extra_arrival != library['S'][keyword]['extra_days_arrival']:
                something_changed = True

            if new_arrival != library['S'][keyword]['arrival_time']:
                something_changed = True

            if new_dur != library['S'][keyword]['duration']:
                something_changed = True

            if new_start != library['S'][keyword]['start']:
                something_changed = True

            if new_end != library['S'][keyword]['end']:
                something_changed = True

            if new_origin != library['S'][keyword]['origin']:
                something_changed = True

            if new_destiny != library['S'][keyword]['destiny']:
                something_changed = True

            if new_color != library['S'][keyword]['color']:
                something_changed = True

            if new_autopush != library['S'][keyword]['autopush']:
                something_changed = True

        # Overwrite json and update library
        if something_changed or keyword is None:
            try:
                if new_name != keyword and new_name in library['S']:
                    messagebox.showerror('Error', lang.liberror2)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

                if keyword is not None:
                    library['S'].pop(keyword, None)

                library['S'][new_name] = {
                    'extensible': new_extensible,
                    'autolocation': new_autolocation,
                    'km': new_km,
                    'forced': new_condition,
                    'bans': new_bans,
                    'departure_time': new_departure,
                    'extra_days_arrival': new_extra_arrival,
                    'arrival_time': new_arrival,
                    'duration': new_dur,
                    'start': new_start,
                    'end': new_end,
                    'origin': new_origin,
                    'destiny': new_destiny,
                    'color': new_color,
                    'autopush': new_autopush
                }
                p = relative_to_settings('library.json')
                with p.open('w', encoding='utf-8') as f:
                    json.dump(library, f, indent=4)
            except:
                messagebox.showerror('Error', lang.liberror1)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

        self.propwindow.destroy()
        item.configure(text=new_name)
        item.configure(bg=new_color)
        item.configure(fg="#000716")

        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)

    def m_save_element(self, item, keyword):
        global library

        something_changed = False

        # Get the data and check if something changed
        try:
            new_name = self.maint_id.get()
            if new_name == '':
                messagebox.showerror(lang.error_saving, lang.liberror13)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return
        except:
            messagebox.showerror('Error', lang.liberror12)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        new_dur = self.maint_dur.get()
        new_km = self.maint_kminfo.get()
        new_departure = self.maint_departure.get()
        new_extra_arrival = self.maint_extra_arrival.get()
        new_arrival = self.maint_arrival.get()
        new_extensible = self.maint_extensible.get()
        new_autopush = self.maint_autopush.get()

        try:
            new_km = eval(new_km)
        except:
            messagebox.showerror(lang.error_saving, lang.liberror15)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        # Some additional checking
        if new_extensible:
            new_start = None
            new_end = None

        elif new_autopush != 'No':
            new_start = None
            new_end = None
            if new_dur != '':
                try:
                    new_dur = float(new_dur)
                    if new_dur < 0:
                        messagebox.showerror(lang.error_saving, lang.liberror10)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror9)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

            else:
                messagebox.showerror(lang.error_saving, lang.liberror5)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return
            
        else:
            if new_dur != '':
                try:
                    new_dur = float(new_dur)
                    if new_dur < 0:
                        messagebox.showerror(lang.error_saving, lang.liberror10)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror9)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

            if new_departure != '':
                try:
                    t = datetime.strptime(new_departure, '%H:%M').time()
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror8)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_start = t.hour + t.minute / 60
            else:
                new_start = None

            if new_arrival != '':
                try:
                    t = datetime.strptime(new_arrival, '%H:%M').time()
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror7)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                if new_extra_arrival != '':
                    try:
                        extra_days = int(new_extra_arrival)
                    except:
                        messagebox.showerror(lang.error_saving, lang.liberror6)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                else:
                    extra_days = 0
                new_end = (extra_days * 24) + t.hour + t.minute / 60
            else:
                new_end = None

            # Actual new_start and new_end values, with duration always having preference unless both are stated?
            if new_start is None and new_end is None and new_dur == '':
                messagebox.showerror(lang.error_saving, lang.liberror14)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return
            elif new_start is None and new_end is None and new_dur != '':
                new_start = None
                new_end = None
            elif new_start is not None and new_end is not None:
                new_dur = new_end - new_start
            elif new_start is not None and new_end is None:
                if new_dur == '':
                    messagebox.showerror(lang.error_saving, lang.liberror14)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_end = new_start + new_dur
            elif new_start is None and new_end is not None:
                if new_dur == '':
                    messagebox.showerror(lang.error_saving, lang.liberror14)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_start = new_end - new_dur

        if keyword is not None:
            if new_name != keyword:
                something_changed = True

            if new_extensible != library['M'][keyword]['extensible']:
                something_changed = True

            if new_km != library['M'][keyword]['kmlimit']:
                something_changed = True

            if new_departure != library['M'][keyword]['departure_time']:
                something_changed = True

            if new_arrival != library['M'][keyword]['arrival_time']:
                something_changed = True

            if new_extra_arrival != library['M'][keyword]['extra_days_arrival']:
                something_changed = True

            if new_dur != library['M'][keyword]['duration']:
                something_changed = True

            if new_start != library['M'][keyword]['start']:
                something_changed = True

            if new_end != library['M'][keyword]['end']:
                something_changed = True

            if new_autopush != library['M'][keyword]['autopush']:
                something_changed = True

        # Overwrite json and update library
        if something_changed or keyword is None:
            try:
                if new_name != keyword and new_name in library['M']:
                    messagebox.showerror('Error', lang.liberror2)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

                if keyword is not None:
                    library['M'].pop(keyword, None)

                library['M'][new_name] = {
                    'extensible': new_extensible,
                    'kmlimit': new_km,
                    'departure_time': new_departure,
                    'extra_days_arrival': new_extra_arrival,
                    'arrival_time': new_arrival,
                    'duration': new_dur,
                    'start': new_start,
                    'end': new_end,
                    'autopush': new_autopush
                }
                p = relative_to_settings('library.json')
                with p.open('w', encoding='utf-8') as f:
                    json.dump(library, f, indent=4)
            except:
                messagebox.showerror('Error', lang.liberror1)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

        self.propwindow.destroy()
        item.configure(text=new_name)
        item.configure(bg=settings.MAINTENANCE_COLOR)
        item.configure(fg="#000716")

        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)

    def t_save_element(self, item, keyword):
        global library

        something_changed = False

        # Get the data and check if something changed
        try:
            new_name = self.transfer_name.get()
            if new_name == '':
                messagebox.showerror(lang.error_saving, lang.liberror13)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return
        except:
            messagebox.showerror('Error', lang.liberror12)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        new_dur = self.transfer_dur.get()
        new_km = self.transfer_km.get()
        new_departure = self.transfer_departure.get()
        new_arrival = self.transfer_arrival.get()
        new_extra_arrival = self.transfer_extra_arrival.get()
        new_depot_location = self.transfer_depot_location.get()
        new_from_to = self.transfer_from_or_to.get()
        new_transfer_type = self.maintenance_or_overnight.get()
        new_color = self.transfer_color.get()
        new_extensible = self.transfer_extensible.get()
        new_autolocation = self.transfer_autolocation.get()
        new_autopush = self.transfer_autopush.get()

        try:
            new_km = eval(new_km)
        except:
            messagebox.showerror(lang.error_saving, lang.liberror11)
            self.propwindow.attributes('-topmost', True)
            self.propwindow.attributes('-topmost', False)
            return

        # Some additional checking
        if new_extensible:
            new_start = None
            new_end = None

        elif new_autopush != 'No':
            new_start = None
            new_end = None
            if new_dur != '':
                try:
                    new_dur = float(new_dur)
                    if new_dur < 0:
                        messagebox.showerror(lang.error_saving, lang.liberror10)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror9)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

            else:
                messagebox.showerror(lang.error_saving, lang.liberror5)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

        else:
            if new_dur != '':
                try:
                    new_dur = float(new_dur)
                    if new_dur < 0:
                        messagebox.showerror(lang.error_saving, lang.liberror10)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror9)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

            if new_departure != '':
                try:
                    t = datetime.strptime(new_departure, '%H:%M').time()
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror8)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_start = t.hour + t.minute / 60
            else:
                new_start = None

            if new_arrival != '':
                try:
                    t = datetime.strptime(new_arrival, '%H:%M').time()
                except:
                    messagebox.showerror(lang.error_saving, lang.liberror7)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                if new_extra_arrival != '':
                    try:
                        extra_days = int(new_extra_arrival)
                    except:
                        messagebox.showerror(lang.error_saving, lang.liberror6)
                        self.propwindow.attributes('-topmost', True)
                        self.propwindow.attributes('-topmost', False)
                        return
                else:
                    extra_days = 0
                new_end = (extra_days * 24) + t.hour + t.minute / 60
            else:
                new_end = None

            # Actual new_start and new_end values, with duration always having preference unless both are stated?
            if new_start is None and new_end is None and new_dur == '':
                messagebox.showerror(lang.error_saving, lang.liberror5)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return
            elif new_start is None and new_end is None and new_dur != '':
                new_start = None
                new_end = None
            elif new_start is not None and new_end is not None:
                new_dur = new_end - new_start
            elif new_start is not None and new_end is None:
                if new_dur == '':
                    messagebox.showerror(lang.error_saving, lang.liberror5)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_end = new_start + new_dur
            elif new_start is None and new_end is not None:
                if new_dur == '':
                    messagebox.showerror(lang.error_saving, lang.liberror5)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return
                new_start = new_end - new_dur

        if not new_autolocation:
            if new_depot_location == '':
                messagebox.showerror(lang.error_saving, lang.liberror4)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

            if lang.CHECK_DEPOT in new_depot_location.lower() or lang.CHECK_MAINTENANCE in new_depot_location.lower() or lang.CHECK_OVERNIGHT in new_depot_location.lower():
                messagebox.showerror(lang.error_saving, lang.liberror3)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

        if keyword is not None:
            if new_name != keyword:
                something_changed = True

            if new_extensible != library['T'][keyword]['extensible']:
                something_changed = True

            if new_autolocation != library['T'][keyword]['autolocation']:
                something_changed = True

            if new_km != library['T'][keyword]['km']:
                something_changed = True

            if new_from_to != library['T'][keyword]['to_from_depot']:
                something_changed = True

            if new_transfer_type != library['T'][keyword]['transfertype']:
                something_changed = True

            if new_departure != library['T'][keyword]['departure_time']:
                something_changed = True

            if new_extra_arrival != library['T'][keyword]['extra_days_arrival']:
                something_changed = True

            if new_arrival != library['T'][keyword]['arrival_time']:
                something_changed = True

            if new_dur != library['T'][keyword]['duration']:
                something_changed = True

            if new_start != library['T'][keyword]['start']:
                something_changed = True

            if new_end != library['T'][keyword]['end']:
                something_changed = True

            if new_depot_location != library['T'][keyword]['depot']:
                something_changed = True

            if new_color != library['T'][keyword]['color']:
                something_changed = True

            if new_autopush != library['T'][keyword]['autopush']:
                something_changed = True

        # Overwrite json and update library
        if something_changed or keyword is None:
            try:
                if new_name != keyword and new_name in library['T']:
                    messagebox.showerror('Error', lang.liberror2)
                    self.propwindow.attributes('-topmost', True)
                    self.propwindow.attributes('-topmost', False)
                    return

                if keyword is not None:
                    library['T'].pop(keyword, None)

                p = relative_to_settings('library.json')
                with p.open('w', encoding='utf-8') as f:
                    json.dump(library, f, indent=4)
                library['T'][new_name] = {
                    'extensible': new_extensible,
                    'autolocation': new_autolocation,
                    'km': new_km,
                    'to_from_depot': new_from_to,
                    'transfertype': new_transfer_type,
                    'departure_time': new_departure,
                    'extra_days_arrival': new_extra_arrival,
                    'arrival_time': new_arrival,
                    'duration': new_dur,
                    'start': new_start,
                    'end': new_end,
                    'depot': new_depot_location,
                    'color': new_color,
                    'autopush': new_autopush
                }
            except:
                messagebox.showerror('Error', lang.liberror1)
                self.propwindow.attributes('-topmost', True)
                self.propwindow.attributes('-topmost', False)
                return

        self.propwindow.destroy()
        item.configure(text=new_name)
        item.configure(bg=new_color)
        item.configure(fg="#000716")

        self.root.attributes('-topmost', True)
        self.root.update()
        self.root.attributes('-topmost', False)

def librarywin(winmaster, fullcanvas_parent=None):
    win = Toplevel(winmaster)
    win.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
    win.bind("<Destroy>", lambda e: window_blocker.window_destruction_protocol())
    window_blocker.IS_OPEN = True
    win.configure(background=colour.WINDOW_BACKGROUNDS)
    win.geometry('1600x600')
    win.minsize(width=1600, height=100)
    win.title(lang.libtitle)
    root_icon = PhotoImage(file=relative_to_services("icon2.png"))
    win.iconphoto(False, root_icon)

    labelframe = Frame(win, bg=colour.WINDOW_BACKGROUNDS, bd=0)
    labelframe.pack(fill='x', pady=10)
    Label(labelframe, text=lang.gui_servlib, font=('futura', 16), bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, sticky='ew')
    Label(labelframe, text=lang.gui_maintlib, font=('futura', 16), bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, sticky='ew')
    Label(labelframe, text=lang.gui_translib, font=('futura', 16), bg=colour.WINDOW_BACKGROUNDS, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, sticky='ew')
    labelframe.columnconfigure(0, weight=1)
    labelframe.columnconfigure(1, weight=1)
    labelframe.columnconfigure(2, weight=1)

    # Initialize a Scrollable frame:
    Scrollable = library_ScrollableFrame(win, fullcanvas_parent, bg=colour.FRAME_BACKGROUND, bd=0, x_scroll=False)
    win.attributes('-topmost', True)
    win.attributes('-topmost', False)

def load_library():
    global library
    p = relative_to_settings('library.json')

    with p.open('r', encoding='utf-8') as f:
        library = json.load(f)
    return

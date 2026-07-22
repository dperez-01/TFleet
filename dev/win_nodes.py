'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        win_nodesV2.py

 Author:      Diego Pérez

 Created:     23/04/2024
 Copyright:   (c) perez 2024
-------------------------------------------------------------------------------
'''
from copy import deepcopy
from tkinter import Entry, Button, Toplevel, END, PhotoImage, Label, Checkbutton, BooleanVar, messagebox, Frame
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

from tkwidgets import ScrollableFrame
from help_manager import open_help
import startmenu_blocker as window_blocker

def relative_to_nodes(path: str) -> Path:
    return OUTPUT_PATH / Path(path)

nodeslist = []
depotnodes = {}
shortenings = {}
NODES_ARE_NEW = {}

class nodes_scrollableframe(ScrollableFrame):
    def addNewLabel(self):
        self.entries.append([])

        # Node name
        self.entries[-1].append(Entry(self, bd=2, width=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=0, padx=10, sticky='ew')

        # Node shortening
        self.entries[-1].append(Entry(self, bd=2, width=2, font='futura', relief='flat', highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, insertbackground=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=self.i, column=1, padx=10, sticky='ew')

        # Depot availability
        self.bools.append(BooleanVar(self, value=False))
        self.backgroundlabels.append(Label(self, bd=2, highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.backgroundlabels[-1].grid(row=self.i, column=2, padx=10, ipadx=10)
        self.backgroundlabels[-1].columnconfigure(0, weight=1)
        self.entries[-1].append(Checkbutton(self.backgroundlabels[-1], text='Exists?', onvalue=True, offvalue=False, bd=2, variable=self.bools[-1], selectcolor=colour.INPUT_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND))
        self.entries[-1][-1].grid(row=0, column=0)

        # Basket
        self.basket.append(Label(self, text='\U0001F5D1', bd=2, highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, relief='flat', bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, width=3))
        self.basket[-1].bind("<Button-1>", self.deleterow)
        self.basket[-1].grid(row=self.i, column=3, padx=10, sticky='ew')

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
        del self.bools[index]

        self.backgroundlabels[index].grid_forget()
        self.falselabels[index].grid_forget()
        self.basket[index].grid_forget()

        del self.backgroundlabels[index]
        del self.falselabels[index]
        del self.basket[index]

        self.i -= 2
        self.updateScrollRegion()
        self.root.lift()

    def __init__(self, winmaster, y_scroll=True, x_scroll=True, frameborder=10, **kwargs):
        ScrollableFrame.__init__(self, winmaster, y_scroll=y_scroll, x_scroll=x_scroll, frameborder=frameborder, **kwargs)
        self.i = 2
        self.entries = []
        self.backgroundlabels = []
        self.bools = []
        self.basket = []
        self.falselabels = []

        Label(self, bd=2, text=lang.gui_station, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=0, sticky='news')
        Label(self, bd=2, text=lang.gui_shortening, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=1, sticky='news')
        Label(self, bd=2, text=lang.gui_maintenancedepot, font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=2, sticky='news')
        Label(self, bd=2, text='', font=('futura', 13), relief='flat', highlightthickness=0, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND).grid(row=0, column=3, sticky='news')

        self.columnconfigure(0, weight=6, uniform='uniform')
        self.columnconfigure(1, weight=6, uniform='uniform')
        self.columnconfigure(2, weight=6, uniform='uniform')
        self.columnconfigure(3, weight=1)

        Label(self, text="", bg=colour.FRAME_BACKGROUND, height=1).grid(row=1, column=0, sticky='news')


    def define_nodes(self):
        global nodeslist, depotnodes, shortenings, NODES_ARE_NEW
        previous_depotnodes = deepcopy(depotnodes)
        new_nodeslist = []
        new_depotnodes = {}
        new_shortenings = {}
        repetition_checking = []
        NODES_ARE_NEW = {} # TODO It should be made that when something that was a depot is no longer a depot, it is DELETED from the transfer and sleeper dicts if existing. Those windows can not import win_nodes then, so we have to fix that

        for row in range(len(self.entries)):
            try:
                node = self.entries[row][0].get()
                shortening = self.entries[row][1].get()
                if node == '':
                    messagebox.showerror(lang.error_saving, lang.nodeserror1)
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return
                if shortening == '':
                    messagebox.showerror(lang.error_saving, lang.nodeserror2)
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return
                if lang.CHECK_DEPOT in node.lower() or lang.CHECK_MAINTENANCE in node.lower() or lang.CHECK_OVERNIGHT in node.lower() or '<' in node or '>' in node:
                    messagebox.showerror(lang.error_saving, lang.nodeserror3 + node)
                    self.root.attributes('-topmost', True)
                    self.root.attributes('-topmost', False)
                    return

            except:
                messagebox.showerror(lang.error_saving, lang.nodeserror4)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            if shortening in repetition_checking:
                messagebox.showerror(lang.error_saving, lang.nodeserror5 + shortening + lang.nodeserror6)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            if len(shortening) > 2:
                messagebox.showerror(lang.error_saving, lang.nodeserror5 + shortening + lang.nodeserror7)
                self.root.attributes('-topmost', True)
                self.root.attributes('-topmost', False)
                return

            repetition_checking.append(shortening)

            depotbool = self.bools[row].get()

            new_nodeslist.append(node)
            new_depotnodes[node] = depotbool
            new_shortenings[node] = shortening

            try:
                if new_depotnodes[node] == previous_depotnodes[node]:
                    NODES_ARE_NEW[node] = False
                else:
                    NODES_ARE_NEW[node] = True

            except: # Very likely, it did not exist before
                NODES_ARE_NEW[node] = True

        nodeslist = deepcopy(new_nodeslist)
        nodeslist = sorted(nodeslist)

        depotnodes = deepcopy(new_depotnodes)
        depotnodes = dict(sorted(depotnodes.items()))

        shortenings = deepcopy(new_shortenings)
        shortenings = dict(sorted(shortenings.items()))

        self.root.destroy()

def nodeswin(winmaster):
    global nodeslist, depotnodes, shortenings
    if window_blocker.IS_OPEN:
        messagebox.showinfo(lang.generic_windowopen, lang.generic_pleaseclose)
        return

    win = Toplevel(winmaster)
    win.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
    win.bind("<Destroy>", lambda e: window_blocker.window_destruction_protocol())
    window_blocker.IS_OPEN = True
    win.geometry('800x600')
    win.configure(bg=colour.WINDOW_BACKGROUNDS)
    win.title(lang.nodes_title)
    win_icon = PhotoImage(file=relative_to_nodes("icon2.png"))
    win.iconphoto(False, win_icon)

    buttonframe = Frame(master=win, background=colour.WINDOW_BACKGROUNDS)

    btn = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND)
    btn.image = PhotoImage(file=relative_to_nodes('addrow.png'))
    btn.configure(image=btn.image)

    btn2 = Button(buttonframe, borderwidth=0, highlightthickness=0, relief='flat', bg=colour.TITLES_BACKGROUND)
    btn2.image = PhotoImage(file=relative_to_nodes('save.png'))
    btn2.configure(image=btn2.image)

    btn.grid(row=0, column=0, padx=20, pady=10)
    btn2.grid(row=0, column=1, padx=20, pady=10)

    buttonframe.pack(anchor='center')

    # Initialize a Scrollable frame:
    Scrollable = nodes_scrollableframe(win, bg=colour.FRAME_BACKGROUND, x_scroll=False, bd=0)

    # Commands 1 to 3 already defined, reconfiguring
    btn.configure(command=Scrollable.addNewLabel)
    btn2.configure(command=Scrollable.define_nodes)

    if len(nodeslist) == 0:
        Scrollable.addNewLabel()

    else:
        for node in nodeslist:
            Scrollable.addNewLabel()

            # Node name
            Scrollable.entries[-1][0].insert(0, node)

            # Node shortening
            Scrollable.entries[-1][1].insert(0, shortenings[node])

            # Depot availability
            Scrollable.bools[-1].set(value=depotnodes[node])

        Scrollable.update()
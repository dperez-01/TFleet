'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        tkwidgets.py

 Author:      perez

 Created:     23/10/2023
 Copyright:   (c) perez 2023
-------------------------------------------------------------------------------
'''
from tkinter import Frame, Canvas, Scrollbar, END, INSERT, Text, OptionMenu, StringVar, Label, colorchooser, Button, Toplevel, Checkbutton, BooleanVar
from tkinter.ttk import Combobox, Style
from tkcalendar import Calendar

from PIL import Image, ImageTk
from abc import abstractmethod, ABCMeta
import time

font = ('futura', 10)

import settings
if settings.COLOUR_PALETTE == 'Dark':
    import colour.night_palette as colour
elif settings.COLOUR_PALETTE == 'Light':
    import colour.day_palette as colour
elif settings.COLOUR_PALETTE == 'Blue':
    import colour.blue_palette as colour

combostyle = Style()
combostyle.theme_use('clam')
combostyle.configure("Custom.TCombobox", foreground=colour.INPUT_FOREGROUND,  # Text color
                     background=colour.AUX_INPUT_BACKGROUND,  # Arrow background
                     fieldbackground=colour.INPUT_BACKGROUND,  # Entry field background
                     arrowcolor=colour.INPUT_FOREGROUND,  # Dropdown arrow color
                     selectbackground=colour.AUX_INPUT_BACKGROUND,  # Background color when an item is selected (in dropdown)
                     selectforeground=colour.INPUT_FOREGROUND,  # Text color when selected
                     bordercolor=colour.HIGHLIGHT,  # Border around the entry field
                     insertcolor=colour.INPUT_FOREGROUND,  # Cursor color
                     # lightcolor="purple",             # Top-left edge (highlight)
                     # darkcolor="purple",              # Bottom-right edge (shadow)
                     relief="flat"  # Optional: makes edges flat or raised
                     )


class ScrollableFrame(Frame):
    __metaclass__ = ABCMeta

    def __init__(self, winmaster, y_scroll=True, x_scroll=True, frameborder=10, packside='left', **kwargs):
        # General items
        self.canvas = Canvas(winmaster, highlightthickness=0, **kwargs)
        Frame.__init__(self, self.canvas, borderwidth=frameborder, **kwargs)
        self.y_scroll = y_scroll
        self.x_scroll = x_scroll
        self.root = winmaster # Saving reference

        # self.option_add("*TCombobox*Listbox*SelectFont", font)

        # Scrollbars
        if self.y_scroll:
            self.verticalscrollbar = Scrollbar(winmaster, orient='vertical', command=self.canvas.yview)
            self.canvas.config(yscrollcommand=self.verticalscrollbar.set)

            self.root.bind("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))

        if self.x_scroll:
            self.horizontalscrollbar = Scrollbar(winmaster, orient='horizontal', command=self.canvas.xview)
            self.canvas.config(xscrollcommand=self.horizontalscrollbar.set)

            if not self.y_scroll:
                self.root.bind("<MouseWheel>", lambda event: self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))
            else:
                self.root.bind("<Shift-MouseWheel>", lambda event: self.canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

        self.frameid = self.canvas.create_window(0, 0, window=self, anchor='nw', tags=("canvas_frame",))
        self.canvas.bind('<Configure>', lambda event: self.canvas.itemconfigure(self.frameid, width=event.width))

        # Positioning
        if self.y_scroll:
            self.verticalscrollbar.pack(fill='y', side='right', expand='false')

        if self.x_scroll:
            self.horizontalscrollbar.pack(fill='x', side='bottom', expand='false')

        self.canvas.pack(fill='both', side=packside, expand='true')


    def updateScrollRegion(self):
        self.canvas.update_idletasks()
        self.canvas.config(scrollregion=self.bbox())

    @abstractmethod
    def addNewLabel(self, *args, **kwargs):
        raise NotImplementedError("Implemented in child classes")

    @abstractmethod
    def deleterow(self, event, *args, **kwargs):
        raise NotImplementedError("Implemented in child classes")

    @abstractmethod
    def destroy_row(self, index, *args, **kwargs):
        raise NotImplementedError("Implemented in child classes")

class AutocompleteCombobox(Combobox):
    """:class:`Combobox` widget that features autocompletion."""
    def __init__(self, master=None, completevalues=None, **kwargs):
        """
        Create an AutocompleteCombobox.

        :param master: master widget
        :type master: widget
        :param completevalues: autocompletion values
        :type completevalues: list
        :param kwargs: keyword arguments passed to the :class:`Combobox` initializer
        """
        # self.style = Style()
        # self.style.configure('TCombobox', font=('futura', 10), background="#d9d9d9", foreground="#000716")
        Combobox.__init__(self, master, values=completevalues, font=font, style="Custom.TCombobox", **kwargs)
        self.baselist = completevalues
        # self.bind('<KeyRelease>', self.filter)
        self._completion_list = completevalues
        if isinstance(completevalues, list):
            self.set_completion_list(completevalues)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        # navigate on keypress in the dropdown:
        # code taken from https://wiki.tcl-lang.org/page/ttk%3A%3Acombobox by Pawel Salawa, copyright 2011
        self.tk.eval("""
                        proc ComboListKeyPressed {w key} {
                                if {[string length $key] > 1 && [string tolower $key] != $key} {
                                        return
                                }
                        
                                set cb [winfo parent [winfo toplevel $w]]
                                set text [string map [list {[} {\[} {]} {\]}] $key]
                                if {[string equal $text ""]} {
                                        return
                                }
                        
                                set values [$cb cget -values]
                                set x [lsearch -glob -nocase $values $text*]
                                if {$x < 0} {
                                        return
                                }
                        
                                set current [$w curselection]
                                if {$current == $x && [string match -nocase $text* [lindex $values [expr {$x+1}]]]} {
                                        incr x
                                }
                        
                                $w selection clear 0 end
                                $w selection set $x
                                $w activate $x
                                $w see $x
                        }
                        
                        set popdown [ttk::combobox::PopdownWindow %s]
                        bind $popdown.f.l <KeyPress> [list ComboListKeyPressed %%W %%K]
                    """ % (self))
        self.unbind_class("TCombobox", "<MouseWheel>")
        self.lasttime = 0

    def set_completion_list(self, completion_list):
        """
        Use the completion list as drop down selection menu, arrows move through menu.

        :param completion_list: completion values
        :type completion_list: list
        """
        self._completion_list = sorted(completion_list, key=str.lower)  # Work with a sorted list
        self.configure(values=completion_list)
        self._hits = []
        self._hit_index = 0
        self.position = 0
        self.bind('<KeyRelease>', self.handle_keyrelease)
        # self['values'] = self._completion_list  # Setup our popup menu

    def autocomplete(self, delta=0):
        """
        Autocomplete the Combobox.

        :param delta: 0, 1 or -1: how to cycle through possible hits
        :type delta: int
        """
        if time.time() >= self.lasttime + 0.3:
            if delta:  # need to delete selection otherwise we would fix the current position
                self.delete(self.position, END)
            else:  # set position to end so selection starts where textentry ended
                self.position = len(self.get())
            # collect hits
            _hits = []
            for element in self._completion_list:
                if element.lower().startswith(self.get().lower()):  # Match case insensitively
                    _hits.append(element)
            # if we have a new hit list, keep this in mind
            if _hits != self._hits:
                self._hit_index = 0
                self._hits = _hits
            # only allow cycling if we are in a known hit list
            if _hits == self._hits and self._hits:
                self._hit_index = (self._hit_index + delta) % len(self._hits)
            # now finally perform the autocompletion
            if self._hits:
                self.delete(0, END)
                self.insert(0, self._hits[self._hit_index])
                self.select_range(self.position, END)
                self.lasttime = time.time()

    def handle_keyrelease(self, event):
        """
        Event handler for the keyrelease event on this widget.

        :param event: Tkinter event
        """
        self.filter()
        if event.keysym == "BackSpace":
            self.delete(self.index(INSERT), END)
            self.position = self.index(END)
        if event.keysym == "Left":
            if self.position < self.index(END):  # delete the selection
                self.delete(self.position, END)
            else:
                self.position -= 1  # delete one character
                self.delete(self.position, END)
        if event.keysym == "Right":
            self.position = self.index(END)  # go to end (no selection)
        if event.keysym == "Return":
            self.handle_return(None)
            return
        if len(event.keysym) == 1:
            self.autocomplete()
            # No need for up/down, we'll jump to the popup
            # list at the position of the autocompletion

    # noinspection PyUnusedLocal
    def handle_return(self, event):
        """
        Function to bind to the Enter/Return key so if Enter is pressed the selection is cleared

        :param event: Tkinter event
        """
        self.icursor(END)
        self.selection_clear()

    def config(self, **kwargs):
        """Alias for configure"""
        self.configure(**kwargs)

    def configure(self, **kwargs):
        """Configure widget specific keyword arguments in addition to :class:`Combobox` keyword arguments."""
        if "completevalues" in kwargs:
            self.set_completion_list(kwargs.pop("completevalues"))
        return Combobox.configure(self, **kwargs)

    def cget(self, key):
        """Return value for widget specific keyword arguments"""
        if key == "completevalues":
            return self._completion_list
        return Combobox.cget(self, key)

    def keys(self):
        """Return a list of all resource names of this widget."""
        keys = Combobox.keys(self)
        keys.append("completevalues")
        return keys

    def __setitem__(self, key, value):
        self.configure(**{key: value})

    def __getitem__(self, item):
        return self.cget(item)

    def filter(self):
        value = self.get()
        if value == '':
            self['values'] = self.baselist

        else:
            valid = []
            for item in self.baselist:
                if value.lower() in item.lower():
                    valid.append(item)

            self['values'] = valid

# class iText(Text):
#     def __init__(self, stdwidth_mult=2, stdheight_mult=3, width=142, height=19, **kwargs):
#         Text.__init__(self, **kwargs)
#
#         self.master.update()
#         self.stdwidth = width/3840.0 # Si diseñase a la misma resolucion que imprimo, el denominador seria self.master.winfo_width()
#         self.stdheight = height/2160.0 # Si diseñase a la misma resolucion que imprimo, el denominador seria self.master.winfo_height()
#         self.stdwidth_mult = stdwidth_mult
#         self.stdheight_mult = stdheight_mult
#         self.bind("<Tab>", self.focus_next_widget)
#         self.bind('<FocusIn>', self.text_resizer)
#         self.bind('<FocusOut>', self.text_resizer)
#         self.place(relwidth=self.stdwidth, relheight=self.stdheight)
#     def focus_next_widget(self, event):
#         event.widget.tk_focusNext().focus()
#         return "break"
#
#     def text_resizer(self, event):  # values get None when forced by place method # todo DEPRECATED comment?? <-> never None
#         if event.widget == event.widget.focus_get(): # event is get
#             if not event.widget.stdheight == None: event.widget.place(relheight=event.widget.stdheight*event.widget.stdheight_mult)
#             if not event.widget.stdwidth == None: event.widget.place(relwidth=event.widget.stdwidth_mult*event.widget.stdwidth)
#             # event.widget.lift() Careful
#         else: # event is "un"-get (drop)
#             if not event.widget.stdheight == None: event.widget.place(relheight=event.widget.stdheight)
#             if not event.widget.stdwidth == None: event.widget.place(relwidth=event.widget.stdwidth)

class ToolTip(object): # TODO mandar a tkwidgets

    def __init__(self, widget, text):
        self.widget = widget
        self.tipwindow = None
        self.text = text
        self.widget.bind('<Enter>', self.enter)
        self.widget.bind('<Leave>', self.leave)

    def showtip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return

        self.tipwindow = Toplevel(self.widget)
        self.tipwindow.wm_overrideredirect(1)
        label = Label(self.tipwindow, text=self.text, justify='left', relief='solid', borderwidth=1)
        label.pack(ipadx=1, ipady=1)
        self.tipwindow.update()
        x, y, cx, cy = self.widget.bbox("insert")
        x = x + self.widget.winfo_rootx() + self.widget.winfo_width()
        y = y + self.widget.winfo_rooty() + self.widget.winfo_height() - self.tipwindow.winfo_height()
        self.tipwindow.wm_geometry("+%d+%d" % (x, y))

    def hidetip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

    def enter(self, event): # noqa
        self.showtip(self.text)
    def leave(self, event): # noqa
        self.hidetip()

class iText(Text):
    def __init__(self, stdheight_mult=3, height=1, **kwargs):
        Text.__init__(self, height=height, width=20, **kwargs)

        self.master.update()
        self.stdheight = height # Si diseñase a la misma resolucion que imprimo, el denominador seria self.master.winfo_height()
        self.stdheight_mult = stdheight_mult
        self.bind("<Tab>", self.focus_next_widget)
        self.bind('<FocusIn>', self.text_resizer)
        self.bind('<FocusOut>', self.text_resizer)
        # self.row = row
        # self.column = column
        # self.padx = padx
        # self.ipadx = ipadx
        # self.ipadx = sticky
        # self.grid(row=self.row, column=self.column, )

    def focus_next_widget(self, event):
        event.widget.tk_focusNext().focus()
        return "break"

    def text_resizer(self, event):  # values get None when forced by place method # todo DEPRECATED comment?? <-> never None
        if self == event.widget.focus_get(): # event is get
            self.configure(height=self.stdheight*self.stdheight_mult)
            self.master.update()
        else: # event is "un"-get (drop)
            self.configure(height=self.stdheight)
            self.master.update()

class CustomCalendar(Calendar):
    def __init__(self, master=None, allowed_weekdays=[], **kw):
        self._select_only = allowed_weekdays
        Calendar.__init__(self, master, **kw)
        # change initially selected day if not right day
        if self._sel_date and not (self._sel_date.isoweekday() - 1) in allowed_weekdays:
            year, week, wday = self._sel_date.isocalendar()
            # get closest weekday
            next_wday = max(allowed_weekdays, key=lambda d: (d - wday + 1) > 0) + 1
            sel_date = self.date.fromisocalendar(year, week + int(next_wday < wday), next_wday)
            self.selection_set(sel_date)

    def _display_calendar(self):
        # display calendar
        Calendar._display_calendar(self)
        # disable not allowed days
        for i in range(6):
            for j in range(7):
                if j in self._select_only:
                    continue
                self._calendar[i][j].state(['disabled'])

class ImagedOptionMenu(OptionMenu):
    def __init__(self, master, value, images_values_dict, **kwargs):
        values = list(images_values_dict.keys())

        # Store dict
        self.images = images_values_dict

        # Create var and track it
        self.trackvar = StringVar(master=master, value=value)

        # Init standard class
        OptionMenu.__init__(self, master, self.trackvar, *values, **kwargs)

        # Assign initial image
        self.configure(image=images_values_dict[value], compound="left", indicatoron=0)

        # Assign images to menu
        for val, image in images_values_dict.items():
            self['menu'].entryconfigure(val, image=images_values_dict[val], compound="left")

        # Track var
        self.trackvar.trace_add("write", self.trackvar_callback)

    def trackvar_callback(self, *args): #noqa
        self.configure(image=self.images[self.get()], compound="left")

    def get(self):
        return self.trackvar.get()

class ColorEntry(Label):
    def __init__(self, master, base_color, **kwargs):
        Label.__init__(self, master=master, text=base_color, bg=base_color, **kwargs)
        self.bind("<Button-1>", self.color_picker)

    def color_picker(self, event):
        color = colorchooser.askcolor(title='Choose color')
        color = color[1]

        if not color == None:
            self.configure(bg=color, text=color)

        self.nametowidget(self.winfo_toplevel()).lift()

    def set(self, str_color):
        self.configure(bg=str_color, text=str_color)

    def get(self):
        return self.cget('bg')

class iButton(Button):
    def __init__(self, imageobj=None, **kwargs):
        Button.__init__(self, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.imageobj = imageobj
        self.image = ImageTk.PhotoImage(self.imageobj) # Garbage collection

    def on_resize(self, event):
        new_width = event.width
        new_height = event.height
        new_im = self.imageobj.resize((new_width, new_height), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(new_im) # Garbage collection
        self.configure(image=self.image)

class ResizingCanvas(Canvas):
    def __init__(self, parent, imageobj, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.imageobj = imageobj
        self.bind("<Configure>", self.on_resize)
        self.canvasimage = self.create_image(0, 0, image=ImageTk.PhotoImage(self.imageobj), anchor='nw') # Garbage collection
        self.texts = []

    def on_resize(self, event):
        new_width = event.width
        new_height = event.height
        self.mywidth = new_width
        self.myheight = new_height
        new_im = self.imageobj.resize((new_width, new_height), Image.LANCZOS)
        self.image = ImageTk.PhotoImage(new_im) # Garbage collection
        self.itemconfig(self.canvasimage, image=self.image)

class FancyCheckButton(Label):
    def __init__(self, master, initial_value, **kwargs):
        Label.__init__(self, master=master, bd=2, highlightcolor=colour.HIGHLIGHT, highlightbackground=colour.HIGHLIGHT, highlightthickness=2, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND)
        self.var = BooleanVar(master=master, value=initial_value)
        self.columnconfigure(0, weight=1)
        self.checkbutton = Checkbutton(self, variable=self.var, bd=2, selectcolor=colour.INPUT_BACKGROUND, bg=colour.INPUT_BACKGROUND, fg=colour.INPUT_FOREGROUND, **kwargs)
        self.checkbutton.grid(row=0, column=0)

    def get(self):
        return self.var.get()

    def set(self, value):
        self.var.set(value)
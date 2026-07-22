'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        startmenu.py

 Author:      perez

 Created:     14/09/2023
 Copyright:   (c) perez 2023
-------------------------------------------------------------------------------
'''
if __name__ == '__main__':
    from multiprocessing import freeze_support
    freeze_support()

    import ctypes.wintypes
    ctypes.windll.shcore.SetProcessDpiAwareness(True)
    # import sys
    # if getattr(sys, 'frozen', False):
    #     import pyi_splash

    import settings
    from tkinter import Tk # Main window should be initialised immeadiately to prevent styling quirks
    window = Tk()

    import settings_manager

    # Also utils
    import startmenu_utils as utils

    # Now, import language and assets
    from pathlib import Path
    if settings.LANGUAGE == 'English':
        import language.EN as lang
        if settings.COLOUR_PALETTE == 'Dark':
            import colour.night_palette as colour
            OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\EN\night\startmenu")
            OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\night\solved")
        elif settings.COLOUR_PALETTE == 'Light':
            import colour.day_palette as colour
            OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\EN\day\startmenu")
            OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\day\solved")
        elif settings.COLOUR_PALETTE == 'Blue':
            import colour.blue_palette as colour
            OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\EN\blue\startmenu")
            OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\EN\blue\solved")

    elif settings.LANGUAGE == 'Castellano':
        import language.ES as lang
        if settings.COLOUR_PALETTE == 'Dark':
            import colour.night_palette as colour
            OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\ES\night\startmenu")
            OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\night\solved")
        elif settings.COLOUR_PALETTE == 'Light':
            import colour.day_palette as colour
            OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\ES\day\startmenu")
            OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\day\solved")
        elif settings.COLOUR_PALETTE == 'Blue':
            import colour.blue_palette as colour
            OUTPUT_PATH1 = Path(__file__).parent / Path(r".\assets\ES\blue\startmenu")
            OUTPUT_PATH2 = Path(__file__).parent / Path(r".\assets\ES\blue\solved")

    # Simple user identification
    import licensevalidation
    # TODO hay que poner un aviso de expiración de licencia, y que se vea bien pero no moleste (nada de pop-ups)
    # App imports
    from help_manager import open_help
    import win_nodes
    import win_services
    import win_iniservices
    import win_depottransfers
    import win_sleepers
    import win_linkers
    import boxes_library as win_library
    from copy import deepcopy

    # Other imports
    from tkinter import PhotoImage, Label, Button, Spinbox, IntVar
    from tkwidgets import ResizingCanvas, iButton, ToolTip

    from PIL import Image
    import webbrowser

    def relative_to_assets(path: str) -> Path:
        return OUTPUT_PATH1 / Path(path)
    def relative_to_solved(path: str) -> Path:
        return OUTPUT_PATH2 / Path(path)

    # if getattr(sys, 'frozen', False):
    #     pyi_splash.close()

    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - 1280) // 2
    y = (screen_height - 720) // 2
    window.geometry(f"1280x720+{x}+{y}")
    window.configure(bg="#000000")
    window.bind("<F1>", lambda e: open_help())  # Bind F1 key to open help
    window.title(lang.start_title)
    window_icon=PhotoImage(file=relative_to_assets("icon0.png"))
    window.iconphoto(False, window_icon)

    canvas = ResizingCanvas(window, Image.open(relative_to_assets("image_1.png")), bg="#9D6C80", width=1280, height=720, bd=0, highlightthickness=0, relief="ridge")
    canvas.pack(fill="both", expand=True)

    # Buttons
    settings_button = iButton(imageobj=Image.open(relative_to_assets("settings.png")), borderwidth=0, highlightthickness=0, command=lambda: settings_manager.settings_window(window), relief="flat")
    settings_button.place(relx=35.0/3840.0, rely=143.0/2160.0, relwidth=180.0/3840.0, relheight=180.0/2160.0)
    ToolTip(settings_button, text=lang.tt_settings)

    help_button = iButton(imageobj=Image.open(relative_to_assets("help.png")), borderwidth=0, highlightthickness=0, command=open_help, relief="flat")
    help_button.place(relx=35.0/3840.0, rely=426.0/2160.0, relwidth=180.0/3840.0, relheight=180.0/2160.0)
    ToolTip(help_button, text=lang.tt_help)

    save_button = iButton(imageobj=Image.open(relative_to_assets("savefile.png")), borderwidth=0, highlightthickness=0, command=utils.save_file, relief="flat")
    save_button.place(relx=35.0/3840.0, rely=709.0/2160.0, relwidth=180.0/3840.0, relheight=180.0/2160.0)
    ToolTip(save_button, text=lang.tt_save)

    load_button = iButton(imageobj=Image.open(relative_to_assets("loadfile.png")), borderwidth=0, highlightthickness=0, command=utils.load_file, relief="flat")
    load_button.place(relx=35.0/3840.0, rely=992.0/2160.0, relwidth=180.0/3840.0, relheight=180.0/2160.0)
    ToolTip(load_button, text=lang.tt_load)

    loadsolution_button = iButton(imageobj=Image.open(relative_to_assets("loadsolution.png")), borderwidth=0, highlightthickness=0, command=lambda: utils.load_solution(window), relief="flat")
    loadsolution_button.place(relx=35.0/3840.0, rely=1275.0/2160.0, relwidth=180.0/3840.0, relheight=180.0/2160.0)
    ToolTip(loadsolution_button, text=lang.tt_loadsol)

    merge_button = iButton(imageobj=Image.open(relative_to_assets("merge.png")), borderwidth=0, highlightthickness=0, command=lambda: utils.merger(window), relief="flat")
    merge_button.place(relx=35.0/3840.0, rely=1558.0/2160.0, relwidth=180.0/3840.0, relheight=180.0/2160.0)
    ToolTip(merge_button, text=lang.tt_merge)

    library_button = iButton(imageobj=Image.open(relative_to_assets("library.png")), borderwidth=0, highlightthickness=0, command=lambda: win_library.librarywin(window), relief="flat")
    library_button.place(relx=35.0/3840.0, rely=1841.0/2160.0, relwidth=180.0/3840.0, relheight=180.0/2160.0)
    ToolTip(library_button, text=lang.tt_library)

    nodes_button = iButton(imageobj=Image.open(relative_to_assets("nodes.png")), borderwidth=0, highlightthickness=0, command=lambda: win_nodes.nodeswin(window), relief="flat")
    nodes_button.place(relx=350.0/3840.0, rely=1849/2160.0, relwidth=320/3840.0, relheight=228/2160.0)

    iniservices_button = iButton(imageobj=Image.open(relative_to_assets("iniservices.png")), borderwidth=0, highlightthickness=0, command=lambda: win_iniservices.iniserviceswin(window, deepcopy(win_nodes.nodeslist), win_nodes.depotnodes), relief="flat")
    iniservices_button.place(relx=776.0/3840.0, rely=1849/2160.0, relwidth=320/3840.0, relheight=228/2160.0)

    services_button = iButton(imageobj=Image.open(relative_to_assets("services.png")), borderwidth=0, highlightthickness=0, command=lambda: win_services.serviceswin(window, win_nodes.nodeslist), relief="flat")
    services_button.place(relx=1202.0/3840.0, rely=1849/2160.0, relwidth=320/3840.0, relheight=228/2160.0)

    linkers_button = iButton(imageobj=Image.open(relative_to_assets("linkers.png")), borderwidth=0, highlightthickness=0, command=lambda: win_linkers.linkerswin(window, win_nodes.nodeslist, [service for service in win_services.services]), relief="flat")
    linkers_button.place(relx=1628.0/3840.0, rely=1849/2160.0, relwidth=320/3840.0, relheight=228/2160.0)

    transfers_button = iButton(imageobj=Image.open(relative_to_assets("transfers.png")), borderwidth=0, highlightthickness=0, command=lambda: win_depottransfers.transferswin(window), relief="flat")
    transfers_button.place(relx=2054.0/3840.0, rely=1849/2160.0, relwidth=320/3840.0, relheight=228/2160.0)

    sleepers_button = iButton(imageobj=Image.open(relative_to_assets("sleepers.png")), borderwidth=0, highlightthickness=0, command=lambda: win_sleepers.sleeperswin(window), relief="flat")
    sleepers_button.place(relx=2480.0/3840.0, rely=1849/2160.0, relwidth=320/3840.0, relheight=228/2160.0)


    intv = IntVar(window, value=7)
    daystocalculate = Spinbox(window, from_=1, to=7, textvariable=intv, bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND, bd=0, highlightthickness=0, relief="flat", font=('futura', 10))
    daystocalculate.place(relx=2906.0/3840.0, rely=1770/2160.0, relwidth=120/3840.0)
    daystocalculate_label = Label(window, text="days", bg=colour.TITLES_BACKGROUND, fg=colour.TITLES_FOREGROUND, bd=0, highlightthickness=0, relief="flat", font=('futura', 10))
    daystocalculate_label.place(relx=3026.0/3840.0, rely=1770/2160.0, relwidth=200/3840.0)

    calculate_button = iButton(imageobj=Image.open(relative_to_assets("calculate.png")), borderwidth=0, highlightthickness=0, command=lambda: utils.calculate(window, intv), relief="flat")
    calculate_button.place(relx=2906.0/3840.0, rely=1849/2160.0, relwidth=320/3840.0, relheight=228/2160.0)

    cut_calculation_button = iButton(imageobj=Image.open(relative_to_assets("multicuts.png")), borderwidth=0, highlightthickness=0, command=lambda: utils.multicuts_calculate(window), relief="flat")
    cut_calculation_button.place(relx=3332.0/3840.0, rely=1849/2160.0, relwidth=320/3840.0, relheight=228/2160.0)

    window.attributes('-topmost', True)

    # welcome_text
    licensevalidation.check_license()
    text_value = lang.welcome + str(licensevalidation.USER) + lang.serial_number + str(licensevalidation.SERIAL_NUMBER) + lang.expiring_on + str(licensevalidation.EXPIRY_DATE)
    welcome_text = Label(window, text=text_value, bg=colour.LICENSE_BACKGROUND, fg=colour.LICENSE_FOREGROUND, justify='left', relief='flat', bd=0, highlightthickness=0, font=("TkFixedFont", 7))
    welcome_text.place(relx=250.0/3840.0, rely=1670/2160.0)

    window.attributes('-topmost', False)


    win_library.load_library()
    window.mainloop()











'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        startmenu_blocker.py

 Author:      Diego Pérez

 Created:     11/09/2025
 Copyright:   (c) perez 2025
-------------------------------------------------------------------------------
'''
# Prevents having more than one window open at the same time, and running the algorith while one is still open
IS_OPEN = False

def window_destruction_protocol():  # noqa
    global IS_OPEN
    IS_OPEN = False
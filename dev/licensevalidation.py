'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        licensevalidation.py

 Author:      perez

 Created:     31/01/2024
 Copyright:   (c) perez 2023
-------------------------------------------------------------------------------
'''
import datetime
import subprocess
import os
# import hashlib
import argon2
import sys
from tkinter import messagebox
from pathlib import Path

# Now, import language
import settings
if settings.LANGUAGE == 'English':
    import language.EN as lang
elif settings.LANGUAGE == 'Castellano':
    import language.ES as lang


USER = None
EXPIRY_DATE = None
SERIAL_NUMBER = None

# def check_license():
#     where = Path(__file__).parent / Path(r".\license\LICENSE.lic")
#     try:
#         file = open(where, 'r')
#         baselines = file.readlines()
#         file.close()
#     except:
#         messagebox.showerror("Could not open license file", 'No LICENSE.lic file found in directory ' + str(Path(__file__).parent / Path(r".\license")))
#         sys.exit()
#
#     lines = []
#     for item in baselines:
#         lines.append(item.strip())
#
#     supposed_machine_id = hashlib.sha512('44x53wc46e5v7b68t7nym'.encode() + subprocess.check_output('wmic bios get serialnumber').decode().split('\n')[1].strip().encode()).hexdigest()
#     supposed_username = hashlib.sha512('44x53wc46e5v7b68t7nym'.encode() + os.getlogin().encode()).hexdigest()
#     supposed_datetime = hashlib.sha512('44x53wc46e5v7b68t7nym'.encode() + lines[3].encode()).hexdigest()
#
#
#     if not supposed_machine_id == lines[1]:
#         messagebox.showerror('Invalid license file', 'This license is not valid for this device.')
#         sys.exit()
#
#     if not lines[2] == supposed_username:
#         messagebox.showerror('Invalid license file', 'This license is not valid for this user.')
#         sys.exit()
#
#     if datetime.datetime.now() <= datetime.datetime.strptime(lines[3], '%Y-%m-%d'):
#         if not lines[4] == supposed_datetime:
#             messagebox.showerror('Invalid license file', 'It seems that you have modified your current license expiry date. This is not accepted. You are encouraged to restore it.')
#             sys.exit()
#     else:
#         messagebox.showerror('Invalid license file', 'Your license has expired.')
#         sys.exit()
#
#     return os.getlogin()


def check_license():
    global USER, EXPIRY_DATE, SERIAL_NUMBER

    where = Path(__file__).parent / Path(r".\license\LICENSE.lic")
    try:
        file = open(where, 'r')
        baselines = file.readlines()
        file.close()
    except:
        messagebox.showerror(lang.lic_not_open, lang.lic_not_found + str(Path(__file__).parent / Path(r".\license")))
        sys.exit()

    lines = []
    for item in baselines:
        lines.append(item.strip())

    USER = os.getlogin()
    EXPIRY_DATE = lines[3]
    SERIAL_NUMBER = subprocess.check_output('wmic bios get serialnumber').decode().split('\n')[1].strip()

    machine_id_manager = argon2.PasswordHasher(type=argon2.Type.I)
    username_manager = argon2.PasswordHasher(type=argon2.Type.I)
    datetime_manager = argon2.PasswordHasher(type=argon2.Type.I)

    try:
        machine_id_manager.verify(lines[1], subprocess.check_output('wmic bios get serialnumber').decode().split('\n')[1].strip().upper())
    except:
        messagebox.showerror(lang.lic_invalid, lang.lic_device)
        sys.exit()

    try:
        username_manager.verify(lines[2], USER.upper())
    except:
        messagebox.showerror(lang.lic_invalid, lang.lic_user)
        sys.exit()

    try:
        datetime_manager.verify(lines[4], lines[3])
    except:
        messagebox.showerror(lang.lic_invalid, lang.lic_modified)
        sys.exit()

    if not datetime.datetime.now() <= datetime.datetime.strptime(lines[3], '%Y-%m-%d'):
        messagebox.showerror(lang.lic_invalid, lang.lic_expired)
        sys.exit()

    return os.getlogin()

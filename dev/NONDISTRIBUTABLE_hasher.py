'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        NONDISTRIBUTABLE_hasher.py

 Author:      perez

 Created:     31/01/2024
 Copyright:   (c) perez 2024
-------------------------------------------------------------------------------
'''
# COMANDOS A UTILIZAR en el simbolo del sistema:
# Machine ID (numero de serie): wmic bios get serialnumber
# Nombre de usuario: whoami y coger solo lo ultimo



# import hashlib
# def generate_valid_license(machine_id, username, kill_date):
#     hashed_machine_id = hashlib.sha512('44x53wc46e5v7b68t7nym'.encode() + machine_id.encode()).hexdigest()
#     hashed_username = hashlib.sha512('44x53wc46e5v7b68t7nym'.encode() + username.encode()).hexdigest()
#     hashed_datetime = hashlib.sha512('44x53wc46e5v7b68t7nym'.encode() + kill_date.encode()).hexdigest()
#
#     file = open('LICENSE ' + username.upper() + '.lic', 'w')
#     file.writelines([str('[LICENSE KEY]') + '\n', str(hashed_machine_id) + '\n', str(hashed_username) + '\n', str(kill_date) + '\n', str(hashed_datetime) + '\n'])
#     file.close()

import argon2
def generate_valid_license(machine_id, username, kill_date):
    machine_id_manager = argon2.PasswordHasher(type=argon2.Type.I)
    username_manager = argon2.PasswordHasher(type=argon2.Type.I)
    datetime_manager = argon2.PasswordHasher(type=argon2.Type.I)

    hashed_machine_id = machine_id_manager.hash(machine_id.upper())
    hashed_username = username_manager.hash(username.upper())
    hashed_datetime = datetime_manager.hash(kill_date)

    file = open('LICENSE ' + username.upper() + '.lic', 'w')
    file.writelines([str('[LICENSE KEY]') + '\n', str(hashed_machine_id) + '\n', str(hashed_username) + '\n', str(kill_date) + '\n', str(hashed_datetime) + '\n'])
    file.close()

# Year, Month, Day
# Talgo A
# generate_valid_license('5CD321HC13', 'Jamarcos', '2027-05-31') # 5CD321HC13,  Jamarcos

# Fuencarral
generate_valid_license('5CG3414LR4', 'msanz', '2027-05-31') # 5CG3414LR4,  msanz
generate_valid_license('5CD4201DY1', 'pcaerols', '2027-05-31') # 5CD4201DY1,  pcaerols
generate_valid_license('5CD4201DWG', '75532', '2027-05-31') # 5CD4201DWG,  75532,  María del Pilar Ruiz
generate_valid_license('5CD4201DXB', 'jmvelix', '2027-05-31') # 5CD4201DXB,  jmvelix,  José Manuel Vélix
generate_valid_license('5CD9141CXT', 'ibajo', '2027-05-31') # 5CD9141CXT,  ibajo,  Inmaculada Bajo
generate_valid_license('5CD9141ZX2', '71522', '2027-05-31') # 5CD9141ZX2,  71522,  leticia bravo
generate_valid_license('5CD3490G48', '14893', '2027-05-31') # 5CD3490G48,  14893,  Luis madrigal

# Málaga
generate_valid_license('5CD0152W70', 'adelpino', '2027-05-31') # 5CD0152W70,  adelpino
generate_valid_license('5CD9141ZXQ', 'cramirez', '2027-05-31') # 5CD0152W70,  Celia Ramírez Gallardo
generate_valid_license('5CD2432SHR', 'mjconejo', '2027-05-31') # 5CD2432SHR,  mjconejo,  María José Conejo
generate_valid_license('5CD3490G2F', 'rgbernal', '2027-05-31') # 5CD3490G2F,  rgbernal,  Remedios González Bernal

# Barcelona
generate_valid_license('5CD4201DWL', '77106', '2027-05-31') # 5CD4201DWL,  Raúl Martínez Gálvez, 77106
generate_valid_license('5CD3490G4L', 'magiron', '2027-05-31') # 5CD0152W70,  Miguel Ángel Girón

# Talgo B
generate_valid_license('5CD321HC18', '70584', '2027-05-31') # 5CD321HC18,  70584,  Sonia Sánchez

# Ingeman
# generate_valid_license('CV6T5J3', 'adolf', '2099-01-01')

# Pro master of the universe
# generate_valid_license('5CD2114L08', 'perez', '2099-01-01')



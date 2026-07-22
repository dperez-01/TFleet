'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        HEURISTIC_matrix_builder.py

 Author:      Diego Pérez

 Created:     28/05/2024
 Copyright:   (c) perez 2024
-------------------------------------------------------------------------------
'''
from copy import deepcopy
from tkinter import messagebox

import numpy as np

# First of all, import settings manager to configure the applicaction
import settings

# Now, import language
if settings.LANGUAGE == 'English':
    import language.EN as lang
elif settings.LANGUAGE == 'Castellano':
    import language.ES as lang

import copy
import datetime
from frozendict import frozendict # TODO probably no longer needed, as no cached nor njit functions are longer needed

def build_km_service(services):
    return [services[service]['kilometers'] for service in services]

def build_departure_time(services):
    return [services[service]['departure-time'] for service in services]

def build_duration_service(services):
    return [services[service]['arrival-time'] - services[service]['departure-time'] for service in services]

def build_arrival_time(services):
    return [services[service]['arrival-time'] for service in services]

def build_depot(services, depotnodes):
    return [1 if depotnodes[services[service]['destiny']] else 0 for service in services]

# def build_condition(numservices, services):
#     condition = [0 for _ in range(numservices)]
#     stringed_condition = ['' for _ in services]
#     already_forced = []
#     for i in range(numservices):
#         for s in range(numservices):
#             if services['service' + str(s + 1)]['id'] == services['service' + str(i + 1)]['forced'] and services['service' + str(s + 1)]['departure-time'] >= services['service' + str(i + 1)]['arrival-time'] and s not in already_forced:
#                 already_forced.append(s)
#                 condition[i] = s
#                 stringed_condition[i] = services['service' + str(s + 1)]['id']
#                 break
#
#     return condition, stringed_condition

def build_table_conversion(services):
    return [services[service]['id'] for service in services]

def build_color_list(services):
    return [services[service]['color'] for service in services]

def build_valid_predecessors(numtrains, numservices, services, expanded_services, linkers):
    # Create all predecessors
    predecessors = [[0 for _ in range(numservices)] for _ in range(numservices)] # En cada columna, 1 si es un predecesor; ojo con los iniservices. Si lo miras por filas, estás viendo los sucesores.
    uses_linkers = [[0 for _ in range(numservices)] for _ in range(numservices)]
    valid_linkers = [[[] for _ in range(numservices)] for _ in range(numservices)]

    for col in range(numtrains, numservices):
        for row in range(numservices):
            if services['service' + str(row + 1)]['arrival-time'] + settings.GAP_HOUR <= services['service' + str(col + 1)]['departure-time'] and services['service' + str(row + 1)]['destiny'] == services['service' + str(col + 1)]['origin'] and services['service' + str(row + 1)]['forced'] == '' and row != col:
                predecessors[row][col] = 1

    # Apply bans
    not_banned_yet = [list(services['service' + str(row + 1)]['bans']) for row in range(numservices)]
    for row in range(numservices):
        for col in range(numtrains, numservices):
            if len(not_banned_yet[row]) == 0:
                break # No bans left, check next row
            if services['service' + str(col + 1)]['id'] in services['service' + str(row + 1)]['bans'] and services['service' + str(col + 1)]['departure-time'] >= services['service' + str(row + 1)]['arrival-time'] and services['service' + str(col + 1)]['id'] in not_banned_yet[row]:
                predecessors[row][col] = 0
                not_banned_yet[row].remove(services['service' + str(col + 1)]['id'])

    # Apply conditioned
    # Note: a separate condition array is kept, as it enables avoidance of row_pool creation processes. Implications in this matrix are to check infeasibilities
    condition = [0 for _ in range(numservices)]
    already_forced = []

    for row in range(numservices):
        for col in range(numtrains, numservices):
            if services['service' + str(col + 1)]['id'] == services['service' + str(row + 1)]['forced'] and services['service' + str(col + 1)]['departure-time'] >= services['service' + str(row + 1)]['arrival-time'] and col not in already_forced:
                already_forced.append(col)
                condition[row] = col
                predecessors[row] = [0 for _ in range(numservices)]
                for row2 in range(numservices):
                    predecessors[row2][col] = 0
                predecessors[row][col] = 1
                break

    # Create stringed condition, spanning a double horizon and cutting down to ensure that constraint information is displayed correctly even when the forced service does not exist within the standard horizon # TODO piensa que luego hay que recortar stringed condition a su valor originañ
    stringed_condition = ['' for _ in services]
    already_forced = []
    for row in range(numservices):
        for col in range(numtrains, len(expanded_services)):
            if expanded_services['service' + str(col + 1)]['id'] == expanded_services['service' + str(row + 1)]['forced'] and expanded_services['service' + str(col + 1)]['departure-time'] >= expanded_services['service' + str(row + 1)]['arrival-time'] and col not in already_forced:
                already_forced.append(col)
                stringed_condition[row] = expanded_services['service' + str(col + 1)]['id']
                break

    for row in range(numservices): # "Predecessors"
        if not condition[row]: # skip if forces something
            for col in range(numservices):  # "Successors"
                if not col in already_forced: # skip if is forced by something else
                    link_index = -1
                    for link in linkers: # Check all linkers
                        link_index += 1
                        if services['service' + str(row + 1)]['destiny'] == linkers[link]['origin'] and services['service' + str(col + 1)]['origin'] == linkers[link]['destiny']: # check location # TODO apply other restrictions around here, if needed
                            # intersection
                            interval_start = max(services['service' + str(row + 1)]['arrival-time'], linkers[link]['opening-time'])
                            interval_end = min(services['service' + str(col + 1)]['departure-time'], linkers[link]['ending-time'])

                            # no overlap if intersection does not exist
                            if interval_start > interval_end:
                                continue

                            # TODO está comprobado que interval_start + duración paso >= interval_end?
                            if interval_start + linkers[link]['duration'] <= interval_end and services['service' + str(col + 1)]['departure-time'] - services['service' + str(row + 1)]['arrival-time'] >= settings.GAP_HOUR:
                                predecessors[row][col] = 1
                                uses_linkers[row][col] = 1
                                valid_linkers[row][col].append(link_index)


    # Check that every service has at least a predecessor
    for col in range(numtrains, numservices):
        if sum([predecessors[row][col] for row in range(numservices)]) < 1:
            if sum([uses_linkers[row][col] for row in range(numservices)]) < 1:
                print('\x1b[38;5;220mCtrl-f me in matrix builder, something happened.\x1b[0m Col is ', col)
                print('\x1b[38;5;129mService is\x1b[0m', services['service' + str(col + 1)]['id'], '\x1b[38;5;129mwith departure time\x1b[0m', services['service' + str(col + 1)]['departure-time'])
                [print(predecessors[row]) for row in range(numservices)]
                print('\n\nLINKERS USE')
                [print(uses_linkers[row]) for row in range(numservices)]
                return False, services['service' + str(col + 1)]['id'],  services['service' + str(col + 1)]['departure-time'], None, None

    lens = []
    for row in range(numservices):
        for col in range(numservices):
            lens.append(len(valid_linkers[row][col]))
    max_valid_linkers = max(lens)
    for row in range(numservices):
        for col in range(numservices):
            [valid_linkers[row][col].append(-1) for _ in range(max_valid_linkers - len(valid_linkers[row][col]))]

    return predecessors, condition, stringed_condition, uses_linkers, valid_linkers

def build_capacities(numservices, services, depotnodes, predecessors, transfers, numerical_week, next_m_duration, initial_occupation, uses_linkers, valid_linkers, info_linkers): # TODO esta hecho ya pero comprueba por que sigue aqui-> additionally, data must be provided for the canvas builder. This data is basically the id of the service, as well as duration and color data. The canvas might directly use the item referred as "transfers" here
    pos = 0
    times_manager = {}
    total_capacity = []
    capacities_management = [[[] for _ in range(numservices)] for _ in range(numservices)]
    for depot in transfers:
        if transfers[depot]['location'] != depot:
            continue # Skip, and later redirect to the forwarded depot

        times_manager[depot] = []
        first = True
        day = -1
        for day_reference in numerical_week:
            day += 1
            for start, end, week_data in transfers[depot]['partitions']: # TODO important to check that these works as intended when using the continuation
                if not first and week_data[day_reference] == '->':
                    end_ = datetime.datetime.strptime(end, '%H:%M').time()  # datetime.time
                    end_ = end_.hour + end_.minute / 60
                    end_ = 24 * (day + 1) if end_ == 0 else 24 * day + end_
                    times_manager[depot][-1][0][1] = end_

                else:
                    if week_data[day_reference] != '':
                        if week_data[day_reference] != '->':
                            total_capacity.append(week_data[day_reference])
                        else: # Reached here because first is True. week_data[day_reference] known to be '->'
                            rows = len(transfers[depot]['partitions']) # Tener en cuenta que para la primera columna, vamos a querer ir hacia atrás desde una cierta posición específica. Es conocida? Es constante?
                            # print(numerical_week, list(reversed(numerical_week)))
                            for col in reversed(numerical_week): # I don't really need to look at the things below the same column. It's non-sense, even if everything is "->" excepting a single number below in my column; then I would just have a single row and make one number as a "first row"
                                for row in range(rows-1, -1, -1):
                                    if transfers[depot]['partitions'][row][2][col] != '->':
                                        total_capacity.append(transfers[depot]['partitions'][row][2][col])
                                        break
                                else: # For loop completely iterated. Yes, this is a weird syntax but having else in the same height of a for loop is a pythonic way of saying that the for loop was not interrupted by a break statement. THen the outer one has to continue and not break
                                    continue
                                break

                    else:
                        total_capacity.append(0)

                    if first:
                        reference_to_very_first = total_capacity[-1] # TODO esta es la linea que casca
                        total_capacity[-1] -= initial_occupation[depot]
                        first = False
                    # TODO trigger a kill if the number becomes negative. Should not be happening.
                    start_ = datetime.datetime.strptime(start, '%H:%M').time()  # datetime.time
                    start_ = 24 * day + start_.hour + start_.minute / 60

                    end_ = datetime.datetime.strptime(end, '%H:%M').time()  # datetime.time
                    end_ = end_.hour + end_.minute / 60
                    end_ = 24 * (day + 1) if end_ == 0 else 24 * day + end_

                    times_manager[depot].append([[start_, end_], pos])
                    pos += 1

        # Expand with the first case of a fictional 8th day
        times, _ = deepcopy(times_manager[depot][0])
        times[0] += 168
        times[1] += 168
        times_manager[depot].append([times, len(total_capacity)])
        total_capacity.append(reference_to_very_first)
        # total_capacity.append(transfers[depot]['partitions'][0][2][numerical_week[0]]) if transfers[depot]['partitions'][0][2][numerical_week[0]] != '' else total_capacity.append(0)

    for depot in transfers:
        if transfers[depot]['location'] != depot:
            forwarded_depot = transfers[depot]['location'].split(' < ')[1]
            times_manager[depot] = deepcopy(times_manager[forwarded_depot])

    for row in range(numservices):
        if depotnodes[services['service' + str(row + 1)]['destiny']]:
            for col in range(numservices):
                if predecessors[row][col]:
                    for times, pos_ref in times_manager[services['service' + str(row + 1)]['destiny']]:
                        # if services['service' + str(row + 1)]['arrival-time'] <= times[0] < services['service' + str(col + 1)]['departure-time'] or times[0] < services['service' + str(row + 1)]['arrival-time'] < times[1]: # TODO no me fio de esta declaracion, para emepzar
                        if (times[0] <= services['service' + str(row + 1)]['arrival-time'] < times[1])   or   (times[0] < services['service' + str(col + 1)]['departure-time'] <= times[1])   or   (services['service' + str(row + 1)]['arrival-time'] <= times[0] < times[1] <= services['service' + str(col + 1)]['departure-time']):
                            definitive_start = max(services['service' + str(row + 1)]['arrival-time'], times[0])
                            available_time = services['service' + str(col + 1)]['departure-time'] - definitive_start - 2 * (transfers[services['service' + str(row + 1)]['destiny']]['duration'] / 60)
                            if uses_linkers[row][col]:
                                # We need to check if both places are related depots. Otherwise (right is not a related depot to left, or not a depot), the available time must consider the linker time as well as the transfer's time
                                left_loc = services['service' + str(row + 1)]['destiny']
                                right_loc = services['service' + str(col + 1)]['origin']
                                if (right_loc not in transfers) or not (right_loc in transfers[left_loc]['location'] or left_loc in transfers[right_loc]['location']): # Transfers would stack with the linker, so we have to reduce the available time.
                                    durations = []
                                    for linker_idx in valid_linkers[row][col]:
                                        if linker_idx != -1:
                                            durations.append(info_linkers[linker_idx]['duration'])
                                    available_time -= sum(durations) / len(durations)
                                # TODO elif The transfers might sometimes be shorter in related depots depending on whether the master is at left or right. Could be implemented here as elif and else.
                            if min(next_m_duration) <= available_time: # Bigger interventions won't fit either, put prevents checking in elements were the most little intervention would not fit, as they would be unnecessary
                                capacities_management[row][col].append([pos_ref, available_time, (transfers[services['service' + str(row + 1)]['destiny']]['duration'] / 60) + definitive_start])
                elif col == row:
                    for times, pos_ref in times_manager[services['service' + str(row + 1)]['destiny']]:
                        if services['service' + str(row + 1)]['arrival-time'] < times[1]:
                            definitive_start = max(services['service' + str(row + 1)]['arrival-time'], times[0])
                            capacities_management[row][col].append([pos_ref, 10000, (transfers[services['service' + str(row + 1)]['destiny']]['duration'] / 60) + definitive_start])

    max_dimension = max([len(capacities_management[row][col]) for row in range(numservices) for col in range(numservices)])
    for row in range(numservices):
        for col in range(numservices):
            if len(capacities_management[row][col]) < max_dimension:
                [capacities_management[row][col].append([-1, -1, -1]) for _ in range(max_dimension - len(capacities_management[row][col]))]

    if len(capacities_management[0][0]) == 0: # If one len is 0, all of them are zero, due to the previous filling mechanism. Fill all with -1 to force Infeasible (C) error as long as one train requires maintenance. @njit will colapse otherwise due to static typing with crazy errors
        for row in range(numservices):
            for col in range(numservices):
                capacities_management[row][col].append([-1, -1, -1])

        messagebox.showerror(lang.hh68, lang.hh69)

    return total_capacity, capacities_management

def build_services_origins(services):
    return [services[service]['origin'] for service in services]

def build_services_destinies(services):
    return [services[service]['destiny'] for service in services]

def build_stringed_departures(services):
    return [services[service]['str_departure-time'] for service in services]

def build_stringed_arrivals(services):
    return [services[service]['str_arrival-time'] for service in services]

def build_arrayed_bans(services):
    return [list(services[service]['bans']) for service in services]

def build_trimmed_km_limit(km_limit, transfers):
    km = max([transfers[depot]['kilometers'] for depot in transfers])
    return [limit - km for limit in km_limit]

def build_linkers_numericals(linkers):
    linkers_km = [linkers[link]['kilometers'] for link in linkers]
    linkers_capacity = [linkers[link]['capacity'] for link in linkers]
    return linkers_km, linkers_capacity

def build_info_linkers(linkers):
    return [linker for linker in linkers.values()]

def build_matrices(daystosolve, realservices, iniservices, depotnodes, numtrains, weekday, next_m_duration, transfers, reallinkers, km_limit):
    week = [0, 1, 2, 3, 4, 5, 6]

    days = lang.FULL_WEEK
    current = datetime.datetime.now().isoweekday() - 1 if weekday == lang.CURRENT else days.index(weekday)

    week = week[current:] + week[:current]
    _week = week

    if daystosolve < 7:
        week = week[:daystosolve]

    expanded_week = week + _week

    services = {}
    expanded_services = {}

    c = 0
    for service in realservices:
        dt = datetime.datetime.strptime(realservices[service]['str_departure-time'], '%H:%M').time()  # datetime.time
        at = datetime.datetime.strptime(realservices[service]['str_arrival-time'], '%H:%M').time()  # datetime.time

        # Turn empty to 0:
        for day in range(7):
            if realservices[service]['week'][day] == '':
                realservices[service]['week'][day] = 0

        # Definition of standard horizon's services
        day = -1
        for day_reference in week:
            day += 1
            for reps in range(realservices[service]['week'][day_reference]):
                c += 1

                services['service' + str(c)] = {}
                services['service' + str(c)]['id'] = service
                services['service' + str(c)]['origin'] = realservices[service]['origin']
                services['service' + str(c)]['destiny'] = realservices[service]['destiny']
                services['service' + str(c)]['kilometers'] = realservices[service]['kilometers']
                services['service' + str(c)]['departure-time'] = 24 * day + dt.hour + dt.minute / 60
                services['service' + str(c)]['arrival_extra_days'] = realservices[service]['arrival_extra_days']
                extradays = 0 if services['service' + str(c)]['arrival_extra_days'] == '' else services['service' + str(c)]['arrival_extra_days']
                services['service' + str(c)]['arrival-time'] = 24 * (day + extradays) + at.hour + at.minute / 60
                services['service' + str(c)]['color'] = realservices[service]['color']
                services['service' + str(c)]['forced'] = realservices[service]['forced']

                services['service' + str(c)]['str_departure-time'] = realservices[service]['str_departure-time']
                services['service' + str(c)]['str_arrival-time'] = realservices[service]['str_arrival-time']
                services['service' + str(c)]['week'] = tuple(realservices[service]['week'])
                services['service' + str(c)]['bans'] = tuple(realservices[service]['bans'])

        # Definition of services for the expanded horizon
        day = -1
        for day_reference in expanded_week:
            day += 1
            for reps in range(realservices[service]['week'][day_reference]):
                c += 1

                expanded_services['service' + str(c)] = {}
                expanded_services['service' + str(c)]['id'] = service
                expanded_services['service' + str(c)]['origin'] = realservices[service]['origin']
                expanded_services['service' + str(c)]['destiny'] = realservices[service]['destiny']
                expanded_services['service' + str(c)]['kilometers'] = realservices[service]['kilometers']
                expanded_services['service' + str(c)]['departure-time'] = 24 * day + dt.hour + dt.minute / 60
                expanded_services['service' + str(c)]['arrival_extra_days'] = realservices[service]['arrival_extra_days']
                extradays = 0 if expanded_services['service' + str(c)]['arrival_extra_days'] == '' else expanded_services['service' + str(c)]['arrival_extra_days']
                expanded_services['service' + str(c)]['arrival-time'] = 24 * (day + extradays) + at.hour + at.minute / 60
                expanded_services['service' + str(c)]['color'] = realservices[service]['color']
                expanded_services['service' + str(c)]['forced'] = realservices[service]['forced']

                expanded_services['service' + str(c)]['str_departure-time'] = realservices[service]['str_departure-time']
                expanded_services['service' + str(c)]['str_arrival-time'] = realservices[service]['str_arrival-time']
                expanded_services['service' + str(c)]['week'] = tuple(realservices[service]['week'])
                expanded_services['service' + str(c)]['bans'] = tuple(realservices[service]['bans'])

    # Create initial occupation:
    initial_occupation = {}
    for node in depotnodes:
        if depotnodes[node]:
            initial_occupation[node] = 0

    # Check iniservices arrival-time
    for ini in iniservices:
        if iniservices[ini]['arrival-time'] == 0 or iniservices[ini]['arrival-time'] == '':
            iniservices[ini]['arrival-time'] = 0.1 # TODO quien dice 0.1, quizas dice 3 (parametro ajustable)
        if '-Depot' in iniservices[ini]['origin']:
            if lang.CHECK_MAINTENANCE in iniservices[ini]['origin']:
                location = iniservices[ini]['origin'].replace(lang.DEPOT_MAINTENANCE, '')
                initial_occupation[location] += 1
            else: # elif 'overnight' in iniservices[ini]['origin']:
                location = iniservices[ini]['origin'].replace(lang.DEPOT_OVERNIGHT, '')
            iniservices[ini]['origin'] = location
            iniservices[ini]['destiny'] = location

    # Defining linkers
    c = 0
    linkers = {}
    for link in reallinkers:
        dt = datetime.datetime.strptime(reallinkers[link]['str_opening-time'], '%H:%M').time()  # datetime.time
        at = datetime.datetime.strptime(reallinkers[link]['str_ending-time'], '%H:%M').time()  # datetime.time

        # Turn empty to 0:
        for day in range(7):
            if reallinkers[link]['week'][day] == '':
                reallinkers[link]['week'][day] = 0

        # Definition of standard horizon's linkers
        day = -1
        for day_reference in week:
            day += 1
            c += 1
            linkers['link' + str(c)] = {}
            linkers['link' + str(c)]['id'] = link
            linkers['link' + str(c)]['origin'] = reallinkers[link]['origin']
            linkers['link' + str(c)]['destiny'] = reallinkers[link]['destiny']
            linkers['link' + str(c)]['kilometers'] = reallinkers[link]['kilometers']
            linkers['link' + str(c)]['duration'] = reallinkers[link]['duration'] / 60
            linkers['link' + str(c)]['opening-time'] = 24 * day + dt.hour + dt.minute / 60
            linkers['link' + str(c)]['ending_extra_days'] = reallinkers[link]['ending_extra_days']
            extradays = 0 if linkers['link' + str(c)]['ending_extra_days'] == '' else linkers['link' + str(c)]['ending_extra_days']
            linkers['link' + str(c)]['ending-time'] = 24 * (day + extradays) + at.hour + at.minute / 60
            if linkers['link' + str(c)]['opening-time'] > linkers['link' + str(c)]['ending-time']:
                linkers['link' + str(c)]['ending-time'] += 24
            linkers['link' + str(c)]['color'] = reallinkers[link]['color']
            linkers['link' + str(c)]['forced'] = reallinkers[link]['forced']
            linkers['link' + str(c)]['str_opening-time'] = reallinkers[link]['str_opening-time']
            linkers['link' + str(c)]['str_ending-time'] = reallinkers[link]['str_ending-time']
            linkers['link' + str(c)]['capacity'] = reallinkers[link]['week'][day_reference]
            linkers['link' + str(c)]['week'] = tuple(reallinkers[link]['week'])
            linkers['link' + str(c)]['bans'] = tuple(reallinkers[link]['bans'])


    auxs = copy.deepcopy(iniservices) # TODO estoy sumand dicts simplemente, por qué hacerlo así?
    for service in services:
        auxs[service] = copy.deepcopy(services[service])

    auxs2 = copy.deepcopy(iniservices) # TODO estoy sumand dicts simplemente, por qué hacerlo así?
    for service in expanded_services:
        auxs2[service] = copy.deepcopy(expanded_services[service])


    # Reordering services according to departure time:
    auxs = sorted(auxs.items(), key=lambda x: x[1]['departure-time'])
    auxs2 = sorted(auxs2.items(), key=lambda x: x[1]['departure-time'])
    auxs3 = sorted(linkers.items(), key=lambda x: x[1]['opening-time'])

    # Hashing dicts # TODO en este matrix builder no se necesita el frozendict. Pero si te lo cargas, ojo porque aquí es donde estas fusionando los services con los iniservices
    services = frozendict({'service' + str(i + 1): frozendict(auxs[i][1]) for i in range(len(auxs))})
    expanded_services = frozendict({'service' + str(i + 1): frozendict(auxs2[i][1]) for i in range(len(auxs2))})
    linkers = {'link' + str(i + 1): auxs3[i][1] for i in range(len(auxs3))}
    depotnodes = frozendict(depotnodes)

    # Other data
    numservices = len(services)

    error = False
    matrix = {}
    matrix['km_service'] = build_km_service(services)
    matrix['departure_time'] = build_departure_time(services)
    matrix['duration_service'] = build_duration_service(services)
    matrix['arrival_time'] = build_arrival_time(services)
    matrix['depot'] = build_depot(services, depotnodes)
    # matrix['condition'], matrix['stringed_condition'] = build_condition(numservices, services)
    matrix['table_conversion'] = build_table_conversion(services)
    matrix['dict_color'] = build_color_list(services)
    a, b, c, d, e = build_valid_predecessors(numtrains, numservices, services, expanded_services, linkers)
    if a == False:
        error = {'title': "", 'content': ""}
        error['title'] = lang.hh3
        day = int(c // 24)
        error['content'] = lang.hh4 + str(b) + lang.hh5 + str(day) + ' (' + str(days[week[day]]) + lang.hh6
        return None, error
    else:
        matrix['predecessors'], matrix['condition'], matrix['stringed_condition'], matrix['uses_linkers'], matrix['valid_linkers'] = a, b, c, d, e

    matrix['origins'] = build_services_origins(services)
    matrix['destinies'] = build_services_destinies(services)
    matrix['stringed_departures'] = build_stringed_departures(services)
    matrix['stringed_arrivals'] = build_stringed_arrivals(services)
    matrix['bans'] = build_arrayed_bans(services)
    matrix['trimmed_km_limit'] = build_trimmed_km_limit(km_limit, transfers)
    matrix['linkers_km'], matrix['linkers_capacity'] = build_linkers_numericals(linkers)
    matrix['info_linkers'] = build_info_linkers(linkers)
    matrix['total_capacity'], matrix['capacities_management'] = build_capacities(numservices, services, depotnodes, matrix['predecessors'], transfers, _week, next_m_duration, initial_occupation, matrix['uses_linkers'], matrix['valid_linkers'], matrix['info_linkers'])

    return (matrix, numservices, weekday), error
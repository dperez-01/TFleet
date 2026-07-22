'''
 -*- coding: utf-8 -*-
-------------------------------------------------------------------------------
 Name:        NO_HEURISTIC_model.py

 Author:      Diego Pérez

 Created:     28/05/2024
 Copyright:   (c) perez 2024
-------------------------------------------------------------------------------
'''
import sys
from abc import abstractmethod
from tkinter import END, messagebox


import settings

if settings.LANGUAGE == 'English':
    import language.EN as lang
elif settings.LANGUAGE == 'Castellano':
    import language.ES as lang

import traceback
import time
import HEURISTIC_matrix_builder as builder

import numpy as np
from datetime import datetime
from pathos.multiprocessing import ProcessPool, cpu_count
from numba import njit, uint8, uint16, float64, int16
# from numpy import uint8, uint16, float64, int16
import psutil
from copy import deepcopy

from gc import collect as gccollect


class TrackedObject:
    def __init__(self, initial_value=False):
        self._value = initial_value
        self._callbacks = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        old_value = self._value
        self._value = new_value
        self._notify_observers(old_value, new_value)

    def _notify_observers(self, old_value, new_value):
        self._callbacks(old_value, new_value)

    def register_callback(self, callback):
        self._callbacks = callback

class deme_class(object):
    def __init__(self, numtrains, numservices, predecessors, condition, kmlimit, kmservice, depots, departure_time, next_m_duration, total_capacity, capacities_management, uses_linkers, valid_linkers, kmlinker, total_linkers_capacity, avoidance_margin, critical_margin):
        self.numtrains = numtrains
        self.numservices = numservices
        self.predecessors = predecessors
        self.condition = condition
        self.kmlimit = kmlimit
        self.kmservice = kmservice
        self.depots = depots
        self.departure_time = departure_time
        self.next_m_duration = next_m_duration
        self.total_capacity = total_capacity
        self.capacities_management = capacities_management
        self.avoidance_margin = avoidance_margin
        self.critical_margin = critical_margin
        self.uses_linkers = uses_linkers
        self.valid_linkers = valid_linkers
        self.kmlinker = kmlinker
        self.total_linkers_capacity = total_linkers_capacity

        self.cores_setup()
        self.pool = ProcessPool(nodes=self.avl_cores, maxtasksperchild=4) # TODO probar impacto de este parametro
        self.pool.daemon = True

    def cores_setup(self):
        '''
        A function used when initializing deme_class, to determine the number of threads that will be used on how the population will be distributed among those.
        '''
        self.avl_cores = cpu_count()
        self.avl_cores -= 2
        # self.avl_cores = 1
        if self.avl_cores <= 0:
            sys.exit()

    def _get_sizepop_per_core(self, sizepop):
        base = int(sizepop / self.avl_cores)
        self.sizepop_per_core = [base for _ in range(self.avl_cores)]
        over = sizepop % self.avl_cores
        if over:
            i = -1
            while over > 0:
                i += 1
                if i == len(self.sizepop_per_core):
                    i = 0

                self.sizepop_per_core[i] += 1
                over -= 1

    # Generates a pop of the size of sizepop, among different cores
    def gen_pop(self, sizepop):
        self._get_sizepop_per_core(sizepop)
        self.pool.restart()
        results = self.pool.map(self.population_engine_servicedistributor, self.sizepop_per_core, [self.numtrains for _ in range(self.avl_cores)], [self.numservices for _ in range(self.avl_cores)], [self.predecessors for _ in range(self.avl_cores)], [self.condition for _ in range(self.avl_cores)], [self.kmlimit for _ in range(self.avl_cores)], [self.kmservice for _ in range(self.avl_cores)], [self.depots for _ in range(self.avl_cores)], [self.next_m_duration for _ in range(self.avl_cores)], [self.total_capacity for _ in range(self.avl_cores)], [self.capacities_management for _ in range(self.avl_cores)], [self.uses_linkers for _ in range(self.avl_cores)], [self.valid_linkers for _ in range(self.avl_cores)], [self.kmlinker for _ in range(self.avl_cores)], [self.total_linkers_capacity for _ in range(self.avl_cores)], [self.avoidance_margin for _ in range(self.avl_cores)], [self.critical_margin for _ in range(self.avl_cores)])
        self.pool.close()
        self.pool.join()

        best_values = []
        best_schedules = []
        best_maintenances = []
        best_linkers = []
        infeasibleAs = []
        infeasibleBs = []
        infeasibleCs = []
        infeasibleA_cols = np.empty(0, dtype=np.int16)

        for processors_results in results:
            best_values.append(processors_results[0])
            best_schedules.append(processors_results[1])
            best_maintenances.append(processors_results[2])
            best_linkers.append(processors_results[3])
            infeasibleAs.append(processors_results[4])
            infeasibleBs.append(processors_results[5])
            infeasibleCs.append(processors_results[6])
            infeasibleA_cols = np.concatenate([infeasibleA_cols, processors_results[7]], dtype=np.int16)

        idx = best_values.index(max(best_values))
        return best_values[idx], best_schedules[idx], best_maintenances[idx], best_linkers[idx], sum(infeasibleAs), sum(infeasibleBs), sum(infeasibleCs), infeasibleA_cols

    @staticmethod
    @njit
    def population_engine_servicedistributor(minipop, numtrains, numservices, predecessors, condition, km_limit, kmservice, depots, next_m_duration, total_capacity, capacities_management, uses_linkers, valid_linkers, kmlinker, total_linkers_capacity, avoidance_margin, critical_margin):
        fleet = np.arange(numtrains, dtype=uint8)

        best_value = -np.inf
        best_schedule = np.zeros((numtrains, numservices), dtype=uint8)
        best_maintenance = np.zeros(numtrains, dtype=float64)
        best_linkers = np.ones((numtrains, numservices), dtype=int16) * -1
        infeasibleA_cols = np.ones(minipop, dtype=int16) * -1
        infeasibleA = 0
        infeasibleB = 0
        infeasibleC = 0
        for each in range(minipop):
            conditions_done = np.zeros(numservices, dtype=uint8)
            last_done_service = np.arange(numtrains, dtype=uint16) # Handles forced services and latest service at any moment
            habitant = np.eye(numtrains, numservices, dtype=uint8)
            sol_linkers = np.ones((numtrains, numservices), dtype=int16) * -1
            usable = np.zeros((numtrains, numservices), dtype=uint8)
            trains_skipping_maintenance = np.zeros(numtrains, dtype=uint8)
            capacity = total_capacity.copy()
            linkers_capacity = total_linkers_capacity.copy()
            real_kmservice = kmservice.copy()
            killed = False

            for rowcol in range(numtrains): # TODO no crear generadores sin parar. Probar que pasa si pongo el generador ya creado
                next_col = rowcol  # Using while, not if, in case a conditonal chain exists
                while condition[next_col]:
                    habitant[rowcol, condition[next_col]] = 1  # Automatically assigns the condition service too
                    last_done_service[rowcol] = condition[next_col]  # Prevents train from being assigned before the conditioned service is reached through col for loop
                    conditions_done[condition[next_col]] = 1  # Prevents the conditioned successor from being reassigned later
                    next_col = condition[next_col]

            for col in range(numtrains, numservices):
                if conditions_done[col]:
                    continue

                row_pool = np.zeros(numtrains, dtype=uint8)
                valids = np.nonzero(predecessors[:, col])[0]
                for row in fleet:
                    if last_done_service[row] in valids:
                        row_pool[row] = 1

                validity_confirmed = False
                while not validity_confirmed:
                    valid_rows = np.nonzero(row_pool)[0]
                    validity_confirmed = True
                    if valid_rows.size:
                        # Assign schedule
                        weights = np.ones(numtrains, dtype=float64) / valid_rows.size
                        chosen_row = valid_rows[np.searchsorted(np.cumsum(weights), int(10000 * np.random.random()) / 10000, side="right")]  # Opcion b: float(str(np.random.random())[:6]) # TODO Is the 10000 trick needed? why am I doing this? cant remember
                        # print('a', last_done_service[chosen_row], col, uses_linkers[last_done_service[chosen_row], col])
                        if uses_linkers[last_done_service[chosen_row], col]:
                            for linker in valid_linkers[last_done_service[chosen_row], col]: # TODO valid_linkers is just a suqared matrix with a flat list containing indices that relate to a specific linker. -1 for null positions
                                if linker > -1:
                                    if linkers_capacity[linker] > 0:
                                        # print('d', col)
                                        sol_linkers[chosen_row, last_done_service[chosen_row]] = linker
                                        real_kmservice[col] += kmlinker[linker]
                                        break
                            else:
                                validity_confirmed = False
                                row_pool[chosen_row] = 0
                                continue

                        habitant[chosen_row, col] = 1
                        last_done_service[chosen_row] = col

                        next_col = col  # Using while, not if, in case a conditonal chain exists
                        while condition[next_col]:
                            habitant[chosen_row, condition[next_col]] = 1  # Automatically assigns the condition service too
                            last_done_service[chosen_row] = condition[next_col]  # Prevents train from being assigned before the conditioned service is reached through col for loop
                            conditions_done[condition[next_col]] = 1  # Prevents the conditioned successor from being reassigned later
                            next_col = condition[next_col]

                    else:
                        infeasibleA_cols[each] = col
                        killed = True
                        break


            # Fast check - Is already infeasible? (code: reason A)
            if killed:
                sol_value = -np.inf # noqa
                infeasibleA += 1
                continue

            # --- FO evaluation starts ------------------------
            fleet_done_kms = habitant * kmservice
            fleet_done_kms_real = habitant * real_kmservice
            fleet_maintenance_time = np.zeros(numtrains, dtype=float64)
            kms_before_maintenance = np.zeros(numtrains, dtype=float64)
            cumulative_kms = np.zeros((numtrains, numservices), dtype=float64)
            cumulative_kms_real = np.zeros((numtrains, numservices), dtype=float64)
            for i in range(numtrains):
                cumulative_kms[i] = fleet_done_kms[i].cumsum()
                cumulative_kms_real[i] = fleet_done_kms_real[i].cumsum()
            cumulative_depots = cumulative_kms_real * depots * habitant
            reason = 0

            # Defines usable depots
            for train in range(numtrains):
                # # # ---- Start: Insert maintenance block
                # # # ----

                if fleet_done_kms_real[train].sum() <= km_limit[train] - avoidance_margin:
                    # print(each, 'Train', train, 'Done')
                    fleet_maintenance_time[train] = 0  # -> means no maintenance (but not infeasible) / Yes, line is not needed but is left as indication
                    kms_before_maintenance[train] = fleet_done_kms[train].sum()
                    trains_skipping_maintenance[train] = 1
                    continue

                else:  # From now on will always TRY to do maintenance
                    usable[train] = np.where((cumulative_depots[train] < km_limit[train]) & (cumulative_depots[train] > 0), 1, 0)
                    if usable[train].sum() == 0:
                        if fleet_done_kms_real[train].sum() <= km_limit[train] - critical_margin:
                            # print(each, 'Train', train, 'Done')
                            fleet_maintenance_time[train] = 0  # -> means no maintenance (but not infeasible) / Yes, line is not needed but is left as indication
                            kms_before_maintenance[train] = fleet_done_kms[train].sum()
                            trains_skipping_maintenance[train] = 1
                            continue
                        else:
                            reason = 2
                            killed = True
                            break  # # # ---- End: Insert maintenance block  # # # ----

            # Fast check - Is already infeasible? (code: reason 2)
            if killed:
                sol_value = -np.inf # noqa
                infeasibleC += 1 # No indices (Either bad km, or very few service depots and cannot be assigned to trains)
                continue

            # After this point, any train that never reaches a depot has checked if it was necessary to do maintenance or not
            # Assign maintenance slots. Consider available time and depot capacity
            sums = usable.sum(axis=1)
            valids = sums.nonzero()[0]
            sorted_indices = valids[np.argsort(sums[valids], kind='quicksort')]
            for train in sorted_indices:
                if trains_skipping_maintenance[train]:
                    continue

                maintenance_applied = False
                indices = usable[train].nonzero()[0]

                # Maybe the depot is the last service, so position "selected_depot + 1:" (when defining "successors") would be greater than habitant's len (error), and successors would be an empty array # TODO nota, al parecer por como funciona numpy y el slicing no da ERROR, por lo que se podría ver si se elimina el caso particular ya que asumiría 0 sucesores correctamente
                if indices[-1] == numservices - 1:
                    for pos, available_time, start_time in capacities_management[indices[-1], indices[-1]]:
                        # if pos > -1:
                        #     print(each, 'Train', train, 'Pos', pos, 'Capacity', capacity[int(pos)])
                        if pos > -1 and capacity[int(pos)] > 0:
                            fleet_maintenance_time[train] = start_time
                            kms_before_maintenance[train] = cumulative_kms[train, -1]
                            capacity[int(pos)] -= 1
                            maintenance_applied = True
                            break
                        elif pos == -1: # -1s are always the last ones, it is known that nothing worth lies ahead
                            break

                if maintenance_applied:
                    continue

                idx = len(indices) - 1
                if indices[-1] == numservices - 1: idx -= 1 # Prevents strange case where the last service is a depot, has capacity 0 (as teh previous exceptional block didn't result in maintenance being applied), and a train initially intended to do maintenance there # TODO potential skip if the previous exceptional block is skipped
                while idx >= 0:
                    selected_depot = indices[idx]
                    successors = habitant[train, selected_depot + 1:]
                    # Maybe there are only zeroes after the depot, so else should be triggered
                    if successors.sum() > 0:
                        next_service = np.argmax(successors) + selected_depot + 1  # It is another index (immediate next service) # TODO Although getting the first of the ones as we want with this version, we should find a method to specifically say that we want the first one
                        for pos, available_time, start_time in capacities_management[selected_depot, next_service]:
                            # if uses_linkers[selected_depot, next_service]:
                            #     linker = sol_linkers[selected_depot, next_service]
                            #     available_time -= linker_duration[linker]
                            # if pos > -1:
                            #     print(each, 'Train', train, 'Pos', pos, 'Capacity', capacity[int(pos)], available_time)
                            if pos > -1 and capacity[int(pos)] > 0 and next_m_duration[train] <= available_time:
                                fleet_maintenance_time[train] = start_time
                                kms_before_maintenance[train] = cumulative_kms[train, selected_depot]
                                capacity[int(pos)] -= 1
                                maintenance_applied = True
                                break
                            elif pos == -1: # -1s are always the last ones, it is known that nothing worth lies ahead
                                break
                        if maintenance_applied:
                            break

                    else:
                        for pos, available_time, start_time in capacities_management[selected_depot, selected_depot]:
                            # if pos > -1:
                            #     print(each, 'Train', train, 'Pos', pos, 'Capacity', capacity[int(pos)])
                            if pos > -1 and capacity[int(pos)] > 0:
                                fleet_maintenance_time[train] = start_time
                                kms_before_maintenance[train] = cumulative_kms[train, selected_depot]
                                capacity[int(pos)] -= 1
                                maintenance_applied = True
                                break
                            elif pos == -1: # -1s are always the last ones, it is known that nothing worth lies ahead
                                break
                        if maintenance_applied:
                            break

                    idx -= 1

                if maintenance_applied:
                    continue

                #  However, you wont do that here, as you still need some numbers for the OF. Consider doing it after the complete execution of the algorithm.
                # If reached here, maintenance is not done. Was it necessary?
                if fleet_done_kms_real[train].sum() <= km_limit[train] - critical_margin:
                    fleet_maintenance_time[train] = 0  # -> means no maintenance (but not infeasible) / Yes, line is not needed but is left as indication
                    kms_before_maintenance[train] = fleet_done_kms[train].sum()
                    continue

                else:  # Indices exist (therefore not bad km) but not possible to fit maintenance (too long)
                    reason = 1
                    break

            if reason == 1:  # Indices exist but not possible to fit maintenance (lack of valid slots due to length or capacity)
                sol_value = -np.inf
                infeasibleB += 1

            elif reason == 2:  # No indices (Either bad km, or very few service depots and cannot be assigned to trains)
                sol_value = -np.inf
                infeasibleC += 1

            else:
                sol_value = kms_before_maintenance.sum()

            # --- FO evaluation finished  # --------------------------

            if sol_value > best_value:
                # print(fleet_done_kms_real[0].sum(), km_limit[0], cumulative_depots)
                best_value = sol_value
                best_schedule = habitant.copy()
                best_maintenance = fleet_maintenance_time.copy()  # noqa
                best_linkers = sol_linkers.copy()

        return best_value, best_schedule, best_maintenance, best_linkers, infeasibleA, infeasibleB, infeasibleC, infeasibleA_cols


class heuristic_handler(object):
    @abstractmethod
    def __init__(self, windowlog, textlog, km_limit, next_m_duration, numtrains, numservices, table_conversion, km_service, departure_time, predecessors, condition, depot, total_capacity, capacities_management, uses_linkers, valid_linkers, kmlinker, total_linkers_capacity, avoidance_margin, critical_margin):
        self.windowlog = windowlog
        self.textlog = textlog
        self.nuke_order = False
        self.finishtracker = TrackedObject()
        self.stop_order = False
        self.departure_time = departure_time
        self.table_conversion = table_conversion

        # Prepare population handler
        self.population_handler = deme_class(numtrains, numservices, np.array(predecessors, dtype=np.uint8), np.array(condition, dtype=np.uint16), np.array(km_limit, dtype=np.float64), np.array(km_service, dtype=np.float64), np.array(depot, dtype=np.uint8), np.array(departure_time, dtype=np.float64), np.array(next_m_duration, dtype=np.float64), np.array(total_capacity, dtype=np.uint8), np.array(capacities_management, dtype=np.float64), np.array(uses_linkers, dtype=np.uint8), np.array(valid_linkers, dtype=np.int16), np.array(kmlinker, dtype=np.float64), np.array(total_linkers_capacity, dtype=np.uint8), avoidance_margin, critical_margin)

        self.accumulated_pop = 0
        self.accumulated_complete_sols = 0
        self.infeasibleA = 0
        self.infeasibleB = 0
        self.infeasibleC = 0
        self.infeasibleA_cols = np.empty(0, dtype=np.int16)

        # Defining logger color option settings
        np.set_printoptions(precision=9, floatmode='fixed', linewidth=200)
        self.textlog.tag_configure('orange', foreground='#fc8803', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('darkorange', foreground='#c76c04', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('pink', foreground='#ff00a6', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('green', foreground='#2bff00', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('darkgreen', foreground='#2da814', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('blue', foreground='#14e0ff', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('red', foreground='#f50206', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('darkred', foreground='#8c0104', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('yellow', foreground='#fcd703', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('purple', foreground='#e600ff', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('aquamarine', foreground='#5cf9ac', font=('TkFixedFont', 11, 'bold'))

    def _loggingevent_Welcome(self):
        self.textlog.configure(state="normal")

        self.textlog.insert(END, lang.hh7)
        self.textlog.insert(END, lang.hh8)
        self.textlog.insert(END, str(self.population_handler.avl_cores), 'blue')
        self.textlog.insert(END, lang.hh9)
        self.textlog.insert(END, str(cpu_count()), 'blue')
        self.textlog.insert(END, lang.hh10)
        self.textlog.insert(END, lang.hh11)
        self.textlog.insert(END, str(round(psutil.virtual_memory()[0] / (1024 ** 3), 2)), 'purple')
        self.textlog.insert(END, ' GB\n\n\n')

        self.textlog.configure(state="disabled")
        self.textlog.see(END)
        self.windowlog.update()

    def _loggingevent_StartingIteration(self):
        if self.nuke_order:
            return

        self.textlog.configure(state="normal")

        self.textlog.insert(END, lang.hh12 + str(self.step) + '/')
        self.textlog.insert(END, str(settings.HEURISTIC_STEPS), 'yellow')
        self.textlog.insert(END, ' \U0001F684\n\n')
        self.textlog.configure(state="disabled")
        self.textlog.see(END)
        self.windowlog.update()

    def _loggingevent_StepFinished(self, failuresA, failuresB, failuresC, elapsed_time, new_bestie=False):
        if self.nuke_order:
            return

        self.textlog.configure(state="normal")

        self.textlog.insert(END, lang.hh13)
        self.textlog.insert(END, str(elapsed_time), 'blue')
        self.textlog.insert(END, lang.hh14)
        if failuresA + failuresB + failuresC < self.checkpoint_frequency:
            self.textlog.insert(END, lang.hh15)
            self.textlog.insert(END, str(self.checkpoint_frequency), 'darkgreen')
            self.textlog.insert(END, lang.hh16)
            self.textlog.insert(END, str(round(100 * (failuresA + failuresB + failuresC) / self.checkpoint_frequency, 2)) + '%', 'darkorange')
            self.textlog.insert(END, lang.hh17)

        else:
            self.textlog.insert(END, lang.hh15)
            self.textlog.insert(END, str(self.checkpoint_frequency), 'darkred')
            self.textlog.insert(END, lang.hh18)
            self.textlog.insert(END, '100%', 'darkred')

        if new_bestie:
            self._loggingevent_NewBestie()

        self._loggingevent_EvaluationFinished()

        self.textlog.configure(state="disabled")
        self.textlog.see(END)
        self.windowlog.update()

    def _loggingevent_NewBestie(self):
        if self.nuke_order:
            return

        self.textlog.configure(state="normal")

        self.textlog.insert(END, '\nA new')
        self.textlog.insert(END, lang.hh19, 'aquamarine')
        self.textlog.insert(END, lang.hh20)
        self.textlog.insert(END, str(self.best_value) + '\n', 'aquamarine')

        self.textlog.configure(state="disabled")
        self.textlog.see(END)
        self.windowlog.update()

    def _loggingevent_EvaluationFinished(self):
        if self.nuke_order:
            return

        self.textlog.configure(state="normal")

        self.textlog.insert(END, lang.hh21)
        self.textlog.insert(END, str(self.accumulated_pop), 'yellow')
        self.textlog.insert(END, lang.hh22)

        if self.infeasibleA + self.infeasibleB + self.infeasibleC > 0:
            self.textlog.insert(END, str(self.accumulated_pop - self.accumulated_complete_sols), 'pink')
            self.textlog.insert(END, ' (')

            self.textlog.insert(END, str(round(100 * (self.accumulated_pop - self.accumulated_complete_sols) / self.accumulated_pop, 2)) + '%', 'pink')

            self.textlog.insert(END, lang.hh23)
            self.textlog.insert(END, lang.hh24, 'pink')
            self.textlog.insert(END, lang.hh25)

            if self.infeasibleA:
                self.textlog.insert(END, str(self.infeasibleB), 'purple')
                self.textlog.insert(END, lang.hh26)

                self.textlog.insert(END, str(round(100 * self.infeasibleA / self.accumulated_pop, 2)) + '%', 'purple')

                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh28, 'purple')
                self.textlog.insert(END, lang.hh29)

                if self.infeasibleA / self.accumulated_pop > 0.95:
                    all_infeasibleA = self.infeasibleA_cols[self.infeasibleA_cols > 0]
                    vals, counts = np.unique(all_infeasibleA, return_counts=True)
                    mask = counts >= (0.1 * all_infeasibleA.size)
                    valid_infeasibleA = dict(zip(vals[mask], counts[mask]))

                    self.textlog.insert(END, lang.hh30)
                    for service, count in valid_infeasibleA.items():
                        self.textlog.insert(END, lang.hh31)
                        self.textlog.insert(END, str(self.table_conversion[int(service)]), 'purple')
                        self.textlog.insert(END, lang.hh32)
                        self.textlog.insert(END, str(int(1 + (self.departure_time[int(service)] // 24))), 'purple')
                        self.textlog.insert(END, lang.hh33 + str(count) + lang.hh34)
                    self.textlog.insert(END, lang.hh35)

            if self.infeasibleB:
                self.textlog.insert(END, str(self.infeasibleB), 'orange')
                self.textlog.insert(END, lang.hh26)

                self.textlog.insert(END, str(round(100 * self.infeasibleB / self.accumulated_pop, 2)) + '%', 'orange')

                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh36, 'orange')
                self.textlog.insert(END, lang.hh37)

            if self.infeasibleC:
                self.textlog.insert(END, str(self.infeasibleC), 'red')
                self.textlog.insert(END, lang.hh26)

                self.textlog.insert(END, str(round(100 * self.infeasibleC / self.accumulated_pop, 2)) + '%', 'red')

                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh38, 'red')
                self.textlog.insert(END, lang.hh39)

            self.textlog.insert(END, str(self.accumulated_complete_sols), 'green')
            self.textlog.insert(END, ' (')
            self.textlog.insert(END, str(round(100 * self.accumulated_complete_sols / self.accumulated_pop, 2)) + '%', 'green')
            self.textlog.insert(END, lang.hh40)

        else:
            self.textlog.insert(END, str(self.accumulated_pop), 'green')
            self.textlog.insert(END, ' (')
            self.textlog.insert(END, '100.0%', 'green')
            self.textlog.insert(END, lang.hh41)

        self.textlog.insert(END, lang.hh42)
        self.textlog.insert(END, lang.hh43, 'aquamarine')
        self.textlog.insert(END, lang.hh44)
        self.textlog.insert(END, str(self.best_value), 'aquamarine')
        self.textlog.insert(END, lang.hh45)
        self.textlog.insert(END, str(self.accumulated_complete_sols), 'green')
        self.textlog.insert(END, ' (')

        self.textlog.insert(END, str(round(100 * self.accumulated_complete_sols / self.accumulated_pop, 2)) + '%', 'green')

        self.textlog.insert(END, lang.hh46)

        self.textlog.configure(state="disabled")
        self.textlog.see(END)
        self.windowlog.update()

    def _loggingevent_RunFinished(self):
        if self.nuke_order:
            return

        self.textlog.configure(state="normal")

        self.textlog.insert(END, lang.hh47)
        self.textlog.insert(END, str(round(self.accumulated_time, 2)), 'blue')
        self.textlog.insert(END, lang.hh48)

        self.textlog.insert(END, str(self.accumulated_pop), 'yellow')
        self.textlog.insert(END, lang.hh49)

        if self.infeasibleA + self.infeasibleB + self.infeasibleC > 0:
            self.textlog.insert(END, str(self.accumulated_pop - self.accumulated_complete_sols), 'pink')
            self.textlog.insert(END, ' (')

            self.textlog.insert(END, str(round(100 * (self.accumulated_pop - self.accumulated_complete_sols) / self.accumulated_pop, 2)) + '%', 'pink')

            self.textlog.insert(END, lang.hh50)
            self.textlog.insert(END, lang.hh51, 'pink')
            self.textlog.insert(END, ':\n')

            if self.infeasibleA:
                self.textlog.insert(END, str(self.infeasibleB), 'purple')
                self.textlog.insert(END, lang.hh26)

                self.textlog.insert(END, str(round(100 * self.infeasibleA / self.accumulated_pop, 2)) + '%', 'purple')

                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh28, 'purple')
                self.textlog.insert(END, lang.hh29)

            if self.infeasibleB:
                self.textlog.insert(END, str(self.infeasibleB), 'orange')
                self.textlog.insert(END, lang.hh26)

                self.textlog.insert(END, str(round(100 * self.infeasibleB / self.accumulated_pop, 2)) + '%', 'orange')

                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh36, 'orange')
                self.textlog.insert(END, lang.hh37)

            if self.infeasibleC:
                self.textlog.insert(END, str(self.infeasibleC), 'red')
                self.textlog.insert(END, lang.hh26)

                self.textlog.insert(END, str(round(100 * self.infeasibleC / self.accumulated_pop, 2)) + '%', 'red')

                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh38, 'red')
                self.textlog.insert(END, lang.hh39)

            self.textlog.insert(END, str(self.accumulated_complete_sols), 'green')
            self.textlog.insert(END, ' (')
            self.textlog.insert(END, str(round(100 * self.accumulated_complete_sols / self.accumulated_pop, 2)) + '%', 'green')
            self.textlog.insert(END, lang.hh52)

        else:
            self.textlog.insert(END, str(self.accumulated_pop), 'green')
            self.textlog.insert(END, ' (')
            self.textlog.insert(END, '100%', 'green')
            self.textlog.insert(END, lang.hh52)

        self.textlog.insert(END, lang.hh53, 'aquamarine')
        self.textlog.insert(END, lang.hh44)
        self.textlog.insert(END, str(self.best_value) + '\n', 'aquamarine')
        self.textlog.insert(END, lang.hh54)
        self.textlog.insert(END, lang.hh55, 'blue')
        self.textlog.insert(END, lang.hh56)
        self.textlog.insert(END, lang.hh57, 'blue')
        self.textlog.insert(END, lang.hh58)

        self.textlog.configure(state="disabled")
        self.textlog.see(END)
        self.windowlog.update()

    def optimise(self, steps, checkpoint_frequency=300000, first_time=True):
        if first_time:
            self.accumulated_time = 0
            self.step = 0
            self.best_schedule = None
            self.best_maintenance = None
            self.best_linkers = None
            self.best_value = -np.inf
            self._loggingevent_Welcome()

        self.finishtracker.value = False
        self.stop_order = False

        try:
            self.run(steps, checkpoint_frequency)
            while self.best_value == -np.inf and settings.HEURISTIC_SOLVE_ABOVE_ALL:
                if self.nuke_order or self.stop_order:
                    break
                self.run(1, checkpoint_frequency)

            self._loggingevent_RunFinished()

        except:
            error = traceback.format_exc()
            print(error)
            messagebox.showerror(lang.hh59, lang.hh60 + error)

        if not self.nuke_order:
            self.finishtracker.value = True

        else:
            self.population_handler.pool.terminate()
            del self.best_value, self.best_schedule, self.best_maintenance, self.best_linkers

            gccollect()

    def run(self, steps, checkpoint_frequency=300000):
        '''
        This function will create and get the best solution from a population.
        The current best is not resetted with this function.
        '''
        self.checkpoint_frequency = checkpoint_frequency

        for i in range(steps):
            start_time = time.time()
            self.step += 1
            self._loggingevent_StartingIteration()

            best_value, best_schedule, best_maintenance, best_linkers, infeasibleA, infeasibleB, infeasibleC, infeasibleA_cols = self.population_handler.gen_pop(checkpoint_frequency)

            self.accumulated_pop += checkpoint_frequency
            timespaced_pop = checkpoint_frequency - infeasibleA
            self.infeasibleA += infeasibleA
            self.infeasibleB += infeasibleB
            self.infeasibleC += infeasibleC
            self.infeasibleA_cols = np.concatenate([self.infeasibleA_cols, infeasibleA_cols], dtype=np.int16)
            self.accumulated_complete_sols += timespaced_pop - infeasibleB - infeasibleC

            new_bestie = False
            if best_value > self.best_value:
                self.best_value = best_value
                self.best_schedule = best_schedule.copy()
                self.best_maintenance = best_maintenance.copy()
                self.best_linkers = best_linkers.copy()
                new_bestie = True

            elapsed_time = round(time.time() - start_time, 2)
            self.accumulated_time += elapsed_time
            self._loggingevent_StepFinished(failuresA=infeasibleA, failuresB=infeasibleB, failuresC=infeasibleC, elapsed_time=elapsed_time, new_bestie=new_bestie)

            if self.stop_order or self.nuke_order:
                break

class multienvironment_heuristic_handler(heuristic_handler):
    def __init__(self, cuts, days_per_cut, starting_weekday, windowlog, textlog, depotnodes, realservices, iniservices, km_limit, next_m_duration, next_m_name, numtrains, transfers, reallinkers, avoidance_margin, critical_margin):
        self.cuts = cuts
        self.days_per_cut = days_per_cut
        self.current_cuts = 0
        self.accumulated_cut_time = 0

        # Similar init to baseclass
        self.windowlog = windowlog
        self.textlog = textlog
        self.nuke_order = False
        self.finishtracker = TrackedObject()
        self.stop_order = False

        # Elements that need to be created here, in spite of the other heuristic model
        self.accumulated_time = 0
        self.best_schedule = None
        self.best_maintenance = None
        self.best_value = -np.inf

        # Defining logger color option settings
        # np.set_printoptions(precision=9, floatmode='fixed', linewidth=200)
        self.textlog.tag_configure('orange', foreground='#fc8803', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('darkorange', foreground='#c76c04', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('pink', foreground='#ff00a6', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('green', foreground='#2bff00', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('darkgreen', foreground='#2da814', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('blue', foreground='#14e0ff', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('red', foreground='#f50206', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('darkred', foreground='#8c0104', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('yellow', foreground='#fcd703', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('purple', foreground='#e600ff', font=('TkFixedFont', 11, 'bold'))
        self.textlog.tag_configure('aquamarine', foreground='#5cf9ac', font=('TkFixedFont', 11, 'bold'))

        # Constant elements across runs
        self.numtrains = numtrains
        self.avoidance_margin = avoidance_margin
        self.critical_margin = critical_margin
        self.depotnodes = deepcopy(depotnodes)
        self.services = deepcopy(realservices)
        self.iniservices = deepcopy(iniservices)
        self.transfers = deepcopy(transfers)
        self.linkers = deepcopy(reallinkers)


        # Solution storing
        self.store_schedule = np.empty((self.numtrains, 0), dtype=np.uint8)
        self.store_maintenance = np.empty((self.numtrains, 0), dtype=np.float64)
        self.store_km_limit = np.empty((self.numtrains, 0)) # TODO definirle algun dtype entero
        self.store_next_m_duration = np.empty((self.numtrains, 0), dtype=np.float64)
        self.store_next_m_name = np.empty((self.numtrains, 0))
        self.store_linkers_solution = np.empty((self.numtrains, 0), dtype=np.int16)

        # Storing variables, kept along runs
        self.store_departure_time = np.empty(0, dtype=np.float64)
        self.store_duration_service = np.empty(0, dtype=np.float64)
        self.store_arrival_time = np.empty(0, dtype=np.float64)
        self.store_table_conversion = np.empty(0)
        self.store_km_service = np.empty(0, dtype=object)
        self.store_origins = np.empty(0)
        self.store_destinies = np.empty(0)
        self.store_conditioned_successor = np.empty(0)
        self.store_banned_successors = []
        self.store_str_departures = np.empty(0)
        self.store_str_arrivals = np.empty(0)
        self.store_str_condition = np.empty(0)
        self.store_dict_color = np.empty(0)
        self.store_info_linkers = np.empty(0, dtype=object)

        # Elements that can be autoupdated
        self.last_services = []
        self.km_limit = np.array(km_limit)
        self.next_m_duration = np.array(next_m_duration)
        self.next_m_name = np.array(next_m_name)
        self.starting_weekday = starting_weekday

    def _loggingevent_CutFinished(self):
        self.textlog.configure(state="normal")

        self.textlog.insert(END, lang.hh61)
        self.textlog.insert(END, str(self.current_cuts), 'blue')
        self.textlog.insert(END, "/")
        self.textlog.insert(END, str(self.cuts), 'yellow')
        self.textlog.insert(END, ' \U0001F69D\n\n')


        self.textlog.insert(END, lang.hh62)
        self.textlog.insert(END, str(round(self.accumulated_time, 2)), 'blue')
        self.textlog.insert(END, lang.hh48)

        self.textlog.insert(END, str(self.accumulated_pop), 'yellow')
        self.textlog.insert(END, lang.hh49)

        if self.infeasibleA + self.infeasibleB + self.infeasibleC > 0:
            self.textlog.insert(END, str(self.accumulated_pop - self.accumulated_complete_sols), 'pink')
            self.textlog.insert(END, ' (')
            if self.accumulated_pop:
                self.textlog.insert(END, str(round(100 * (self.accumulated_pop - self.accumulated_complete_sols) / self.accumulated_pop, 2)) + '%', 'pink')
            else:
                self.textlog.insert(END, '100.0%', 'pink')
            self.textlog.insert(END, lang.hh50)
            self.textlog.insert(END, lang.hh51, 'pink')
            self.textlog.insert(END, ':\n')

            if self.infeasibleA:
                self.textlog.insert(END, str(self.infeasibleB), 'purple')
                self.textlog.insert(END, lang.hh26)
                if self.accumulated_pop:
                    self.textlog.insert(END, str(round(100 * self.infeasibleA / self.accumulated_pop, 2)) + '%', 'purple')
                else:
                    self.textlog.insert(END, '100.0%', 'purple')
                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh28, 'purple')
                self.textlog.insert(END, lang.hh29)

            if self.infeasibleB:
                self.textlog.insert(END, str(self.infeasibleB), 'orange')
                self.textlog.insert(END, lang.hh26)
                if self.accumulated_pop:
                    self.textlog.insert(END, str(round(100 * self.infeasibleB / self.accumulated_pop, 2)) + '%', 'orange')
                else:
                    self.textlog.insert(END, '100.0%', 'orange')
                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh36, 'orange')
                self.textlog.insert(END, lang.hh63)

            if self.infeasibleC:
                self.textlog.insert(END, str(self.infeasibleC), 'red')
                self.textlog.insert(END, lang.hh26)
                if self.accumulated_pop:
                    self.textlog.insert(END, str(round(100 * self.infeasibleC / self.accumulated_pop, 2)) + '%', 'red')
                else:
                    self.textlog.insert(END, '100.0%', 'red')
                self.textlog.insert(END, lang.hh27)
                self.textlog.insert(END, lang.hh38, 'red')
                self.textlog.insert(END, lang.hh39)

            self.textlog.insert(END, str(self.accumulated_pop), 'green')
            self.textlog.insert(END, ' (')
            self.textlog.insert(END, str(round(100 * self.accumulated_complete_sols / self.accumulated_pop, 2)) + '%', 'green')
            self.textlog.insert(END, lang.hh52)

        else:
            self.textlog.insert(END, str(self.accumulated_complete_sols), 'green')
            self.textlog.insert(END, ' (')
            self.textlog.insert(END, '100%', 'green')
            self.textlog.insert(END, lang.hh52)

        self.textlog.insert(END, lang.hh64)
        self.textlog.insert(END, str(self.best_value) + '\n', 'aquamarine')

        self.textlog.insert(END, lang.hh65)

        self.textlog.configure(state="disabled")
        self.textlog.see(END)
        self.windowlog.update()

    def _loggingevent_NewCut(self):
        self.textlog.configure(state="normal")

        self.textlog.insert(END, lang.hh66)
        self.textlog.insert(END, str(self.current_cuts + 1), 'blue')
        self.textlog.insert(END, "/")
        self.textlog.insert(END, str(self.cuts), 'yellow')
        self.textlog.insert(END, " \U0001F4C5\n")

        self.textlog.configure(state="disabled")
        self.textlog.see(END)
        self.windowlog.update()

    def executor(self):
        force_quit = self._matrix_builder()
        if force_quit:
            return True
        self._create_population_handler()
        if self.current_cuts == 0:
            self._loggingevent_Welcome()

        try:
            self.step = 0
            self._loggingevent_NewCut()
            self.run(settings.HEURISTIC_STEPS, settings.HEURISTIC_ITERS_PER_STEP)
            while self.best_value == -np.inf and settings.HEURISTIC_SOLVE_ABOVE_ALL:
                if self.nuke_order or self.stop_order:
                    break # TODO Button has not been implemented yet (only closing window behaviour). Cores are safely stopped at this point. A button here should kill the process
                self.run(1, settings.HEURISTIC_ITERS_PER_STEP)

        except:
            error = traceback.format_exc()
            print(error)
            messagebox.showerror(lang.hh59, lang.hh60 + error)
        
        return False
        
    def multiple_run(self):
        try:
            self.finishtracker.value = False

            for i in range(self.cuts):
                force_quit = self.executor()
                if force_quit:
                    self.nuke_order = True
                    return True
                
                if self.nuke_order: # TODO Button has not been implemented yet, only a close window kill. Cores are safely stopped at this point. We should slightly modify the structure and several buttons, to cancel the process and to jump to the next solution calculation
                    self.population_handler.pool.terminate()
                    del self.best_value, self.best_schedule, self.best_maintenance, self.best_linkers
                    gccollect()
                    break

                # Cut must be performed here; even in the last calculation, as the cut also stores the solution
                self._days_cutter(self.days_per_cut * 24, self.best_schedule, self.best_maintenance, self.best_linkers)
                self._loggingevent_CutFinished()
            self.finishtracker.value = True
        except:
            error = traceback.format_exc()
            messagebox.showerror(lang.hh59, lang.hh67 + error)
        
        return False
        
    def _create_population_handler(self):
        self.population_handler = deme_class(self.numtrains, self.numservices, np.array(self.predecessors, dtype=np.uint8), np.array(self.condition, dtype=np.uint16), np.array(self.trimmed_km_limit, dtype=np.float64), np.array(self.km_service, dtype=np.float64), np.array(self.depot, dtype=np.uint8), np.array(self.departure_time, dtype=np.float64), np.array(self.next_m_duration, dtype=np.float64), np.array(self.total_capacity, dtype=np.uint8), np.array(self.capacities_management, dtype=np.float64), np.array(self.uses_linkers, dtype=np.uint8), np.array(self.valid_linkers, dtype=np.int16), np.array(self.kmlinker, dtype=np.float64), np.array(self.total_linkers_capacity, dtype=np.uint8), self.avoidance_margin, self.critical_margin)
        self.best_value = -np.inf

        self.accumulated_pop = 0
        self.accumulated_complete_sols = 0
        self.infeasibleA = 0
        self.infeasibleB = 0
        self.infeasibleC = 0
        self.infeasibleA_cols = np.empty(0, dtype=np.int16)

    def _matrix_builder(self):
        utils, error = builder.build_matrices(7, self.services, self.iniservices, self.depotnodes, self.numtrains, self.starting_weekday, self.next_m_duration, self.transfers, self.linkers, self.km_limit)
        if utils is None:
            messagebox.showerror(error['title'], error['content'])
            return True
        else:
            matrix, numservices, ignore = utils

        self.numservices = numservices
        self.predecessors = matrix['predecessors']
        self.condition = matrix['condition']
        self.km_service = matrix['km_service']
        self.depot = matrix['depot']
        self.departure_time = np.array(matrix['departure_time'])
        self.duration_service = np.array(matrix['duration_service'])
        self.arrival_time = np.array(matrix['arrival_time'])
        self.bans = matrix['bans']
        self.table_conversion = matrix['table_conversion']
        self.dict_color = matrix['dict_color']
        self.str_arrivals = matrix['stringed_arrivals']
        self.str_departures = matrix['stringed_departures']
        self.str_condition = matrix['stringed_condition']
        self.origins = matrix['origins']
        self.destinies = matrix['destinies']
        self.total_capacity = matrix['total_capacity']
        self.capacities_management = matrix['capacities_management']
        self.trimmed_km_limit = matrix['trimmed_km_limit']
        self.uses_linkers = matrix['uses_linkers']
        self.valid_linkers = matrix['valid_linkers']
        self.kmlinker = matrix['linkers_km']
        self.total_linkers_capacity = matrix['linkers_capacity']
        self.info_linkers = matrix['info_linkers']
        
        return False

    def _days_cutter(self, cutting_hour, x_solution, m_solution, linkers_solution):
        last_index = self.numservices
        for i in range(len(self.departure_time)):
            if self.departure_time[i] > cutting_hour:
                last_index = i
                break

        self.iniservices = {}
        curr_km_limit = np.zeros(self.numtrains)
        curr_next_m_name = np.empty_like(self.next_m_name)
        curr_next_m_duration = np.zeros(self.numtrains, dtype=np.float64)

        # Edition of variables
        x_section = x_solution[:, :last_index]

        # Linkers solution preparation
        linkers_section = linkers_solution[:, :last_index]
        nrows, ncols = x_section.shape
        # index of first '1' from the right (distance from right), per row
        idx_from_right = np.argmax(x_section[:, ::-1], axis=1)
        # Previous step gives the result of the reversed (flipped) equivalent. We unflip the following way. -1 accounts for zero-based indexation
        last_one_idx = ncols - 1 - idx_from_right
        # Build mask: True for column positions >= last_one_idx for each row
        mask = np.arange(ncols) >= last_one_idx[:, None]  # shape (nrows, ncols)
        # Apply
        linkers_section[mask] = -1

        departures_x_section = x_section * self.departure_time[:last_index]
        # np.set_printoptions(edgeitems=1000, precision=0)
        last_services = np.zeros(self.numtrains, dtype=np.uint8)
        for i in range(self.numtrains):
            # Check the last_service
            last_services[i] = x_section[i, :].nonzero()[0][-1]

            # Check maintenance and inideprecation from last_maintenance
            if 0 < m_solution[i] <= cutting_hour:
                curr_km_limit[i] = self.km_limit[i]
                curr_next_m_name[i] = self.next_m_name[i]
                curr_next_m_duration[i] = self.next_m_duration[i]

                self.km_limit[i] = settings.DEFAULT_INTERVENTION_KM
                self.next_m_name[i] = settings.DEFAULT_INTERVENTION
                self.next_m_duration[i] = settings.DEFAULT_INTERVENTION_TIME
            else:
                m_solution[i] = 0 # Ignore maintenance; override to 0

            # Get km since last maintenance
            km = np.where(departures_x_section[i] > m_solution[i], self.km_service[:last_index], 0).astype(np.array(self.km_service).dtype).sum()

            applying_linkers = np.where(departures_x_section[i] > m_solution[i], linkers_section[i], -1)
            for linker_idx in applying_linkers:
                if linker_idx > -1:
                    km += self.kmlinker[linker_idx]

            # Departure time of iniservice is 0, so in case of no maintenance this one is till not being counted (0 > 0 is False). Fixing
            if not m_solution[i]:
                km += self.km_service[i]

            # Compare maintenance and last_Service. Also, comapre the end_maintenance or arrival time according to the situation.
            if self.departure_time[last_services[i]] >= m_solution[i]:
                # if i == 0:
                #     print('tocaservicio', m_solution[i], self.next_m_duration[i], self.next_m_name[i], self.departure_time[last_services[i]], self.arrival_time[last_services[i]])
                # Maintenance was before
                endtime = self.arrival_time[last_services[i]]
                if endtime <= cutting_hour:
                    block = 0.1
                    location = self.destinies[last_services[i]]
                else:
                    block = endtime - cutting_hour
                    location = self.destinies[last_services[i]]
            else:
                # Maintenance was after the last accepted service. It is potentially being cut
                endtime = m_solution[i] + curr_next_m_duration[i] # Check if maintenance is finished
                # if i == 0:
                #     print('wakawaka', m_solution[i], self.next_m_duration[i], self.next_m_name[i], endtime)
                if endtime <= cutting_hour: # Maintenance is not being cut
                    block = 0.1
                    location = self.destinies[last_services[i]]
                    if lang.DEPOT_MAINTENANCE in location:
                        location = location.replace(lang.DEPOT_MAINTENANCE, lang.DEPOT_OVERNIGHT)
                else: # Maintenance is being cut
                    block = endtime - cutting_hour
                    location = self.destinies[last_services[i]] + lang.DEPOT_MAINTENANCE

            # if i == 0:
            #     print('final', m_solution[i], self.next_m_duration[i], self.next_m_name[i], endtime, block, location)

            # Update maintenance variables by applying offset
            if m_solution[i]:
                m_solution[i] += self.accumulated_cut_time

            # Update iniservice
            self.iniservices['iniservice' + str(i+1)] = {}
            self.iniservices['iniservice' + str(i+1)]['id'] = 'Irrelevant'
            self.iniservices['iniservice' + str(i+1)]['origin'] = location
            self.iniservices['iniservice' + str(i+1)]['destiny'] = location
            self.iniservices['iniservice' + str(i+1)]['kilometers'] = km
            self.iniservices['iniservice' + str(i+1)]['departure-time'] = 0
            self.iniservices['iniservice' + str(i+1)]['arrival-time'] = block
            self.iniservices['iniservice' + str(i+1)]['str_departure-time'] = 'Irrelevant'
            self.iniservices['iniservice' + str(i+1)]['str_arrival-time'] = 'Irrelevant'
            self.iniservices['iniservice' + str(i+1)]['color'] = '#6d6d6d'
            self.iniservices['iniservice' + str(i+1)]['forced'] = self.str_condition[last_services[i]]
            self.iniservices['iniservice' + str(i+1)]['bans'] = deepcopy(self.bans[last_services[i]])

        # Update storing variables
        self.departure_time += self.accumulated_cut_time
        self.arrival_time += self.accumulated_cut_time

        # Update linkers_index, define linkers to save (all until the last one needed, even if useless ones fall in the middle)
        # Flatten and mask the non -1 entries
        flat = linkers_section.ravel()
        nonneg_mask = flat != -1

        # Order-preserving unique extraction (fast and avoids sorting)
        linkers_to_save = []
        for v in flat[nonneg_mask]:
            # convert to Python int for safe serialization later
            vi = int(v)
            if vi not in linkers_to_save:
                linkers_to_save.append(vi)

        if len(linkers_to_save) > 0:
            linkers_section[linkers_section != -1] += self.store_info_linkers.shape[0] # Apply offset to linkers indexes based on preexisting info_linkers

            last_valuable_linker = max(linkers_to_save)
            needed_info_linkers = self.info_linkers[:last_valuable_linker+1]

            for idx in range(len(needed_info_linkers)):
                needed_info_linkers[idx]['opening-time'] += self.accumulated_cut_time
                needed_info_linkers[idx]['ending-time'] += self.accumulated_cut_time

        else:
            needed_info_linkers = []

        # TODO linkers_solutions has the same shape as x_solution, so it will probably be cut the same way as x_section
        # TODO info linkers has a more weird shape. We only need the indexes that are being used, but those indexes will be appended to previous indexes. Hence, the values in linkers sections need to increased based on the preexisting linkers in info_linkers. Non-used linkers might be removed (maybe). Also, inside info_linkers there might be departure/arrival times that might need to see an offset applied
        self._store_sol(x_section, m_solution, last_index, curr_km_limit, curr_next_m_name, curr_next_m_duration, linkers_section, needed_info_linkers)

        # Due to elimination of the iniservices in subsequent runs, there is a mismatch that inherently removes information about linkers where an iniservice is involved.
        # Moreover, as linkers after the latest cutted service are intentionally ignored, a necessary linker could not be displayed accordingly.
        # The following solves such problem
        idx_from_right = np.argmax(self.store_schedule[:, ::-1], axis=1)
        # Previous step gives the result of the reversed (flipped) equivalent. We unflip the following way. -1 accounts for zero-based indexation
        ncols = self.store_schedule.shape[1]
        self.last_services = ncols - 1 - idx_from_right


        today_is = datetime.now().isoweekday() - 1 if self.starting_weekday == lang.CURRENT else lang.FULL_WEEK.index(self.starting_weekday)
        adding = round(cutting_hour/24, 0)

        if today_is + adding > 6:
            self.starting_weekday = lang.FULL_WEEK[int(today_is + adding - 7)]
        else:
            self.starting_weekday = lang.FULL_WEEK[int(today_is + adding)]
        self.accumulated_cut_time += cutting_hour
        self.current_cuts += 1

    def _store_sol(self, x_section, m_solution, last_index, curr_km_limit, curr_next_m_name, curr_next_m_duration, linkers_section, needed_info_linkers): # Store solutions in a predefined element
        self.store_maintenance = np.concatenate([self.store_maintenance, m_solution[:, np.newaxis]], dtype=np.float64, axis=1)


        # print(m_solution)
        # print([self.iniservices[item]['kilometers'] for item in self.iniservices])
        # print(self.km_limit)
        # print(self.store_maintenance, '\n\n')
        self.store_km_limit = np.concatenate([self.store_km_limit, curr_km_limit[:, np.newaxis]], axis=1)
        self.store_next_m_duration = np.concatenate([self.store_next_m_duration, curr_next_m_duration[:, np.newaxis]], dtype=np.float64, axis=1)
        self.store_next_m_name = np.concatenate([self.store_next_m_name, curr_next_m_name[:, np.newaxis]], axis=1)

        if self.current_cuts == 0:
            self.store_schedule = np.concatenate([self.store_schedule, x_section], dtype=np.uint8, axis=1)
            self.store_linkers_solution = np.concatenate([self.store_linkers_solution, linkers_section], dtype=np.int16, axis=1)
            # Store other elements belonging to the matrices
            self.store_departure_time = np.concatenate([self.store_departure_time, self.departure_time[:last_index]])
            self.store_duration_service = np.concatenate([self.store_duration_service, self.duration_service[:last_index]])
            self.store_arrival_time = np.concatenate([self.store_arrival_time, self.arrival_time[:last_index]])
            self.store_table_conversion = np.concatenate([self.store_table_conversion, self.table_conversion[:last_index]])
            self.store_km_service = np.concatenate([self.store_km_service, self.km_service[:last_index]])
            self.store_origins = np.concatenate([self.store_origins, self.origins[:last_index]])
            self.store_destinies = np.concatenate([self.store_destinies, self.destinies[:last_index]])
            self.store_conditioned_successor = np.concatenate([self.store_conditioned_successor, self.condition[:last_index]])
            self.store_str_departures = np.concatenate([self.store_str_departures, self.str_departures[:last_index]])
            self.store_str_arrivals = np.concatenate([self.store_str_arrivals, self.str_arrivals[:last_index]])
            self.store_str_condition = np.concatenate([self.store_str_condition, self.str_condition[:last_index]])
            self.store_dict_color = np.concatenate([self.store_dict_color, self.dict_color[:last_index]])
            [self.store_banned_successors.append(self.bans[i]) for i in range(last_index)]

        else:
            # Before stacking the new solution, check if an iniservice requires linkers
            for i in range(self.numtrains):
                if linkers_section[i, i] > -1:
                    self.store_schedule[i, self.last_services[i]] = linkers_section[i, i]

            # print(len(self.departure_time) - self.numtrains)
            self.store_schedule = np.concatenate([self.store_schedule, x_section[:, self.numtrains:]], dtype=np.uint8, axis=1)
            self.store_linkers_solution = np.concatenate([self.store_linkers_solution, linkers_section[:, self.numtrains:]], dtype=np.int16, axis=1)
            # Store other elements belonging to the matrices
            self.store_departure_time = np.concatenate([self.store_departure_time, self.departure_time[self.numtrains:last_index]])
            self.store_duration_service = np.concatenate([self.store_duration_service, self.duration_service[self.numtrains:last_index]])
            self.store_arrival_time = np.concatenate([self.store_arrival_time, self.arrival_time[self.numtrains:last_index]])
            self.store_table_conversion = np.concatenate([self.store_table_conversion, self.table_conversion[self.numtrains:last_index]])
            self.store_km_service = np.concatenate([self.store_km_service, self.km_service[self.numtrains:last_index]])
            self.store_origins = np.concatenate([self.store_origins, self.origins[self.numtrains:last_index]])
            self.store_destinies = np.concatenate([self.store_destinies, self.destinies[self.numtrains:last_index]])
            self.store_conditioned_successor = np.concatenate([self.store_conditioned_successor, self.condition[self.numtrains:last_index]]) # TODO do we need this one?
            self.store_str_departures = np.concatenate([self.store_str_departures, self.str_departures[self.numtrains:last_index]])
            self.store_str_arrivals = np.concatenate([self.store_str_arrivals, self.str_arrivals[self.numtrains:last_index]])
            self.store_str_condition = np.concatenate([self.store_str_condition, self.str_condition[self.numtrains:last_index]])
            self.store_dict_color = np.concatenate([self.store_dict_color, self.dict_color[self.numtrains:last_index]])
            [self.store_banned_successors.append(self.bans[i]) for i in range(self.numtrains, last_index)]

        self.store_info_linkers = np.concatenate([self.store_info_linkers, needed_info_linkers], axis=0)


# -*- coding: utf-8 -*-
"""
Created on Tue Nov  1 13:40:05 2022

@author: naftabi
"""

import os
import re
import numpy as np
from math import sqrt
from time import time
from gurobipy import Model, GRB

PATH = os.getcwd()
DATA_PATH = os.path.join(PATH, 'data')
LOG_PATH = os.path.join(PATH, 'logs')

def clear_logs(filename):
    for ext in ['.log', '.lp', '.sol', '.time']:
        filepath = os.path.join(LOG_PATH, f'{filename}{ext}')
        if os.path.exists(filepath):
            os.remove(filepath)

def _read_matrix(param_name, experiment):
    filepath = os.path.join(DATA_PATH, experiment, f'{param_name}.txt')
    return np.matrix(_read_file(filepath))

def _read_vector(param_name, experiment):
    filepath = os.path.join(DATA_PATH, experiment, f'{param_name}.txt')
    return np.array(_read_file(filepath)[0])

def _read_scalar(param_name, experiment):
    filepath = os.path.join(DATA_PATH, experiment, f'{param_name}.txt')
    return _read_file(filepath)[0][0]

def _read_file(filepath):
    with open(filepath, 'r') as file:
        return [
            [float(value) for value in re.sub(r"[\t\n ]", ' ', line).split()]
            for line in file.readlines()
        ]


class AttackerModel:
    def __init__(self,
                 K: int,
                 T: int,
                 expr: str,
                 sd_v: float = None,
                 sd_w: float = None,
                 sd_s: float = None,
                 filename: str = None):
        self.K = K
        self.T = T
        self.S = None
        self.C = None
        self.G = None
        self.filename = f'{filename}-K{K}-T{T}'
        clear_logs(self.filename)
        self.model = self._initialize_model()
        if expr != 'cyber':
            self._load_parameters(sd_v, sd_w, sd_s, expr)
        
    def _load_parameters(self, sd_v, sd_w, sd_s, expr):
        self.sd_v = sd_v
        self.sd_w = sd_w
        self.sd_s = sd_s
        self.z_preception = 3
        self.A = _read_matrix('A', expr)
        self.B = _read_matrix('B', expr)
        self.D = _read_matrix('D', expr)
        self.E = self._compute_E()
        self.gamma = _read_vector('gamma', expr)
        self.kappa = sqrt(2) * _read_scalar('kappa', expr)
        self.lamb = _read_scalar('lambda', expr)
        self.sigma_z = _read_vector('sigma_z', expr)
        self.M = {f'M{i+1}': i for i in range(self.A.shape[0])}
        if expr == 'case':
            self.Zref = _read_matrix(f'Zref-{self.T}', expr)
        
    def _initialize_model(self):
        log_file = os.path.join(LOG_PATH, f'{self.filename}.log')
        model = Model()
        model.setParam('LogFile', log_file)
        model.setParam('LogToConsole', 0)
        model.setParam('Heuristics', 0)
        model.setParam('IntFeasTol', 1e-9)
        model.setParam('IntegralityFocus', 1)
        model.setParam('TimeLimit', 2 * 3600)
        return model

    def _compute_E(self):
        term1 = np.linalg.inv(self.B.T @ self.B) @ self.B.T
        term2 = np.linalg.inv(self.D.T @ self.D) @ self.D.T
        E = -1 * (term1 @ self.A @ term2)
        return E

    def solve(self):
        start_time = time()
        self.model.update()
        self.model.optimize()
        elapsed_time = time() - start_time

        self._log_solution(elapsed_time)

    def _log_solution(self, elapsed_time):
        log_file = os.path.join(LOG_PATH, self.filename)
        self.model.write(f'{log_file}.lp')

        if self.model.Status in {GRB.OPTIMAL, GRB.TIME_LIMIT}:
            print(f'The optimal objective is {self.model.ObjVal:.4f}')
            self._write_time_file(log_file, elapsed_time)
            self.model.write(f'{log_file}.sol')
        else:
            print(f'Optimization was stopped with status {self.model.Status}')

    def _write_time_file(self, log_path, elapsed_time):
        with open(f'{log_path}.time', 'w') as file:
            file.write(f'Status: {self.model.Status}\n')
            file.write(f'Time: {elapsed_time:.2f} seconds\n')

    def get_lb_ub(self):
        self.lb_a = -np.round(3 * self.sd_w, 2)
        self.ub_a = np.round(3 * self.sd_w, 2)
        self.lb_b = -np.round(3 * self.sd_v, 2)
        self.ub_b = np.round(3 * self.sd_v, 2)
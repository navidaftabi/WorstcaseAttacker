# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 10:34:14 2024

@author: aftabi
"""

import os
import re
import pickle
import numpy as np
from collections import defaultdict
from collections.abc import Iterable, Mapping

LOG_PATH = os.path.join(os.getcwd(), 'logs')

def maybeMakeNumber(s):
    if not s:
        return s
    try:
        f = float(s)
        i = int(f)
        return i if f == i else f
    except ValueError:
        return s

def convertEr(iterab):
    if isinstance(iterab, str):
        return maybeMakeNumber(iterab)

    if isinstance(iterab, Mapping):
        return iterab

    if isinstance(iterab, Iterable):
        return  iterab.__class__(convertEr(p) for p in iterab)


def create_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)


def save_results(sol, path):
    for var_name, values in sol.items():
        create_directory(path)
        if isinstance(values, np.ndarray):
            np.save(os.path.join(path, f'{var_name}.npy'), values)
        else:
            with open(os.path.join(path, f'{var_name}.pkl'), 'wb') as f:
                pickle.dump(values, f)

def get_vars(m):
    T = m.T
    sol = defaultdict(dict)
    for v in m.model.getVars():
        vname = v.varName
        if vname.startswith('h'):
            n_id = convertEr(re.sub(r'[h\[\]]', '', vname))
            if n_id != 'AUX':
                sol['h'][n_id] = round(v.x)
        elif vname.startswith('y'):
            sol['y'][convertEr(tuple(re.sub(r'[y\[,\]]', ' ', vname).split()))] = v.x
        elif vname.startswith('f'):
            sol['f'][convertEr(tuple(re.sub(r'[f\[,\]]', ' ', vname).split()))] = round(v.x)
        elif vname.startswith('alpha'):
            sol['alpha'][convertEr(tuple(re.sub(r'[alpha\[,\]]', ' ', vname).split()))] = v.x
        elif vname.startswith('beta'):
            sol['beta'][convertEr(tuple(re.sub(r'[beta\[,\]]', ' ', vname).split()))] = v.x
        elif vname.startswith('x'):
            sol['x'][convertEr(tuple(re.sub(r'[x\[,\]]', ' ', vname).split()))] = v.x
        elif vname.startswith('u'):
            sol['u'][convertEr(tuple(re.sub(r'[u\[,\]]', ' ', vname).split()))] = v.x
        elif vname.startswith('z'):
            sol['z'][convertEr(tuple(re.sub(r'[z\[,\]]', ' ', vname).split()))] = v.x
        elif vname.startswith('a'):
            sol['a'][convertEr(tuple(re.sub(r'[a\[,\]]', ' ', vname).split()))] = v.x
        elif vname.startswith('b'):
            sol['b'][convertEr(tuple(re.sub(r'[b\[,\]]', ' ', vname).split()))] = v.x
    if 'x' in sol.keys():        
        sol['x'] = np.reshape(np.fromiter(sol['x'].values(), dtype=float), (len(m.M), T+1))
    if 'u' in sol.keys(): 
        sol['u'] = np.reshape(np.fromiter(sol['u'].values(), dtype=float), (len(m.C), T))
    if 'z' in sol.keys(): 
        sol['z'] = np.reshape(np.fromiter(sol['z'].values(), dtype=float), (len(m.S), T))
    if 'a' in sol.keys(): 
        sol['a'] = np.reshape(np.fromiter(sol['a'].values(), dtype=float), (len(m.S), T))
    if 'b' in sol.keys(): 
        sol['b'] = np.reshape(np.fromiter(sol['b'].values(), dtype=float), (len(m.C), T))
    return sol

def set_detection_params(m, d):
    detect_power = {
        'loose': 5,
        'medium': 3,
        'strict': 1
    }[d]

    m.lb_a = - np.round(detect_power * m.sd_w, 2)
    m.ub_a = np.round(detect_power * m.sd_w, 2)

    m.lb_b = - np.round(detect_power * m.sd_v, 2)
    m.ub_b = np.round(detect_power * m.sd_v, 2)
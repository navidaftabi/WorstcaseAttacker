# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 11:21:33 2024

@author: aftabi
"""

import os
import pickle
import logging
from math import sqrt

from model.attack_model import Attacker
from utils import get_vars, save_results

DATA_PATH = os.path.join(os.getcwd(), 'data')
OUT_PATH = os.path.join(os.getcwd(), 'result')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

EXPERIMENT_CONFIG = {
    'case': {
        'sd_v': 0.05,
        'sd_w': 0.05,
        'sd_s': 0.1,
    },
    'random': {
        'sd_v': 0.1,
        'sd_w': sqrt(0.001),
        'sd_s': 0.1,
    },
}

def run_experiment():
    scenarios = {
        'type1': ['S2', 'C1', 'C3'],
        'type2': ['C1', 'C2', 'C3'],
        'type3': ['S1', 'S2', 'C2'],
        'case': ['GT', 'P1', 'P2', 'L2']
    }

    T = 400

    for experiment_name, components in scenarios.items():
        logger.info(f"Running disjoint problem for experiment: {experiment_name}")

        if experiment_name.startswith('type'):
            ag_path = os.path.join(DATA_PATH, 'random', f'cl-{experiment_name}.pkl')
            config = EXPERIMENT_CONFIG['random']
            expr = 'random'
        else:
            ag_path = os.path.join(DATA_PATH, 'case', 'cl.pkl')
            config = EXPERIMENT_CONFIG['case']
            expr = 'case'

        try:
            with open(ag_path, 'rb') as f:
                cl = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Graph file not found: {ag_path}. Please ensure the graph exists.")

        K = len(components)
        sd_v, sd_w, sd_s = config['sd_v'], config['sd_w'], config['sd_s']
        logfile = f'disjoint-{experiment_name}'
        cl.add_aux()

        logger.info(f"Solving disjoint optimization problem for {experiment_name} with K={K} T={T} ...")
        m = Attacker(K=K, T=T, sd_v=sd_v, sd_w=sd_w, sd_s=sd_s, 
                     filename=logfile, expr=expr)
        m.G = cl.DAG
        m.S = cl.sensors
        m.C = cl.controllers
        m.build_model()

        for component in list(m.S.keys()) + list(m.C.keys()):
            if component not in components:
                for t in range(T):
                    if component in m.S.keys():
                        m.a[component, t].lb = 0.0
                        m.a[component, t].ub = 0.0
                    else:
                        m.b[component, t].lb = 0.0
                        m.b[component, t].ub = 0.0
                    m.alpha[component, t].lb = 0.0
                    m.alpha[component, t].ub = 0.0

        m.solve()
        cl.remove_aux()

        if m.model.status not in [3, 4, 5]:
            sol = get_vars(m)
            out_path = os.path.join(OUT_PATH, 'disjoint', experiment_name, f'T{T}-K{K}')
            save_results(sol, out_path)
        else:
            logger.warning(f"Optimization failed for {experiment_name} T{T}-K{T} with status {m.model.status}.")


if __name__ == '__main__':
    logger.info("Starting analysis script.")
    run_experiment()
    logger.info("Analysis complete.")
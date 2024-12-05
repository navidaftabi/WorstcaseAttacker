# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 10:29:02 2024

@author: aftabi
"""

import os
import logging
import pickle

from model.cyber_attack_model import Attacker
from utils import get_vars, save_results

DATA_PATH = os.path.join(os.getcwd(), 'data')
OUT_PATH = os.path.join(os.getcwd(), 'result')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def run_experiment():
    experiments = ['type1', 'type2', 'type3', 'case']
    T = 200

    for experiment_name in experiments:
        logger.info(f"Solving cyber-only problem for experiment: {experiment_name}")

        if experiment_name.startswith('type'):
            ag_path = os.path.join(DATA_PATH, 'random', f'cl-{experiment_name}.pkl')
            K = 3
        else:
            ag_path = os.path.join(DATA_PATH, 'case', 'cl.pkl')
            K = 4

        logger.info("Loading existing attack graph.")
        try:
            with open(ag_path, 'rb') as f:
                cl = pickle.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Graph file not found: {ag_path}. Please ensure the graph exists.")


        logfile = f'cyber-{experiment_name}'
        logger.info(f"Solving cyber only optimization problem for {experiment_name} with K={K} ...")
        cl.add_aux()
        m = Attacker(K=K, T=T, expr='cyber', filename=logfile)
        m.G = cl.DAG
        m.S = cl.sensors
        m.C = cl.controllers
        m.build_model()
        m.solve()
        cl.remove_aux()

        if m.model.status not in [3, 4, 5]:
            sol = get_vars(m)
            out_path = os.path.join(OUT_PATH, 'cyber', experiment_name, f'K{K}')
            save_results(sol, out_path)
        else:
            logger.warning(f"Optimization failed for {experiment_name} with status {m.model.status}.")


if __name__ == '__main__':
    logger.info("Starting analysis script.")
    run_experiment()
    logger.info("Analysis complete.")
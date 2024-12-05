# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:00:26 2024

@author: aftabi
"""

import os
import pickle
import logging

from model.attack_model_biehler import Attacker
from utils import get_vars, save_results

OUT_PATH = os.path.join(os.getcwd(), 'result')
DATA_PATH = os.path.join(os.getcwd(), 'data')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def run_experiment():
    logger.info("Loading attack graph for case study.")
    ag_path = os.path.join(DATA_PATH, 'case', 'cl.pkl')
    try:
        with open(ag_path, 'rb') as f:
            cl = pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Graph file not found: {ag_path}. Please ensure the graph exists.")
    K = cl.num_sensor + cl.num_controller
    T = [200, 400, 600, 1000]
    sd_v = 0.05
    sd_w = 0.05
    sd_s = 0.1
    for t in T:
        logger.info(f"Solving Biehler et al. on case study for T={t} ...")
        logfile = 'biehler'
        m = Attacker(K=K, T=t, sd_v=sd_v, sd_w=sd_w, sd_s=sd_s,
                     filename=logfile, expr='case')
        m.G = cl.DAG
        m.S = cl.sensors
        m.C = cl.controllers
        m.build_model()
        m.solve()
        cl.remove_aux()
        if m.model.status not in [3, 4, 5]:
            sol = get_vars(m)
            out_path = os.path.join(OUT_PATH, 'biehler', f'T{t}')
            save_results(sol, out_path)
        else:
            logger.warning(f"Optimization failed for T={t} with status {m.model.status}.")


if __name__ == '__main__':
    logger.info("Starting analysis script.")
    run_experiment()
    logger.info("Analysis complete.")
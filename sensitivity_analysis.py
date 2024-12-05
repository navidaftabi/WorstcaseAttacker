# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 22:08:43 2024

@author: aftabi
"""

import logging
import os
import pickle
from math import sqrt

from model.attack_model import Attacker
from utils import set_detection_params, get_vars, save_results


OUT_PATH = os.path.join(os.getcwd(), 'result')
DATA_PATH = os.path.join(os.getcwd(), 'data')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

 
def run_sensitivity_analysis():
    net_type = 1
    T = 400
    K = 3
    detection_schemes = ['loose', 'medium', 'strict']
    sd_v, sd_w, sd_s = 0.1, sqrt(0.001), 0.1

    logger.info("Loading existing attack graph.")
    file_path = os.path.join(DATA_PATH, 'random', f'cl-type{net_type}.pkl')
    try:
        with open(file_path, 'rb') as f:
            cl = pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Graph file not found: {file_path}. Please ensure the graph exists.")

    for d in detection_schemes:
        pathfile = f'sa-random-type{net_type}-detection-{d}'
        logger.info(f"Running optimization model for detection scheme: {d}.")
        cl.add_aux()
        m = Attacker(K=K, T=T, sd_v=sd_v, sd_w=sd_w, sd_s=sd_s, 
                     filename=pathfile, expr='random')
        m.G = cl.DAG
        m.S = cl.sensors
        m.C = cl.controllers
        set_detection_params(m, d)
        logger.info(f"Detection parameters: sensors [{m.lb_a}, {m.ub_a}], controllers [{m.lb_b}, {m.ub_b}]")
        m.build_model()
        m.solve()
        cl.remove_aux()
        if m.model.status not in [3, 4, 5]:
            out_path = os.path.join(OUT_PATH, 'sa', f'type{net_type}', 'detection_{d}')
            sol = get_vars(m)
            save_results(sol, out_path)
        else:
            logger.warning(f"Optimization failed for {d} with status {m.model.status}.")


if __name__ == '__main__':
    logger.info("Starting sensitivity analysis.")
    run_sensitivity_analysis()
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 14:40:32 2024

@author: aftabi
"""

import os
import pickle
import logging

from model.attack_model import Attacker
from utils import get_vars, save_results

DATA_PATH = os.path.join(os.getcwd(), 'data')
OUT_PATH = os.path.join(os.getcwd(), 'result')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def run_experiment():
    scenario = ['WV', 'GT', 'P2', 'L1', 'L2']
    access = {'P1': 104, 'FV': 120, 'SV': 128}

    T = [200, 400, 600, 1000]
    K = len(access)
    sd_v = 0.05
    sd_w = 0.05
    sd_s = 0.1
    ag_path = os.path.join(DATA_PATH, 'case', 'cl.pkl')

    try:
        with open(ag_path, 'rb') as f:
            cl = pickle.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Graph file not found: {ag_path}. Please ensure the graph exists.")
    for t in T:
        logfile = 'huang'
        cl.add_aux()

        logger.info(f"Solving Huang et al. attack scenario optimization problem for with K={K} T={T} ...")
        m = Attacker(K=K, T=t, sd_v=sd_v, sd_w=sd_w, sd_s=sd_s, 
                     filename=logfile, expr='case')
        m.G = cl.DAG
        m.S = cl.sensors
        m.C = cl.controllers
        m.build_model()

        for component in list(m.S.keys()) + list(m.C.keys()):
            if component in scenario:
                for tt in range(m.T):
                    if component in m.S.keys():
                        m.a[component, tt].lb = 0.0
                        m.a[component, tt].ub = 0.0
                    else:
                        m.b[component, tt].lb = 0.0
                        m.b[component, tt].ub = 0.0
                    m.alpha[component, tt].lb = 0.0
                    m.alpha[component, tt].ub = 0.0
                    
        for component, time in access.items():
            for tt in range(time):
                m.alpha[component, tt].lb = 0.0
                m.alpha[component, tt].ub = 0.0
                if component in m.S.keys():
                    m.a[component, tt].lb = 0.0
                    m.a[component, tt].ub = 0.0
                else:
                    m.b[component, tt].lb = 0.0
                    m.b[component, tt].ub = 0.0
                
        m.solve()
        cl.remove_aux()

        if m.model.status not in [3, 4, 5]:
            sol = get_vars(m)
            out_path = os.path.join(OUT_PATH, 'huang', f'T{T}')
            save_results(sol, out_path)
        else:
            logger.warning(f"Optimization failed for T={t} with status {m.model.status}.")


if __name__ == '__main__':
    logger.info("Starting analysis script.")
    run_experiment()
    logger.info("Analysis complete.")
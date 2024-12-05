# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 19:04:51 2024

@author: aftabi
"""

import argparse
import logging

import os
import pickle
import numpy as np
from math import sqrt

from model.attack_model import Attacker
from model.attack_graph import RandomCyberLayer
from case_attack_graph import get_graph
from utils import get_vars, save_results

OUT_PATH = os.path.join(os.getcwd(), 'result')
DATA_PATH = os.path.join(os.getcwd(), 'data')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

EXPERIMENT_CONFIG = {
    'case': {
        'T': [100, 200, 400, 600, 1000],
        'K': list(range(1, 9)),
        'sd_v': 0.05,
        'sd_w': 0.05,
        'sd_s': 0.1,
    },
    'random': {
        'T': list(range(200, 1100, 100)),
        'K': list(range(1, 7)),
        'sd_v': 0.1,
        'sd_w': sqrt(0.001),
        'sd_s': 0.1,
    },
}


def setup_experiment(experiment_type, generate, **kwargs):
    cl_dict = dict()
    if experiment_type == 'case':
        file_path = os.path.join(DATA_PATH, experiment_type, 'cl.pkl')
        if generate:
            logger.info("Generating attack graph for 'case study' from .txt file.")
            cl = get_graph('graph.txt')  # Generate the graph from .txt file
            with open(file_path, 'wb') as f:
                pickle.dump(cl, f, pickle.HIGHEST_PROTOCOL)
        else:
            logger.info("Loading existing attack graph for 'case study'.")
            try:
                with open(file_path, 'rb') as f:
                    cl = pickle.load(f)
            except FileNotFoundError:
                raise FileNotFoundError(f"Graph file not found: {file_path}. Did you forget to use --generate?")
        cl.plot_attack_graph(name='case')
        cl.plot_shortest_path(name='case')
        cl_dict['case'] = cl
    elif experiment_type == 'random':
        net_type = [1, 2, 3]
        for net in net_type:
            file_path = os.path.join(DATA_PATH, experiment_type, f'cl-type{net}.pkl')
            if generate:
                logger.info(f"Generating new graph for 'random-type{net}'.")
                cl = RandomCyberLayer(
                    kwargs['no_states'], kwargs['no_sensors'], kwargs['no_controllers'], kwargs['t_lb'], kwargs['t_ub']
                )
                num_ends = 3 if net == 3 else (np.random.randint(2, 4) if net == 1 else 2)
                cl.gen_cyber_network(p=kwargs['p'], num_ends=num_ends)
                cl.add_target_grp(net=net)
                cl.plot_attack_graph(name=f'random-type{net}')
                cl.plot_shortest_path(name=f'random-type{net}')
                with open(file_path, 'wb') as f:
                    pickle.dump(cl, f, pickle.HIGHEST_PROTOCOL)
            else:
                logger.info(f"Loading existing graph for 'random-type{net}'.")
                try:
                    with open(file_path, 'rb') as f:
                        cl = pickle.load(f)
                except FileNotFoundError:
                    raise FileNotFoundError(f"Graph file not found: {file_path}. Did you forget to use --generate?")
            cl_dict[net] = cl
    else:
        raise ValueError(f"Unsupported experiment type: {experiment_type}")

    return cl_dict


def run_experiment(experiment_type, generate):
    
    config = EXPERIMENT_CONFIG[experiment_type]
    T, K = config['T'], config['K']
    sd_v, sd_w, sd_s = config['sd_v'], config['sd_w'], config['sd_s']

    kwargs = {
        'no_states': 12,
        'no_sensors': 3,
        'no_controllers': 3,
        'p': 0.5,
        't_lb': 1,
        't_ub': 50
    } if experiment_type == 'random' else {}

    cl_dict = setup_experiment(experiment_type, generate, **kwargs)
    
    for _type, cl in cl_dict.items():
        for t in T:
            for k in K:
                pathfile = f'{experiment_type}-type{_type}'
                logger.info(f"Solving optimization model: {pathfile}-T{t}-K{k} ...")
                cl.add_aux()
                m = Attacker(K=k, T=t, sd_v=sd_v, sd_w=sd_w, sd_s=sd_s, 
                             filename=pathfile, expr=experiment_type)
                m.G = cl.DAG
                m.S = cl.sensors
                m.C = cl.controllers
                m.build_model()
                m.solve()
                cl.remove_aux()
                if m.model.status not in [3, 4, 5]:
                    if _type in [1, 2, 3]:
                        out_path = os.path.join(OUT_PATH, experiment_type, f'type{_type}', f'T{t}-K{k}')
                    else:
                        out_path = os.path.join(OUT_PATH, experiment_type, f'T{t}-K{k}')
                    sol = get_vars(m)
                    save_results(sol, out_path)
                else:
                    logger.warning(f"Optimization failed for {_type} T{t}-K{k} with status {m.model.status}.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run analysis for case or random experiments.")
    parser.add_argument(
        '--experiment',
        choices=['case', 'random'],
        required=True,
        help="Specify which experiment to run: 'case' or 'random'."
    )
    parser.add_argument(
        '--generate',
        action='store_true',
        default=False,
        help="If set, generates new attack graphs for the experiment."
    )
    args = parser.parse_args()

    logger.info(f"Starting experiment: {args.experiment}, Generate: {args.generate}.")
    run_experiment(args.experiment, args.generate)

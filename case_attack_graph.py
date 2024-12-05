# -*- coding: utf-8 -*-
"""
Created on Wed Mar  1 09:58:06 2023

@author: naftabi
"""

import os
import pickle
import networkx as nx

from model.attack_graph import RandomCyberLayer

DATA_PATH = os.path.join(os.getcwd(), 'data', 'case')

def read_data(name):
    path = os.path.join(DATA_PATH, name)
    with open(path, 'r') as f:
        file = f.readlines()
        for line in file:
            if line.startswith('SENSORS'):
                sensors = line.split()[-1].split(',')
            if line.startswith('CONTROLLERS'):
                controllers = line.split()[-1].split(',')
            if line.startswith('INITIAL_ID'):
                init = int(line.split()[-1])
            if line.startswith('EDGE_EXPLOIT_SECTION'):
                e_lst = []
                for e in file[file.index(line)+1:]:
                    e_lst.append(e.split())
    return sensors, controllers, e_lst, init

def get_graph(name):
    sensors, controllers, edges, init = read_data(name)
    num_sensor, num_controller = len(sensors), len(controllers)
    edge_lst = []
    for u, v, t in edges:
        if u.isdigit() and v.isdigit():
            edge_lst.append((int(u), int(v), {'weight': int(t)}))
        else:
            if u.isdigit() and not v.isdigit():
                edge_lst.append((int(u), v, {'weight': int(t)}))
            elif not u.isdigit() and v.isdigit():
                edge_lst.append((u, int(v), {'weight': int(t)}))
            else:
                edge_lst.append((u, v, {'weight': int(t)}))
    DAG = nx.DiGraph(edge_lst)
    
    num_state = DAG.number_of_nodes() - num_sensor - num_controller
    cl_case = RandomCyberLayer(num_state=num_state, 
                               num_sensor=num_sensor, 
                               num_controller=num_controller,
                               t_lb=0,
                               t_ub=0)
    cl_case.DAG = DAG
    cl_case.init = init
    cl_case.ends = [5,6,7]
    cl_case.controllers = {'FV': 0, 'SV': 1, 'WV': 2}
    cl_case.sensors = {'P1':0, 'P2':1, 'GT': 2, 'L1': 3, 'L2': 4}
    cl_case.shortest_path_graph()
    return cl_case
    
if __name__ == '__main__':
    case_cl = get_graph('graph.txt')
    with open('./data/cl-case.pkl', 'wb') as f:
        pickle.dump(case_cl, f, pickle.HIGHEST_PROTOCOL)
            
                    
                
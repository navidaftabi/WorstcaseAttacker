# -*- coding: utf-8 -*-
"""
Created on Sat Jan 14 11:58:08 2023

@author: Navid
"""


import copy
import random
import networkx as nx
from random import sample
import matplotlib.pyplot as plt


def get_points(DG):
    initial_point = []
    end_points = []
    for n in DG.nodes():
        if DG.in_degree(n) == 0:
            initial_point.append(n)
        if DG.out_degree(n) == 0:
            end_points.append(n)
        
    return initial_point, end_points

def gnp_graph(N, p, seed):
    return nx.gnp_random_graph(n=N, p=p, directed=True, seed=seed)

class RandomCyberLayer:
    def __init__(self, 
                 num_state: int = 10,
                 num_sensor: int = 3,
                 num_controller: int = 3,
                 t_lb: int = 1,
                 t_ub: int = 50
                 ):
        
        self.num_state = num_state
        self.num_sensor = num_sensor
        self.num_controller = num_controller
        self.t_lb = t_lb
        self.t_ub = t_ub
        self.DAG = None
        self.SDAG = None
        self.init = None
        self.ends = None
        self.sensors = {f"S{s+1}":s for s in range(num_sensor)}
        self.controllers = {f"C{c+1}":c for c in range(num_controller)}
    
    def gen_cyber_network(self, p, num_ends):
        seed = 3425
        while True:
            G = gnp_graph(self.num_state + 1, p, seed)
            DAG = nx.DiGraph([(u,v,{'weight':random.randint(self.t_lb, self.t_ub)}) for (u,v) in G.edges() if u<v])
            init, ends = get_points(DAG)
            
            if len(init) == 1 and len(ends) == num_ends and nx.is_weakly_connected(DAG):
                self.init = init
                self.ends = ends
                break
            else:
                seed += 312

        no_edge = set(init) | set(range(1, round(self.num_state / 2)-1))
        safe_nodes = list(
            set(DAG.nodes()) - 
            no_edge - 
            set(ends)
            )
        for u,v,t in list(DAG.edges(data=True)):
            if u in no_edge and v in ends:
                DAG.remove_edge(u, v)
                new_u = sample(safe_nodes, 1)[0]
                if (v, new_u) not in DAG.edges() and new_u < v:
                    DAG.add_edge(new_u, v, weight=t['weight'])
        
        self.DAG = DAG
        return
    
    def add_target_grp(self, net):
        ends = copy.deepcopy(self.ends)
        s = list(self.sensors.keys())
        c = list(self.controllers.keys())
        target_edge = []
        if net == 3:
            assert len(self.ends) == 3, "Number of ends Must be 3 ..."
            while len(ends) > 0:
                e_s = random.sample(ends, 1)[-1]
                r_s = random.sample(s, 1)[-1]
                r_c = random.sample(c, 1)[-1]
                target_edge.append((e_s,r_s,{'weight':random.randint(self.t_lb, self.t_ub)}))
                target_edge.append((e_s,r_c,{'weight':random.randint(self.t_lb, self.t_ub)}))
                ends.remove(e_s)
                s.remove(r_s)
                c.remove(r_c)
        elif net == 1:
            for u in ends:
                for v in s:
                    target_edge.append( (u, v, {'weight':random.randint(self.t_lb, self.t_ub)}) )
                for v in c:
                    target_edge.append( (u, v, {'weight':random.randint(self.t_lb, self.t_ub)}) )
        else:
            assert len(self.ends) == 2, "Number of ends Must be 2 ..."
            e_s = random.sample(ends, 1)[-1]
            ends.remove(e_s)
            target_edge = [(e_s,v,{'weight':random.randint(self.t_lb, self.t_ub)}) for v in s]
            target_edge += [(ends[-1],v,{'weight':random.randint(self.t_lb, self.t_ub)}) for v in c]
        
        self.DAG.add_nodes_from(s + c)
        self.DAG.add_edges_from(target_edge)
        return
    
    def shortest_path_graph(self):
        _, targets = get_points(self.DAG)
        edges = []
        
        for tar in targets:
            length, path = nx.single_source_dijkstra(G=self.DAG, source=0, target=tar, weight='weight')
            path_edges = list(zip(path,path[1:]))
            for e in path_edges:
                if e not in edges:
                    edges.append(e)
                    
        self.SDAG = self.DAG.edge_subgraph(edges).copy()
        return
    
    def add_aux(self):
        targets = list(self.sensors.keys()) + list(self.controllers.keys()) 
        e = [(u, 'AUX', {'weight': 0}) for u in targets]
        self.DAG.add_node('AUX')
        self.DAG.add_edges_from(e)
        return
    
    def remove_aux(self):
        self.DAG.remove_node('AUX')
        return
    
    def plot_attack_graph(self, name):
        edge_labels = dict()
        for u, v, t in self.DAG.edges(data=True):
            edge_labels[(u, v)] = t['weight']
        
        nodes_set = set(self.DAG.nodes())
        _, targets = get_points(self.DAG)
        mid_node_set = nodes_set - set(self.init) - set(self.ends) - set(targets)
                
        pos = nx.shell_layout(self.DAG)

        plt.figure(figsize=(11,11))
        nx.draw_networkx_nodes(self.DAG, pos, nodelist=self.init, node_shape='^', node_color='tab:green', node_size=500)
        nx.draw_networkx_nodes(self.DAG, pos, nodelist=self.ends, node_shape='s', node_color='tab:red',alpha=0.9, node_size=500)
        nx.draw_networkx_nodes(self.DAG, pos, nodelist=list(mid_node_set), node_shape='s', node_color='tab:gray', node_size=500)
        nx.draw_networkx_nodes(self.DAG, pos, nodelist=targets, node_shape='h', node_color='tab:blue', alpha=0.9, node_size=500)
        nx.draw_networkx_labels(self.DAG, pos, font_color="whitesmoke")
        nx.draw_networkx_edges(self.DAG, pos)
        nx.draw_networkx_edge_labels(self.DAG, pos, edge_labels=edge_labels)
        plt.savefig(f'./img/{name}-attackgraph.pdf', format='pdf', dpi=1200, bbox_inches='tight')
        plt.show()
        
    def plot_shortest_path(self, name):
        edge_labels = dict()
        for e in self.DAG.edges(data=True):
            edge_labels[(e[0], e[1])] = e[2]['weight']
        
        nodes_set = set(self.DAG.nodes())
        _, targets = get_points(self.DAG)
        mid_node_set = nodes_set - set(self.init) - set(self.ends) - set(targets)
                
        pos = nx.shell_layout(self.DAG)
        pos_higher = {}
        for k, v in pos.items():
            pos_higher[k] = (v[0]-0.1, v[1]-0.1)
        
        red_edges = []
        length = dict()
        for tar in targets:
            length[tar], path = nx.single_source_dijkstra(G=self.DAG, source=0, target=tar, weight='weight')
            path_edges = list(zip(path,path[1:]))
            for e in path_edges:
                if e not in red_edges:
                    red_edges.append(e)
        
        edge_col = ['black' if not edge in red_edges else 'red' for edge in self.DAG.edges()]
        plt.figure(figsize=(11,11))
        nx.draw_networkx_nodes(self.DAG, pos, nodelist=self.init, node_shape='^', node_color='tab:green', node_size=500)
        nx.draw_networkx_nodes(self.DAG, pos, nodelist=self.ends, node_shape='s', node_color='tab:red',alpha=0.9, node_size=500)
        nx.draw_networkx_nodes(self.DAG, pos, nodelist=list(mid_node_set), node_shape='s', node_color='tab:gray', node_size=500)
        nx.draw_networkx_nodes(self.DAG, pos, nodelist=targets, node_shape='h', node_color='tab:blue', alpha=0.9, node_size=500)
        nx.draw_networkx_labels(self.DAG, pos, font_color="whitesmoke")
        nx.draw_networkx_labels(self.DAG, pos_higher, labels=length)
        nx.draw_networkx_edges(self.DAG, pos, edge_color= edge_col)
        nx.draw_networkx_edge_labels(self.DAG, pos, edge_labels=edge_labels)
        plt.savefig('./img/{}-shortestpath.pdf'.format(name), format='pdf', dpi=1200, bbox_inches='tight')
        plt.show()
        
        
            

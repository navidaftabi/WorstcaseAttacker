# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 15:20:43 2022

@author: naftabi
"""

import gurobipy as gp
from gurobipy import GRB, quicksum

from model.attackerbase import AttackerModel


class Attacker(AttackerModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.h = None
        self.f = None
        self.y = None
        
    def build_model(self):
        self.add_variables()
        self.add_constraints()
        self.set_objective()
        
        
    def add_variables(self):
        self.h = self.model.addVars(list(self.G.nodes()),
                                    lb=0, ub=GRB.INFINITY, 
                                    vtype=GRB.CONTINUOUS,
                                    name='h')
        self.h[0].lb = 0
        self.h[0].ub = 0
        
        edge_lst = gp.tuplelist(self.G.edges())
        self.y = self.model.addVars(edge_lst,
                                    vtype=GRB.BINARY,
                                    name='y')
        
        self.f = self.model.addVars(edge_lst,
                                    lb=0, ub=GRB.INFINITY,
                                    vtype=GRB.INTEGER,
                                    name='f')
        
        self.alpha = self.model.addVars(list(self.G.nodes()),
                                    vtype=GRB.BINARY,
                                    name='r')
        
        
    def set_objective(self):
        self.model.setObjective(
            self.h['AUX'], 
            GRB.MINIMIZE)
        return
        
         
    def add_constraints(self):
        for i in self.G.nodes():
            if i == 0:
                self.model.addConstr(
                    self.f.sum(i,'*') == self.K
                    )
            elif i == 'AUX':
                self.model.addConstr(
                    self.f.sum('*',i) == self.K
                    )
            else:
                self.model.addConstr(
                    self.f.sum(i,'*') - self.f.sum('*', i) == 0
                    )
        
        for i, j, t in self.G.edges(data=True):
            self.model.addConstr(
                self.h[j] >= 
                self.h[i] + 
                t['weight'] - 
                self.T * (1 - self.y[i, j])
                )
            
            self.model.addConstr(
                self.f[i,j] <= self.K * self.y[i,j]
                )
            
            self.model.addConstr(
                self.f[i,j] >= self.y[i,j]
                )
            
            
            self.model.addConstr(
                self.alpha[j] >= self.y[i,j]
                )
            
        self.model.addConstr(
            quicksum(self.alpha[j] for j in list(self.S.keys()) + list(self.C.keys())) == self.K
            )
        for j in list(self.G.nodes()):
            self.model.addConstr(
                self.alpha[j] <= self.y.sum('*', j)
                )
            
        return
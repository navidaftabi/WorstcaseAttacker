# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 15:20:43 2022

@author: naftabi
"""

import numpy as np
import gurobipy as gp
from gurobipy import GRB, quicksum

from model.attackerbase import AttackerModel


class Attacker(AttackerModel):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.a = None
        self.b = None
        
    def build_model(self):
        self.get_lb_ub()
        self.add_variables()
        self.add_constraints()
        self.set_objective()
        
        
    def add_variables(self):
        s = list(self.S.keys())
        c = list(self.C.keys())
        
        self.a = self.model.addVars(s, self.T,
                                    lb=-GRB.INFINITY,
                                    ub=GRB.INFINITY,
                                    vtype=GRB.CONTINUOUS,
                                    name='a')
        
        self.b = self.model.addVars(c, self.T,
                                   lb=-GRB.INFINITY,
                                   ub=GRB.INFINITY,
                                   vtype=GRB.CONTINUOUS,
                                   name='b')
        self.w = self.model.addVars(s, self.T,
                                    lb=0,
                                    ub=GRB.INFINITY,
                                    vtype=GRB.CONTINUOUS,
                                    name='w')
        
        for ss in s:
            for t in range(118):
                self.a[ss,t].lb = 0
                self.a[ss,t].ub = 0
        for cc in c:
            for t in range(118):
                self.b[cc,t].lb = 0
                self.b[cc,t].ub = 0
        
    def set_objective(self):
        S = list(self.S.keys())
        self.model.setObjective(
            quicksum(
                self.w[s,t]
                for s in S
                for t in range(self.T)
                ), 
            GRB.MINIMIZE)
        return
        
    def add_constraints(self):
        self.constraint_b()
        self.constraint_c()
        self.constraint_d()
        self.constraint_e()
        self.constraint_f()
    
    def constraint_b(self):
        S = list(self.S.keys())
        self.model.addConstrs(
            (
                self.a[s,t] >= self.lb_a 
                )
            for t in range(self.T)
            for s in S
            )
        
        self.model.addConstrs(
            (
                self.a[s,t] <= self.ub_a 
                )
            for t in range(self.T)
            for s in S
            )
        return
    
    def constraint_c(self):
        C = list(self.C.keys())
        self.model.addConstrs(
            (
                self.b[c,t] >= self.lb_b
                )
            for t in range(self.T)
            for c in C
            )
        
        self.model.addConstrs(
            (
                self.b[c,t] <= self.ub_b
                )
            for t in range(self.T)
            for c in C
            )
        return
    
    def constraint_d(self):
        C = list(self.C.keys())
        S = list(self.S.keys())
        EDB = self.E @ self.D @ self.B
        self.model.addConstrs(
            (
                quicksum(EDB[self.C[c],self.C[cc]] * self.b[cc,t-1] for cc in C) + 
                quicksum(self.E[self.C[c],self.S[s]] * self.a[s,t] for s in S) == 0
                )
            for c in C
            for t in range(1,self.T)
            )
        return
    
    def constraint_e(self):
        C = list(self.C.keys())
        S = list(self.S.keys())
        DB = self.D @ self.B
        self.model.addConstrs(
            (
                self.a[s,t] +
                quicksum(DB[self.S[s],self.C[c]] * self.b[c,t-1] for c in C)
                <= self.z_preception * self.sigma_z[self.S[s]]
                )
            for s in S
            for t in range(1,self.T)
            )
        
        self.model.addConstrs(
            (
                self.a[s,t] +
                quicksum(DB[self.S[s],self.C[c]] * self.b[c,t-1] for c in C)
                >= -self.z_preception * self.sigma_z[self.S[s]]
                )
            for s in S
            for t in range(1, self.T)
            )
        return
    
    def constraint_f(self):
        C = list(self.C.keys())
        S = list(self.S.keys())
        DB = self.D @ self.B
        self.model.addConstrs(
            (self.Zref[self.S[s],t] - self.a[s,t] -
            quicksum(DB[self.S[s],self.C[c]] * self.b[c,t-1] for c in C) <= self.w[s,t]
            )
            for s in S
            for t in range(1, self.T)
            )
        self.model.addConstrs(
            (self.Zref[self.S[s],t] - self.a[s,t] -
            quicksum(DB[self.S[s],self.C[c]] * self.b[c,t-1] for c in C) >= -self.w[s,t]
            )
            for s in S
            for t in range(1, self.T)
            )
        return
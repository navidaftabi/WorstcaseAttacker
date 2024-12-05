# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 15:20:43 2022

@author: naftabi
"""

from math import sqrt
import gurobipy as gp
from gurobipy import GRB, quicksum

from model.attackerbase import AttackerModel


class Attacker(AttackerModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.h = None
        self.f = None
        self.y = None
        self.alpha = None
        self.x = None
        self.u = None
        self.z = None
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
        m = list(self.M.keys())
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
        
        self.alpha = self.model.addVars(s + c, self.T,
                                        vtype=GRB.BINARY,
                                        name='alpha')
        
        self.x = self.model.addVars(m, self.T + 1,
                                    lb=-GRB.INFINITY,
                                    ub=GRB.INFINITY,
                                    vtype=GRB.CONTINUOUS,
                                    name='x')
        
        self.x['M1',0].lb = 0
        self.x['M1',0].ub = 0
        self.x['M2',0].lb = 0
        self.x['M2',0].ub = 0
        self.x['M3',0].lb = 0
        self.x['M3',0].ub = 0
        
        self.u = self.model.addVars(c, self.T,
                                    lb=-GRB.INFINITY,
                                    ub=GRB.INFINITY,
                                    vtype=GRB.CONTINUOUS,
                                    name='u')
        
        self.z = self.model.addVars(s, self.T,
                                    lb=-GRB.INFINITY,
                                    ub=GRB.INFINITY,
                                    vtype=GRB.CONTINUOUS,
                                    name='z')
        
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
        
    def set_objective(self):
        self.model.setObjective(
            quicksum(
                (1 / (self.sd_s * sqrt(tau))) *
                (
                    self.lamb - (self.kappa * tau) - 
                    quicksum(self.gamma[v] * self.x[k,t] for k,v in self.M.items() for t in range(1, tau+1))
                    )
                for tau in range(1, self.T+1) 
                ) , 
            GRB.MINIMIZE)
        return
        
    def add_constraints(self):
        self.constraint_cyber()
        self.constraint_connect()
        self.constraint_physical()
        
         
    def constraint_cyber(self):
        # constraints (b), (c)
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
            
        # constraints (d)
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
            
    def constraint_connect(self):
        S = list(self.S.keys())
        C = list(self.C.keys())
        # # constraint (e)
        self.model.addConstrs(
            (
                self.alpha[j,t] <= self.y.sum('*',j)
                )
            for j in S + C
            for t in range(self.T)
            )
        
        # constraint (f)
        self.model.addConstrs(
            (
                self.h[j] - 1 <= 
                quicksum((1 - self.alpha[j,t]) for t in range(self.T))
                )
            for j in S + C
            )
        
        # constraint (g)
        self.model.addConstrs(
            (
                self.alpha[j,t-1] <= self.alpha[j,t]
                ) 
            for j in S + C
            for t in range(1, self.T) 
            )
    
    
    def constraint_physical(self):
        M = list(self.M.keys())
        C = list(self.C.keys())
        S = list(self.S.keys())
        
        # constraint (h)
        self.model.addConstrs(
            (
                self.x[m,t+1] ==
                quicksum(self.A[self.M[m],self.M[j]] * self.x[j,t] for j in M) + 
                quicksum(self.B[self.M[m],self.C[j]] * (self.u[j,t] + self.b[j,t]) for j in C) 
             )
            for t in range(self.T)
            for m in M
            )
        
        # constraint (i)
        self.model.addConstrs(
            (
                self.z[s,t] ==
                quicksum(self.D[self.S[s],self.M[m]] * self.x[m,t] for m in M) +
                self.a[s,t]
             )
            for t in range(self.T)
            for s in S
            )
        
        # constraint (j)
        self.model.addConstrs(
            (
                self.u[c,t] ==
                quicksum(self.E[self.C[c],self.S[s]] * self.z[s,t] for s in S)
             )
            for t in range(self.T)
            for c in C
            )
        
        # constraint (k)
        self.model.addConstrs(
            (
                self.z[s,t] <= self.z_preception * self.sigma_z[self.S[s]]
                )
            for t in range(self.T)
            for s in S
            )
        
        self.model.addConstrs(
            (
                self.z[s,t] >= -self.z_preception * self.sigma_z[self.S[s]]
                )
            for t in range(self.T)
            for s in S
            )
        
        # constraint (l)
        self.model.addConstrs(
            (
                self.a[i,t] >= self.lb_a * self.alpha[i,t]
                )
            for t in range(self.T)
            for i in S
            )
        
        self.model.addConstrs(
            (
                self.a[i,t] <= self.ub_a * self.alpha[i,t]
                )
            for t in range(self.T)
            for i in S
            )
        
        # constraint (m)
        self.model.addConstrs(
            (
                self.b[i,t] >= self.lb_b * self.alpha[i,t]
                )
            for t in range(self.T)
            for i in C
            )
        
        self.model.addConstrs(
            (
                self.b[i,t] <= self.ub_b * self.alpha[i,t]
                )
            for t in range(self.T)
            for i in C
            )

        
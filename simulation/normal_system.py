# -*- coding: utf-8 -*-
"""
Created on Thu Nov 17 17:45:10 2022

@author: naftabi
"""

import os
import re
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

PATH = os.getcwd()
DATA_PATH = os.path.join(PATH, 'data')
LOG_PATH = os.path.join(PATH, 'logs')

def _read_matrix(param_name, experiment):
    filepath = os.path.join(DATA_PATH, experiment, f'{param_name}.txt')
    return np.matrix(_read_file(filepath))

def _read_vector(param_name, experiment):
    filepath = os.path.join(DATA_PATH, experiment, f'{param_name}.txt')
    return np.array(_read_file(filepath)[0])

def _read_scalar(param_name, experiment):
    filepath = os.path.join(DATA_PATH, experiment, f'{param_name}.txt')
    return _read_file(filepath)[0][0]

def _read_file(filepath):
    with open(filepath, 'r') as file:
        return [
            [float(value) for value in re.sub(r"[\t\n ]", ' ', line).split()]
            for line in file.readlines()
        ]

class System:
    def __init__(self,
                 no_states: int,
                 no_controllers: int,
                 no_sensors: int,
                 inits: list,
                 expr: str):
        
        self.states = no_states
        self.controllers = no_controllers
        self.sensors = no_sensors
        self.inits = np.transpose(np.matrix(inits))
        
        self.s = None
        self.x = None
        self.u = None
        self.z = None
        
        self.sa = None
        self.xa = None
        self.ua = None
        self.za = None
        
        self.v = None
        self.w = None
        
        self.T = None
        self.sd_v = None
        self.sd_w = None
        
        self.A = _read_matrix('A', expr)
        self.B = _read_matrix('B', expr)
        self.D = _read_matrix('D', expr)
        self.E = self.compute_E() 
        self.gamma = _read_vector('gamma', expr)
        self.kappa = sqrt(2) * _read_scalar('kappa', expr)
        
        assert self.A.shape[0] == self.A.shape[1] == self.states, "A is not singular or no states does not match the shape of A"
        
        assert self.B.shape[0] == self.A.shape[0] == self.D.shape[1], "A, B, and D shapes does not match"
        
        assert self.B.shape[1] == self.controllers, "B does not match no of controllers"
        
        assert self.D.shape[0] == self.sensors, "D does not match no of sensors"
        
    def compute_E(self):
        term1 = np.linalg.inv(self.B.T @ self.B) @ self.B.T
        term2 = np.linalg.inv(self.D.T @ self.D) @ self.D.T
        E = -1 * (term1 @ self.A @ term2)
        return E
        
    def noises(self, sd_v, sd_w):
        v = np.matrix(np.random.normal(loc=0.0, scale=sd_v, size=(self.states, 1)))
        w = np.matrix(np.random.normal(loc=0.0, scale=sd_w, size=(self.sensors, 1)))
        return v, w
    
    def simulate(self, sd_v, sd_w, T):
        self.T = T
        self.sd_v = sd_v
        self.sd_w = sd_w
        
        x = np.matrix(np.zeros((self.states, T+1)))
        u = np.matrix(np.zeros((self.controllers, T)))
        z = np.matrix(np.zeros((self.sensors, T)))
        V = np.matrix(np.zeros((self.states, T)))
        W = np.matrix(np.zeros((self.sensors, T)))
        
        for t in range(T):
            v, w = self.noises(sd_v, sd_w)
            V[:,t], W[:,t] = v, w
            z[:,t] = (self.D @ x[:,t]) + w
            u[:,t] = self.E @ z[:,t]
            x[:,t+1] = (self.A @ x[:,t])  + (self.B @ u[:,t]) + v
            
        self.x = x
        self.u = u
        self.z = z
        self.v = V
        self.w = W
        return
    
    def simulateAttack(self, a, b):
        x = np.matrix(np.zeros_like(self.x))
        u = np.matrix(np.zeros_like(self.u))
        z = np.matrix(np.zeros_like(self.z))
        
        for t in range(self.T):
            v, w = self.v[:,t], self.w[:,t]
            z[:,t] = (self.D @ x[:,t]) + a[:,t] + w
            u[:,t] = self.E @ z[:,t]
            x[:,t+1] = (self.A @ x[:,t]) + (self.B @ (u[:,t] + b[:,t])) + v
            
        self.xa = x 
        self.ua = u
        self.za = z
        return
    
    def degradation(self, sd_s):
        s = np.array(np.zeros(self.T + 1))
        
        for t in range(self.T):
            e = np.random.normal(loc=0.0, scale=sd_s, size=1)
            theta = self.kappa + (self.gamma @ self.x[:,t]) 
            s[t + 1] = s[t] + theta + e
            
        self.s = s
        return
    
    def degradationAttack(self, sd_s):
        s = np.array(np.zeros(self.T + 1))
        
        for t in range(self.T):
            e = np.random.normal(loc=0.0, scale=sd_s, size=1)
            s[t + 1] = s[t] + self.kappa + (self.gamma @ self.xa[:,t]) + e
            
        self.sa = s
        return
        
            
        
    
        

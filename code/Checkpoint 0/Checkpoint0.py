# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 13:26:46 2023

@author: nolo7
"""
import numpy as np

A = np.matrix('1 2 3;4 5 6;2 0 1')
B = np.matrix('6;8;5')

x = np.linalg.solve(A, B)
print(x)


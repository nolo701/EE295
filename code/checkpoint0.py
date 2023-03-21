import sympy as sym
from sympy import *
from sympy import Subs
import numpy as np
from scipy import sparse

from IPython.display import display

# Used as a reference/idea of sympy on stack overflow:
# https://stackoverflow.com/questions/49553006/compute-the-jacobian-matrix-in-python

def Jacobian(vars, funcArray, solution):
    numFunctions = len(funcArray)
    numVars = len(vars)
    J_eval = np.zeros([numFunctions,numVars])
    J = sym.Matrix.zeros(numFunctions,numVars)
    values = {}
    #pprint(vars)
    #pprint(solution)
    for var, v in enumerate(vars):
        values[v] = solution[var].item()
    # Evalutate the taylor series at this point
    for i, fi in enumerate(funcArray):
        for j, s in enumerate(vars):
            J[i,j] = sym.diff(fi, s)
            #pprint(J[i,j])
            J_eval[i,j] = sym.Subs.subs(J[i,j],values)
            #print(J_eval[i,j])
    # evaluate the function value for this solution
    F_k = np.array([sym.Subs.subs(funcArray[0],values), sym.Subs.subs(funcArray[1],values), sym.Subs.subs(funcArray[2],values)])
    #print("F(x)")
    #print(F_k)
    #print("F'(x)")
    #print(J_eval)
    return F_k,J_eval

def newtonRaphson(problemMatrix, variables, solution):
    # Take the given problem matrix and calculate the jacobian at
    # the current solution
    F_k,jac = Jacobian(variables, problemMatrix, solution)
    #x_k = np.array([sym.Subs.subs(problemMatrix[1],)])
    #print("A:")
    A = sparse.csr_matrix(jac)
    #print(A)
    b = -F_k
    #print("b:")
    #print(b)

    solution_a = np.array(sparse.linalg.spsolve(A,b.astype(np.float64)))
    #print("x:")
    iterate = solution_a.reshape(-1,1)
    #display(solution_a)

    solution_b = iterate + solution

    return solution_b,iterate


x,y,z = sym.symbols('x,y,z')
f1 = x**2 + y**2 - z**2 -1
f2 = x**3 - y**3 + z**3 -2
f3 = sym.sin(x) + sym.cos(y) + sym.tan(z) - 3
funcArray =[f1,f2,f3]
print("HERE")
pprint(funcArray[1])
print("HERE2")
#display(funcArray.evalf([.1,.1,.1]))
vars = np.array([x,y,z])
f1_dx = diff(f1,x)
sym.pprint(f1)
sym.pprint(f1_dx)
display(vars)

# From the run_solver
# the settings for the solver
settings = {
    "Tolerance": 1E-05,
    "Max Iters": 1000,
    "Limiting":  False
}

# make a command to find the solution to the system of nonlinear
# equations using newton raphson
solution = np.array([4, 2, .1])
solution = solution.reshape(-1,1)

# This is an initial guess
problem = funcArray

variables = vars
#pprint(solution)
step=1

iterations = 0
while((np.linalg.norm(dx)>settings["Tolerance"]) and (iterations<settings["Max Iters"])):
    print("Iteration: ")
    print(iterations)
    solution,step = newtonRaphson(problem, variables, solution)
    
    pprint(solution)
    display(np.linalg.norm(step))
    iterations += 1



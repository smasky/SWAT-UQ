import sys
# sys.path.append("../..")
sys.path.append(".")

import numpy as np

from swatuq import SWAT_UQ

projectPath = "E:/DJBasin/TxtInOutFSB"  # your SWAT Project Path
workPath = "E:/DJ_FSB" # your Work Path
exeName = "swat.exe" # the name of swat.exe you want to run
paraFileName = "para_pres_0119.par" # the parameter file you prepared
evalFileName = "ob_0119.evl" # the evaluation file you prepared

problem = SWAT_UQ(projectPath = projectPath, workPath = workPath, 
                  swatExeName = exeName, paraFileName = paraFileName, 
                  evalFileName = evalFileName, verboseFlag = True, maxThreads = 12,
                  numParallel = 1, optType = 'max')

# from UQPyL.optimization.soea import PSO

# pso = PSO(nPop = 50, maxFEs = 5000, verboseFlag = True, saveFlag = True, verboseFreq=1)

# pso.run(problem = problem)


from UQPyL.analysis import Sobol, FAST
from UQPyL.doe import LHS

lhs = LHS()

X = lhs.sample(problem, nt = 5000)
import time
a = time.time()
Y = problem.objFunc(X[0:10,:])
b = time.time()
print(b-a)
# fast = FAST()

# X = fast.sample(problem, N = 256)

# Y = problem.objFunc(X)

# res = fast.analyze(problem, X, Y)


# a = 1
# sobol = Sobol()

# X = sobol.sample(problem, N = 256, secondOrder = False)

# Y = problem.objFunc(X)

# res = sobol.analyze(problem, X, Y, secondOrder = False)

# a = 1
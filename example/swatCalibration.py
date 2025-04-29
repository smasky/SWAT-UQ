import sys
sys.path.append(".")

import numpy as np
from swatuq import SWAT_UQ
from UQPyL.optimization.single_objective import GA

nInput = 25
nOutput = 3

projectPath = "D:\\BMPs\\TxtInOut"
exeName = "swat.exe"
workPath = "D:\\DJ_FSB"
paraFileName = "para_bmp.par"
evalFileName = "obj_bmp.evl"
specialFileName = "special_paras1.txt"


problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName, specialFileName = specialFileName,
                    workPath = workPath, paraFileName = paraFileName, evalFileName = evalFileName,
                    verboseFlag = True, numParallel = 1)

X = np.array([1, 50.0, 1, 5, 50, 1, 50.0, 1, 5, 50, 1, 50.0, 1, 5, 50, 1, 50.0, 1, 5, 50, 1, 50.0, 1, 5, 50])

res = problem.apply_parameters(X)

a = 1
# from UQPyL.DoE import LHS

# lhs = LHS()

# X = lhs.sample(nt = 100, problem = problem)

# X = np.array([-0.0781, 0.3761, 0.6200, 1.1167, 8.1841, 175.5632, 0.8667, 11.9633, 0.9307, 8.6665, 31.4787, 0.6447])

# y = problem.objFunc(X.reshape(1, -1))

# print(y)

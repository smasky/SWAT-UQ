import sys
sys.path.append(".")

import numpy as np
from swatuq import SWAT_UQ
from UQPyL.optimization.single_objective import GA

nInput = 24
nOutput = 1

projectPath = "D:\\DJBasin\\TxtInOutFSB\\TxtInOutFSB"
exeName = "swat.exe"
workPath = "D:\\DJ_FSB"
paraFileName = "para_op.par"
evalFileName = "obj_op.evl"

problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName,
                    workPath = workPath, paraFileName = paraFileName, evalFileName = evalFileName,
                    verboseFlag = True, numParallel = 1)

X = np.array([-0.0781, 0.3761, 0.6200, 1.1167, 8.1841, 175.5632, 0.8667, 11.9633, 0.9307, 8.6665, 31.4787, 0.6447])

res = problem.extract_series(X, seriesFile = "series.evl")

a = 1
# from UQPyL.DoE import LHS

# lhs = LHS()

# X = lhs.sample(nt = 100, problem = problem)

# X = np.array([-0.0781, 0.3761, 0.6200, 1.1167, 8.1841, 175.5632, 0.8667, 11.9633, 0.9307, 8.6665, 31.4787, 0.6447])

# y = problem.objFunc(X.reshape(1, -1))

# print(y)

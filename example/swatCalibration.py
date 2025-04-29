import sys
sys.path.append(".")

import numpy as np
from swatuq import SWAT_UQ
from UQPyL.optimization.single_objective import GA

nInput = 25
nOutput = 3

projectPath = "E:\\BMPs\\TxtInOut"
exeName = "swat.exe"
workPath = "E:\\DJ_FSB"
paraFileName = "para_bmp.par"
evalFileName = "obj_bmp.evl"
specialFileName = "special_paras1.txt"

TN_Base = 1.558e7 # base
TP_Base = 1.154e6 # base

Basins = [1, 13, 14, 20, 31] #BasinID for BMPs


def userObjFunc(attr):
  
  objs = np.zeros(3) # Three objectives

  x = attr["x"]

  objs[0] = (TN_Base - attr["objs"][1])/TN_Base # Compute obj_1

  objs[1] = (TP_Base - attr["objs"][2])/TP_Base # Compute obj_2

  # Compute obj_3

  HRUInfos = attr["HRUInfos"]

  cost = 0

  for i, ID in enumerate(Basins):

    # Compute the area of AGRL of SUB
    areas = np.sum(HRUInfos.loc[
    (HRUInfos.SUB_ID == ID) & (HRUInfos.Luse == "AGRL"),
    "Area"].tolist())

    filter_I = x[5*i]
    filter_ratio = x[5*i+1]

    graw_I = x[5*i+2]
    graw_W = x[5*i+3]
    graw_L = x[5*i+4]

    cost_filter = areas * filter_ratio * filter_I * 420
    cost_graw = graw_W * graw_L * graw_I * 600
    cost += cost_filter + cost_graw

  objs[2] = cost

  return objs


problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName, specialFileName = specialFileName,
                    workPath = workPath, paraFileName = paraFileName, evalFileName = evalFileName,
                    verboseFlag = True, numParallel = 1, userObjFunc = userObjFunc, nOutput = 3, optType = ["max", "max", "min"])

X = np.array([1, 50.0, 1, 5, 50, 1, 50.0, 1, 5, 50, 1, 50.0, 1, 5, 50, 1, 50.0, 1, 5, 50, 1, 50.0, 1, 5, 50])

y = problem.objFunc(X.reshape(1, -1))

# from UQPyL.DoE import LHS

# lhs = LHS()

# X = lhs.sample(nt = 100, problem = problem)

# X = np.array([-0.0781, 0.3761, 0.6200, 1.1167, 8.1841, 175.5632, 0.8667, 11.9633, 0.9307, 8.6665, 31.4787, 0.6447])

# y = problem.objFunc(X.reshape(1, -1))

# print(y)

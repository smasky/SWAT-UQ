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

TN_Base = 3.314e7 # base
TP_Base = 3.717e6 # base

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
    (HRUInfos.SUB_ID == ID),
    "Area"].tolist())

    filter_I = x[5*i]
    filter_ratio = x[5*i+1]

    graw_I = x[5*i+2]
    graw_W = x[5*i+3]
    graw_L = x[5*i+4]

    cost_filter = areas / filter_ratio * filter_I * 420
    cost_graw = graw_W * graw_L * graw_I * 600
    cost += cost_filter + cost_graw

  objs[2] = cost

  return objs


problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName, specialFileName = specialFileName,
                    workPath = workPath, paraFileName = paraFileName, evalFileName = evalFileName,
                    verboseFlag = True, numParallel = 1, userObjFunc = userObjFunc, nOutput = 3, optType = ["max", "max", "min"])

# X = np.array([1, 300.0, 1, 30, 50, 1, 300.0, 1, 30, 50, 1, 300.0, 1, 30, 50, 0, 300.0, 1, 30, 50, 1, 300.0, 1, 30, 50])
# X = np.array([1, 300,1, 0.05819589, 10, 1, 28.45296891 ,0, 0.164965636, 147.0389025, 0, 88.66996205, 0, 0.116025497, 14.15498887, 1, 192.8721855, 0, 0.270599526, 158.8032125, 1, 14.58824361, 0, 0.057089199, 19.68750278])

# y = problem.objFunc(X.reshape(1, -1))


a = 0
# from UQPyL.DoE import LHS

# lhs = LHS()

# X = lhs.sample(nt = 100, problem = problem)

# X = np.array([-0.0781, 0.3761, 0.6200, 1.1167, 8.1841, 175.5632, 0.8667, 11.9633, 0.9307, 8.6665, 31.4787, 0.6447])

# y = problem.objFunc(X.reshape(1, -1))

# print(y)

import sys
sys.path.append(".")


from swatuq import SWAT_UQ
from UQPyL.optimization.single_objective import GA

nInput = 24
nOutput = 1

projectPath = "D:\\djBasin\\TxtInOutFSB\\TxtInOutFSB"
exeName = "swat.exe"
workPath = "D:\\DJ_FSB"
paraFileName = "para_sa.par"
evalFileName = "obj_sa.evl"

problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName,
                    workPath = workPath, paraFileName = paraFileName, evalFileName = evalFileName,
                    verboseFlag = True, numParallel = 1)

from UQPyL.DoE import LHS

lhs = LHS()

X = lhs.sample(nt = 100, problem = problem)

problem.objFunc(X[0:1, :])
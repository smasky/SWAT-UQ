
from swatuq import SWAT_UQ
from UQPyL.optimization.single_objective import GA

nInput = 13
nOutput = 1

projectPath = "D:\\djBasin\\TxtInOutFSB\\TxtInOutFSB"
exeName = "swat.exe"
workPath = "D:\\DJ_FSB"
paraFileName = "paras_infos.txt"
evalFileName = "ob1.txt"

problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName,
                    workPath = workPath, paraFileName = paraFileName, evalFileName = evalFileName,
                    verboseFlag = True, numParallel = 2)

from UQPyL.DoE import LHS

lhs = LHS()

X = lhs.sample(nt = 100, problem = problem)

problem.evaluate(X)


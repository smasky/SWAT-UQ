from swatuq import SWAT_UQ

projectPath = "E:\\projectPath"
workPath = "E:\\workPath"
exeName = "swat.exe"

paraFileName = "para_op.par"
evalFileName = "obj_op.evl"

problem = SWAT_UQ(projectPath = projectPath, workPath = workPath, swatExeName = exeName,
                   paraFileName = paraFileName, evalFileName = evalFileName,
                   verboseFlag = True, numParallel = 20, optType = 'max')

from UQPyL.optimization import PSO

pso = PSO(nPop = 50, maxFEs = 30000, verboseFlag = True, saveFlag = True)

pso.run(problem = problem)
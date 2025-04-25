from swatuq import SWAT_UQ

projectPath = "E:\\projectPath"
exeName = "swat.exe"

workPath = "E:\\workPath"
parFile = "para_sa.par"
evalFile = "obj_sa.evl"

problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName,
                    workPath = workPath, paraFileName = parFile, evalFileName = evalFile,
                    verboseFlag = True, numParallel = 20, optType = 'max')

from UQPyL.sensibility import FAST

fast = FAST(saveFlag = True)

X = fast.sample(problem, 256)

Y = problem.evaluate(X)

res =fast.analyze(problem, X, Y)

print(res)
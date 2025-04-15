import sys
sys.path.insert(0, '.')

from swatuq import SWAT_UQ


projectPath = "E:\\example_runoff\\TxtInOutFSB"
exeName = "swat.exe"

workPath = "E:\\example_runoff"
parFile = "scenario1.par"
evalFile = "scenario1.obj"

problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName,
                    workPath = workPath, paraFileName = parFile, evalFileName = evalFile,
                    verboseFlag = True, numParallel = 10, optType = 'max')

from UQPyL.sensibility import FAST

fast = FAST()

X = fast.sample(problem, 100)

Y = problem.evaluate(X)

res =fast.analyze(problem, X, Y)

print(res)

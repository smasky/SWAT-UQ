import sys
sys.path.insert(0, '.')

from swatuq import SWAT_UQ

projectPath = "D:\\example_runoff\\TxtInOutFSB"
exeName = "swat.exe"

workPath = "D:\\example_runoff"
parFile = "scenario1.par"
evalFile = "scenario1.obj"

problem = SWAT_UQ(projectPath = projectPath, swatExeName = exeName,
                    workPath = workPath, paraFileName = parFile, evalFileName = evalFile,
                    verboseFlag = True, numParallel = 10, optType = 'max')

from UQPyL.optimization import GA

ga = GA(nPop = 50, verboseFreq = 1)

ga.run(problem = problem)
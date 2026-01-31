import sys
sys.path.append(".")

from swatuq import SWAT_UQ
import numpy as np

from UQPyL.utility.metrics import nse

projectPath = "D:/YS_swat/TxtInOutABH"  # your SWAT Project Path
workPath = "D:/YS_swat" # your Work Path
exeName = "swat.exe" # the name of swat.exe you want to run
paraFileName = "paras.par" # the parameter file you prepared
evalFileName = "eval.evl" # the evaluation file you prepared

problem = SWAT_UQ(
   projectPath = projectPath, # set projectPath
   workPath = workPath, # set workPath
   swatExeName = exeName, # set swatExeName
   paraFileName = paraFileName, # set paraFileName
   evalFileName = evalFileName, # set evalFileName
   nInput = 21, # number of parameters, if not indicated, this would be determined by parameter file
   nOutput = 1, # number of objectives, if not indicated, this would be determined by evaluation file # number of constraints, if not indicated, this would be determined by evaluation file
   verboseFlag = True, # enable verboseFlag to check if setup is configured properly.
   numParallel = 1, # set the number of parallels
   maxThreads = 20,
   optType = 'max'
)

# from UQPyL.optimization import GA

# ga = GA(maxFEs = 1000, verboseFlag=True, saveFlag=True, verboseFreq=1)

# ga.run(problem = problem)
from time import time
from UQPyL.DoE import LHS

lhs = LHS()
X = lhs.sample(nt = 10, problem = problem)


# X = np.array([1.32, 3.135, 0.001, 7.255, 0.02, 0.539, 30, 0.151, 872.016, 0.892])
a = time()
Y = problem.apply_parameters(X[0:1,:].reshape(1, -1))
b =time()

print(b-a)



# X = np.array([-0.022, 0.201, 6.797, 0.788, 0.021, 0.201, 449.971, 0.166, 355.059, 0.083])

# Y = problem.apply_parameters(X)


# Y = problem.extract_series(X)

# Y = problem.objFunc(X[None, :])
# a=1


# from UQPyL.DoE import LHS

# lhs = LHS()

# X = lhs.sample(500, problem = problem)

# Y = problem.evaluate(X)

# np.savetxt("X_test.txt", X)
# np.savetxt("Y_test.txt", Y["objs"])

# from UQPyL.sensibility import FAST, Morris


# morris = Morris(verboseFlag = True)
# X = morris.sample(problem, 250)
# Y = problem.evaluate(X)

# np.savetxt("X.txt", X)
# np.savetxt("Y.txt", Y["objs"])

# morris.analyze(problem, X, Y["objs"])


# fast = FAST(verboseFlag = True)
# X = fast.sample(problem, 256)

# Y = problem.evaluate(X)

# np.savetxt("X.txt", X)
# np.savetxt("Y.txt", Y["objs"])

# fast.analyze(problem, X, Y["objs"])
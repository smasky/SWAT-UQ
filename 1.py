from UQPyL.problems.single_objective import Sphere
from UQPyL.optimization.single_objective import GA
from UQPyL.problems.multi_objective import ZDT1
from UQPyL.optimization.multi_objective import NSGAII

def getOptimum():
    
    return None

sphere=Sphere()



zdt=ZDT1()
zdt.getOptimum=getOptimum 
nsga=NSGAII(verbose=True, saveFlag=True)

nsga.run(problem=zdt)
# ga=GA(saveFlag=True)


# ga.run(sphere)
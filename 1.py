from UQPyL.problems.single_objective import Sphere
from UQPyL.optimization.single_objective import GA

sphere=Sphere()

ga=GA(saveFlag=True)

ga.run(sphere)
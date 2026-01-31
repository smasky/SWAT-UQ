import sys
sys.path.append("../..")

import numpy as np
from swatuq import SWAT_UQ

projectPath = "E:/DJBasin/TxtInOutFSB"
workPath = "E:/DJ_FSB"
exeName = "swat.exe"
paraFileName = "para_ob_0119.par"
evalFileName = "ob_0119.evl"

problem = SWAT_UQ(
    projectPath=projectPath, workPath=workPath,
    swatExeName=exeName, paraFileName=paraFileName,
    evalFileName=evalFileName, verboseFlag=True,
    maxThreads=12, numParallel=10, optType='max'   # NSE一般 max
)

from sufi2 import SUFI2Config, run_sufi2

cfg = SUFI2Config(
    n_samples=1000,        # 每轮跑多少组
    max_iter=50,          # 迭代轮数
    behavioral_frac=0.2,  # 前20%作为行为解
    expand_ratio=0.05,    # 轻微扩张
    range_tol_rel=1e-3,
    seed=1234,
    verbose=True
)

res = run_sufi2(problem, cfg)

print("\n==== SUFI-2 RESULT ====")
print("best_y (NSE) =", res["best_y"])
print("best_x =", res["best_x"])
print("final LB =", problem.LB)
print("final UB =", problem.UB)

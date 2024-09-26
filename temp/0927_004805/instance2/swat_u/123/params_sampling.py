import sys
import numpy as np
from SALib.sample import morris 
from SALib.sample import saltelli
from SALib.sample import fast_sampler

path = sys.argv[1]
# path = "G:\\SWAT\\t3\\"
# 读取参数文件
with open(path+'paramsSum.txt', 'r') as f:
  param_list = f.readlines()

csvHeader = []
num_vars = len(param_list)
names = []
bounds = []
for i in range(0, len(param_list)):
  line = param_list[i].rstrip('\n')
  param = line.split(":")
  names.append(param[0])
  nums = param[1].split(",")
  bounds.append([float(nums[0]),float(nums[1])])
  csvHeader.append('"'+nums[2]+param[0]+'"')

params = {
 'num_vars': num_vars,
 'names': names,
 'groups': None,
 'bounds': bounds
}


# 读取模拟方法
with open(path+'simSetting.txt', 'r') as f:
  sim_list = f.readlines()

method = ""
times = 0
for i in range(0, len(sim_list)):
  line = sim_list[i].rstrip('\n')
  sim = line.split(":")
  if sim[0] == "SAmethod":
    method = sim[1]
  elif sim[0] == "simTimes":
    times = int(sim[1])


# 运行对应的采样方法
X = None
if method == "morris": 
  # 得到的矩阵为：(G+1)*N行D列。 G为组数，若没组，则为参数数量；D为参数数量。
  X = morris.sample(params, times) 
elif method == "sobol": 
  # 如果calc_Second_Order为FALSE，则生成的矩阵有(D+2)*N行，其中D是参数的数量。 
  # 如果calc_Second_Order为True，则生成的矩阵有(2D+2)*N行。
  X = saltelli.sample(params, times)    
elif method == "fast":
  # 得到的矩阵包含D*N行和D列，其中D是参数的数量。
  X = fast_sampler.sample(params, times)

np.save(path+"params_sampling.npy",X)
np.savetxt(path+"params_sampling.csv", X, fmt='%.04f', delimiter=',', header=",".join(csvHeader), comments="")

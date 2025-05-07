# 示例 1：东江流域的径流校准

---

## 背景介绍

东江流域是广东省内重要的淡水水源地，面积超过 35,000 平方公里，为广州、深圳、香港等多个城市提供供水。

本研究选取东江流域的两个子流域——丰水坝（Fengshuba）与新丰江（XinFengJiang）作为径流校准的案例。

本例主要展示丰水坝子流域的校准过程，其汇水面积为 5,150 平方公里，年均降雨量为 1,581 毫米。为了帮助用户熟悉 SWAT-UQ，我们提供了新丰江子流域的校准作为额外练习。

<figure align="center">
  <img src="../assets/images/background_dongjiang.jpg" alt="UQPyL Overview" width="600"/>
</figure>

---

## SWAT 模型构建

在构建丰水坝子流域的 SWAT 模型时，所用数据包括：

- **DEM（数字高程模型）** - 使用 ASTER GDEM，空间分辨率为 30 米  
- **土地利用数据** - 来自中国资源与环境科学数据中心（RESDC）  
- **土壤数据** - 来自世界统一土壤数据库（HWSD）  
- **气象数据** - 使用CMADS（中国气象驱动数据集）  
- **观测数据** - 来自《水文年鉴》的径流数据（2008年1月1日至2017年12月31日）

模型运行时间段如下：

- **预热期**：2008年01月01日至2011年12月31日  
- **校准期**：2012年01月01日至2016年12月31日  
- **验证期**：2017年01月01日至2017年12月31日  

<figure align="center">
  <img src="../assets/images/example_runoff.svg" width="1000"/>
</figure>

💡 **提示：** [点击此链接下载项目文件](https://github.com/smasky/SWAT-UQ/raw/main/example/example1/project_FSB.zip)

---

## 问题定义

问题定义指的是将实际问题抽象成数学和代码可处理的问题。

本例目标是校准 SWAT 模型，使其输出结果尽可能接近观测数据。首先需选定用于评估模型表现的指标。在水文学中，常见的指标包括 NSE、R²、KGE、RMSE、PCC 等。这里我们采用 **NSE** 作为评估指标。

因此，实际问题可以抽象为如下形式：

<figure align="center">
  <img src="../assets/images/example_problem.svg" width="350"/>
</figure>

其中：

- $x$：SWAT 模型中待确定的参数  
- $NSE(\cdot)$：NSE 指标函数  
- $sim$：模型仿真结果  
- $ob$：观测数据  
- $lb$ 与 $ub$：参数的上下限

基于该问题，将使用SWAT-UQ实例化该问题与对其求解。

---

## 敏感性分析

首先，对东江流域的SWAT模型进行敏感性分析。参考SWAT手册和[Liu 等人 (2017)](https://www.sciencedirect.com/science/article/pii/S0022169417305851)的研究，选取了以下参数：

| ID | Abbreviation| Where | Assign Type | Range |
|----|-------|-------|-------------|-------|
| P1 |CN2|MGT| Relative | [-0.4, 0.2] |
| P2 | GW_DELAY| GW | Value | [30, 450] |
| P3 | ALPHA_BF | GW | Value | [0.0, 1.0] |
| P4 | GWQMN | GW | Value | [0.0, 500.0] |
| P5 | GW_REVAP | GW | Value | [0.02, 0.20] |
| P6 | RCHRG_DP | GW | Value | [0.0, 1.0] |
| P7 | SOL_AWC | SOL | Relative | [0.5, 1.5] |
| P8 | SOL_K | SOL | Relative | [0.5, 15.0] |
| P9 | SOL_ALB | SOL | Relative | [0.01, 5.00] |
| P10 | CH_N2 | RTE | Value | [-0.01, 0.30] |
| P11 | CH_K2 | RTE | Value | [-0.01, 500.0] |
| P12 | ALPHA_BNK | RTE | Value | [0.05, 1.00] |
| P13 | TLAPS | SUB | Value | [-10.0, 10.0] |
| P14 | SLSUBSSN | HRU | Relative | [0.05, 25.0] |
| P15 | HRU_SLP | HRU | Relative | [0.50, 1.50] |
| P16 | OV_N | HRU | Relative | [0.10, 15.00] |
| P17 | CANMX | HRU | Value | [0.0, 100.0] |
| P18 | ESCO | HRU | Value | [0.01, 1.00] |
| P19 | EPCO | HRU | Value | [0.01, 1.00] |
| P20 | SFTMP | BSN | Value | [-5.0, 5.0] |
| P21 | SMTMP | BSN | Value | [-5.0, 5.0] |
| P22 | SMFMX | BSN | Value | [0.0, 20.0] |
| P23 | SMFMN | BSN | Value | [0.0, 20.0] |
| P24 | TIMP | BSN | Value | [0.01, 1.00] |

基于[快速教程](./swat_uq_dev.md)介绍。
第一步，准备参数文件（par文件）。

文件名：`paras_sa.par`

```txt
Name Mode Type Min_Max Scope
CN2 r f -0.4_0.2 all
GW_DELAY v f 30_450 all
ALPHA_BF v f 0.0_1.0 all
GWQMN v f 0.0_500.0 all
GW_REVAP v f 0.02_0.20 all
RCHRG_DP v f 0.0_1.0 all
SOL_AWC r f 0.5_1.5 all
SOL_K r f 0.5_15.0 all
SOL_ALB r f 0.01_5.00 all
CH_N2 v f -0.01_0.30 all
CH_K2 v f  -0.01_500.0 all
ALPHA_BNK v f 0.05_1.00 all
TLAPS v f -10.0_10.0 all
SLSUBSSN r f 0.05_25.0 all
HRU_SLP r f 0.50_1.50 all
OV_N r f 0.10_15.00 all
CANMX v f 0.0_100.0 all
ESCO v f 0.01_1.00 all
EPCO v f 0.01_1.00 all
SFTMP v f -5.0_5.0 all
SMTMP v f -5.0_5.0 all
SMFMX v f 0.0_20.0 all
SMFMN v f 0.0_20.0 all
TIMP v f 0.01_1.00 all
```

第二步，准备函数评估文件（evl文件）：

文件名：`obj_sa.evl`

```txt
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_2 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_1 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )

1	2012 1 1	38.6
2	2012 1 2	16.2
3	2012 1 3	24.5
4	2012 1 4	26.9
5	2012 1 5	56.2
6	2012 1 6	82.1
7	2012 1 7	32.8
8	2012 1 8	20.5
9	2012 1 9	32.3
10	2012 1 10	28.9
11	2012 1 11	36.5
...
...
...
1821	2016 12 25	94.8
1822	2016 12 26	106
1823	2016 12 27	135
1824	2016 12 28	87.4
1825	2016 12 29	81.5
1826	2016 12 30	94.9
1827	2016 12 31	89.9
```

💡 **提示：** [点击此链接下载相关文件](https://github.com/smasky/SWAT-UQ/raw/main/example/example1/sa.zip)

基于evl文件，SWAT-UQ将从`output.rch`中提取2012至2016年Reach23的数据，并使用NSE指标评估模型性能。

第三步，基于Python环境进行敏感性分析：

```python
from swat_uq import SWAT_UQ
# 初始化 SWAT-UQ 问题
problem = SWAT_UQ(...)

from UQPyL.sensibility import FAST
fast = FAST()
X = fast.sample(problem, N = 512)
Y = problem.objFunc(X)
res = fast.analyze(X, Y)
print(res)
```

最终的FAST敏感性分析如下图所示：

<figure align="center">
  <img src="../assets/images/fast.svg" width="1000"/>
</figure>

选取灵敏度前10个参数用于后续优化：CN2、ALPHA_BNK、SOL_K、SLSUBSSN、ESCO、HRU_SLP、OV_N、TLAPS、SOL_ALB、CH_K2。

---

## 参数优化

基于敏感性分析结果，创建新的参数文件：

文件名：`para_op.par`

```
Name Mode Type Min_Max Scope
CN2 r f -0.4_0.2 all
SOL_K r f 0.5_15.0 all
SOL_ALB r f 0.01_5.00 all
CH_K2 v f  -0.01_500.0 all
ALPHA_BNK v f 0.05_1.00 all
TLAPS v f -10.0_10.0 all
SLSUBSSN r f 0.05_25.0 all
HRU_SLP r f 0.50_1.50 all
OV_N r f 0.10_15.00 all
ESCO v f 0.01_1.00 all
```

函数评估文件可与敏感性分析共用，但推荐另存为 `obj_op.evl`。

💡 **提示：** [点击此链接下载相关文件](https://github.com/smasky/SWAT-UQ/raw/main/example/example1/op.zip)

编程示例：

```python
from swat_uq import SWAT_UQ

projectPath = "E://swatProjectPath" # Use your SWAT project path
workPath = "E://workPath" # Use your work path
exeName = "swat2012.exe" # The exe name you want execute

#Blew two files should be created in the workPath
paraFileName = "paras_sa.par" # the parameter file you prepared
evalFileName = "obj_sa.evl" # the evaluation file you prepared

problem = SWAT_UQ(
   projectPath = projectPath, # set projectPath
   workPath = workPath, # set workPath
   swatExeName = exeName # set swatExeName
   paraFileName = paraFileName, # set paraFileName
   evalFileName = evalFileName, # set evalFileName
   verboseFlag = True, # enable verboseFlag to check if setup is configured properly.
   numParallel = 10 # set the parallel numbers of SWAT
)

# The SWAT-related Problem is completed. 

from UQPyL.optimization import PSO

pso = PSO(nPop = 50, maxFEs = 30000, verboseFlag = True, saveFlag = True)

pso.run(problem = problem)
```

优化结果如下：

<figure align="center">
  <img src="../assets/images/PSO.svg" width="1000"/>
</figure>

最优参数（NSE≈0.88）如下表：

| CN2 | SOL_K | SOL_ALB | CH_K2 | ALPHA_BNK | TLAPS | SLSUBSSN | HRU_SLP | OV_N | ESCO |
|-----|--------|----------|--------|------------|--------|------------|-----------|--------|-------|
| -0.236 | 14.278 | 0.325 | 46.604 | 1.000 | -5.532 | 1.611 | 0.515 | 3.162 | 0.010 |

---

## 参数验证

接下来，基于最优参数进行模型验证。

准备验证期的函数评估文件 `val_op.evl`（使用2017年的实测数据）

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_2 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_1 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )

1 2017 1 1 74.4
2 2017 1 2 99.4
3 2017 1 3 77.4
...
...
365 2017 12 31 19.1
```

编程示例：

```python

X = np.array([...])  # 最优参数值
res = problem.validate_parameters(X, valFile="val_op.evl")
print(res["objs"])

```

---

## 数据后处理

除了敏感性分析与优化，SWAT-UQ还支持从模型输出中提取时间序列数据：

构建新的evl文件：

文件名：`series.evl`
```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1 : Weight of series combination
RCH_23  : ID of subbasin to be included in the objective function
COL_2 : Column ID of variables in output.rch
FUNC_10     : Type of objective function (e.g., 1: NSE, 2: RMSE. 3:PCC, 4:Pbias, 5:KGE)
2012/1/1 to 2016/12/31 : Period for data extraction
```

```python

X = np.array([...])
attr = problem.extract_series(X, seriesFile="series.evl")

```

此处，`attr`是一个python字典，其API如下：

```
attr -> Python Dict

关键字说明：

- x : 输入决策变量，类型为 np.1darray（一维数组）
- objs : 当前输入决策对应的目标函数值，是一个 Python 字典，可通过 `attr['objs'][objID]` 访问，对应在 *.evl 文件中定义的 objID
- cons : 与 objs 类似，用于表示约束函数值
- objSeries : 一个 Python 字典，记录 *.evl 文件中关于目标函数的数据序列，可通过 `attr['objSeries'][objID][serID]` 访问
- conSeries : 与 objSeries 类似，用于记录关于约束函数的数据序列
```

关于此例：

```
simData = attr['objSeries'][1][1]['sim']
obData = attr['objSeries'][1][1]['obs']

```

## 导入最优解

```python
X = np.array([...])
problem.apply_parameters(X, replace=False)  # 不改动原始项目，只改动工作目录的Origin文件夹
# 或：
problem.apply_parameters(X, replace=True)  # 覆盖原始项目（不推荐）
```

至此，模型校准工作完成。

---

## 额外练习

另外，本项目提供了新丰江子流域的完整练习项目：

👉 [点击此处下载项目文件](https://github.com/smasky/SWAT-UQ/raw/main/example/example1/project_XFJ.zip)

观测数据在 `observed.txt` 文件中。

如有任何问题，欢迎联系我们！
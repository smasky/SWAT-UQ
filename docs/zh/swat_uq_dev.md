# SWAT-UQ-DEV教程

---

## 概述

**SWAT-UQ-DEV**是一个基于**Python语言环境**并于PyPi平台托管的扩展包（Package）。该扩展包定义了名为`SWAT_UQ`的 Python类，继承自UQPyL的`Problem`类。因此，用户实例化`SWAT_UQ`类后，即可直接调用UQPyL的所有方法和算法，完成各项任务。

此外`SWAT_UQ`类还封装了一系列功能函数，包括写入自定义参数、读取模拟模拟结果等，简化了问题构建->分析->求解的流程，提升效率。

因此，SWAT-UQ-DEV特别适合希望自定义工作流（集成UQPyL或其他Python扩展包）的用户。


## 功能特点

1. **并行执行：** 无论是项目文件读写，还是**SWAT模型的模拟仿真**，均支持并行处理。（经过一台40核服务器上的案例测试，Dev版本能稳定并行运行80个SWAT实例以上，并实现了一个小时内完成两万次模型模拟）。

2. **文件控制：** 用户只在前期准备若干UTF-8格式的txt文件，即可完成如流量或水质等模型校准任务时。

3. **流程简化：** 基于[UQPyL](https://github.com/smasky/UQPyL)的支持，用户可轻松执行完整的建模流程，包括：敏感性分析（Sensitivity Analysis）->参数优化（Optimization）->最优参数反代（Back-substitution）


## 安装方式

Python版本：3.6 - 3.12  

操作系统：Windows 或者 Linux

**推荐安装方式（使用 PyPi 或 Conda）：**

```bash
pip install -U swatuq
```

```bash
conda install swatuq --upgrade
```

## 快速入门

本节将提供SWAT-UQ-DEV的详细指南，帮助用户解决基于SWAT模型的水文问题。

首先，需要实例化`SWAT-UQ`类。该类实质上继承自UQPyL中的`Problem`类。该类将使用户可随意调用UQPyL的所有方法和算法（参考[UQPyL Project](https://github.com/smasky/UQPyL)）。

### 概述

具体步骤如下：

1. 准备**SWAT项目文件夹**（简称SWAT Project Folder）。

2. 另外创建独立的**工作文件夹（Work Folder）**，用于存放控制文件和并行运行生成的临时文件。

3. 在Work Folder中，创建参数文件（UTF-8编码）。该文件存储分析或优化的参数的关键信息。

4. 在Work Folder中，创建评估文件（UTF-8编码），该文件存储构造目标函数或约束函数的关键信息。

5. 基于Python环境编程解决问题。

### 参数文件

示例：

   ```
   Name Type Mode Min_Max Scope
   CN2 r f -0.4_0.2 all
   GW_DELAY v f 30.0_450.0 all
   ...
   ```

第一行始终用于显示提示信息，请勿移除。

除首行外，每一行均应包含下述完整的字段信息：`Name`、`Mode`、`Type`、`Min_Max` 和 `Scope`。

**Name（参数名）：** 可为`.gw`、`.hru`、`.mgt`、`.sol`、`.rte`、`.sub`、`.sep`、`.swq`等文件中出现的任何参数名。参数名原则上应与SWAT项目文件中的参数名一致。针对`*.sol`文件的参数，可针对特定土层修改，例如：

```
SOL_K(2) r f 0.5_15.0 all    # 仅修改第二层
SOL_K(3) r f 0.5_15.0 all    # 仅修改第三层
SOL_K r f 0.5_15.0 all       # 修改所有层
```

如果有些HRU的土壤层数不足3层或者2层，则默认不对该HRU修改。

**Mode（赋值模式）：** 使用`r`、`v`、`a`等单字符定义项目文件中的参数数值。（参考SWAT-CUP软件的用法）

   - `r`：相对赋值 -> 新值 = 原值 × (1+val)
   - `v`：绝对赋值 -> 直接用新值替换
   - `a`：加法赋值 -> 新值 = 原值 + val  

**Type（变量类型）：** `i` 表示整数，`f` 表示浮点数，`d` 表示离散型。

**Min_Max（取值范围）：** 最小值与最大值，用 `_` 分隔。对于离散变量则使用`_`串联所有可能的取值。

**Scope（作用范围）：**

  - 默认设置为 `all`：参数在全局范围修改。

  - 或者可以指定特定的 **流域 ID（SUB ID）** 或 **子流域 ID（SUB ID）+ 土地利用单元 ID（HRU ID）**，例如：

```
CN2 r f -0.4_0.2 all # 默认范围
CN2 r f -0.4_0.2 3(1,2,3,4,5,6,7,8,9) 4(1,2,3,4) 5 # 指定范围
```

格式说明：

- `SUB ID`：作用于指定子流域内的所有 HRU
- `SUB ID(HRU ID1, HRU ID2, ...)`：作用于指定子流域中的特定 HRU
- 多个子流域用空格或制表符分隔  

### 评估文件

对于创建评估文件，具体要求如下：

💡 **注意：** 也推荐使用 `.evl` 扩展名以与 GUI 版本保持一致。

**示例：**

文件名： `eval.evl`

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_2 : Variable of Column, within *.rch, *.sub, *.hru.
FUNC_1 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min, 10 - None)

1 2012_1 2.1
2 2012_2 3.2
3 2012_3 3.5
4 2012_4 6.7
5 2012_5 14.55
6 2012_6 21.54
...
12 2012_12 22.44
```

评估文件可包含多个序列（series），每个序列可对应不同位置、变量或时间。

每个序列应包含两部分：a.Head Section；b. Data Section

**Head Section：**

下述标签`ID` 或 `NUM`需用实际数字替换。

- **SER_ID：** 每个序列的唯一标识。
- **OBJ_ID 或 CON_ID：** `OBJ`表示目标函数，`CON`表示约束函数。`ID`为唯一标识。

💡 **注意：** SWAT-UQ-DEV 支持多个序列共享同一`OBJ ID` 或 `CON ID`，`SER_ID`应是唯一的。

- **WGT_NUM：** `NUM`为该序列在同一`OBJ ID` 或 `CON ID`组合时的线性权重。
- **RCH_ID / SUB_ID / HRU_ID：** 指定要从`output.rch`、`output.sub`或`output.hru`文件中提取数据。ID为RCH、SUB、HRU的对应位置标识。
- **COL_NUM：** 指定从对应输出文件的第几列提取数据（可参考下表）。
- **FUNC_NUM：** 定义目标函数类型：1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min, 10 - None (only for extract)

**有效的COL_NUM 值（不同输出文件对应列号）：**

| 文件名      | 有效值 |
|-------------|--------|
| output.rch  | 1-FLOW_IN, 2-FLOW_OUT, 3-EVAP, 4-TLOSS, 5-SED_IN, 6-SED_OUT, 8-ORGN_IN, 9-ORGN_OUT, ... 38-BACTP_OUT, 39-BACTLP_OUT, 43-TOT_N, 44-TOT_P |
| output.sub  | 1-PRECIP, 2-SNOMELT, 3-PET, 4-ET, 5-SW, 6-PERC, 7-SURQ, 8-GW_Q, 9-WYLD, 10-SYLD, 11-ORGN, 12-ORGP, 13-NSURQ, 14-SOLP, 15-SEDP |
| output.hru  | 1-PRECIP, 2-SNOFALL, 3-SNOMELT, 4-IRR, 5-PET, 6-ET, 7-SW_INIT, 8-SW_END, 9-PERA, 10-GW_RCHG, 11-DA_RCHC, 12-REVAP, ... 49-NUP, 50-PUP, ... 67-BACTP, 68-BACTLP |

💡 **注意：** 这些编号取自SWAT手册；也可以直接打开output文件手动数列号以确定对应变量。

 **Data Section**

Data Section结构应为 `NUM`、`YEAR`、`MONTH`、`DAY`、`DATA`。其中：

- **NUM:** 序号，用于数据完整性检查，是否缺漏
- **YEAR:** 年份，
- **MONTH:** 月份，
- **DAY:** 日,
- **DATA:** 数据值（整数或浮点数）。

如果SWAT项目的`file.cio`文件中`IPRINT`为0，则同时读取YEAR、MONTH、DAY；若为1，则只读取YEAR、MONTH，DAY的位置请默认写1。

示例:

```
1 2012 1 1 2.1
2 2012 1 2 3.2
3 2012 1 3 3.5
4 2012 1 4 6.7
5 2012 1 5 14.55
6 2012 1 6 21.54
...
12 2012 1 12 22.44
```

某些情况下，目标函数（Objective Function）不依赖于观测数据，仅需通过从模型输出文件中提取的数据来计算。对此，SWAT-UQ还提供更简便的方法：

示例：

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_6 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_1 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )
2012/01/01 to 2018/12/31 : Period for data extraction
```

基于此，2012/01/01至2018/12/31的数据会被提取出来。


### 编程示例

下述展示了基于Python语言环境如何定义并运行一个SWAT-UQ定义的问题：

```python

# First import SWAT_UQ class
from swatuq import SWAT_UQ

# Second define requirement variables:
projectPath = "E://swatProjectPath"  # your SWAT Project Path
workPath = "E://workPath" # your Work Path
exeName = "swat2012.exe" # the name of swat.exe you want to run
paraFileName = "paras.par" # the parameter file you prepared
evalFileName = "eval.obj" # the evaluation file you prepared

problem = SWAT_UQ(
   projectPath = projectPath, # set projectPath
   workPath = workPath, # set workPath
   swatExeName = exeName # set swatExeName
   paraFileName = paraFileName, # set paraFileName
   evalFileName = evalFileName, # set evalFileName
   verboseFlag = True, # enable verboseFlag to check if setup is configured properly.
   numParallel = 2 # set the number of parallels
)

# The SWAT-related Problem is completed. You can enjoy all methods and algorithms of UQPyL.

#For example:
from UQPyL.optimization.single_objective import GA

ga = GA()
ga.run(problem = problem)
```

💡 **提示：** 更多关于 UQPyL 的用法详见 [UQPyL 使用文档](https://uqpyl.readthedocs.io/en/latest/)


## 高级操作

### 载入最优参数

通过以下代码将最优参数应用到原始项目文件夹中，或只作用于工作目录：

```python

X = np.array([...]) # 输入变量，X should be a list or a NumPy 1D or 2D array
problem.apply_parameter(X, replace=False) # 应用于工作路径下的Origin文件夹，不修改原始项目
problem.apply_parameter(X, replace=True) # 直接写入原始SWAT项目
```

### 提取模拟结果

SWAT-UQ支持从output文件提取任意时间内的模拟数据

类似于评估文件的格式，准备UTF8格式的序列文件：

文件名：`series.evl`

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1 : Weight of series combination
RCH_23  : ID of subbasin to be included in the objective function
COL_2 : Column ID of variables in output.rch
FUNC_10 : Type of objective function
2012/1/1 to 2016/12/31 : Period for data extraction
```

格式和编写规则同评估文件,Python环境编程示例如下：

```Python

X = np.array([...]) # 输入变量，np.1darray

attr = problem.extract_series(X, seriesFile="series.evl")

```

`extract_series`函数返回的变量`attr`是一个python字典，其API如下：


```
attr -> Python Dict

关键字说明：

- x : 输入决策变量，类型为 np.1darray（一维数组）
- objs : 当前输入决策对应的目标函数值，是一个 Python 字典，可通过 `attr['objs'][objID]` 访问，对应在 *.evl 文件中定义的 objID
- cons : 与 objs 类似，用于表示约束函数值
- objSeries : 一个 Python 字典，记录 *.evl 文件中关于目标函数的数据序列，可通过 `dataS = attr['objSeries'][objID][serID]` 访问，其中dataS['sim']表示模拟数据，dataS['obs']表示观测数据
- conSeries : 与 objSeries 类似，用于记录关于约束函数的数据序列
```

因此，使用如下方法获得（2012/01/01-2016/12/31）模拟数据：

```Python

simData = attr['objSeries'][1][1]['sim'] # 关键词 'objSeries' 表示目标序列，非约束序列，
# 关键词 第一个1表示objID, 第二个1表示serID
# 关键词 'sim' 表示模拟数据，非'obs'观测数据

```

### 验证最优参数

基于验证期观测数据对模型验证所得优化结果，是构建高精度 SWAT 模型的关键步骤。对此，SWAT-UQ-DEV内置了`validate_parameters`函数。

首先，准备UTF8格式的验证文件，导入验证期数据，格式和规则同评估文件：

文件名：`val_op.evl`

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

```

`validate_parameters`函数返回的`res`是Python字典形式的变量，包含两个固定关键词：`objs` 和 `cons`，代表目标值和约束值。
对于本例，想获取的是目标值：

```Python

objs = res['objs']

```

### 自定义评估函数

在某些应用场景中（例如 BMPs 优化），**目标函数或约束函数的构建**并不能仅依赖评估文件直接完成。不过，SWAT-UQ可以首先通过评估文件提取模拟结果中的关键数据，进而为用户自定义的目标函数`userObjFunc`或约束函数`userConFunc`提供支持。

这两个函数有一个共同的接口特征：**都接收一个名为`attr`的参数**。

该参数`attr`的本质结构与`extract_series`函数的返回结果一致，都是一个 **Python 字典对象**，其关键词（key）完全相同，并额外包含以下字段：

```
- HRUInfos：一个 Pandas 数据表（DataFrame），用于记录 HRU（汇流单元）的相关信息，包含以下列：
  ["HRU_ID", "SUB_ID", "HRU_Local_ID", "Slope_Low", "Slope_High", "Luse", "Area"]
```

因此`attr`字典汇集了模拟数据、观测数据以及流域空间信息，为用户在`userObjFunc`和`userConFunc`中灵活构造目标函数或约束函数提供了完整的数据基础。具体自定义目标函数与约束函数的案例请参考[工程管理优化](./best_management_practices.md)
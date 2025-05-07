# SWAT-UQ-DEV 模块

---

## DEV 版本概述

**SWAT-UQ-DEV**是一个专为**Python脚本环境**设计的软件包。该模块定义了一个名为`SWAT_UQ`的 Python类，继承自UQPyL的`Problem`类。实例化`SWAT_UQ`类后，用户即可直接调用UQPyL的所有方法和算法。

此外`SWAT_UQ`还封装了一系列内置函数，包括自定义参数写入、模拟结果读取等，旨在简化构建与求解实际问题（如模型校准、最佳管理实践等）的流程，提升解决问题的效率。

总体而言，SWAT-UQ-DEV特别适合希望自定义工作流程、集成UQPyL或其他Python软件包的用户。

---

## 主要特性

1. **并行执行：** 无论是对项目文件的数据读写，还是**SWAT模型的模拟仿真**，均支持并行处理。  
   🎉：在一台 40 核服务器上的基准测试表明，该代码版本可稳定同时运行80个SWAT实例（2万次模拟时间缩短至1小时）。

2. **文件控制：** 完成如流量或水质等模型校准任务时，用户只需准备若干 `.txt` 文件，即可完成问题的定义。

3. **流程简化：** 借助[UQPyL](https://github.com/smasky/UQPyL)的支持，用户可轻松执行完整的建模流程，包括：敏感性分析（Sensitivity Analysis）->参数优化（Optimization）->最优参数反代（Back-substitution）

---

## 安装方式

Python版本：3.6 - 3.12  
系统：Windows、Linux

**推荐安装方式（使用 PyPi 或 Conda）：**

```bash
pip install -U swatuq
```

```bash
conda install swatuq --upgrade
```

---

## 快速入门

本节将提供逐步指南，帮助你通过SWAT-UQ-DEV解决基于SWAT模型的建模问题。

要开始使用，首先需要实例化 `SWAT-UQ` 类。该类继承自 UQPyL 中的 `Problem` 类。这将使您能够访问 UQPyL 中提供的所有方法和算法（参见 [UQPyL Project](https://github.com/smasky/UQPyL)）。

### 准备工作

在使用前需要进行一些准备工作：

1. 准备**SWAT项目文件夹**（以下简称 SWAT Project Folder）。

2. 随后创建独立的**工作文件夹（Work Folder）**，用于存放控制文件和并行运行时生成的临时文件。

3. 在 Work Folder 中，创建一个名为 `paras.par` 的参数文件，需为UTF-8编码。该文件会显示分析或优化的参数的详细信息，示例如下：

💡 **注意：** 文件名并没有强制要求，但推荐使用`.par`扩展名以保持与GUI版本一致。文件中所有元素必须使用空格或制表符分隔。

   ```
   Name Type Mode Min_Max Scope
   CN2 r f -0.4_0.2 all
   GW_DELAY v f 30.0_450.0 all
   ...
   ```
第一行应保留，作为用户提示。
参数文件每一行需提供 `Name`、`Mode`、`Type`、`Min_Max` 和 `Scope`：

**Name（参数名）：** 可为 `.gw`、`.hru`、`.mgt`、`.sol`、`.rte`、`.sub`、`.sep`、`.swq` 文件中出现的任何参数名。要求该名称与 SWAT 项目文件中的参数名**完全一致**（支持多达 308 个参数）。对于 `*.sol` 文件中的参数，还可以针对特定土层修改值，例如：

```
SOL_K(2) r f 0.5_15.0 all    # 仅修改第二层
SOL_K(3) r f 0.5_15.0 all    # 仅修改第三层
SOL_K r f 0.5_15.0 all       # 修改所有层
```

如果有些HRU的土壤层数不足3层或者2层，默认不作任何修改。

**Mode（赋值模式）：** 用一个字符表示赋值模式，如 `r`、`v`、`a`：

   - `r`：相对赋值 -> 新值 = 原值 × (1+val)
   - `v`：绝对赋值 -> 直接用新值替换
   - `a`：加法赋值 -> 新值 = 原值 + val  

**Type（变量类型）：** `i` 表示整数，`f` 表示浮点数，`d` 表示离散型。

**Min_Max（取值范围）：** 最小值与最大值，用 `_` 分隔。对于离散变量则使用`_`组合所有可能的值。

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


4.在工作文件夹中创建一个 **评价文件**（编码为 UTF-8），用于基于观测数据构造目标函数或约束函数。

**文件名：** `eval.evl`

💡 **注意：** 也推荐使用 `.evl` 扩展名以与 GUI 版本保持一致。

示例：

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_2 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_1 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )

1 2012_1 2.1
2 2012_2 3.2
3 2012_3 3.5
4 2012_4 6.7
5 2012_5 14.55
6 2012_6 21.54
...
12 2012_12 22.44
```

**evl文件**可以包含多个序列（series），每个序列可对应不同位置、输出变量或时间段。

每个序列包含两个部分：a.头部分（Head Section）；b. 数据部分（Data Section）

**头部分（Head Section）：**

下述标签 `ID` 或 `NUM` 需用实际数字替换。

- **SER_ID：** 每个数据序列的唯一标识。
- **OBJ_ID 或 CON_ID：** `OBJ` 表示目标函数，`CON` 表示约束函数。`ID` 为唯一标识。

  💡 **注意：** SWAT-UQ-DEV 支持多个序列共享同一 `OBJ ID` 或 `CON ID`。

- **WGT_NUM：** `NUM` 为该序列在组合时的线性权重。
- **RCH_ID / SUB_ID / HRU_ID：** 指定要从 `output.rch`、`output.sub` 或 `output.hru` 文件中提取数据。ID为位置标识。
- **COL_NUM：** 指定从输出文件的第几列提取数据（可参考下表）。
- **FUNC_NUM：** 定义目标函数类型：1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min

**有效的 COL_NUM 值（不同输出文件对应列号）：**

| 文件名      | 有效值 |
|-------------|--------|
| output.rch  | 1-FLOW_IN, 2-FLOW_OUT, 3-EVAP, 4-TLOSS, 5-SED_IN, 6-SED_OUT, 8-ORGN_IN, 9-ORGN_OUT, ... 38-BACTP_OUT, 39-BACTLP_OUT, 43-TOT_N, 44-TOT_P |
| output.sub  | 1-PRECIP, 2-SNOMELT, 3-PET, 4-ET, 5-SW, 6-PERC, 7-SURQ, 8-GW_Q, 9-WYLD, 10-SYLD, 11-ORGN, 12-ORGP, 13-NSURQ, 14-SOLP, 15-SEDP |
| output.hru  | 1-PRECIP, 2-SNOFALL, 3-SNOMELT, 4-IRR, 5-PET, 6-ET, 7-SW_INIT, 8-SW_END, 9-PERA, 10-GW_RCHG, 11-DA_RCHC, 12-REVAP, ... 49-NUP, 50-PUP, ... 67-BACTP, 68-BACTLP |

💡 **注意：** 这些编号取自 SWAT 手册。也可以直接打开输出文件手动数列号以确定对应变量。

 **数据部分（Data Section）：**

数据部分的结构应为 `NUM`、`YEAR`、`MONTH`、`DAY`、`DATA`。其中：

- **NUM:** 用于数据完整性检查，在SWAT-UQ-DEV中不会用到,
- **YEAR:** 年份，
- **MONTH:** 月份，
- **DAY:** 日,
- **DATA:** 数据值（整数或浮点数）。

如果SWAT 项目中`file.cio`的`IPRINT`为0，则同时读取YEAR、Month、Day；若为1，则只读取YEAR、Month，Day的位置请默认写1。

示例
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

在某些情况下，目标函数（Objective Function）可以不依赖观测数据，仅通过从模型输出文件中提取数据来进行计算。

SWAT-UQ还提供了更简便的方法：

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

因此，2012/01/01至2018/12/31的数据会被提取出来。

---

### 编程示例

以下展示了如何使用Python语言定义并运行一个基于SWAT-UQ的问题：

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

---

### 应用最优参数

你可以通过以下代码将最优参数应用到原始项目文件夹中，或只作用于工作目录：

```python
# X should be a list or a NumPy 1D or 2D array
problem.apply_parameter(X, replace=False) # 应用于工作路径下的Origin文件夹，不修改原始项目
problem.apply_parameter(X, replace=True) # 直接写入原始SWAT项目
```
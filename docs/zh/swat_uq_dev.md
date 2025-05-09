# SWAT-UQ-DEV教程

---

## 概述

**SWAT-UQ-DEV**是一个基于**Python语言环境**并于PyPi平台托管的扩展包（Package）。该扩展包定义了名为`SWAT_UQ`的 Python类，继承自UQPyL的`Problem`类。因此，用户实例化`SWAT_UQ`类后，即可直接调用UQPyL的所有方法和算法，帮助完成各种任务。

此外`SWAT_UQ`类还封装了一系列功能函数，包括写入自定义参数、读取模型模拟结果等，简化“问题构建->分析->求解”的流程，提升解决问题效率。

因此，SWAT-UQ-DEV特别适合希望自定义工作流（集成UQPyL或其他Python扩展包）的用户。


## 功能特点

1. **并行执行：** 无论是项目文件读写，还是**SWAT模型的模拟仿真**，均支持并行处理。（经过一台40核服务器上的压力测试，SWAT-UQ-Dev并行运行80个SWAT模拟实例以上，实现一小时内完成两万次模拟）。

2. **文件控制：** 用户只在前期准备若干UTF-8格式的文本文件，即可轻易完成如径流或水质等关于SWAT模型的校准任务。

3. **流程简化：** 基于[UQPyL](https://github.com/smasky/UQPyL)的支持，用户可轻松完成全部建模流程：敏感性分析->参数优化->最优参数载入


## 安装方式

Python版本：3.6 - 3.12  

操作系统：Windows 或者 Linux

**推荐使用pip或conda**

```bash
pip install -U swatuq
```

```bash
conda install swatuq --upgrade
```

## 快速入门

本节将提供SWAT-UQ-DEV的详细指南，帮助用户解决各类基于SWAT模型的水文问题。SWAT-UQ-DEV的设计核心是通过实例化`SWAT-UQ`类，来串联SWAT模型与UQPyL。因此，`SWAT-UQ`类实质上继承自UQPyL中的`Problem`类。该类的实例化将使用户可简单快速调用UQPyL的所有方法（参考[UQPyL Project](https://github.com/smasky/UQPyL)）。

### 概述

具体步骤如下：

1. 准备**SWAT项目文件夹**，即TxtInOut文件夹（简称项目文件夹）。

2. 创建另外的**工作文件夹（Work Folder）**，存放控制文件和临时文件。

3. 在工作文件夹，创建并编辑参数文件（使用UTF-8编码）。该文件用于存储待分析或优化参数的信息。

4. 在工作文件夹，创建并编辑评估文件（使用UTF-8编码），该文件用于存储构造目标函数或约束函数的信息。

5. 基于Python环境编程并解决问题。

### 参数文件

参数文件示例如下：

```
Name Type Mode Min_Max Scope
CN2 r f -0.4_0.2 all
GW_DELAY v f 30.0_450.0 all
...
```

第一行始终用于显示提示信息，请勿移除。

除首行外，每一行均应包含下述完整的字段信息：`Name`、`Mode`、`Type`、`Min_Max` 和 `Scope`。

**Name（参数名）：** 可为`.gw`、`.hru`、`.mgt`、`.sol`、`.rte`、`.sub`、`.sep`、`.swq`等项目文件中的任意参数名。参数名原则上应与SWAT项目文件中的参数名一致。同时，针对`*.sol`文件的参数，可针对特定土层修改，例如：

```
SOL_K(2) r f 0.5_15.0 all    # 仅修改第二层
SOL_K(3) r f 0.5_15.0 all    # 仅修改第三层
SOL_K r f 0.5_15.0 all       # 修改所有层
```

如果，有些HRU的土壤层数不足3层或者2层，则默认不对该HRU修改。

**Mode（赋值模式）：** 通过`r`、`v`、`a`等单字符定义项目文件对应参数的赋值模式。（参考SWAT-CUP软件的用法）

   - val 表示分析或优化的数值
   - `r`：相对赋值 -> 新值 = 原值 × (1 + val)
   - `v`：绝对赋值 -> 新值 = val
   - `a`：加法赋值 -> 新值 = 原值 + val  

**Type（变量类型）：** `i` 表示整数，`f` 表示浮点数，`d` 表示离散型。

**Min_Max（取值范围）：** 定义最小值与最大值，用 `_` 分隔。对于离散变量则使用`_`串联所有可能的值。

**Scope（作用范围）：**

  - 默认设置为`all`表示参数将在全流域进行赋值。

  - 或者指定子流域**SUB ID**或HRU**SUB ID(HRU ID)**，例如：

```
CN2 r f -0.4_0.2 all # 默认范围
CN2 r f -0.4_0.2 3(1,2,3,4,5,6,7,8,9) 4(1,2,3,4) 5 # 指定范围
```
说明如下：

- 多个子流域用空格或制表符分隔 
- 单个`SUB ID`：作用于指定子流域内的的所有HRU
- `SUB ID(HRU ID1, HRU ID2, ...)`：作用于指定子流域的特定HRU。
 

### 评估文件

对于创建评估文件，也推荐使用 `.evl` 扩展名以与 GUI 版本保持一致

**示例：**

文件名： `eval.evl`

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_2 : Variable of Column, within *.rch, *.sub, *.hru.
FUNC_1 : Func Type( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min, 10 - None)

1 2012_1 2.1
2 2012_2 3.2
3 2012_3 3.5
4 2012_4 6.7
5 2012_5 14.55
6 2012_6 21.54
...
12 2012_12 22.44
```

评估文件可由多个序列（series）组成，上面示例为一个序列，每个序列可对应流域内不同位置、变量或时间。

每个序列应包含两部分：a.Head Section；b. Data Section

**Head Section：**

在下述说明中，标签`ID`或`NUM`需根据实际问题用数字替换。

- **SER_ID：** 每个序列的唯一标识。（用户自行决定具体数值，但应保证不同序列拥有不同ID）
- **OBJ_ID / CON_ID：** `OBJ`或`CON`定义该序列属于目标函数还是约束函数。`ID`表示`OBJ`或`CON`的标识，用户自行定义。
💡 **注意：** SWAT-UQ-DEV 支持多个序列共享同一`OBJ ID` 或 `CON ID`，但`SER_ID`应是唯一的。
- **WGT_NUM：** 线性权重参数，用于在组合相同 OBJ ID 或 CON ID 的多个序列时，指定当前序列的权重值。
- **RCH_ID / SUB_ID / HRU_ID：** 前缀表示数据来源，即RCH表示从`output.rch`抽取数据，SUB表示`output.sub`，HRU表示`output.hru`。ID则表示河道、子流域和HRU的标识码。
- **COL_NUM：** 指定从输出文件中提取数据的列号。各输出文件的列结构有所不同，具体列号对应的变量请参考下表。
- **FUNC_NUM：** 指定评价函数或数据处理方法的编号，例如：1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min, 10 - None (仅用于数据提取)

**不同输出文件对应的数据列号**

| 文件名      | 有效值 |
|-------------|--------|
| output.rch  | 1-FLOW_IN, 2-FLOW_OUT, 3-EVAP, 4-TLOSS, 5-SED_IN, 6-SED_OUT, 8-ORGN_IN, 9-ORGN_OUT, ... 38-BACTP_OUT, 39-BACTLP_OUT, 43-TOT_N, 44-TOT_P |
| output.sub  | 1-PRECIP, 2-SNOMELT, 3-PET, 4-ET, 5-SW, 6-PERC, 7-SURQ, 8-GW_Q, 9-WYLD, 10-SYLD, 11-ORGN, 12-ORGP, 13-NSURQ, 14-SOLP, 15-SEDP |
| output.hru  | 1-PRECIP, 2-SNOFALL, 3-SNOMELT, 4-IRR, 5-PET, 6-ET, 7-SW_INIT, 8-SW_END, 9-PERA, 10-GW_RCHG, 11-DA_RCHC, 12-REVAP, ... 49-NUP, 50-PUP, ... 67-BACTP, 68-BACTLP |

💡 **注意：** 上述编号均取自SWAT手册；用户也可以直接打开响应的output文件自行确定变量的列号。

 **Data Section**

该部分的数据结构应为 `NUM`、`YEAR`、`MONTH`、`DAY`、`DATA`。其中：

- **NUM:** 序号，仅用于用户检查数据完整性，是否缺漏
- **YEAR:** 年份，
- **MONTH:** 月份，
- **DAY:** 日,
- **DATA:** 数据值（整数或浮点数）。

💡 **注意：** 当SWAT项目的`file.cio`文件的`IPRINT`为0，输出文件按日生成，SWAT-UQ将读取YEAR、MONTH、DAY；若为1，输出文件按月生成，SWAT-UQ将则仅读取YEAR，MONTH（DAY字段在此模式下无效，但必须提供）。

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

在某些工况下，目标函数或者约束函数不依赖于观测数据，只需要模型输出文件的模拟数据。对此，SWAT-UQ还提供更简便方法：

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

通过`YYYY/MM/DD to YYYY/MM/DD`设定数据提取区间。在本例中，SWAT-UQ将提取2012年1月1日-2018年12月31日期间的模拟数据。


### 编程示例

以下代码展示了如何在 Python 环境中如何定义`SWAT-UQ`类：

```python

# 导入SWAT-UQ类
from swatuq import SWAT_UQ

# 定义环境变量
projectPath = "E://swatProjectPath"  #项目文件夹 地址
workPath = "E://workPath" #工作文件夹 地址
exeName = "swat2012.exe" #SWAT可执行程序的名称
paraFileName = "paras.par" #参数文件名称，该文件应位于工作文件夹
evalFileName = "eval.obj" #评估文件名称，该文件应位于工作文件夹

problem = SWAT_UQ(
   projectPath = projectPath,
   workPath = workPath,
   swatExeName = exeName,
   paraFileName = paraFileName,
   evalFileName = evalFileName,
   nInput = 10, # 待定参数个数
   nOuput = 1, # 目标个数，若不指定则依据eval.obj文件设定的目标个数
   nConstraint = 0, #约束个数，若不指定则依据eval.obj文件设定的目标个数
   verboseFlag = True, # 是否输出调试信息
   numParallel = 2 #并行SWAT模型的数量
)

# 以上为实例化SWAT-UQ的过程，下面就可以随意调用UQPyL的方法

#例如，单目标优化:
from UQPyL.optimization.single_objective import GA

ga = GA()
ga.run(problem = problem)
```

💡 **提示：** 更多关于UQPyL的用法请详见[UQPyL 使用文档](https://uqpyl.readthedocs.io/en/latest/)


## 高级操作

### 载入最优参数

下述代码展示了如何将最优参数导入到项目文件夹：

```python
X = np.array([...]) # 输入变量，X应为np.1darray格式
problem.apply_parameter(X, replace = False) # replace为False时，该参数应用于工作文件夹下的Origin文件夹，不直接修改原始项目
problem.apply_parameter(X, replace = True) # replace为True时，直接将参数写入原始SWAT项目
# replace默认为False
```

### 提取模拟数据

SWAT-UQ-DEV提供全方位的模拟数据读取能力：

- 从输出文件中精确提取任意时间区间的模拟结果
- 灵活选择任意空间位置的数据点
- 自由定义并获取各类模拟变量和参数

只需要准备序列文件，并使用内置的`extract_series`函数：

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

代码示例如下：

```Python

X = np.array([...]) # 输入变量，np.1darray
attr = problem.extract_series(X, seriesFile="series.evl")

```

💡 **注意：** 该函数返回的变量`attr`是一个python字典格式的变量，其API如下：


```
attr -> Python Dict

关键字说明：

- x : 输入决策变量，类型为 np.1darray（一维数组）
- objs : 当前输入决策对应的目标函数值，是一个 Python 字典，可通过 `attr['objs'][objID]` 访问，对应在 *.evl 文件中定义的objID
- cons : 与 objs 类似，用于表示约束函数值
- objSeries : 一个 Python 字典，记录 *.evl 文件中关于目标函数的数据序列，可通过 `dataS = attr['objSeries'][objID][serID]` 访问，其中dataS['sim']表示模拟数据，dataS['obs']表示观测数据
- conSeries : 与 objSeries 类似，用于记录关于约束函数的数据序列
```

因此，使用如下代码可获取（2012/01/01-2016/12/31）模拟数据：

```Python

simData = attr['objSeries'][1][1]['sim'] # 关键词 'objSeries' 表示目标序列，非约束序列，
# 关键词 第一个1表示objID, 第二个1表示serID
# 关键词 'sim' 表示模拟数据，非'obs'观测数据

```

### 验证最优参数

基于验证期观测数据对优化结果进行评估，是构建高精度SWAT模型的关键环节。为满足这一核心需求，SWAT-UQ-DEV内置了`validate_parameters`函数。

只需准备验证文件，文件格式和规则同评估文件、序列文件，示例如下：

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

该函数返回的`res`也是Python字典格式的变量，包含两个固定关键词：`objs`或`cons`，代表目标值或约束值。

对于本例，基于观测数据的NSE如下：

```Python

objs = res['objs']
print(objs)

```

### 自定义评估函数

在复杂应用场景（如最优工程管理措施规划）中，**目标函数或约束函数**很难通过评估文件直接定义。不过，SWAT-UQ提供了通过灵活的数据处理机制解决了这一挑战——首先基于评估文件精准提取模拟数据，然后用户基于这些模拟数据以及流域信息自定义目标函数`userObjFunc`或约束函数`userConFunc`，实现了优化过程的高度定制化与问题针对性，从而满足各类专业化工程决策的精细化需求。

上述两函数均接收名为`attr`的参数，`attr`是提取的模拟数据与流域基本信息的载体，为Python字典对象。其数据结构与`extract_series`函数的返回值基本一致，但`attr`包含以下关键词：

```
- HRUInfos：一个 Pandas 数据表（DataFrame），用于记录 HRU（汇流单元）的相关信息，包含以下列：
  ["HRU_ID", "SUB_ID", "HRU_Local_ID", "Slope_Low", "Slope_High", "Luse", "Area"]
```

具体自定义目标函数与约束函数的案例请参考[工程管理优化](./best_management_practices.md)
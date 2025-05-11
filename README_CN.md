# SWAT-UQ: Uncertainty Quantification for SWAT

<p align="center"><img src="./docs/assets/SWAT-UQ.svg" width="400"/></p>

![GitHub last commit](https://img.shields.io/github/last-commit/smasky/SWAT-UQ) ![Static Badge](https://img.shields.io/badge/Author-wmtSky-orange) ![Static Badge](https://img.shields.io/badge/Contact-wmtsmasky%40gmail.com-blue)

👉[Readme](https://github.com/smasky/SWAT-UQ/blob/main/README.md)

👉[中文文档](https://swat-uq.readthedocs.io/en/latest/zh/index.html)

**SWAT-UQ** 是 [UQPyL](https://github.com/smasky/UQPyL) 项目的延伸项目。UQPyL是一个功能全面的不确定性分析与参数优化平台；而开发SWAT-UQ项目的目标是将UQPyL与SWAT模型无缝集成，使用户能够轻松开展敏感性分析、单目标优化、多目标优化等工作，实现SWAT模型快速建立，水资源高效管理等任务。

目前SWAT-UQ项目提供两个版本，满足不同类型用户的需求：

 - **SWAT-UQ-DEV（开发者版本）**：适用于需要高度灵活性和自定义建模、分析、优化流程的用户。
 - **SWAT-UQ-GUI（图形界面版本）**：提供直观的图形化界面，简化操作流程，适合希望尽量减少编程的用户。

总体而言，借助SWAT-UQ项目，用户可以将UQPyL强大的不确定性分析与优化功能无缝融入基于SWAT模型的研究项目。

## 实用链接

- **官网**：[参数敏感性分析及优化实验室](http://www.uq-pyl.com)（**待更新**）
- **源代码**：[GitHub 仓库](https://github.com/smasky/SWAT-UQ/)
- **文档资料**：[查看文档](https://swat-uq.readthedocs.io/en/latest/)
- **引用信息**：SWAT-UQ（**投稿至Environment Modelling & SoftWare**）

---


## content
- [开发版](#swat-uq-开发版)
    - [功能特点](#-功能特点)
    - [安装指南](#-安装指南)
    - [快速开始](#-快速开始)
- [欢迎合作](#-欢迎合作)
- [联系方式](#-联系方式)

## SWAT-UQ 开发版

**SWAT-UQ-DEV**是一个基于**Python语言环境**并于PyPi平台托管的扩展包（Package）。该扩展包定义了名为`SWAT_UQ`的 Python类，继承自UQPyL的`Problem`类。因此，用户实例化`SWAT_UQ`类后，即可直接调用UQPyL的所有方法和算法，帮助完成各种任务。

此外`SWAT_UQ`类还封装了一系列功能函数，包括写入自定义参数、读取模型模拟结果等，简化“问题构建->分析->求解”的流程，提升解决问题效率。

因此，SWAT-UQ-DEV特别适合希望自定义工作流（集成UQPyL或其他Python扩展包）的用户。

### ✨ 功能特点

1. **并行执行：** 无论是项目文件读写，还是**SWAT模型的模拟仿真**，均支持并行处理。（经过一台40核服务器上的压力测试，SWAT-UQ-Dev并行运行80个SWAT模拟实例以上，实现一小时内完成两万次模拟）。

2. **文件控制：** 用户只在前期准备若干UTF-8格式的文本文件，即可轻易完成如径流或水质等关于SWAT模型的校准任务。

3. **流程简化：** 基于[UQPyL](https://github.com/smasky/UQPyL)的支持，用户可轻松完成全部建模流程：敏感性分析->参数优化->最优参数载入

### ⚙️ 安装指南

 ![Static Badge](https://img.shields.io/badge/Python-3.6%2C%203.7%2C%203.8%2C%203.9%2C%203.10%2C%203.11%2C%203.12-blue) ![Static Badge](https://img.shields.io/badge/OS-Windows%2C%20Linux-orange)

 **推荐 (pip or conda):**

```bash
pip install -U swatuq
```

```bash
conda install swatuq --upgrade
```

### 🍭 快速开始

本节将提供SWAT-UQ-DEV的详细指南，帮助用户解决各类基于SWAT模型的水文问题。SWAT-UQ-DEV的设计核心是通过实例化`SWAT-UQ`类，来串联SWAT模型与UQPyL。因此，`SWAT-UQ`类实质上继承自UQPyL中的`Problem`类。该类的实例化将使用户可简单快速调用UQPyL的所有方法（参考[UQPyL Project](https://github.com/smasky/UQPyL)）。

具体步骤如下：

第1步：准备**SWAT项目文件夹**，即TxtInOut文件夹（简称项目文件夹）。

第2步：创建另外的**工作文件夹（Work Folder）**，存放控制文件和临时文件。

第3步：在工作文件夹，创建并编辑参数文件（使用UTF-8编码）。该文件用于存储待分析或优化参数的信息。

第4步：在工作文件夹，创建并编辑评估文件（使用UTF-8编码），该文件用于存储构造目标函数或约束函数的信息。

第5步：基于Python环境编程并解决问题。

工作文件夹的文件结构应为：

```
Work Folder/
├── tempForParallel/  # 并行临时目录，计算结束请自行删除以免占满硬盘
│   ├── 0505_081713/ # 每一次运行，SWAT-UQ-DEV按照日期自动生成单独文件夹，方便后期Debug
│   │   ├── origin/ # 原始SWAT项目文件夹，apply_parameters函数可载入最优参数至该目录
│   │   ├── validation/ # 用于模型验证
│   │   ├── parallel0/ # 用于并行的SWAT项目文件夹
│   │   ├── parallel1/ # 用于并行的SWAT项目文件夹
│   │   └── parallel2/ # 用于并行的SWAT项目文件夹
│   └── 0504_215113/
├── paras.par # 参数文件
└── eval.evl # 评估文件
```

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

  - 或者指定子流域**SUB ID**或**SUB ID(HRU ID)**，例如：

```
CN2 r f -0.4_0.2 all # 默认范围
CN2 r f -0.4_0.2 3(1,2,3,4,5,6,7,8,9) 4(1,2,3,4) 5 # 指定范围
```
说明如下：

- 多个子流域用空格或制表符分隔 
- 单个`SUB ID`：作用于指定子流域内的的所有HRU
- `SUB ID(HRU ID1, HRU ID2, ...)`：作用于指定子流域的特定HRU。

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

💡 **注意：** 当SWAT项目的`file.cio`文件的`IPRINT`为1，输出文件按日生成，SWAT-UQ将读取YEAR、MONTH、DAY；若为0，输出文件按月生成，SWAT-UQ将则仅读取YEAR，MONTH（DAY字段在此模式下无效，但必须提供）。

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

以下代码展示了如何在 Python 环境中如何定义`SWAT-UQ`类：

```python

# 导入SWAT-UQ类
from swatuq import SWAT_UQ

# 定义环境变量
projectPath = "E://swatProjectPath"  #项目文件夹 地址
workPath = "E://workPath" #工作文件夹 地址
exeName = "swat2012.exe" #SWAT可执行程序的名称
paraFileName = "paras.par" #参数文件名称，该文件应位于工作文件夹
evalFileName = "eval.evl" #评估文件名称，该文件应位于工作文件夹

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

💡 **提示：** 更多关于UQPyL的用法请详见[UQPyL 使用文档](https://uqpyl.readthedocs.io/en/latest/)。SWAT-UQ-DEV更多高级用法请详见[SWAT-UQ 使用文档](https://swat-uq.readthedocs.io/en/latest/)

## SWAT-UQ界面操作版

💡 **提示:** 目前推荐使用SWAT-UQ-DEV，DEV版本更领先，GUI版本有待后续更新！

## 🔥 欢迎合作

欢迎大家参与贡献，共同扩展UQPyL，加入更多先进的敏感性方法、优化算法以及实际工程问题的示例。

## 📧 联系方式

如有任何问题，请联系：

**wmtSky**  
Email: [wmtsmasky@gmail.com](mailto:wmtsmasky@gmail.com)(优先), [wmtsky@hhu.edu.cn](mailto:wmtsky@hhu.edu.cn)

---

**本项目遵循 MIT 许可协议 - 具体内容详见 [LICENSE](https://github.com/smasky/SWAT-UQ/LICENSE)**

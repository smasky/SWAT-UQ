# SWAT-UQ: Uncertainty Quantification for SWAT

<p align="center"><img src="./resource/SWAT-UQ.svg" width="400"/></p>

![GitHub last commit](https://img.shields.io/github/last-commit/smasky/SWAT-UQ) ![Static Badge](https://img.shields.io/badge/Author-wmtSky-orange) ![Static Badge](https://img.shields.io/badge/Contact-wmtsmasky%40gmail.com-blue)


SWAT-UQ 是 [UQPyL](https://github.com/smasky/UQPyL) 项目的扩展子项目。UQPyL 是一个面向参数不确定性分析与优化的综合性平台。SWAT-UQ 旨在实现 UQPyL 与 SWAT 水文模型的深度耦合，帮助用户以极简的方式开展参数敏感性分析、单目标优化、多目标优化等任务，亦可灵活支持其他不确定性相关工作。

面向不同的用户群体，SWAT-UQ提供两个版本：
- **SWAT-UQ-DEV:** 开发版，提供灵活的代码接口，适用于具备一定编程能力、追求高度定制化建模流程的高级用户。
- **SWAT-UQ-GUI:** 图形界面版，配备直观易用的可视化操作界面，简化工作流程，适合希望减少编码参与的用户群体。

SWAT-UQ使用户能够将先进的不确定性分析方法与优化算法，便捷地融入基于SWAT模型的水文建模流程之中。

## content
- [开发版](#swat-uq-开发版)
    - [功能特点](#-功能特点)
    - [快速开始](#-快速开始)
- [欢迎合作](#-欢迎合作)
- [联系方式](#-联系方式)

## SWAT-UQ 开发版

**SWAT-UQ-DEV**是面向Python环境的扩展包。该版本实现了一个名为`SWAT_UQ`的Python类，继承自 UQPyL框架中的`Problem`基类。用户通过实例化SWAT_UQ类，不仅能够直接调用UQPyL提供的各类方法与算法，还可借助其内置的多种辅助函数，高效开展模型参数率定、最佳管理措施优化等不确定性分析与优化任务。

该版本尤其适合有自定义建模流程需求，或希望将其与 UQPyL 及其他 Python 工具进行集成的用户。

### ✨ 功能特点

1. **并行执行:** 项目文件夹内的数据输入输出操作以及 SWAT 模型仿真 都支持并行化处理。(🎉在一台 40核Linux服务器上的基准测试表明，当前版本的代码可以稳定地同时运行最多80个SWAT实例。)

2. **文件控制:** 在模型参数率定任务中（如径流、泥沙、水质），用户只需准备一组 .txt 文件即可完成整个设置过程。

3. **工作流集成:** 在 UQPyL 的支持下，用户能够高效地执行完整的基于建模的工作流：敏感性分析 -> 优化 -> 参数回代分析。

### 🍭 快速开始

在本节，我们提供了使用SWAT-UQ-DEV解决基于SWAT模型的分析及优化问题的指南。

首先，实例化`SWAT-UQ`类，该类继承自UQPyL中的`Problem`类。通过这样操作，您将能够访问UQPyL中所有可用的方法和算法(有关详细信息，请参考[UQPyL文档](https://github.com/smasky/UQPyL))。

在开始之前，需要进行一些准备工作：

**步骤1:** 获得SWAT项目文件夹(为方便起见，称为**SWAT Project Folder**)。

**步骤2:** 创建一个单独的文件夹，作为工作文件夹(**Work Folder**)，用于存放问题设定所需的控制文件，以及在并行运行 SWAT 模型过程中生成的临时文件。

**步骤3:** 在工作文件夹中创建一个使用UTF-8编码的参数文件，用于定义您希望分析或优化的参数信息。格式示例如下:

**文件名:** `paras.par`

💡 **注意:** 参数文件的文件名没有严格限制，但建议使用 .par 扩展名，以保持与图形界面版本的一致性。文件中的所有元素应使用空格或制表符（Tab）进行分隔。

```
Name Mode Min Max Scope
CN2 r -0.4 0.2 all
GW_DELAY v 30.0 450.0 all
ALPHA_BF v 0.0 1.0 all
GWQMN v 0.0 500.0 all
... 
SMFMN v 0.0 20.0 all
TIMP v 0.01 1.0 all
SURLAG v 0.05 24.0 all
```

参数文件的**第一行**是固定保留的，用作提示说明。

接下来的每一行参数信息需按照以下顺序填写: Name(参数名)、Mode(赋值方式)、Min(最小值)、Max(最大值)和 Scope(作用范围)，具体说明如下：

- **Name(参数名):** 可以填写出现在`.gw`, `.hru`, `.mgt`, `.sol`, `.rte`, `.sub`, `.sep`, `.swq`等文件中的任意参数。唯一要求是，参数名必须与SWAT项目文件中的名称完全一致。目前已支持多达308个参数。

- **Mode(赋值方式):** 表示参数的赋值模式，用一个字符表示(`r`, `v` 或 `a`)。
    - 假设`val`是参数文件中给出的值，`originVal`是SWAT项目文件中的原始值。
    - **`r`** 相对赋值方式，输入项目文件的实际值将通过公式`(1+val)*originVal`计算。
    - **`v`** 绝对赋值方式，直接使用`val`作为实际值。
    - **`a`** 增量赋值方式，实际值为`originVal+val`。
- **Min(最小值):** 表示该参数的最小值(下界)。
- **Max(最大值):** 表示该参数的最大值(上界)。
- **Scope(作用范围):** 表示该参数生效的目标范围。默认设置为`all`，即在全局范围内修改该参数。你也可以指定具体的`SUB ID`，或指定`SUB ID`与`HRU ID`的组合，从而只在特定区域上应用该参数。例如：

 ```
 CN2 r -0.4 0.2 all # Default Scope
 CN2 r -0.4 0.2 3(1,2,3,4,5,6,7,8,9) 4(1,2,3,4) 5 # Appoint Scope
 ```

作用范围的格式可以采用以下两种方式之一：

- `SUB ID`：将该参数应用于指定子流域（Sub-basin）中的所有 HRU 单元。
- `SUB ID(HRU ID_1, HRU ID_2, ..., HRU ID_N)`：将该参数仅应用于指定子流域中部分HRU单元。

多个子流域之间应使用空格或制表符（Tab）分隔。
(后续即将推出以HRU的slope来划分作用范围)

**步骤4:** 在工作目录(Work Folder)中创建一个评估文件(evaluation file)，文件编码为UTF-8。该文件用于基于观测数据构建目标函数或约束函数。

文件名: `eval.obj`

💡 **注意:** 评估文件的文件名没有严格限制，但建议使用`.obj`扩展名，以保持与图形界面版本的一致性。

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_6 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_1 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min)

1 2012_1 2.1
2 2012_2 3.2
3 2012_3 3.5
4 2012_4 6.7
5 2012_5 14.55
6 2012_6 21.54
...
12 2012_12 22.44
```

评估文件(evaluation file)可以包含多个数据序列(data series)，每个序列可对应流域内不同的位置、输出变量、时间段。
本示例中仅展示一个数据序列的格式。
每个数据序列由两部分组成：a.头部定义(Head Definition); b.数据部分(Data Section)

**头部定义(Head Definition)说明**: (以下带有 ID 或 NUM 的标签需用具体数字替代)

- **SER_ID:** 该ID是该数据序列的唯一标识符，需用不同的int型数字区分不同数据序列。
- **OBJ_ID** 或 **CON_ID:** `OBJ`表示该序列用于构建目标函数(Objective Function);`CON`表示该序列用于构建约束函数(Constraint Function)；其后的 ID 是对应函数的唯一标识符。
💡**提示:** SWAT-UQ-DEV支持多个数据序列(Data series)共用同一个OBJ_ID或CON_ID。共同ID的数据序列将使用后续定义的权重来线性组合。

- **WGT_NUM:** 此`NUM`表示该序列在组合为同一OBJ_ID或CON_ID时的线性权重。`NUM`应为int或float型数字

- **RCH_ID**, **SUB_ID** 或 **HRU_ID:** 这些标签用于指定读取的输出文件类型，分别对应SWAT模型中的河道(RCH)、子流域(SUB)或水文响应单元(HRU)。ID应与SWAT项目中的对应编号一致，并可根据实际需求进行设定。

- **VAR_NUM:** 此`NUM`表示要从`output.rch`, `output.sub`或`output.hru`文件中提取的变量列号(请参考后续表格以获取正确数值)。

- **FUNC_NUM:** 此`NUM`用于定义基于观测值与模拟值的目标或约束函数类型。`NUM`取值如下: 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min

各输出文件（output.rch、output.sub、output.hru）中可提取变量的列号一览表
| File Name | Valid Value |
| ----------|-------------|
| output.rch| 1-FLOW_IN, 2-FLOW_OUT, 3-EVAP, 4-TLOSS, 5-SED_IN, 6-SED_OUT, 8-ORGN_IN, 9-OGRN_OUT, 10-ORGP_IN, 11-ORGP_OUT, 12-NO3_IN, 13-NO3_OUT, 14-NH4-IN, 15-NH4-OUT, 16-NO2_IN, 17-NO2_OUT, 18-MINP_IN, 19-MINP_OUT, 20-CHLA_IN, 21-CHLA_OUT, 22-CBOD_IN, 23-CBOD_OUT ... 38-BACTP_OUT, 39-BACTLP_OUT... 43-TOT_N, 44-TOT_P |
| output.sub| 1-PRECIP, 2-SNOMELT, 3-PET, 4-ET, 5-SW, 6-PERC, 7-SURQ, 8-GW_Q, 9-WYLD, 10-SYLD, 11-ORGN, 12-ORGP, 13-NSURQ, 14-SOLP, 15-SEDP|
| output.hru| 1-PRECIP, 2-SNOFALL, 3-SNOMELT, 4-IRR, 5-PET, 6-ET, 7-SW_INIT, 8-SW_END, 9-PERA, 10-GW_RCHG, 11-DA_RCHC, 12-REVAP ... 49-NUP, 50-PUP ...67-BACTP, 68-BACTLP|

**步骤5:** 在Python环境，构建基于SWAT模型的问题

```Python
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

## SWAT-UQ 界面操作版

💡 **提示:** 目前推荐使用SWAT-UQ-DEV，DEV版本更领先，GUI版本有待后续更新！

## 🔥 欢迎合作

欢迎大家参与贡献，共同扩展UQPyL，加入更多先进的敏感性方法、优化算法以及实际工程问题的示例。

## 📧 联系方式

如有任何问题，请联系：

**wmtSky**  
Email: [wmtsmasky@gmail.com](mailto:wmtsmasky@gmail.com)(优先), [wmtsky@hhu.edu.cn](mailto:wmtsky@hhu.edu.cn)

---

**本项目遵循 MIT 许可协议 - 具体内容详见 [LICENSE](https://github.com/smasky/SWAT-UQ/LICENSE)**

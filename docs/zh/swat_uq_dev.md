# SWAT-UQ-DEV 模块

---

## DEV 版本概述

**SWAT-UQ-DEV** 是一个专为 **脚本化环境** 设计的 Python 软件包。该模块定义了一个名为 `SWAT_UQ` 的 Python 类，继承自 UQPyL 的 `Problem` 类。通过实例化 `SWAT_UQ` 类，用户即可直接调用 UQPyL 提供的全部方法和算法。

此外，`SWAT_UQ` 还封装了一系列内置函数，旨在简化构建与求解实际问题（如模型校准、最佳管理实践等）的流程，提升效率。

SWAT-UQ-DEV 特别适合希望自定义工作流程、集成 UQPyL 或其他 Python 工具的用户。

---

## 主要特性

1. **并行执行：** 无论是项目文件夹中的数据读写，还是 **SWAT 模型仿真**，均支持并行处理。  
   🎉 在一台 40 核服务器上的基准测试表明，该代码版本可稳定同时运行 80 个 SWAT 实例。

2. **文件控制简化：** 在进行如流量或水质等模型校准任务时，用户只需准备若干 `.txt` 文件，即可完成全部设置。

3. **流程集成性强：** 借助 [UQPyL](https://github.com/smasky/UQPyL) 的支持，用户可轻松执行完整的建模流程，包括：敏感性分析（Sensitivity Analysis）-> 参数优化（Optimization）-> 最优参数反代（Back-substitution）

---

## 安装方式

支持的 Python 版本：3.6 至 3.12  
支持系统：Windows、Linux

**推荐安装方式（使用 PyPi 或 Conda）：**

```bash
pip install -U swatuq
```

```bash
conda install swatuq --upgrade
```

---

## 快速入门

本节将提供逐步指南，帮助你通过 SWAT-UQ-DEV 解决基于 SWAT 的建模问题。

### 第一步：准备文件与目录结构

1. 获取一个 **SWAT 项目文件夹**（以下简称 SWAT Project Folder）。
2. 创建一个独立的 **工作文件夹（Work Folder）**，用于存放控制文件和并行运行时生成的临时文件。
3. 在 Work Folder 中，创建一个名为 `paras.par` 的参数文件，内容需为 UTF-8 编码。

   文件格式如下：

   ```
   Name Type Mode Min_Max Scope
   CN2 r f -0.4_0.2 all
   GW_DELAY v f 30.0_450.0 all
   ...
   ```

   - 参数名称需与 SWAT 项目中的名称严格一致。
   - 支持的赋值方式包括：
     - `r`：相对赋值（新值 = 原值 × (1+val)）
     - `v`：绝对赋值
     - `a`：加法赋值（新值 = 原值 + val）
   - 参数类型可为整数 (`i`)、浮点数 (`f`)、离散 (`d`)。
   - 作用范围（Scope）支持全局（`all`），也支持精确指定子流域和 HRU ID。

4. 创建一个名为 `eval.obj` 的 UTF-8 编码文件，用于定义目标函数或约束函数。  
   文件包括：
   - **头部定义区（Head Definition）：** 用于声明数据系列 ID、目标函数 ID、权重、输出变量列号、评价指标类型等；
   - **数据区（Data Section）：** 为对应观测数据，支持月、日时间尺度；

   支持的评价指标包括：NSE、RMSE、PCC、Pbias、KGE、均值、总和、最大值、最小值。

---

## 编程示例

以下 Python 脚本展示了如何定义并运行一个 SWAT-UQ 问题：

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

## 应用最优参数

你可以通过以下代码将最优参数应用到原始项目文件夹中，或只作用于工作目录：

```python
# X should be a list or a NumPy 1D or 2D array
problem.apply_parameter(X, replace=False)  # 应用于工作路径，不修改原始项目
problem.apply_parameter(X, replace=True)   # 直接写入原始 SWAT 项目
```
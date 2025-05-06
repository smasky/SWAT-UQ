# SWAT-UQ-GUI

---

## GUI 版本概述

💡 **注意：** SWAT-UQ-GUI 仍处于演示阶段（目前推荐使用 SWAT-UQ-DEV）。欢迎体验，我们正在开发完整版！

**SWAT-UQ-GUI** 是专为 **SWAT** 模型的参数不确定性量化（UQ）而设计的图形用户界面工具。它的核心功能构建在我们已公开发布的 Python UQ 工具包 [UQPyL](https://github.com/smasky/UQPyL) 之上。这个平台的显著优势在于用户**无需编程**，即可实现从**敏感性分析**到**参数优化**、**结果检查**再到**数据可视化**的完整流程自动化。

<p align="center"><img src="/pic/MainUI.jpg" alt="Main GUI" width="350"/> <img src="/pic/TableList.jpg" alt="Table List" width="350"/></p>

<p align="center"><strong>图 1. 启动界面</strong></p>

SWAT-UQ-GUI 包含三个主要模块，分别对应前处理、执行过程和后处理。如**图 1**所示，前处理包括**参数设置**和**目标定义**；执行过程包括**敏感性分析**、**问题优化**、**结果验证与应用**；后处理提供直方图（**可视化 A**）和点线图（**可视化 B**）的绘图界面。

---

## 主要功能特色

- **端到端可视化流程：** SWAT-UQ-GUI 提供完整的图形化操作，覆盖问题定义、敏感性分析、参数优化和结果验证全过程。
- **模块化与可扩展架构：** 采用模块化设计，可轻松扩展新方法与工具，不影响现有流程。

---

## 快速开始

我们提供快速开始教程，未来将补充详细文档和教学视频。

请下载 SWAT-UQ 的最新版本。

**演示版已发布：** [SWAT-UQ](https://github.com/smasky/SWAT-UQ/releases/tag/v0.0)

---

### 第一步：创建或打开项目

在 **Get Started** 界面中，点击 **New Project** 卡片创建新项目，或点击 **Open Project** 打开已有项目。你也可以选择 **Example** 卡片查看案例，或点击 **Help** 获取帮助。

<p align="center"><img src="/pic/New_Project.png" alt="New Widget" width="300"/> <img src="/pic/Open_Project.png" alt="Open Widget" width="300"/></p>

<p align="center"><strong>图 2. 创建项目与打开项目界面</strong></p>

**New Project：** 用户需填写 UQ 项目名称、UQ 项目路径和 SWAT 项目路径。填写后程序将验证 SWAT 项目文件是否有效，验证成功后将激活其他模块。项目创建成功后，会在指定路径下保存一个名为 *.prj 的项目文件。

**Open Project：** 用户选择包含 *.prj 文件的文件夹，程序将检查其有效性。

---

### 第二步：参数设置与目标定义

在参数设置与目标定义界面，用户需创建 `.par` 参数文件和 `.obj` 目标文件，这些文件用于指定将修改的参数及评估的目标函数。

<p align="center"><img src="/pic/Parameter_Setting.jpg" alt="Main GUI" width="350"/> <img src="/pic/Objective_Widget.jpg" alt="Table List" width="350"/></p> 

<p align="center"><strong>图 3 和图 4：参数设置与目标定义界面</strong></p>

如图 3 所示，用户可通过导入现有文件或点击“添加”按钮打开 **参数选择** 窗口来设置参数。参数按 SWAT 文件后缀分类排列，支持搜索功能。

<p align="center"><img src="/pic/Parameter_Selection.png" alt="Parameter Selection" width="300"/></p>

<p align="center"><strong>图 5. 参数选择表</strong></p>

用户可设置每个参数的调优方式、上下限和使用的文件范围，设置后点击“保存当前参数”按钮将其保存到项目目录中。

目标函数定义同样支持导入或手动添加。点击“添加”按钮手动定义目标函数。

<p align="center"><img src="/pic/Objective_Define.png" alt="Objective Define" width="300"/></p> 
<p align="center"><strong>图 6. 目标函数定义表</strong></p>

用户需填写目标 ID、序列 ID、目标类型、变量类型、权重等信息。目标 ID 与序列 ID 可重复，用于定义加权组合目标函数。完成后可保存为 `.obj` 文件，一个文件中也可定义多个目标函数。

---

### 第三步：执行敏感性分析或参数优化

以敏感性分析为例，如图 6 所示，用户先选择参数文件和目标文件，然后选择分析方法与采样方式，并设置超参数。

设置完成后点击“下一步”，进入仿真设置界面，选择 SWAT 可执行文件、并行线程数与问题名称，依次点击“初始化”、“采样”、“仿真”按钮开始分析。过程可实时查看进度，也可暂停调整设置。分析结果保存在项目路径下 `./Result/data/` 中，可用于后续可视化。

<p align="center"><img src="/pic/Sensibility_Analysis.jpg" alt="SA_Setup" width="400"/> <img src="/pic/Sensibility_Analysis_Simulation.jpg" alt="SA_Simulation" width="400"/></p>

<p align="center"><strong>图 7. 敏感性分析界面</strong></p>

对于参数优化，仍然需选择参数与目标文件。如果目标数量 > 1，将启用多目标优化；否则为单目标优化。优化过程也支持进度显示，显示每轮迭代的最优参数值。

<p align="center"><img src="/pic/Optimization.jpg" alt="OP_Setup" width="350"/> <img src="/pic/Optimization_Simulation.jpg" alt="OP_Simulation" width="350"/></p>

<p align="center"><strong>图 8. 参数优化界面</strong></p>

---

### 可用方法列表

**敏感性分析方法：**
- Sobol'
- Delta Test (DT) #TODO
- eFAST
- RBD-FAST
- MARS-SA #TODO
- Morris
- RSA

**优化算法：**
（* 表示适用于高计算量优化问题）

- **单目标优化**：SCE-UA、ML-SCE-UA、GA、CSA、PSO、DE、ABC、ASMO* (#TODO)、EGO* (#TODO)  
- **多目标优化**：MOEA/D、NSGA-II、RVEA、MOASMO* (#TODO)

---

### 第四步：结果验证与应用

在结果验证界面，SWAT-UQ 允许用户模拟指定参数组合，并提取所需时间序列，或将最优参数直接应用到 SWAT 项目中。参数组合可以是用户定义的，也可以来自已有优化结果文件。

<p align="center"><img src="/pic/Validation.jpg" alt="OP_Setup" width="400"/></p>

<p align="center"><strong>图 9. 结果验证界面</strong></p>

---

### 第五步：结果可视化

当前 SWAT-UQ 支持两类图形：柱状图（敏感性分析）与收敛图（优化分析），未来将持续添加更多类型。

<p align="center"><img src="/pic/FAST.png" alt="SA_Result" width="800"/></p>

<p align="center"><strong>图 10. 敏感性分析可视化</strong></p>

<p align="center"><img src="/pic/GA.png" alt="OP_Result" width="600"/></p>

<p align="center"><strong>图 11. 优化结果可视化</strong></p>

在可视化 A/B 界面中，用户选择结果文件后将显示初始图形。点击“配置”按钮可打开参数设置界面，调整图像外观，如图 12 所示。

<p align="center"><img src="/pic/Visualization_A.png" alt="Visualization_A" width="350"/> <img src="/pic/Visualization_B.png" alt="Visualization_B" width="350"/></p>

<p align="center"><strong>图 12. 可视化界面</strong></p>

---

**以上为 SWAT-UQ 快速开始部分。如需更多高级功能，请参阅完整文档。**
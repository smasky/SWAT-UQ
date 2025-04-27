# SWAT-UQ: Uncertainty Quantification for SWAT

<p align="center"><img src="./docs/pic/SWAT-UQ.svg" width="400"/></p>

[![PyPI version](https://badge.fury.io/py/swatuq.svg)](https://badge.fury.io/py/swatuq) ![PyPI - Downloads](https://img.shields.io/pypi/dm/swatuq) ![PyPI - License](https://img.shields.io/pypi/l/swatuq) ![GitHub last commit](https://img.shields.io/github/last-commit/smasky/SWAT-UQ) ![Static Badge](https://img.shields.io/badge/Author-wmtSky-orange) ![Static Badge](https://img.shields.io/badge/Contact-wmtsmasky%40gmail.com-blue)

**SWAT-UQ** is an extend project of [UQPyL](https://github.com/smasky/UQPyL) - a comprehensive platform for uncertainty analysis and parameter optimization. This project aims to provide full integration of UQPyL and **Soil and Water Assessment Tool** (SWAT), enabling users to easily perform sensitivity analysis, single-objective optimization, and multi-objective optimization and so on. 

👉[中文简介](https://github.com/smasky/SWAT-UQ/blob/main/README_CN.md)

👉[Documentation](https://swat-uq.readthedocs.io/en/latest/)

There are two available versions of SWAT-UQ, tailored to meet different user needs:
 - **SWAT-UQ-DEV (Develop Version)** - Designed for advanced users who require high flexibility and customization in building and managing their modeling workflows.
 - **SWAT-UQ-GUI (GUI Version)** - Offers an intuitive graphical interface for streamlined operation, ideal for users seeking minimal coding involvement.

With SWAT-UQ, users can seamlessly incorporate powerful uncertainty quantification and optimization algorithms into their SWAT-based hydrological modeling projects.

## Useful Links

- **Website**: [UQPyL Official Site](http://www.uq-pyl.com) (**TODO**: Needs update)
- **Source Code**: [GitHub Repository](https://github.com/smasky/SWAT-UQ/)
- **Documentation**: [ReadTheDocs](https://swat-uq.readthedocs.io/en/latest/)
- **Citation Infos**: [SWAT-UQ](Future Plan)

---


## Content
 - [Develop Version](#develop-version-of-swat-uq)
    - [Key Features](#key-features)
    - [Installation](#installation)
    - [Quick Start](#quick-start)
 - [GUI Version](#gui-version-of-swat-uq)
    - [Key Features](#key-features-1)
    - [Quick Start](#quick-start-1)

## Develop Version of SWAT-UQ

**SWAT-UQ-DEV** is a Python package designed for **script-based environments**. It designs a Python class named `SWAT_UQ`, which inherits from `Problem` class of UQPyL. By instantiating `SWAT_UQ` class, users can directly access all methods and algorithms offered by UQPyL. In addition, `SWAT_UQ` contains a suite of built-in functions to streamline and accelerate the process of building and solving problems (e.g., model calibration, best management practices).

This version is particularly suited for users who wish to customize their workflows, integrate with UQPyL, or other Python tools.

### ✨ Key Features

1. **Parallel Execution:** Both data I/O operations within project folder and **SWAT model simulations** support parallelization. ( 🎉 Benchmark tests on a 40-core server demonstrate that the current code version can stably run up to 80 SWAT instances concurrently.)

2. **File Control:** For model calibration tasks — such as streamflow and water quality,  users only need to prepare a set of `.txt` files to complete the entire setup process. 

3. **Workflow Integration:** With the support of  [UQPyL](https://github.com/smasky/UQPyL), users can efficiently carry out the complete modelling-based workflows: sensitivity analysis -> optimization -> back-substitution.

### ⚙️ Installation

 ![Static Badge](https://img.shields.io/badge/Python-3.6%2C%203.7%2C%203.8%2C%203.9%2C%203.10%2C%203.11%2C%203.12-blue) ![Static Badge](https://img.shields.io/badge/OS-Windows%2C%20Linux-orange)

 **Recommended (PyPi or Conda):**

```bash
pip install -U swatuq
```

```bash
conda install swatuq --upgrade
```


### 🍭 Quick Start

Here, we provide a step-by-step guide to solving SWAT-based problems with SWAT-UQ-DEV.

To get started, instantiate the `SWAT-UQ` class, which inherits from the `Problem` class in UQPyL. This will enable all accesses to methods and algorithms available in UQPyL (see the [UQPyL Documentation](https://github.com/smasky/UQPyL)).

Some preparatory works are required:

**Step 1:** Obtain a **SWAT project folder** (named **SWAT Project Folder** for convenience).

**Step 2:** Create **separate folder**  as **Work Folder** to store control files for setting up your problems, as well as temporary files used when running the SWAT model in parallel.

**Step 3:** In the Work Folder, create a **parameter file** encoded in UTF-8. This file would show the details of the parameters you want to analyze or optimize, as shown below:

**File name:** `paras.par`

💡 **Noted:**  The file name is not restricted, but it is recommended to use the `.par` extension for consistency with the GUI version. In this file, all elements must be separated by spaces or tabs.

```
Name Mode Min_Max Scope
CN2 r f -0.4_0.2 all
GW_DELAY v f 30.0_450.0 all
ALPHA_BF v f 0.0_1.0 all
GWQMN v f 0.0_500.0 all
... 
SMFMN v f 0.0_20.0 all
TIMP v f 0.01_1.0 all
SURLAG v f 0.05_24.0 all
```

The first line should be kept as a hint for users.

Following line of the parameter file should be structured by `Name`, `Mode`, `Type`, `Min_Max` and `Scope`:
 - **Name:** Any parameter occurred in `.gw`, `.hru`, `.mgt`, `.sol`, `.rte`, `.sub`, `.sep`, `.swq` files can be wrote. The only requirement is that the parameter names used here must exactly match those in the SWAT project file. (Totally support 308 parameters). For parameters in `*.sol` files, it is possible to modify values for specific layers. For example:

```
SOL_K(2) r f 0.5_15.0 all    # Modify only the second layer
SOL_K(3) r f 0.5_15.0 all    # Modify only the third layer
SOL_K r f 0.5_15.0 all       # Modify all layers
```

 - **Mode:** The title 'Mode' means assigning mode of parameters, which is represented by a single character, e.g., `r`, `v`, `a`. 
   - where `val` is the value in this parameter file, and `originVal` is the origin value of SWAT project files.
   - **`r`** denotes relative assignment. The true value would be calculated by $(1+val)*originVal$.
   - **`v`** denotes absolute assignment, directly use `val`.
   - **`a`** denotes for adding assignment, the true value is calculated by $originVal+val$.
 - **Type:** The title 'Type' denotes the variable types of parameters, i.e., `i` - int, `f` - float, `d` - discrete.  
 - **Min_Maz:** The title 'Min' is the lower bound of the parameter. The title 'Max' is the upper bound of the parameter.
 - **Scope:** The title 'Scope' means the target scope of the parameter. By default, it sets to `all` - the parameter would be modified globally. Alternatively, you can specify a particular BSN ID or a combination of SUB ID and HRU IDs to apply the parameter selectively. For example:

 ```
 CN2 r f -0.4_0.2 all # Default Scope
 CN2 r f -0.4_0.2 3(1,2,3,4,5,6,7,8,9) 4(1,2,3,4) 5 # Appoint Scope
 ```

The format follows either:
 - `SUB ID` - apply the parameter to all HRUs within the specified basin
 - `SUB ID(HRU ID_1, HRU ID_2, ..., HRU ID_N)` - apply the parameter to specific HRUs within the given basin

Different basin should be separated by spaces or tabs.

**Step 4:** In the Work Folder, create an **evaluation file** encoded UTF-8, used to construct objective or constraint functions using observed data.

**File Name:** `eval.obj` 

💡 **Noted:**  It is also recommended to use the `.obj` extension for consistency with the GUI version.

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_6 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_1 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )

1 2012 1 1 2.1
2 2012 1 2 3.2
3 2012 1 3 3.5
4 2012 1 4 6.7
5 2012 1 5 14.55
6 2012 1 6 21.54
...
12 2012 1 12 22.44
```

The **evaluation file** can consists of multiple data series, which may correspond to different locations, output variable, or time periods.

In this example, just one data series is shown.

Each series consists of two parts: a. **Head Definition**; b. **Data Section**.

**Head Definition**: (Following label `ID` or `NUM` should be replaced by a number)
- **SER_ID:** The `ID` should be an unique label for different data series.
- **OBJ_ID** or **CON_ID:** The `OBJ` or `CON` determine the type of the data series. And this `ID` denotes the **unique label** of objective or constraint functions. 
   💡 **Noted:** SWAT-UQ-DEV support the multiple series set the same `OBJ ID` or `CON ID`
- **WGT_NUM:** The `NUM` denotes the linear weight for combing series obtaining the same `OBJ ID` or `CON ID`.
- **RCH_ID**, **SUB_ID** or **HRU_ID:** The `RCH`, `SUB` or `HRU` determine the type of output file loaded. The `ID` should be consistent with the SWAT project (which RCH, SUB, HRU) and can be set according to your requirements.
- **COL_NUM:** The `NUM` specifies which data columns to extract from the `output.rch`, `output.hru` or `output.sub` file (Please see following table for checking valid values). 
- **FUNC_NUM:** The `NUM` defines the objective function type to compare observed and simulated data. (Valid values: 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min)

The valid values of `COL_NUM` (extract variable) in `output.rch`, `output.hru`, `output.sub` can be:
| File Name | Valid Value |
| ----------|-------------|
| output.rch| 1-FLOW_IN, 2-FLOW_OUT, 3-EVAP, 4-TLOSS, 5-SED_IN, 6-SED_OUT, 8-ORGN_IN, 9-OGRN_OUT, 10-ORGP_IN, 11-ORGP_OUT, 12-NO3_IN, 13-NO3_OUT, 14-NH4-IN, 15-NH4-OUT, 16-NO2_IN, 17-NO2_OUT, 18-MINP_IN, 19-MINP_OUT, 20-CHLA_IN, 21-CHLA_OUT, 22-CBOD_IN, 23-CBOD_OUT ... 38-BACTP_OUT, 39-BACTLP_OUT... 43-TOT_N, 44-TOT_P |
| output.sub| 1-PRECIP, 2-SNOMELT, 3-PET, 4-ET, 5-SW, 6-PERC, 7-SURQ, 8-GW_Q, 9-WYLD, 10-SYLD, 11-ORGN, 12-ORGP, 13-NSURQ, 14-SOLP, 15-SEDP|
| output.hru| 1-PRECIP, 2-SNOFALL, 3-SNOMELT, 4-IRR, 5-PET, 6-ET, 7-SW_INIT, 8-SW_END, 9-PERA, 10-GW_RCHG, 11-DA_RCHC, 12-REVAP ... 49-NUP, 50-PUP ...67-BACTP, 68-BACTLP|

💡 **Noted:** The numbers above are taken from the SWAT Manual. However, you can actually determine the order of the target variable by checking the output file.

**Data Section** is structured by `NUM`, `YEAR_INDEX`, `DATA`. And there is no need for continuous:
- **NUM:** Not used in SWAT-UQ-DEV, only for data integrity checking.
- **YEAR_INDEX:** The value of `YEAR` means the year index for the data. The value of `INDEX` is the day number when SWAT outputs daily data, otherwise the month number, determined by `IPRINT` in `file.cio` of SWAT project. 
- **DATA:** The type of data can be int or float.

Alternatively,
in some cases, the objective function can be computed without observed data, requiring only extraction of data from output files.
SWAT-UQ provides a more straightforward approach for this purpose.

For example:
```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_23 : ID of RCH, or SUB, or HRU
COL_6 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_1 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )
2012/1/1 to 2018/12/31 : Period for data extraction
```
Therefore, the period (2012/1/1 to 2018/12/31) would be extracted.


**Step 5:** Build your problem in Python script environment.

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
**Step 6:** apply optimal parameters to project folder

```Python
# X should be a list or a NumPy 1D or 2D array
problem.apply_parameter(X, replace=False)  # Applies parameters X to workOriginPath without modifying the original project files
problem.apply_parameter(X, replace=True)   # Applies parameters X directly to the original project directory
```

---
## GUI Version of SWAT-UQ 

💡 **Noted:** SWAT-UQ-GUI is still in demo stage (Now, we advise to use SWAT-UQ-DEV). Feel free to give it a try — the full version is on the way!

**SWAT-UQ-GUI** is designed for parameter uncertainty quantification (UQ) of the **SWAT** model. Its core functionalities are built upon [UQPyL](https://github.com/smasky/UQPyL), our public released Python package for UQ. A key advantage of this platform is that users do not need to worry about coding. It seamlessly automates complete workflow from **sensitivity analysis** to **parameter optimization**, **result checking**, finally **data visualization**.

<p align="center"><img src="./docs/pic/MainUI.jpg" alt="Main GUI" width="400"/> <img src="./docs/pic/TableList.jpg" alt="Table List" width="400"/></p>

<p align="center"><strong>Figure 1. Get Start Card</strong></p>

SWAT-UQ-GUI consists of three modules corresponding to preparation, execution, and post-processing. 
As **Figure 1** shows, preparation involves **Parameter Setting**, **Objective Define**; Execution includes **Sensibility Analysis**, **Problem Optimization**, **Result Validation & Apply**; Post-processing provide interface for histogram (**Visualization A**) and point-line figure (**Visualization B**).

### ✨ Key Features

**End-to-end visualization:** SWAT-UQ-GUI supports fully visualized operations across the entire workflow — from problem definition and sensitivity analysis to optimization and final result validation.

**Modular & Extensible Architecture:** SWAT-UQ-GUI adopts a modular structure that's easy to extend — new methods and tools can be integrated without disrupting existing workflows.


### 🍭 Quick Start

Here, we provide a Quick Start. In future plans, we will provide detailed documentation and videos.

Please choose the latest release version of SWAT-UQ.

**Demo Version has been released:** [SWAT-UQ](https://github.com/smasky/SWAT-UQ/releases/tag/v0.0)

**Step1:** On the **Get Started** interface, click the **New Project** card to create a project or the **Open Project** card to open an existing one. You can also select the **Example** card for reference cases or the **Help** card for assistance.

<p align="center"><img src="./docs/pic/New_Project.png" alt="New Widget" width="300"/> <img src="./docs/pic/Open_Project.png" alt="Open Widget" width="300"/></p>

<p align="center"><strong>Figure 2. New Project Card and Open Project Card</strong></p>

For the New Project Card (left picture of Figure 2), users need to provide the following information: the UQ Project name, the UQ Project path, and the SWAT Project path. After these inputs are provided, the program will verify the validity of the SWAT project files. If the verification is successful, other modules will be activated. Once the UQ Project is created, a project file named *.prj (where * represents the UQ Project name set by the user) will be saved in the specified UQ Project path.  

For the Open Project Card (right picture of Figure 2), users should select the folder that contains *.prj files. SWAT-UQ will then check the validity of the project file before proceeding.  

**Step2:** On the **Parameter Setting** and **Objective Definition**, the parameter file (.par) and the objective file (.obj) should be created. These files are crucial as they specify which parameters will be modified and what objectives will be evaluated by the program.

<p align="center"><img src="./docs/pic/Parameter_Setting.jpg" alt="Main GUI" width="400"/> <img src="./docs/pic/Objective_Widget.jpg" alt="Table List" width="400"/></p> 

<p align="center"><strong>Figure 3. Parameter Setting Card and Figure 4. Objective Define Card</strong></p>

To be specific, as shown in Figure 3, the Parameter Setting Card enables users to define the parameters they wish to tune. There are two ways to add parameters to the information table: either by importing them from an existing file or by clicking the Add button to open the **Parameter Selection** widget. In this table, all selectable parameters are organized by the suffix of the SWAT project files. Additionally, the search bar provides a convenient way to locate specific parameters quickly.

<p align="center"><img src="./docs/pic/Parameter_Selection.png" alt="Parameter Selection" width="300"/></p>

<p align="center"><strong>Figure 4. Parameter Setting Table </strong></p>

After adding parameters, users can set the tuning mode, lower and upper bounds, and specify tuning files (default: all) for each parameter (**Figure 3 shows**). Finally, these settings should be saved to the UQ project folder by clicking "Saving Current Parameter" button.

There are also two ways to define the objective function: by importing from existing files or by user definition. For user definition, you should click "Add" button. 

<p align="center"><img src="./docs/pic/Objective_Define.png" alt="Objective Define" width="300"/></p> 
<p align="center"><strong>Figure 5. Objective Define Table </strong></p>

As shown in Figure 5, users need to accurately fill in the objective ID, series ID, objective type, variable type, weight, and other relevant information. It is important to note that both the series ID and objective ID can be repeated, allowing for combinations of multiple series or weighted combinations of series. For more details, please refer to the comprehensive documentation.

After defining objectives, you can save them to the objective file. It is also allowed to define multiple objective functions within a single file.

**Step3:** Perform sensitivity analysis or parameter optimization as needed. 

Using Sensitivity Analysis as an example, as shown in the left image of Figure 6, users should first select the parameter file and objective file. Next, they choose the desired sensitivity analysis method and sampling technique. Users can then configure additional settings as required, fine-tuning the hyper-parameters to best meet project needs before proceeding. **SWAT-UQ thoughtfully displays the number of parameters and the total sample size to assist users in making informed decisions.**

Once all initial settings are all ready, click the "Next" button to proceed to the simulation and analysis process. The right image of Figure 6 displays the settings of simulation, including the selection of SWAT executable file, parallel numbers and problem name. Finally, click the "Initialize," "Sampling," and "Simulation" buttons in sequence, and wait for simulation completing. **SWAT-UQ can display the simulation progress in real-time, and users can also pause it to reconfigure settings. It would save the analysis result into UQ project folder (./Result/data/). The result file would be used to check or draw visualization picture.**

<p align="center"><img src="./docs/pic/Sensibility_Analysis.jpg" alt="SA_Setup" width="400"/> <img src="./docs/pic/Sensibility_Analysis_Simulation.jpg" alt="SA_Simulation" width="400"/></p>

<p align="center"><strong> Figure 6. Sensibility Analysis Interface </strong></p>

For parameter optimization, users should still select parameter file and objective file at first. When users check more than two objectives, the multi-objective optimization would be activated; conversely, if only one objective is selected, single-objective optimization is used. After fine-tuning hyper-parameters, the optimization process would be started, like sensibility analysis. **SWAT-UQ can display the optimization progress in real-time, along with the optimal parameter values for each iteration.**

<p align="center"><img src="./docs/pic/Optimization.jpg" alt="OP_Setup" width="400"/> <img src="./docs/pic/Optimization_Simulation.jpg" alt="OP_Simulation" width="400"/></p>

<p align="center"><strong> Figure 7. Parameter Optimization Interface </strong></p>

Here, we list the available sensibility analysis method and optimization method.

**Sensibility Analysis:**
- Sobol'
- Delta Test (DT) #TODO
- Extended Fourier Amplitude Sensitivity Test (eFAST)
- Random Balance Designs - Fourier Amplitude Sensitivity Test (RBD-FAST)
- Multivariate Adaptive Regression Splines-Sensitivity Analysis (MARS-SA) #TODO
- Morris
- Regional Sensitivity Analysis (RSA)

**Optimization Algorithm:**
(* indicates solving computational expensive optimization problem)
- **Single Objective Optimization**: SCE-UA, ML-SCE-UA, GA, CSA, PSO, DE, ABC, ASMO* (#TODO), EGO* (#TODO)  
- **Multi-Objective Optimization**: MOEA/D, NSGA-II, RVEA, MOASMO* (#TODO)

**Step 4:** Result Validation and Apply. On Result Validation & Apply interface, SWAT-UQ allows users to simulate a specific set of parameters individually and extract the desired time series data, or apply the optimal parameters directly to the SWAT project files. This parameter set can be user-defined or sourced from completed optimization result files.

<p align="center"><img src="./docs/pic/Validation.jpg" alt="OP_Setup" width="400"/></p>

<p align="center"><strong> Figure 8. Result Validation Interface </strong></p>

**Step 5:** Result Visualization. The current SWAT-UQ provides two types of plot pictures: a bar chart for sensitivity analysis (Visualization A Interface) and an iteration convergence plot for parameter optimization (Visualization B Interface). Of course, additional types of plots will be continuously added in future versions.
**Figures 9 and 10 shows the visualization pictures from two interfaces.**

<p align="center"><img src="./docs/pic/FAST.png" alt="SA_Result" width="800"/></p>

<p align="center"><strong> Figure 9. Sensibility Analysis Visualization </strong></p>

<p align="center"><img src="./docs/pic/GA.png" alt="OP_Result" width="600"/></p>

<p align="center"><strong> Figure 10. Optimization Visualization </strong></p>

Specifically, On the Visualization A and Visualization B, user can select the result file. SWAT-UQ would generates initial visualizations. **Users can click the "Config" button to open the settings panel and tune various parameters of the plot based on the preset values, as Figure 11 indicates.**

<p align="center"><img src="./docs/pic/Visualization_A.png" alt="Visualization_A" width="400"/> <img src="./docs/pic/Visualization_B.png" alt="Visualization_B" width="400"/></p>

<p align="center"><strong> Figure 11. Visualization Interface </strong></p>

**This concludes the Quick Start section for SWAT-UQ. For more advanced operations, please refer to the documentation.**

## 🔥 Call for Contributions

We welcome contributions to expand our library with more sophisticated UQ methods, optimization algorithms and engineering problems.

---

## 📧 Contact

For any inquiries or contributions, please contact:

**wmtSky**  
Email: [wmtsmasky@gmail.com](mailto:wmtsmasky@gmail.com)(Priority), [wmtsky@hhu.edu.cn](mailto:wmtsky@hhu.edu.cn)

---

*This project is licensed under the MIT License - see the [LICENSE](https://github.com/smasky/SWAT-UQ/LICENSE) file for details.*
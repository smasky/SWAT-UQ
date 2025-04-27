# SWAT-UQ-DEV

---

## Overview of DEV Version

**SWAT-UQ-DEV** is a Python package designed for **script-based environments**. It designs a Python class named `SWAT_UQ`, which inherits from `Problem` class of UQPyL. By instantiating `SWAT_UQ` class, users can directly access all methods and algorithms offered by UQPyL. In addition, `SWAT_UQ` contains a suite of built-in functions to streamline and accelerate the process of building and solving practical problems (e.g., model calibration, best management practices).

The SWAT-UQ-DEV is particularly suited for users who wish to customize their workflows, integrate with UQPyL, or other Python tools.

## Key Features

1. **Parallel Execution:** Both data I/O operations within project folder and **SWAT model simulations** support parallelization. ( 🎉 Benchmark tests on a 40-core server demonstrate that the current code version can stably run up to 80 SWAT instances concurrently.)

2. **File Control:** For model calibration tasks — such as streamflow and water quality,  users only need to prepare a set of `.txt` files to complete the entire setup process. 

3. **Workflow Integration:** With the support of  [UQPyL](https://github.com/smasky/UQPyL), users can efficiently carry out the complete modelling-based workflows: sensitivity analysis -> optimization -> back-substitution.

## Installation

 ![Static Badge](https://img.shields.io/badge/Python-3.6%2C%203.7%2C%203.8%2C%203.9%2C%203.10%2C%203.11%2C%203.12-blue) ![Static Badge](https://img.shields.io/badge/OS-Windows%2C%20Linux-orange)

 **Recommended (PyPi or Conda):**

```bash
pip install -U swatuq
```

```bash
conda install swatuq --upgrade
```

## Quick Start

Here, we provide a step-by-step guide to solving SWAT-based problems with SWAT-UQ-DEV.

To get started, instantiate the `SWAT-UQ` class, which inherits from the `Problem` class in UQPyL. This will enable all accesses to methods and algorithms available in UQPyL (see the [UQPyL Project](https://github.com/smasky/UQPyL)).

Some preparatory works are required:

**Step 1:** Obtain a **SWAT project folder** (named **SWAT Project Folder** for convenience).

**Step 2:** Create **separate folder**  as **Work Folder** to store control files for setting up your problems, as well as temporary files used when running the SWAT model in parallel.

**Step 3:** In the Work Folder, create a **parameter file** encoded in UTF-8. This file would show the details of the parameters you want to analyze or optimize, as shown below:

**File name:** `paras.par`

💡 **Noted:**  The file name is not restricted, but it is recommended to use the `.par` extension for consistency with the GUI version. In this file, all elements must be separated by spaces or tabs.

```
Name Type Mode Min_Max Scope
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

💡 **Noted:** The numbers above are taken from the SWAT Manual. Alternatively , you can manually count the order of the target variable by checking the output file.

**Data Section** is structured by `NUM`, `YEAR_INDEX`, `DATA`. And there is no need for continuous:
- **NUM:** Not used in SWAT-UQ-DEV, only for data integrity checking.
- **YEAR_INDEX:** The value of `YEAR` means the year index for the data. The value of `INDEX` is the day number when SWAT outputs daily data, otherwise the month number, determined by `IPRINT` in `file.cio` of SWAT project. 
- **DATA:** The type of data can be int or float.

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
💡 **Noted:** For more detailed usage of UQPyL, please check [UQPyL Documentation](https://uqpyl.readthedocs.io/en/latest/)


**Step 6:** apply optimal parameters to project folder

```Python
# X should be a list or a NumPy 1D or 2D array
problem.apply_parameter(X, replace=False)  # Applies parameters X to workOriginPath without modifying the original project files
problem.apply_parameter(X, replace=True)   # Applies parameters X directly to the original project directory
```
# SWAT-UQ-DEV

---

## Overview of SWAT-UQ-DEV

**SWAT-UQ-DEV** is a Python package tailored for **Python-based scripted environments**. It designs a Python class named `SWAT_UQ`, which inherits from `Problem` class of **UQPyL**. By `SWAT_UQ` class, users can directly access all methods and algorithms offered by UQPyL. In addition, `SWAT_UQ` contains a suite of built-in functions to streamline and accelerate the process of building and solving practical problems (e.g., model calibration, best management practices).

The SWAT-UQ-DEV is particularly suited for users who wish to customize their workflows, integrate with UQPyL, or other Python tools.

## Key Features

1. **Parallel Execution:** Both data I/O operations within project folder and **SWAT model simulations** support parallelization. ( 🎉 Benchmark tests on a 40-core server demonstrate that the current code version can stably run up to 80 SWAT instances concurrently, completing 20,000 simulations within one hour.)

2. **File Control:** For model calibration tasks — such as runoff and water quality,  users only need to prepare a set of text files. The entire work process would be completed.

3. **Workflow Integration:** With the support of  [UQPyL](https://github.com/smasky/UQPyL), users can efficiently carry out the complete modelling-based workflows: sensitivity analysis -> optimization -> optimal parameters loading.

## Installation

 ![Static Badge](https://img.shields.io/badge/Python-3.6%2C%203.7%2C%203.8%2C%203.9%2C%203.10%2C%203.11%2C%203.12-blue) ![Static Badge](https://img.shields.io/badge/OS-Windows%2C%20Linux-orange)

 **Recommended (pip or conda):**

```bash
pip install -U swatuq
```

```bash
conda install swatuq --upgrade
```

## Quick Start

Here, we provide a step-by-step guide to solving SWAT-based problems with SWAT-UQ-DEV.

The key of SWAT-UQ-DEV is to instantiate the `SWAT-UQ` class, which inherits from the `Problem` class in UQPyL. This will enable all accesses to methods and algorithms available in UQPyL (refer to [UQPyL Project](https://github.com/smasky/UQPyL)).


### Overview

Specific steps list below:

**Step 1:** Obtain a **SWAT Project Folder**, i.e., TxtInOut folder.

**Step 2:** Create a new **folder** as **Work Folder** to store text files for setting up solved problems, as well as temporary files when running the SWAT model in parallel.

**Step 3:** In the Work Folder, create a **parameter file** encoded in UTF-8. This file shows the details of the parameters you want to analyze or optimize.

**Step 4:** In the Work Folder,  create a **evaluation file** encoded in UTF-8. This file stores information for defining the objective and/or constraint functions.

**Step 5:** Developing and solving problems using the Python-based script environment. 

### Parameter file

The example of parameter file would be:

**File name:** `paras.par`

💡 **Noted:**  The file name is not restricted, but it is recommended to use the `.par` extension for consistency with the GUI version. 
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

Following line of the parameter file should be structured by `Name`, `Mode`, `Type`, `Min_Max` and `Scope`. And all elements must be separated by spaces or tabs:

**Name:** Any parameter occurred in `.gw`, `.hru`, `.mgt`, `.sol`, `.rte`, `.sub`, `.sep`, `.swq` files can be wrote. The only requirement is that the parameter names used here must exactly match those in the SWAT project file. For parameters in `*.sol` files, it is possible to modify values for specific layers. For example:

```
SOL_K(2) r f 0.5_15.0 all    # Modify only the second layer
SOL_K(3) r f 0.5_15.0 all    # Modify only the third layer
SOL_K r f 0.5_15.0 all       # Modify all layers
```

But, if an HRU has fewer than three or two soil layers, it will not be modified by default.

**Mode:** The title 'Mode' means assigning mode of parameters, which is represented by a single character, e.g., `r`, `v`, `a`. (Refer to the usage of SWAT-CUP)

   - where `val` denotes the value in the parameter file, and `val_origin` is the origin value of SWAT project files.
   - **`r`** denotes relative assignment. The new value would be calculated by $(1+val)*val_{origin}$.
   - **`v`** denotes absolute assignment, directly use `val`.
   - **`a`** denotes for adding assignment, the new value is calculated by $val_{origin}+val$.

**Type:** The title 'Type' denotes the variable types of parameters, i.e., `i` denotes int, `f` denotes float, `d` denotes discrete.  

**Min_Max:** The title 'Min' is the lower bound of the parameter. The title 'Max' is the upper bound of the parameter. For discrete variables, all possible values are concatenated using underscores `_`.

**Scope:** The title 'Scope' means the target scope of the parameter.

- `all` : this parameter would be modified globally
- or indicate sub-basin `SUBID` or **SUB ID(HRU ID)**, for example:

 ```
 CN2 r f -0.4_0.2 all # Default Scope
 CN2 r f -0.4_0.2 3(1,2,3,4,5,6,7,8,9) 4(1,2,3,4) 5 # Appoint Scope
 ```

The format follows either:

 - all scope contents should be separated by space or tab
 - `SUB ID` - apply the parameter to all HRUs within this specific sub-basin
 - `SUB ID(HRU ID_1, HRU ID_2, ..., HRU ID_N)` - apply the parameter to specific HRUs within this basin


### Evaluation file

For evaluation file, it is also recommended to use `.evl` extension to maintain consistency with the GUI version.

For example:

**File Name:** `eval.obj` 

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

The **evaluation file** consists of multiple **data series**, which may correspond to different locations, output variable, or time periods.

In this example, just one data series has been shown.

Each series consists of two parts: a. **Head Definition**; b. **Data Section**.

**Head Definition**: (Following label `ID` or `NUM` should be replaced by a number)

- **SER_ID:** The `ID` should be an unique label for different data series.
- **OBJ_ID** or **CON_ID:** The `OBJ` or `CON` determine the type of the data series. And the `ID` denotes the **unique label** of objective or constraint functions. 
💡 **Noted:** SWAT-UQ-DEV support the multiple series set the same `OBJ ID` or `CON ID`, but `SER_ID` should be unique
- **WGT_NUM:** The `NUM` denotes the linear weight for combing series obtaining the same `OBJ ID` or `CON ID`.
- **RCH_ID**, **SUB_ID** or **HRU_ID:** The `RCH`, `SUB` or `HRU` determine which output file loaded. `RCH` denotes `output.rch`; `SUB` denotes `output.sub`; `HRU` denotes `output.hru`. The `ID` can be set according to your requirements.
- **COL_NUM:** The `NUM` specifies which data columns to extract from the `output.rch`, `output.hru` or `output.sub` file (Please see following table for checking valid values). 

- **FUNC_NUM:** The `NUM` defines the objective function type to compare observed and simulated data. (Valid values: 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min, 10 - None)

The valid values of `COL_NUM` in `output.rch`, `output.hru`, `output.sub` can be:

| File Name | Valid Value |
| ----------|-------------|
| output.rch| 1-FLOW_IN, 2-FLOW_OUT, 3-EVAP, 4-TLOSS, 5-SED_IN, 6-SED_OUT, 8-ORGN_IN, 9-OGRN_OUT, 10-ORGP_IN, 11-ORGP_OUT, 12-NO3_IN, 13-NO3_OUT, 14-NH4-IN, 15-NH4-OUT, 16-NO2_IN, 17-NO2_OUT, 18-MINP_IN, 19-MINP_OUT, 20-CHLA_IN, 21-CHLA_OUT, 22-CBOD_IN, 23-CBOD_OUT ... 38-BACTP_OUT, 39-BACTLP_OUT... 43-TOT_N, 44-TOT_P |
| output.sub| 1-PRECIP, 2-SNOMELT, 3-PET, 4-ET, 5-SW, 6-PERC, 7-SURQ, 8-GW_Q, 9-WYLD, 10-SYLD, 11-ORGN, 12-ORGP, 13-NSURQ, 14-SOLP, 15-SEDP|
| output.hru| 1-PRECIP, 2-SNOFALL, 3-SNOMELT, 4-IRR, 5-PET, 6-ET, 7-SW_INIT, 8-SW_END, 9-PERA, 10-GW_RCHG, 11-DA_RCHC, 12-REVAP ... 49-NUP, 50-PUP ...67-BACTP, 68-BACTLP|

💡 **Noted:** The numbers above are taken from the SWAT Manual. Alternatively, users can manually count the order of the target variable by checking the output file.

**Data Section** is structured by `NUM`, `YEAR`, `MONTH`, `DAY`, `DATA`:

- **NUM:** Not considered in SWAT-UQ-DEV, only for data integrity checking.
- **YEAR:** The value of `YEAR` means the year index for the data. 
- **MONTH:** Month index
- **DAY:** Day index
- **DATA:** The type of data can be int or float.

💡 **Note:** When the `IPRINT` setting in the SWAT project's `file.cio` file is set to `0`, the output files are generated on a daily basis, and SWAT-UQ will read the `YEAR`, `MONTH`, and `DAY` fields. When `IPRINT` is set to `1`, the output files are generated monthly, and SWAT-UQ will only read the `YEAR` and `MONTH` fields. In this mode, the `DAY` field is ignored but still required to be present.

For example:

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

In certain scenarios, the objective function or constraint functions do not rely on observational data and only require simulated data from the model output files. For this purpose, SWAT-UQ also provides a more convenient method.

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

Specify the data extraction period using the format `YYYY/MM/DD` to `YYYY/MM/DD`. In this example, SWAT-UQ will extract simulated data from January 1, 2012, to December 31, 2018.

### Code Example

```Python
# First import SWAT_UQ class
from swatuq import SWAT_UQ

# Second define requirement variables:

projectPath = "E://swatProjectPath"  # your SWAT Project Path
workPath = "E://workPath" # your Work Path
exeName = "swat2012.exe" # the name of swat.exe you want to run
paraFileName = "paras.par" # the parameter file you prepared
evalFileName = "eval.evl" # the evaluation file you prepared

problem = SWAT_UQ(
   projectPath = projectPath, # set projectPath
   workPath = workPath, # set workPath
   swatExeName = exeName # set swatExeName
   paraFileName = paraFileName, # set paraFileName
   evalFileName = evalFileName, # set evalFileName
   nInput = 10, # number of parameters, if not indicated, this would be determined by parameter file
   nOuput = 1, # number of objectives, if not indicated, this would be determined by evaluation file
   nConstraint = 0, # number of constraints, if not indicated, this would be determined by evaluation file
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

### File Structure

The file structure of Work Folder of SWAT-UQ-DEV would be:

```
Work Folder/
├── tempForParallel/  # Temporary directory for parallel processing, please delete after computation to avoid filling up disk space
│   ├── 0505_081713/  # SWAT-UQ-DEV creates a separate folder for each run based on date, facilitating debugging
│   │   ├── origin/   # Original SWAT project folder, apply_parameters function can load optimal parameters into this directory
│   │   ├── validation/  # Used for model validation
│   │   ├── parallel0/   # SWAT project folder used for parallel processing
│   │   ├── parallel1/   # SWAT project folder used for parallel processing
│   │   └── parallel2/   # SWAT project folder used for parallel processing
│   └── 0504_215113/
├── paras.par  # Parameter file
└── eval.evl   # Evaluation file
```

## Advanced Operation

### Import optimal parameter

The following code demonstrates how to import the optimal parameters into the project folder:

```Python
# X should be a list or a NumPy 1D or 2D array
problem.apply_parameter(X, replace=False)  # Applies parameters X to workOriginPath without modifying the original project files. For example, WorkFolder/tempForParallel/0505_081713/origin
problem.apply_parameter(X, replace=True)   # Applies parameters X directly to the original project directory
```

### Extract simulated data

SWAT-UQ-DEV provides comprehensive simulation data reading capabilities:

- Precisely extract simulation results from output files for any time interval
- Flexibly select data points from any spatial location
- Freely define and obtain various simulation variables and parameters

Only prepare the series file and use the built-in extract_series function. For example:

File name: `series.evl`

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1 : Weight of series combination
RCH_23  : ID of subbasin to be included in the objective function
COL_2 : Column ID of variables in output.rch
FUNC_10 : Type of objective function
2012/1/1 to 2016/12/31 : Period for data extraction
```

Code example:

```Python

X = np.array([...]) # np.1darray
attr = problem.extract_series(X, seriesFile="series.evl")

```

💡 **Note:** The function returns a variable `attr` which is a Python dictionary with the following API:

```
attr -> Python Dict

Key descriptions:

- x: Input decision variables, type np.1darray (one-dimensional array)
- objs: Objective function values corresponding to the current input decision, a Python dictionary, accessible via `attr['objs'][objID]`, corresponding to the objID defined in the *.evl file
- cons: Similar to objs, used to represent constraint function values
- objSeries: A Python dictionary recording data sequences for objective functions defined in the *.evl file, accessible via `dataS = attr['objSeries'][objID][serID]`, where dataS['sim'] represents simulation data and dataS['obs'] represents observation data
- conSeries: Similar to objSeries, used to record data sequences for constraint functions
```

Therefore, the following code can be used to obtain simulation data for the period (2012/01/01-2016/12/31):

```python
simData = attr['objSeries'][1][1]['sim'] # Keyword 'objSeries' indicates objective sequences, not constraint sequences
# The first 1 represents objID, the second 1 represents serID
# Keyword 'sim' indicates simulation data, not 'obs' observation data
```


### Validation

Validation is a key step in constructing high-precision SWAT models. To meet this requirement, SWAT-UQ-DEV includes a built-in `validate_parameters` function.

Prepare the validation file, following the same format and rules as evaluation files and sequence files. Example below:

Filename: `val_op.evl`

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

Code example:

```python
X = np.array([...])  # Optimal parameter values
res = problem.validate_parameters(X, valFile="val_op.evl")
```

The `res` returned by this function is also a Python dict, containing two fixed keywords: `objs` or `cons`, representing objective values or constraint values.

For this example, the NSE based on observation data is obtained as follows:

```python
objs = res['objs']
print(objs)
```

### User-define function

In complex application scenarios (such as optimal best management practice planning), **objective functions or constraint functions** can be difficult to define directly through evaluation files. However, SWAT-UQ provides a flexible data processing mechanism to address this challenge — first by precisely extracting simulation data based on evaluation files, then allowing users to define custom objective functions `userObjFunc` or constraint functions `userConFunc` based on these simulation data and watershed information. This enables highly customized optimization processes tailored to specific problems, thereby meeting the detailed requirements of various specialized engineering decisions.

Both functions accept a parameter named `attr`, which serves as a container for extracted simulation data and basic watershed information, and is a Python dictionary object. Its data structure is largely consistent with the return value of the `extract_series` function, but `attr` includes the following keyword:

```
- HRUInfos: A Pandas DataFrame used to record information related to HRUs (Hydrologic Response Units), containing the following columns:
  ["HRU_ID", "SUB_ID", "HRU_Local_ID", "Slope_Low", "Slope_High", "Luse", "Area"]
```

For specific examples of custom objective functions and constraint functions, please refer to [Best Management Practices Optimization](./best_management_practices.md)

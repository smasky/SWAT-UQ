# Example 1: Runoff Calibration

---

## Background

The Dongjiang watershed in Guangdong is a critical freshwater source, covering an area of over 35,000 square kilometers. It supplies water to several major cities, including Guangzhou, Shenzhen, and Hong Kong.

In this study, we use the Fengshuba and XinFengJiang sub-basins of the Dongjiang watershed as examples for runoff calibration.

We primarily present the calibration process for the Fengshuba sub-basin, which has a catchment area of 5,150 km² and an average annual rainfall of 1,581 mm. But, for helping users familiar with SWAT-UQ, the calibration of the XinFengJiang sub-basin is provided as an additional exercise.

<figure align="center">
  <img src="./pic/background_dongjiang.jpg" alt="UQPyL Overview" width="600"/>
</figure>

## SWAT Modelling

For building SWAT model of Fengshuba sub-basin, the data set used includes:

- **DEM** - The ASTER GDEM with a spatial resolution of 30 meters
- **Land Use** - The RESDC (Resource and Environmental Science Data Center) dataset
- **Soil Data** - The HWSD (Harmonized World Soil Database)
- **Meteorological Data** - The CMADS (China Meteorological Assimilation Driving Dataset)

- **Observation** - Runoff of Chinese hydrological yearbook. (2008.1.1 to 2017.12.31)

For calibration, the simulation periods are:

- **Warm up Period** - 2008.1.1 to 2011.12.31
- **Calibration Period** - 2012.1.1 to 2016.12.31
- **Validation Period** - 2017.1.1 to 2017.12.31

<figure align="center">
  <img src="./pic/example_runoff.svg" width="1000"/>
</figure>


## Problem Define

The definition of the problem refers to the process of transforming a practical problem into an abstract problem that can be described using mathematical formulas and code. 

In this example, the ultimate goal is to obtain the SWAT model whose output completely approximate to observed data. First, we need to identify the indicators to evaluate how well the SWAT model has been built. In hydrology, common indicators, e.g., NSE, R2, KGE, RMSE, PCC, and so on. Here, we use the NSE. 

Therefore, this practical problem can be abstracted into:
<figure align="center">
  <img src="./pic/example_problem.svg" width="350"/>
</figure>
Where $x$ denotes the undetermined parameters of the SWAT model; $NSE(\cdot)$ denotes the NSE operation; $sim$ denotes the simulation data obtained from running the SWAT model; $ob$ denotes the observed data from Chinese year book; $lb$, $ub$ denotes the lower and upper bound of each parameters.

Next, based on this abstracted problem, we can describe it using code within the framework of SWAT-UQ.

## Sensitivity Analysis

First, we would conduct sensitivity analysis (SA) for SWAT model. Refer to SWAT Manual and the [article](https://www.sciencedirect.com/science/article/pii/S0022169417305851)(Liu et al, 2017), following parameters are selected for SA.

| ID | Abbreviation| Where | Assign Type | Range |
|----|-------|-------|-------------|-------|
| P1 |CN2|MGT| Relative | [-0.4, 0.2] |
| P2 | GW_DELAY| GW | Value | [30, 450] |
| P3 | ALPHA_BF | GW | Value | [0.0, 1.0] |
| P4 | GWQMN | GW | Value | [0.0, 500.0] |
| P5 | GW_REVAP | GW | Value | [0.02, 0.20] |
| P6 | RCHRG_DP | GW | Value | [0.0, 1.0] |
| P7 | SOL_AWC | SOL | Relative | [0.5, 1.5] |
| P8 | SOL_K | SOL | Relative | [0.5, 15.0] |
| P9 | SOL_ALB | SOL | Relative | [0.01, 5.00] |
| P10 | CH_N2 | RTE | Value | [-0.01, 0.30] |
| P11 | CH_K2 | RTE | Value | [-0.01, 500.0] |
| P12 | ALPHA_BNK | RTE | Value | [0.05, 1.00] |
| P13 | TLAPS | SUB | Value | [-10.0, 10.0] |
| P14 | SLSUBSSN | HRU | Relative | [0.05, 25.0] |
| P15 | HRU_SLP | HRU | Relative | [0.50, 1.50] |
| P16 | OV_N | HRU | Relative | [0.10, 15.00] |
| P17 | CANMX | HRU | Value | [0.0, 100.0] |
| P18 | ESCO | HRU | Value | [0.01, 1.00] |
| P19 | EPCO | HRU | Value | [0.01, 1.00] |
| P20 | SFTMP | BSN | Value | [-5.0, 5.0] |
| P21 | SMTMP | BSN | Value | [-5.0, 5.0] |
| P22 | SMFMX | BSN | Value | [0.0, 20.0] |
| P23 | SMFMN | BSN | Value | [0.0, 20.0] |
| P24 | TIMP | BSN | Value | [0.01, 1.00] |

As the [tutorial](./swat_uq_dev.md#quick-start) introduce, 










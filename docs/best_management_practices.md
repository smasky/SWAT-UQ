# Example 2: Best Management Practices

---

## Background

When watersheds are impacted by nonpoint source pollution, the integration of the SWAT model with best management practices (BMPs) has proven to be a reliable and effective tool. This example come from the [article](https://www.sciencedirect.com/science/article/pii/S0043135424016877)(Long et al, 2025). 

<figure align="center">
  <img src="./pic/sihu.svg"  width="600"/>
  <figcaption>Information about Four Lake watershed</figcaption>
</figure>

The Four Lake watershed is located in the middle reaches of the Yangtze River and the hinterland of the Jianghan Plain. For studying the water quality of this watershed, we build the SWAT model first. The data set used includes:

- **DEM** - The ASTER GDEM with a spatial resolution of 30 meters
- **Land Use** - The CNLUCC (China Land-Use/Cover Change) dataset 
- **Soil Data** - The Second National Land Survey of Nanjing Soil Institute 1:1 million Soil Counts
- **Meteorological Data** - Regional Surface Meteorological Factor-Driven Dataset for China
- **Runoff Observation** - Runoff of Hydrographic Yearbook. (2008.1.1 to 2021.12.31)
- **Water Quality Observation** - China National Environmental Monitoring Center (2020.11 to 2021.12)

The calibration of runoff and water quality is omitted here, with a primary focus on the process of Best Management Practices (BMPs). In China, Total Nitrogen (TN) and Total Phosphorus (TP) concentrations are critical indicators for assessing lake water quality. The distributions of TN and TP in 2021.12.31 are show blew:

<p align="center"><img src="./pic/TN.svg"  width="300"/> <img src="./pic/TP.svg" width="300"/></p>
<p align="center"><strong>The distributions of TN and TP in the Four Lake basin</strong></p>

In the SWAT model used here, the lake is located within the sub-basin 51. Therefore, attention should be focused on the sub-basins 1–50, and management practices should be applied to the critical source areas, i.e., sub-basins  1, 13, 14, 20, and 31.

## Optimization

In SWAT, there are many built-in BMPs, e.g., terracing operation (BMP1), tile drainage (BMP2) ... filter strip (BMP4) ... grassed waterways (BMP7). For reduce TN and TP, the BMP4 and BMP7 are selected and applied to sub-basins 1, 13, 14, 20, and 31.

The **.ops** files in SWAT project control all BMPs. The parameters involving the filter strip are:

- **FILTER_I:** Indicator for filter strip simulation (1 for active, 0 for inactive).
- **FILTER_RATIO:** The ratio of field area to filter strip area (ha/ha). Range: 0–300.
- **FILTER_CON:** Fraction of the HRU area where 10% is densely vegetated and evenly distributed along the filter strip. This 10% area can intercept 25–75% of surface runoff.
- **FILTER_CH:** Fraction of the 10% dense area occupied by fully channelized flow (dimensionless). Fully channelized flow is not filtered by the strip.

The parameters about grassed waterways are:

- **GWATI:** Indicator for vegetative channel simulation (1 for active, 0 for inactive).
- **GWATN:** Manning's roughness coefficient for overland flow within the vegetative channel.
- **GWATSPCON:** Linear parameter for calculating sediment transport capacity in the vegetative channel.
- **GWATD:** Depth of the vegetative channel (m). If not specified, it is set to 3/64 of GWATW.
- **GWATW:** Average width of the vegetative channel (m).
- **GWATL:** Length of the vegetative channel (km).
- **GWATS:** Average slope of the vegetative channel (m/m).

To simplify the application of BMPs, we optimize only five parameters — namely, **FILTER_I**, **FILTER_RATIO**, **GWATI**, **GWATW**, and **GWATL** — across sub-basins 1, 13, 14, 20, and 31. Each sub-basin is assigned a distinct set of parameter values, resulting in a total of 25 variables. The optimization objectives are to minimize the total nitrogen (TN) and total phosphorus (TP) loads, as well as the implementation costs associated with these BMPs. Overall, this example represents a multi-objective optimization problem involving a mixture of parameters.

The type, range of parameters can be concluded by:

| Name | Type | Range|
|------|------|------|
| FILTER_I | int | 0-1 |
| FILTER_RATIO | float | 0-300|
| GWATI | int | 0-1 |
| GWATW | discrete | 1, 5, 10, 15, 20, 25, 30 |
| GWATL | float | 10-1000|

First, we edit the parameter file:

File name: `para.par`

```
Name Mode Type Min_Max Scope
FILTER_I v i 0 1 1
FILTER_RATIO v f 0 300 1
GWATI v i 0 1 1
GWATW v d 1_5_10_15_20_25_30 1
GWATL v f 10 1000 1
FILTER_I v i 0 1 13
FILTER_RATIO v f 0 300 13
GWATI v i 0 1 13
GWATW v d 1_5_10_15_20_25_30 13
GWATL v f 10 1000 13
FILTER_I v i 0 1 14
FILTER_RATIO v f 0 300 14
GWATI v i 0 1 14
GWATW v d 1_5_10_15_20_25_30 14
GWATL v f 10 1000 14
FILTER_I v i 0 1 20
FILTER_RATIO v f 0 300 20
GWATI v i 0 1 20
GWATW v d 1_5_10_15_20_25_30 20
GWATL v f 10 1000 20
FILTER_I v i 0 1 31
FILTER_RATIO v f 0 300 31
GWATI v i 0 1 31
GWATW v d 1_5_10_15_20_25_30 31
GWATL v f 10 1000 31
```

💡 **Noted:** The parameter file supports parameters with the same name, as they are distinguished by their indices.


Now, we introduce the objectives of this example. The first objective is the reduction of TN:

 $\left ( TN_{base} - TN_{now}\right ) / TN_{base}$

where $TN_{base}$ and $TN_{now}$ denote the total amount of TN flowing out of the 51 sub-basin before and after the implementation of BMPs, respectively.

The second objective is the reduction of TP:

 $\left ( TP_{base} - TP_{now}\right ) / TP_{base}$

where $TP_{base}$ and $TP_{now}$ denote the total amount of TP flowing out of the 51 sub-basin before and after the implementation of BMPs, respectively.

The third objective is the cost of BMPs. The unit cost of filter strip is 420 Yuan/ha, while the grassed waterways is 6000 Yuan/ha. Therefore, for a sub-basin, the cost is:

$Area_{AGRI}*FILTER_RATIO*FILTER_I*420 + GWATW*GWATL*GWATI*6000$

where $Area_{AGRI}$ represents the area of agricultural land use.

In this example, the objective computation cannot be completed solely through file control. Instead, the required data are obtained via file control, and the objective function (`objFunc`) is defined manually by the user.

For the first two objectives, we require the total amount of TN and TP flowing out of the 51 sub-basin in 2021.

Therefore, the file control can be:

```
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_51 : ID of RCH, or SUB, or HRU
COL_42 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_7 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )
2021.1.1 to 2021.12.31

SER_2 : ID of series data
OBJ_2 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_51 : ID of RCH, or SUB, or HRU
COL_43 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_7 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )
2021.1.1 to 2021.12.31
```






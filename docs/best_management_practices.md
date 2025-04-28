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

Overall, for setting filter strip, the parameters 'FILTER_I', 'FILTER_RATIO' and 'FILTERW' are considered. And for grassed waterways, the parameters 'GWATI', 'GWATL', 'GAWTW' are considered.

# Example 1: Runoff Calibration

---

## Background

The Dongjiang watershed in Guangdong is a critical freshwater source, covering an area of over 35,000 square kilometers. It supplies water to several major cities, including Guangzhou, Shenzhen, and Hong Kong.

In this study, we use the Fengshuba and XinFengJiang sub-basins of the Dongjiang watershed as examples for runoff calibration.

We primarily present the calibration process for the Fengshuba sub-basin, which has a catchment area of 5,150 km² and an average annual rainfall of 1,581 mm. But, for helping users familiar with SWAT-UQ, the calibration of the XinFengJiang sub-basin is provided as an additional exercise.

<figure align="center">
  <img src="./pic/background_dongjiang.jpg" alt="UQPyL Overview" width="400"/>
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


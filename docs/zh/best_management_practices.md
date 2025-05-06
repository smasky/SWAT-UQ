# 示例 2：四湖流域的最佳管理实践（BMP）优化

---

## 背景介绍

当流域受到非点源污染影响时，将 SWAT 模型与最佳管理实践（Best Management Practices，BMPs）相结合，已被证明是一种可靠且有效的工具。本示例参考了 [Long 等（2025）](https://www.sciencedirect.com/science/article/pii/S0043135424016877) 的研究成果。

<figure align="center">
  <img src="/pic/sihu.svg" width="600"/>
</figure>

<p align="center"><strong>四湖流域概况</strong></p>

四湖流域位于长江中游、江汉平原腹地。为了研究该流域水质输移过程，我们首先构建了 SWAT 模型。所使用的数据包括：

- **DEM（数字高程模型）** - 使用 ASTER GDEM，分辨率为 30 米  
- **土地利用** - 使用中国土地利用/覆盖变化（CNLUCC）数据集  
- **土壤数据** - 来自南京土壤研究所的第二次全国土壤普查（1:100 万）  
- **气象数据** - 中国区域地面气象因子驱动数据集  
- **径流观测** - 水文年鉴数据（2008.1.1 至 2021.12.31）  
- **水质观测** - 中国环境监测总站数据（2020.11 至 2021.12）

本示例省略了径流和水质的校准部分，重点介绍 **最佳管理实践（BMP）** 的优化过程。在中国，**总氮（TN）**和**总磷（TP）**是评估湖泊水质的重要指标。以下是 2021 年 12 月 31 日 TN 和 TP 的分布图：

<p align="center"><img src="/pic/TN.svg"  width="300"/> <img src="/pic/TP.svg" width="300"/></p>
<p align="center"><strong>四湖流域 TN 和 TP 的分布情况</strong></p>

在本研究的 SWAT 模型中，主湖区位于 **子流域 32**；主要入湖流量来自 **子流域 51**。此外，重点管理区域包括识别出的关键污染源子流域：**1、13、14、20、31**。

---

## 优化设置

SWAT 模型中内置了多种 BMP，例如梯田操作（BMP1）、瓦管排水（BMP2）、植被过滤带（BMP4）、植草水道（BMP7）等。

为了减少 TN 和 TP 的排放，植被过滤带（BMP4）和植草水道（BMP7）最为常用。考虑成本后，本示例仅在关键子流域（1、13、14、20、31）中应用 BMP。

SWAT 项目中的 **`.ops` 文件**用于控制 BMP 的设置，其中与植被过滤带有关的参数包括：

- `FILTER_I`：是否启用植被过滤带（1 启用，0 不启用）  
- `FILTER_RATIO`：农田面积与植被过滤带面积的比例（单位：ha/ha，范围：0–300）  
- `FILTER_CON`：植被过滤带中高密植区域占比（未启用）  
- `FILTER_CH`：通道化流量比例（未启用）

与植草水道有关的参数包括：

- `GWATI`：是否启用植草水道（1 启用，0 不启用）  
- `GWATN`、`GWATSPCON`：水力特性（略）  
- `GWATD`：沟渠深度（默认 3/64 * GWATW）  
- `GWATW`：植草水道宽度（单位：米）  
- `GWATL`：植草水道长度（单位：千米）  
- `GWATS`：坡度（单位：m/m）

为简化问题，我们每个子流域仅优化 5 个参数（FILTER_I、FILTER_RATIO、GWATI、GWATW、GWATL），共计 **25 个变量**。优化目标包括：**减少 TN 排放、减少 TP 排放、降低实施成本**，这是一个典型的 **混合型多目标优化问题**。

### 参数信息

| 名称 | 类型 | 范围 | 单位 |
|------|------|------|------|
| FILTER_I | 整数 | 0–1 | 无 |
| FILTER_RATIO | 浮点数 | 1–300 | 无 |
| GWATI | 整数 | 0–1 | 无 |
| GWATW | 离散 | 1, 5, 10, 15, 20, 25, 30 | 米 |
| GWATL | 浮点数 | 10–1000 | 千米 |

### 参数文件准备

由于每个子流域的 BMP 设置不同，需要为每个子流域单独定义这 5 个参数。

注意，离散型参数 `GWATW` 的所有可能值需通过下划线分隔列在 `Min_Max` 字段中：

```
GWATW v d 1_5_10_15_20_25_30 1
```

完整的参数文件命名为：`para_bmp.par`

```
Name Mode Type Min_Max Scope
FILTER_I v i 0_1 1
FILTER_RATIO v f 1_300 1
GWATI v i 0_1 1
GWATW v d 1_5_10_15_20_25_30 1
GWATL v f 10_1000 1
FILTER_I v i 0_1 13
FILTER_RATIO v f 1_300 13
GWATI v i 0_1 13
GWATW v d 1_5_10_15_20_25_30 13
GWATL v f 10_1000 13
FILTER_I v i 0_1 14
FILTER_RATIO v f 1_300 14
GWATI v i 0_1 14
GWATW v d 1_5_10_15_20_25_30 14
GWATL v f 10_1000 14
FILTER_I v i 0_1 20
FILTER_RATIO v f 1_300 20
GWATI v i 0_1 20
GWATW v d 1_5_10_15_20_25_30 20
GWATL v f 10_1000 20
FILTER_I v i 0_1 31
FILTER_RATIO v f 1_300 31
GWATI v i 0_1 31
GWATW v d 1_5_10_15_20_25_30 31
GWATL v f 10_1000 31
```

💡 **提示：** 文件支持重复名称参数，因为通过子流域编号进行区分。

---

### 目标函数定义

本例中包含三个优化目标：

1. **TN 减排率：**
   $$
   Obj_1 = \frac{TN_{base} - TN_{now}}{TN_{base}}
   $$
   表示应用 BMP 前后，子流域 51 的总氮流出量的相对减少量。

2. **TP 减排率：**
   $$
   Obj_2 = \frac{TP_{base} - TP_{now}}{TP_{base}}
   $$

3. **BMP 成本：**
   - 植被过滤带单价：420 元/ha  
   - 植草水道单价：200 元/ha  
   - 子流域 $i$ 的成本为：
     $$
     cost_{filter}^i = Area_{AGRI}^i \times FILTER\_RATIO \times FILTER\_I \times 420
     $$
     $$
     cost_{gwat}^i = GWATW \times GWATL / 10 \times GWATI \times 200
     $$
   - 总成本为：
     $$
     Obj_3 = \sum_{i \in \{1,13,14,20,31\}} (cost_{filter}^i + cost_{gwat}^i)
     $$

由于部分目标无法直接由 `.evl` 文件计算，需自定义目标函数。我们仍需通过 `.evl` 文件提取基础数据：

文件名：`obj_bmp.evl`

```txt
SER_1 : ID of series data
OBJ_1 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_51 : ID of RCH, or SUB, or HRU
COL_42 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_7 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )
2021.1.1 to 2021.12.31 : 

SER_2 : ID of series data
OBJ_2 : ID of objective function
WGT_1.0 : Weight of series combination
RCH_51 : ID of RCH, or SUB, or HRU
COL_43 : Extract Variable. The 'NUM' is differences with *.rch, *.sub, *.hru.
FUNC_7 : Func Type ( 1 - NSE, 2 - RMSE, 3 - PCC, 4 - Pbias, 5 - KGE, 6 - Mean, 7 - Sum, 8 - Max, 9 - Min )
2021.1.1 to 2021.12.31 : Period for data extraction
```

---

### 自定义目标函数

以下是用户自定义函数 `userObjFunc`，用于整合三大目标：

```python
TN_Base = 3.314e7
TP_Base = 3.717e6
Basins = [1, 13, 14, 20, 31]

def userObjFunc(attr):
    objs = np.zeros(3)
    x = attr["x"]
    
    # TN 减排率
    objs[0] = (TN_Base - attr['objs'][1]) / TN_Base
    
    # TP 减排率
    objs[1] = (TP_Base - attr['objs'][2]) / TP_Base
    
    HRUInfosTable = attr["HRUInfos"]
    cost = 0
    
    for i, ID in enumerate(Basins):
        areas = np.sum(HRUInfosTable.loc[HRUInfosTable.SUB_ID == ID, "Area"].tolist())
        filter_I = x[5 * i]
        filter_ratio = x[5 * i + 1]
        graw_I = x[5 * i + 2]
        graw_W = x[5 * i + 3]
        graw_L = x[5 * i + 4]
        
        cost_filter = areas * filter_ratio * filter_I * 420
        cost_graw = graw_W * graw_L * graw_I / 10 * 200
        cost += cost_filter + cost_graw
    
    objs[2] = cost
    return objs
```

---

## 开始优化

优化流程如下：

```python
import numpy as np
from swatuq import SWAT_UQ
from UQPyL.optimization.multi_objective import NSGAII

projectPath = "E:\\BMPs\\TxtInOut"
workPath = "E:\\DJ_FSB"
exeName = "swat.exe"
paraFileName = "para_bmp.par"
evalFileName = "obj_bmp.evl"
specialFileName = "special_paras1.txt"

problem = SWAT_UQ(
    projectPath=projectPath, swatExeName=exeName,
    specialFileName=specialFileName, workPath=workPath,
    paraFileName=paraFileName, evalFileName=evalFileName,
    verboseFlag=True, numParallel=10,
    userObjFunc=userObjFunc, nOutput=3,
    optType=["max", "max", "min"]
)

nsgaii = NSGAII(nPop=100, maxFEs=20000, saveFlag=True, verboseFlag=True, verboseFreq=5)
nsgaii.run(problem=problem)

# 结果将保存在 Result\Data\NSGAII_SWAT-UQ_D25_M3.hdf 中
```

最终 BMP 优化结果可视化如下所示：

<figure align="center">
  <img src="/pic/BMP.svg" width="400"/>
</figure>

---
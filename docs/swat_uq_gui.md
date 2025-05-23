#SWAT-UQ-GUI

---

## Overview of GUI Version

💡 **Noted:** SWAT-UQ-GUI is still in demo stage (Now, we advise to use SWAT-UQ-DEV). Feel free to give it a try — the full version is on the way!

**SWAT-UQ-GUI** is designed for parameter uncertainty quantification (UQ) of the **SWAT** model. Its core functionalities are built upon [UQPyL](https://github.com/smasky/UQPyL), our public released Python package for UQ. A key advantage of this platform is that users do not need to worry about coding. It seamlessly automates complete workflow from **sensitivity analysis** to **parameter optimization**, **result checking**, finally **data visualization**.

<p align="center"><img src="./assets/images/MainUI.jpg" alt="Main GUI" width="350"/> <img src="./assets/images/TableList.jpg" alt="Table List" width="350"/></p>

<p align="center"><strong>Figure 1. Get Start Card</strong></p>

SWAT-UQ-GUI consists of three modules corresponding to preparation, execution, and post-processing. 
As **Figure 1** shows, preparation involves **Parameter Setting**, **Objective Define**; Execution includes **Sensibility Analysis**, **Problem Optimization**, **Result Validation & Apply**; Post-processing provide interface for histogram (**Visualization A**) and point-line figure (**Visualization B**).

## Key Features

**End-to-end visualization:** SWAT-UQ-GUI supports fully visualized operations across the entire workflow — from problem definition and sensitivity analysis to optimization and final result validation.

**Modular & Extensible Architecture:** SWAT-UQ-GUI adopts a modular structure that's easy to extend — new methods and tools can be integrated without disrupting existing workflows.

## Quick Start

Here, we provide a Quick Start. In future plans, we will provide detailed documentation and videos.

Please choose the latest release version of SWAT-UQ.

**Demo Version has been released:** [SWAT-UQ](https://github.com/smasky/SWAT-UQ/releases/tag/v0.0)

**Step1:** On the **Get Started** interface, click the **New Project** card to create a project or the **Open Project** card to open an existing one. You can also select the **Example** card for reference cases or the **Help** card for assistance.

<p align="center"><img src="./assets/images/New_Project.png" alt="New Widget" width="300"/> <img src="./assets/images/Open_Project.png" alt="Open Widget" width="300"/></p>

<p align="center"><strong>Figure 2. New Project Card and Open Project Card</strong></p>

For the New Project Card (left picture of Figure 2), users need to provide the following information: the UQ Project name, the UQ Project path, and the SWAT Project path. After these inputs are provided, the program will verify the validity of the SWAT project files. If the verification is successful, other modules will be activated. Once the UQ Project is created, a project file named *.prj (where * represents the UQ Project name set by the user) will be saved in the specified UQ Project path.  

For the Open Project Card (right picture of Figure 2), users should select the folder that contains *.prj files. SWAT-UQ will then check the validity of the project file before proceeding.  

**Step2:** On the **Parameter Setting** and **Objective Definition**, the parameter file (.par) and the objective file (.obj) should be created. These files are crucial as they specify which parameters will be modified and what objectives will be evaluated by the program.

<p align="center"><img src="./assets/images/Parameter_Setting.jpg" alt="Main GUI" width="350"/> <img src="./assets/images/Objective_Widget.jpg" alt="Table List" width="350"/></p> 

<p align="center"><strong>Figure 3. Parameter Setting Card and Figure 4. Objective Define Card</strong></p>

To be specific, as shown in Figure 3, the Parameter Setting Card enables users to define the parameters they wish to tune. There are two ways to add parameters to the information table: either by importing them from an existing file or by clicking the Add button to open the **Parameter Selection** widget. In this table, all selectable parameters are organized by the suffix of the SWAT project files. Additionally, the search bar provides a convenient way to locate specific parameters quickly.

<p align="center"><img src="./assets/images/Parameter_Selection.png" alt="Parameter Selection" width="300"/></p>

<p align="center"><strong>Figure 4. Parameter Setting Table </strong></p>

After adding parameters, users can set the tuning mode, lower and upper bounds, and specify tuning files (default: all) for each parameter (**Figure 3 shows**). Finally, these settings should be saved to the UQ project folder by clicking "Saving Current Parameter" button.

There are also two ways to define the objective function: by importing from existing files or by user definition. For user definition, you should click "Add" button. 

<p align="center"><img src="./assets/images/Objective_Define.png" alt="Objective Define" width="300"/></p> 
<p align="center"><strong>Figure 5. Objective Define Table </strong></p>

As shown in Figure 5, users need to accurately fill in the objective ID, series ID, objective type, variable type, weight, and other relevant information. It is important to note that both the series ID and objective ID can be repeated, allowing for combinations of multiple series or weighted combinations of series. For more details, please refer to the comprehensive documentation.

After defining objectives, you can save them to the objective file. It is also allowed to define multiple objective functions within a single file.

**Step3:** Perform sensitivity analysis or parameter optimization as needed. 

Using Sensitivity Analysis as an example, as shown in the left image of Figure 6, users should first select the parameter file and objective file. Next, they choose the desired sensitivity analysis method and sampling technique. Users can then configure additional settings as required, fine-tuning the hyper-parameters to best meet project needs before proceeding. **SWAT-UQ thoughtfully displays the number of parameters and the total sample size to assist users in making informed decisions.**

Once all initial settings are all ready, click the "Next" button to proceed to the simulation and analysis process. The right image of Figure 6 displays the settings of simulation, including the selection of SWAT executable file, parallel numbers and problem name. Finally, click the "Initialize," "Sampling," and "Simulation" buttons in sequence, and wait for simulation completing. **SWAT-UQ can display the simulation progress in real-time, and users can also pause it to reconfigure settings. It would save the analysis result into UQ project folder (./Result/data/). The result file would be used to check or draw visualization picture.**

<p align="center"><img src="./assets/images/Sensibility_Analysis.jpg" alt="SA_Setup" width="400"/> <img src="./assets/images/Sensibility_Analysis_Simulation.jpg" alt="SA_Simulation" width="400"/></p>

<p align="center"><strong> Figure 6. Sensibility Analysis Interface </strong></p>

For parameter optimization, users should still select parameter file and objective file at first. When users check more than two objectives, the multi-objective optimization would be activated; conversely, if only one objective is selected, single-objective optimization is used. After fine-tuning hyper-parameters, the optimization process would be started, like sensibility analysis. **SWAT-UQ can display the optimization progress in real-time, along with the optimal parameter values for each iteration.**

<p align="center"><img src="./assets/images/Optimization.jpg" alt="OP_Setup" width="350"/> <img src="./assets/images/Optimization_Simulation.jpg" alt="OP_Simulation" width="350"/></p>

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

<p align="center"><img src="./assets/images/Validation.jpg" alt="OP_Setup" width="400"/></p>

<p align="center"><strong> Figure 8. Result Validation Interface </strong></p>

**Step 5:** Result Visualization. The current SWAT-UQ provides two types of plot pictures: a bar chart for sensitivity analysis (Visualization A Interface) and an iteration convergence plot for parameter optimization (Visualization B Interface). Of course, additional types of plots will be continuously added in future versions.
**Figures 9 and 10 shows the visualization pictures from two interfaces.**

<p align="center"><img src="./assets/images/FAST.png" alt="SA_Result" width="800"/></p>

<p align="center"><strong> Figure 9. Sensibility Analysis Visualization </strong></p>

<p align="center"><img src="./assets/images/GA.png" alt="OP_Result" width="600"/></p>

<p align="center"><strong> Figure 10. Optimization Visualization </strong></p>

Specifically, On the Visualization A and Visualization B, user can select the result file. SWAT-UQ would generates initial visualizations. **Users can click the "Config" button to open the settings panel and tune various parameters of the plot based on the preset values, as Figure 11 indicates.**

<p align="center"><img src="./assets/images/Visualization_A.png" alt="Visualization_A" width="350"/> <img src="./assets/images/Visualization_B.png" alt="Visualization_B" width="350"/></p>

<p align="center"><strong> Figure 11. Visualization Interface </strong></p>

**This concludes the Quick Start section for SWAT-UQ. For more advanced operations, please refer to the documentation.**
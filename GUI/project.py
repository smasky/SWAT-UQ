import os
import re
import glob
import GUI.data
import numpy as np
import itertools
import time
from importlib.resources import path
from datetime import datetime, timedelta
from .swat_uq_core import SWAT_UQ_Flow
from PyQt5.QtWidgets import QApplication
from .woker import InitWorker, ReadWorker
#C++ Module
from .pyd.swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation
from UQPyL.DoE import LHS, FFD, Morris_Sequence, FAST_Sequence, Sobol_Sequence, Random
from UQPyL.sensibility import Sobol, Delta_Test, FAST, RBD_FAST, Morris, RSA
from PyQt5.QtCore import QThread, Qt, QDate
class Project:
    
    INT_MODE={0: 'r', 1: 'v', 2: 'a'}; MODE_INT={'r': 0, 'v':1, 'a':2}
    INT_OBJTYPE={0: 'NSE', 1: 'RMSE', 2: 'PCC', 3: 'Pbias', 4: 'KGE'}; OBJTYPE_INT={'NSE': 0, 'RMSE':1, 'PCC':2, 'Pbias':3, 'KGE':4}
    INT_VAR={0: 'Flow'}; VAR_INT={'Flow': 0}
    
    
    swatPath=""
    projectPath=""
    projectName=""
    swatExe=""
    paraPath=""
    proPath=""
    parameters={}
    objs={}
    paraList={}
    inverseParaList={}
    btnSets=[]
    processBar=None
    
    OBJTYPE={ 0: "NSE", 1: "RMSE", 2: "PCC", 3: "Pbias", 4: "KGE" }
    VARIABLE={ 0 : "Flow" }
    paraInfos=[];bsnInfos={};bsnFile={};modelInfos={}
    
    SA_METHOD={'Sobol': 'Sobol', 'Delta Test': 'Delta_Test', 'FAST': 'FAST', 'RBD-FAST': 'RBF-FAST', 'Morris': 'Morris', 'RSA': 'RSA'}
    SAMPLE_METHOD={'Full Factorial Design': 'FFD', 'Latin Hyper Sampling': 'LHS', 'Random': 'Random', 'Fast Sequence': 'FAST_Sequence', 'Morris Sequence': 'Morris_Sequence', 'Sobol Sequence': 'Sobol_Sequence'}
    SAInfos={}
    hyper={}
    samplingHyper={}
    
    @classmethod
    def openProject(cls, project_name, work_path, swat_path):
        
        projectInfos={}
        projectInfos["projectName"]=project_name
        projectInfos["projectPath"]=work_path
        projectInfos['swatPath']=swat_path
        cls.projectInfos=projectInfos
        
        cls.loadModel()

    @classmethod
    def loadModel(cls):
        
        cls.thread=QThread()
        cls.worker=InitWorker()
        
        def run():
            cls.worker.initModel(cls.projectInfos)
        
        def accept(infos):
            cls.modelInfos=infos
            cls.thread.quit()
            cls.thread.deleteLater()
            cls.worker.deleteLater()
            # statusBar.stop()
        
        cls.worker.moveToThread(cls.thread)
        cls.worker.result.connect(accept, Qt.QueuedConnection)
        cls.thread.started.connect(run)
        cls.thread.start()
        
    @classmethod
    def calDate(cls, observeDate):
        
        beginY, beginI, _ = observeDate[0]
        endY, endI, _ = observeDate[-1]
        printFlag=cls.modelInfos["printFlag"]
        
        if printFlag==1:
            startDate=datetime(beginY, 1, 1)+timedelta(days=beginI-1)
            endDate=datetime(endY, 1, 1)+timedelta(days=endI-1)
        else:
            startDate=datetime(beginY, beginI, 1)
            endDate=datetime(endY, endI, 1)
        
        return startDate, endDate
    
    @classmethod
    def calDateIndex(cls, beginDate, delta):
        
        printFlag=cls.modelInfos["printFlag"]
        baseDate=QDate(beginDate.year(), 1, 1)
        
        if printFlag==1:
            nowDate=beginDate.addDays(delta)
            index=baseDate.daysTo(nowDate)
            return nowDate.year(), index
        else:
            nowDate=beginDate.addMonths(delta)
            return nowDate.year(), nowDate.month()-baseDate.month+1

                
    
    
    @classmethod #TODO
    def initialize(cls):
        
        cls.readHRUInfos()
        cls.readFigCio()
            
    @classmethod 
    def importProFromFile(cls, path):
        
        cls.worker=ReadWorker()
        infos=cls.worker.readObjFile(path)
        
        return infos
                        
    @classmethod
    def importParaFromFile(cls, path):
        
        Infos=[]
        
        with open(path, 'r') as f:
            
            lines=f.readlines()
            
            for line in lines:
                
                content=line.split()
                
                name=content[0]
                
                ext=cls.modelInfos['totalParaList'].loc[name, 'file_name']
                
                mode=cls.MODE_INT[content[1]]
                
                lb=content[2]; ub=content[3]
                
                position=" ".join(content[4:])
                
                paraInfo=[name, ext, mode, lb, ub, position]

                Infos.append(paraInfo)
                
        return Infos
    
    @classmethod #TODO
    def saveParaFile(cls, infos, path):
        
        with open(path, 'w') as f:
            
            lines=[" ".join(info)+"\n" for info in infos]
            
            f.writelines(lines)
            
    
    @classmethod #TODO
    def saveProFile(cls, path, lines):
        
        with open(path, 'w') as f:
            f.writelines(lines)
        
    @classmethod#TODO find
    def checkParaFile(cls):
        
        par_files = glob.glob(os.path.join(cls.projectPath, "*.par"))
        files=[os.path.basename(file_path) for file_path in par_files]
        return files
    
    @classmethod#TODO find
    def checkProFile(cls):
        
        pro_files=glob.glob(os.path.join(cls.projectPath, "*.pro"))
        files=[os.path.basename(file_path) for file_path in pro_files]
        return files
    
    @classmethod#TODO find
    def checkSwatExe(cls):
        
        if cls.swatPath!='':
            exe_name= glob.glob(os.path.join(cls.swatPath, "*.exe"))
            name=[os.path.basename(file_path) for file_path in exe_name]
            return name
        else:
            return []
    
    @classmethod #TODO
    def initializeProject(cls):
        lines=[]
        ################
        lines.append("="*25+"Model Information"+"="*25)
        beginDate=cls.modelInfos["beginDate"].strftime("%Y%m%d")
        endDate=cls.modelInfos['endDate'].strftime('%Y%m%d')
        lines.append(f"The time period of simulation is: {beginDate} to {endDate}")
        lines.append(f"The number of simulation days is: {cls.modelInfos['simulation_days']}")
        lines.append(f"The number of output skip years is: {cls.modelInfos['output_skip_years']}")
        lines.append(f"The number of basins is: {cls.modelInfos['nBsn']}")
        lines.append(f"The number of HRUs is: {cls.modelInfos['nHru']}")
        lines.append(f"The number of Reaches is: {cls.modelInfos['nRch']}")

        if cls.modelInfos["print_flag"]==0:
            lines.append("The print flag of SWAT is: "+"monthly")
        else:
            lines.append("The print flag of SWAT is: "+"daily")
        lines.append("="*70)
        lines.append("\n"*1)
        #######################
        lines.append("="*20+"Parameter Information"+"="*20)
        
        name_formatted="{:^20}".format("Parameter name")
        # type_formatted="{:^7}".format("Type")
        mode_formatted= "{:^7}".format("Mode")
        low_bound_formatted="{:^15}".format("Lower bound")
        up_bound_formatted="{:^15}".format("Upper bound")
        assign_hru_id_formatted="{:^20}".format("HRU ID or Sub_HRU ID")
        lines.append(name_formatted+"||"+mode_formatted+"||"+low_bound_formatted+"||"+up_bound_formatted+"||"+assign_hru_id_formatted)
        
        for para in cls.paraInfos:
            name_formatted="{:^20}".format(para[0])
            # type_formatted="{:^7}".format("Float" if self.disc_var[i]==0 else "int")
            mode_formatted= "{:^7}".format(cls.INVERSETUNEMODE[para[2]])
            low_bound_formatted="{:^15}".format(para[3])
            up_bound_formatted="{:^15}".format(para[4])
            assign_hru_id_formatted="{:^20}".format(para[5])
            lines.append(name_formatted+"||"+mode_formatted+"||"+low_bound_formatted+"||"+up_bound_formatted+"||"+assign_hru_id_formatted)
        
        return lines
    
    @classmethod #TODO
    def createSwatUQ(cls):
        file_path=cls.swatPath
        temp_path=os.path.join(cls.projectPath, "temp")
        swat_exe_name=cls.swatExe
        observed_file_name=os.path.join(cls.projectPath, cls.proPath)
        paras_file_name=os.path.join(cls.projectPath, cls.paraPath)
        
        swat_cup=SWAT_UQ_Flow(work_path=file_path,
                    paras_file_name=paras_file_name,
                    observed_file_name=observed_file_name,
                    swat_exe_name=swat_exe_name,
                    temp_path=temp_path,
                    max_threads=10, num_parallel=3,
                    verbose=True)
        
        # swat_cup.initialize()
        qThread1=QThread()
        swat_cup.moveToThread(qThread1)
        cls.swat_cup=swat_cup
        qThread1.started.connect(swat_cup.test)
        swat_cup.finished.connect(cls.move_back_to_main_thread)  # 任务完成后退出线程
        swat_cup.finished.connect(qThread1.quit)
        # swat_cup.finished.connect(swat_cup.deleteLater)  # 清理 worker
        # cls.qThread.finished.connect(cls.on_thread_finished)
        
        qThread1.start()
        
        qThread1.wait()
        
        # swat_cup.moveToThread(QApplication.instance().thread())
        
        qThread2=QThread()
        swat_cup.moveToThread(qThread2)
        # cls.qThread.started.disconnect(swat_cup.initialize)
        qThread2.started.connect(swat_cup.evaluate)
        qThread2.start()
        qThread2.wait()
        # cls.qThread.quit()
        # problem.moveToThread(None)
        # swat_cup.moveToThread(cls.qThread)
        cls.model=swat_cup
        # cls.qThread=qThread2
        return swat_cup.verbose    
    
    @classmethod#TODO
    def sampling(cls):
        
        problem=cls.model
        hyper=cls.samplingHyper
        initHyper=hyper['__init__']
        sampleHyper=hyper['sample']
        sampler=eval(cls.SAMPLE_METHOD[cls.SAInfos['sampling']])(problem=problem, **initHyper)
        x=sampler.sample(**sampleHyper, nx=problem.nInput)
        return x
    
    @classmethod #TODO
    def simulation(cls, x):
        
        problem=cls.model
        # problem.project=cls
        problem.X=x

        qThread2=QThread()
        problem.moveToThread(qThread2)
        # 连接信号和槽
        qThread2.started.connect(problem.evaluate)  # 当线程开始时，运行任务
        problem.progress.connect(cls.update_progress)  # 更新进度条
        # problem.finished.connect(cls.task_finished)  # 当任务完成时
        problem.finished.connect(qThread2.quit)  # 任务完成后退出线程
        problem.finished.connect(problem.deleteLater)  # 清理 worker
        qThread2.finished.connect(qThread2.deleteLater)  # 清理线程

        # 启动线程
        
        qThread2.start()
        
        qThread2.quit()
    
    @classmethod
    def update_progress(cls, value):
        cls.processBar.setValue(value)
    
    @classmethod
    def initProject(cls):
        cls.thread = QThread()
        cls.worker = InitWorker()
        def run():
            work_path=cls.swatPath
            temp_path=os.path.join(cls.projectPath, "temp")
            swat_exe_name=cls.swatExe
            cls.worker.initQThread(work_path, temp_path, swat_exe_name, 12, 5, cls.paraInfos)
            
        def accept(infos):
            cls.projectInfos=infos["projectInfos"]
            cls.modelInfos=infos["modelInfos"]
            cls.problemInfos=infos["problemInfos"]
            cls.thread.quit()
            cls.thread.deleteLater()
            cls.worker.deleteLater()
            cls.thread.wait()
            print("completed")
        cls.worker.moveToThread(cls.thread)
        cls.worker.result.connect(accept, Qt.QueuedConnection)
        cls.thread.started.connect(run)
        cls.thread.start()
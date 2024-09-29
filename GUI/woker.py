from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import re
import os
import numpy as np
from .pyd.swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation
from datetime import datetime, timedelta
import itertools
import pandas as pd
import tempfile

class VerboseWorker(QObject):
    
    finished = pyqtSignal()
    modelInfos=None
    paraInfos=None
    projectInfos=None
    objInfos=None
    def outputVerbose(self):
        
        ####################Project Information######################
        verboseInfos=[]
        title="="*25+"Project setting"+"="*25
        verboseInfos.append(f"The path of SWAT project is: {self.projectInfos['work_path']}")
        self.verbose.append(f"The file name of optimizing parameters is: {self.projectInfos['paras_file_name']}")
        self.verbose.append(f"The file name of observed data is: {self.projectInfos['observed_file_name']}")
        self.verbose.append(f"The name of SWAT executable is: {self.projectInfos['swat_exe_name']}")
        self.verbose.append(f"Temporary directory has been created in: {self.projectInfos['work_temp_dir']}")
        self.verbose.append("="*len(title))
        
        ####################Model Information#############################
        title="="*25+"Model Information"+"="*25
        verboseInfos.append(title)
        beginDate=self.modelInfos["beginDate"].strftime("%Y%m%d")
        endDate=self.modelInfos['endDate'].strftime('%Y%m%d')
        
        verboseInfos.append(f"The time period of simulation is: {beginDate} to {endDate}")
        verboseInfos.append(f"The number of simulation days is: {self.modelInfos['simulationDays']}")
        verboseInfos.append(f"The number of output skip years is: {self.modelInfos['outputSkipYears']}")
        verboseInfos.append(f"The number of basins is: {self.modelInfos['nSub']}")
        verboseInfos.append(f"The number of HRUs is: {self.modelInfos['nHru']}")
        verboseInfos.append(f"The number of Reaches is: {self.modelInfos['nRch']}")
        
        if self.modelInfos["print_flag"]==0:
            verboseInfos.append("The output flag of SWAT is: "+"monthly")
        else:
            verboseInfos.append("The output flag of SWAT is: "+"daily")
        
        verboseInfos.append("="*len(title))
        
        ########################Parameter Information###################
        verboseInfos+=self.outputParaInfo()
        
        ########################
    def outputObjInfo(self):
        
        verboseInfos=[]
        
        title="="*25+"Observed Information"+"="*25
        
        verboseInfos.append(title)
        verboseInfos.append(f"The number of observed data series is: {self.objInfos['nSeries']}")
        verboseInfos.append(f"The number of observed data points is: {self.objInfos['nObjs']}")
        
        objFormatted=f"{'Objective ID':^10}"
        serIDFormatted=f"{'Series ID':^10}"
        rchFormatted=f"{'Reach ID':^10}"
        objTypeFormatted=f"{'Objective Type':^10}"
        varFormatted=f"{'Variable':^10}"
        weightFormatted=f"{'Weight':^10}"
        readLineFormatted=f"{'Read Line':<30}"
        
        verboseInfos.append(f"{objFormatted}||{serIDFormatted}||{rchFormatted}||{objTypeFormatted}||{varFormatted}||{weightFormatted}||{readLineFormatted}")
        
        for obj, series in self.objInfos['objComb'].items():
            for id in series:
                objFormatted=f"{obj:^10}"
                serIDFormatted=f"{id:^10}"
                rchFormatted=f"{self.objInfos['rch'][id]:^10}"
                objTypeFormatted=f"{self.objInfos['objType'][id]:^10}"
                varFormatted=f"{self.objInfos['var'][id]:^10}"
                weightFormatted=f"{self.objInfos['weight'][id]:^10.2f}"
                
                readLines=self.objInfos['readLines'][id]
                lineStr=""
                for line in readLines:
                    lineStr+=str(line[0])+"-"+str(line[1])+" "
                readLineFormatted=f"{lineStr:<30}"
                
                verboseInfos.append(f"{objFormatted}||{serIDFormatted}||{rchFormatted}||{objTypeFormatted}||{varFormatted}||{weightFormatted}||{readLineFormatted}")
        
        verboseInfos.append("="*len(title))
        
    def outputParaInfo(self):
        
        TUNEMODE={0: "relative", 1: "value", 2: "add"}
        
        verboseInfos=[]
        
        title="="*25+"Model Information"+"="*25
        verboseInfos.append(title)
        nameFormatted=f"{'Parameter name':^20}"
        modeFormatted=f"{'Mode':^7}"
        lbFormatted=f"{'Lower Bound':^15}"
        ubFormatted=f"{'Upper Bound':^15}"
        sub_hruFormatted=f"{'HRU ID or Sub_HRU ID':^20}"
        head=f"{nameFormatted}||{modeFormatted}||{lbFormatted}||{ubFormatted}||{sub_hruFormatted}"
        
        verboseInfos.append(head)
        
        for param in self.paraInfos:
            nameFormatted=f"{param[0]:^20}"
            modeFormatted=f"{TUNEMODE[param[2]]:^7}"
            lbFormatted=f"{param[3]:^15.2f}"
            ubFormatted=f"{param[4]:^15.2f}"
            sub_hruFormatted=f"{param[5]:^20}"
            verboseInfos.append(f"{nameFormatted}||{modeFormatted}||{lbFormatted}||{ubFormatted}||{sub_hruFormatted}")
        
        return verboseInfos
    
    
class ReadWorker(QObject):
    
    finished = pyqtSignal()
    result = pyqtSignal(dict)
    
    
    paraList=None
    
    def readObjFile(self, path):
        
        paraInfos={}
        with open(path, 'r') as f:
            lines=f.readlines()
        
        patternObj=re.compile(r'OBJ_(\d+)\s+')
        patternSer=re.compile(r'SER_(\d+)\s+')
        patternRch=re.compile(r'REACH_(\d+)\s+')
        patternType=re.compile(r'TYPE_(\d+)\s+')
        patternVar=re.compile(r'VAR_(\d+)\s+')
        patternWeight=re.compile(r'(\d+\.?\d*)')
        patternNum=re.compile(r'(\d+)')
        
        patternValue=re.compile(r'(\d+)\s+(\d+)\s+(\d+\.?\d*)')
        
        i=2
        
        while i<len(lines):
            line=lines[i]
            
            match=patternObj.match(line)
            if match:
                
                objID=int(match.group(1))
                paraInfos.setdefault(objID, {})
                
                serID=int(patternSer.match(lines[i+1]).group(1))
                reachID=int(patternRch.match(lines[i+2]).group(1))
                objType=int(patternType.match(lines[i+3]).group(1))
                varType=int(patternVar.match(lines[i+4]).group(1))
                weight=float(patternWeight.match(lines[i+5]).group(1))
                num=int(patternNum.match(lines[i+6]).group(1))
                
                i=i+7
                
                line=lines[i]
                while patternValue.match(line) is None:
                    i+=1
                    line=lines[i]
                
                n=0; data=[]
                while True:
                    line=lines[i];n+=1
                    match=patternValue.match(line)
                    year, index, value=int(match.group(1)), int(match.group(2)), float(match.group(3))
                    data.append((year, index, value))
                    
                    if n==num:
                        break
                    else:
                        i+=1
                
                paraInfos[objID]={"objID": objID, "serID": serID, "reachID": reachID, "objType": objType, "varType": varType, "weight": weight, "data": data}
        
        self.result.emit(paraInfos)
    
    def readParaFile(self, path):
        
        MODE={'r': 'Relative', 'v': 'Value', 'a': 'Add'}
        paraInfos=[]
        
        with open(path, 'r') as f:
            lines=f.readlines()
            
            for line in lines:
                
                content=line.split()
                
                name=content[0]
                ext=self.paraList[name]
                mode=MODE[content[1]]
                
                lb=float(content[2]); ub=float(content[3])
                
                position=" ".join(content[4:])
                
                paraInfos=[name, ext, mode, lb, ub, position]
        
        return paraInfos

class InitWorker(QObject):
    
    result = pyqtSignal(dict)
    Pro=None
    def __init__(self, project):
        super().__init__()
        self.Pro=project
    
    def initProject(self):
        
        
        ProjectInfos={}
        ProjectInfos["work_path"]=self.Pro.work_path
        if self.Pro.temp_path is None:
            work_temp_dir=tempfile.mkdtemp()
        
        ProjectInfos["temp_path"]=self.Pro.work_temp_dir
        ProjectInfos["swat_exe_name"]=self.Pro.swat_exe_name

        ProjectInfos["max_threads"]=self.Pro.max_threads
        ProjectInfos["num_parallel"]=self.Pro.num_parallel
        # print('111')
        # self.result.emit(ProjectInfos)
        # print('222')
        self.Pro.Projectss=ProjectInfos
        return
        
    
    def initModel(self, projectInfos):
        
        modelInfos={}
        work_path=projectInfos["work_path"]
        
        paras=["IPRINT", "NBYR", "IYR", "IDAF", "IDAL", "NYSKIP"]
        pos=["default"]*len(paras)
        dict_values=read_value_swat(self.work_path, "file.cio", paras, pos, 0)
        begin_date=datetime(int(dict_values["IYR"][0]), 1, 1)+timedelta(int(dict_values['IDAF'][0])-1)
        end_date=datetime(int(dict_values["IYR"][0])+int(dict_values['NBYR'][0])-1, 1, 1)+timedelta(int(dict_values['IDAL'][0])-1)
        simulation_days=(end_date-begin_date).days+1
        output_skip_years=int(dict_values["NYSKIP"][0])
        output_skip_days=(datetime(int(dict_values["IYR"][0])+output_skip_years, 1, 1)+timedelta(int(dict_values['IDAF'][0])-1)-begin_date).days
        begin_record=begin_date+timedelta(output_skip_days)
        
        modelInfos["printFlag"]=int(dict_values["IPRINT"][0])
        modelInfos["beginDate"]=begin_date
        modelInfos["endDate"]=end_date
        modelInfos["outputSkipYears"]=output_skip_years
        modelInfos["simulationDays"]=simulation_days
        modelInfos["beginRecord"]=begin_record
        
        subBasin_Hru={}
        with open(os.path.join(work_path, "fig.fig"), "r") as f:
            lines=f.readlines()
            for line in lines:
                match = re.search(r'(\d+)\.sub', line)
                if match:
                    subBasin_Hru[match.group(1)]=[]
        
        for sub in list(subBasin_Hru.keys()):
            file_name=sub+".sub"
            with open(os.path.join(work_path, file_name), "r") as f:
                lines=f.readlines()
                for line in lines:
                    match = re.search(r'(\d+)\.hru', line)
                    if match:
                        subBasin_Hru[sub].append(match.group(1))
        
        modelInfos["sub_hru"]=subBasin_Hru
        modelInfos["subList"]=list(subBasin_Hru.keys())
        modelInfos["nSub"]=len(modelInfos["subBasinList"])
        modelInfos['hruList']=list(itertools.chain.from_iterable(subBasin_Hru.values()))
        modelInfos["nHru"]=len(modelInfos["hruList"])
        modelInfos["nRch"]=len(modelInfos["hruList"])
        modelInfos["totalParaList"]=pd.read_excel(os.path.join(work_path, 'SWAT_paras_files.xlsx'), index_col=0)
        
        self.result.emit(modelInfos)
        
     
    def initProblem(self, projectInfos, modelInfos, paraInfos, objInfos):
        
        lb=[]
        ub=[]
        mode=[]
        position=[]
        xLabels=[]
        
        for paraInfo in paraInfos:
            name=paraInfo[0]
            mode=paraInfo[2]
            lb=paraInfo[3]
            ub=paraInfo[4]
            position=paraInfo[5]
        
        lb=np.array(lb).reshape(1, -1)
        ub=np.array(ub).reshape(1, -1)
        nInput=len(xLabels)
        
        sub_hru=modelInfos["sub_hru"]
    
    def recordDefault(self, paraInfos):
        
        for paraInfo in paraInfos:
            
            name=paraInfo[0]
            
            
                  
        
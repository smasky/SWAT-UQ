from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
import re
import os
import numpy as np
from .pyd.swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation
from datetime import datetime, timedelta
import itertools
import pandas as pd
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    
    def readObjFile(self, path):
        
        proInfos={}
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
                proInfos.setdefault(objID, [])
                
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
                
                proInfos[objID].append({"objID": objID, "serID": serID, "reachID": reachID, "objType": objType, "varType": varType, "weight": weight, "observeData": data})
            i+=1
        return proInfos
    
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

    def __init__(self):
        super().__init__()

    def initQThread(self, max_threads, num_parallel, projectInfos, paraInfos):

        modelInfos=self.initModel(projectInfos)
        
        defaultVar=self.recordDefault(projectInfos, paraInfos, modelInfos)
        
        problemInfos=self.initProblem(paraInfos)
        
        problemInfos['defaultVar']=defaultVar
        
        self.result.emit({"projectInfos": projectInfos, "modelInfos": modelInfos, "problemInfos": problemInfos})
    
    def initModel(self, projectInfos):
        
        modelInfos={}
        work_path=projectInfos["swatPath"]
        
        paras=["IPRINT", "NBYR", "IYR", "IDAF", "IDAL", "NYSKIP"]
        pos=["default"]*len(paras)
        dict_values=read_value_swat(work_path, "file.cio", paras, pos, 0)
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
        sub_hru_simply={}
        with open(os.path.join(work_path, "fig.fig"), "r") as f:
            lines=f.readlines()
            for line in lines:
                match = re.search(r'(\d+)\.sub', line)
                if match:
                    subBasin_Hru[match.group(1)]=[]
                    sub_hru_simply[match.group(1)[:5].lstrip('0')]=[]
        
        for sub in list(subBasin_Hru.keys()):
            file_name=sub+".sub"
            with open(os.path.join(work_path, file_name), "r") as f:
                lines=f.readlines()
                for line in lines:
                    match = re.search(r'(\d+)\.hru', line)
                    if match:
                        subBasin_Hru[sub].append(match.group(1))
                        sub_hru_simply[sub[:5].lstrip('0')].append(match.group(1)[-4:].lstrip('0'))
                        
        modelInfos["sub_hru_simply"]=sub_hru_simply
        modelInfos["sub_hru"]=subBasin_Hru
        modelInfos["subList"]=list(subBasin_Hru.keys())
        modelInfos["nSub"]=len(modelInfos["subList"])
        modelInfos['hruList']=list(itertools.chain.from_iterable(subBasin_Hru.values()))
        modelInfos["nHru"]=len(modelInfos["hruList"])
        modelInfos["nRch"]=len(modelInfos["hruList"])
        
        totalParaList=pd.read_excel(os.path.join(work_path, 'SWAT_paras_files.xlsx'), index_col=0)
        modelInfos["totalParaList"]=totalParaList
        
        para_file={}
        for index, row in totalParaList.iterrows():
            para_name=index
            file_name=row['file_name']
            para_file.setdefault(file_name, [])
            para_file[file_name].append(para_name)
        
        modelInfos['para_file']=para_file
        
        self.result.emit(modelInfos)
     
    def initProblem(self, paraInfos):
        
        problemInfos={}
        
        lb=[]
        ub=[]
        xLabels=[]
        
        for paraInfo in paraInfos:
            xLabels.append(paraInfo[0])
            lb.append(paraInfo[3])
            ub.append(paraInfo[4])
        
        lb=np.array(lb).reshape(1, -1)
        ub=np.array(ub).reshape(1, -1)
        
        problemInfos["xLabels"]=xLabels
        problemInfos["lb"]=lb
        problemInfos['ub']=ub
        
        return problemInfos
        
    def recordDefault(self, projectInfos, paraInfos, modelInfos):
        totalParaInfos=modelInfos["totalParaList"]
        hruSuffix=["chm", "gw", "hru", "mgt", "sdr", "sep", "sol"]
        subBasinSuffix=["pnd", "rte", "sub", "swq", "wgn", "wus"]
        hruList=modelInfos["hruList"]
        sub_hruList=modelInfos["sub_hru"]
        subList=modelInfos["subList"]
        
        file_var={}
        
        for i, paraInfo in enumerate(paraInfos):
            
            name=paraInfo[0]
            suffix=paraInfo[1]
            mode=paraInfo[2]
            position="default"
            
            if(totalParaInfos.query('para_name==@name')['type'].values[0]=="int"):
                data_type_=0
            else:
                data_type_=1
            
            suffix=suffix.lower()
            
            if suffix in hruSuffix:
                if paraInfo[5]=='all':
                    files=[e+".{}".format(suffix) for e in hruList]
                else:
                    files=[]
                    for comb in paraInfo[5].split(" "):
                        if "(" not in comb:
                            code=f"{'0' * (9 - 4 - len(comb))}{comb}{'0'*4}"
                            for hru in sub_hruList[comb]:
                                files.append(f"{hru}.{suffix}")
                        else:
                            sub=comb.split("(")[0]
                            hru=comb.split("(")[1].strip(")").split(',')
                            
                            for e in hru:
                                code=f"{'0' * (9 - 4 - len(sub))}{sub}{'0'*(4-len(e))}{e}"
                                files.append(f"{code}.{suffix}")
            elif suffix in subBasinSuffix:
                if paraInfo[5]=='all':
                    files=[e+".{}".format(suffix) for e in subList]
                else:
                    comb=paraInfo[5].spilt()
                    files=[f"{sub}.{suffix}" for sub in comb]
            elif suffix=="bsn":
                files=["basins.bsn"]
            
            for file in files:
                file_var.setdefault(file, {})
                file_var[file].setdefault("index", [])
                file_var[file].setdefault("mode", [])
                file_var[file].setdefault("name", [])
                file_var[file].setdefault("position", [])
                file_var[file].setdefault("type", [])
                file_var[file]['index'].append(i)
                
                if mode=="v":
                    file_var[file]["mode"].append(0)
                elif mode=="r":
                    file_var[file]["mode"].append(1)
                elif mode=="a":
                    file_var[file]["mode"].append(2)
                
                file_var[file]["name"].append(name)
                file_var[file]["position"].append(position)
                file_var[file]["type"].append(data_type_)
        
        for file_name, infos in file_var.items():
            print(projectInfos["work_path"], file_name)
            read_value_swat(projectInfos["work_path"], file_name, infos["name"], infos["position"], 1)
        
        with ThreadPoolExecutor(max_workers=projectInfos["max_threads"]) as executor:
            futures=[]
            for file_name, infos in file_var.items():
                futures.append(executor.submit(read_value_swat, projectInfos["work_path"], file_name, infos["name"], infos["position"], 1))
        
        for future in as_completed(futures):
            res=future.result()
            for key, items in res.items():
                values=' '.join(str(e) for e in items)
                _, file_name=key.split("|")
                file_var[file_name].setdefault("default", [])
                file_var[file_name]["default"].append(values)
        return file_var

                
                
                
                
                
                        
                        
                
            
            
            
                  
        
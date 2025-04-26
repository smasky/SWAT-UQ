
import re
import os
import queue
import time
import itertools
import numpy as np
import pandas as pd
import subprocess
from datetime import datetime, timedelta
# from UQPyL.problems import Problem
from concurrent.futures import ThreadPoolExecutor, as_completed
from importlib.resources import path
import GUI.data

from PyQt5.QtCore import QThread, QObject, pyqtSignal
from .pyd.swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation
class VerboseWorker(QObject):
    
    def __init__(self, projectInfos, modelInfos, paraInfos, objInfos, runInfos):
        
        self.projectInfos=projectInfos
        self.modelInfos=modelInfos
        self.runInfos=runInfos
        self.paraInfos=paraInfos
        self.objInfos=objInfos

        self.verboseWidth=runInfos['verboseWidth']
        
    def outputVerbose(self):
        
        ####################Project Information######################
        verboseInfos=[]
        title="Project setting"
        spacing=int((self.verboseWidth-len(title))/2)-1
        verboseInfos.append("="*spacing+title+"="*spacing)
        
        verboseInfos.append(f"The path of SWAT project is: {self.projectInfos['swatPath']}")
        verboseInfos.append(f"The path of UQ project is {self.projectInfos['projectPath']}") 
        verboseInfos.append(f"The file name of optimizing parameters is: {self.runInfos['paraPath']}") #TODO
        verboseInfos.append(f"The file name of observed data is: {self.runInfos['objPath']}") #TODO
        verboseInfos.append(f"The name of SWAT executable is: {self.runInfos['swatExe']}")
        verboseInfos.append(f"Temporary directory has been created in: {self.runInfos['tempPath']}")
        verboseInfos.append(f"The number of subprocess to run SWAT: {self.runInfos['numParallel']}")
        
        ####################Model Information#############################
        title="Model Information"
        spacing=int((self.verboseWidth-len(title))/2)-1
        verboseInfos.append("="*spacing+title+"="*spacing)
        
        verboseInfos.append(title)
        beginDate=self.modelInfos["beginDate"].strftime("%Y%m%d")
        endDate=self.modelInfos['endDate'].strftime('%Y%m%d')
        
        verboseInfos.append(f"The time period of simulation is: {beginDate} to {endDate}")
        verboseInfos.append(f"The number of simulation days is: {self.modelInfos['simulationDays']}")
        verboseInfos.append(f"The number of output skip years is: {self.modelInfos['outputSkipYears']}")
        verboseInfos.append(f"The number of basins is: {self.modelInfos['nSub']}")
        verboseInfos.append(f"The number of HRUs is: {self.modelInfos['nHru']}")
        verboseInfos.append(f"The number of Reaches is: {self.modelInfos['nRch']}")
        
        if self.modelInfos["printFlag"]==0:
            
            verboseInfos.append("The output flag of SWAT is: "+"monthly")
            
        else:
            
            verboseInfos.append("The output flag of SWAT is: "+"daily")
        
        # verboseInfos.append("="*len(title))
        
        ########################Parameter Information###################
        verboseInfos+=self.outputParaInfo()
        
        verboseInfos+=self.outputObjInfo()
        
        return verboseInfos
        ########################
    def outputObjInfo(self):
        
        verboseInfos=[]
        
        title="Observed Information"
        spacing=int((self.verboseWidth-len(title))/2)-1
        verboseInfos.append("="*spacing+title+"="*spacing)
        
        verboseInfos.append(title)
        
        objFormatted=f"{'Objective ID':^15}"
        serIDFormatted=f"{'Series ID':^15}"
        rchFormatted=f"{'Reach ID':^15}"
        objTypeFormatted=f"{'Objective Type':^15}"
        varFormatted=f"{'Variable':^15}"
        weightFormatted=f"{'Weight':^15}"
        readLineFormatted=f"{'Read Line':<30}"
        
        verboseInfos.append(f"{objFormatted}||{serIDFormatted}||{rchFormatted}||{objTypeFormatted}||{varFormatted}||{weightFormatted}||{readLineFormatted}")
        
        for objID, Ser in self.objInfos.items():
            
            for series in Ser:
                objID=series['objID']
                serID=series['serID']
                reachID=series['reachID']
                objType=series['objType']
                varType=series['varType']
                weight=series['weight']
                readLines=series['readLines']
                
                objFormatted=f"{objID:^15}"
                serIDFormatted=f"{serID:^15}"
                rchFormatted=f"{reachID:^15}"
                objTypeFormatted=f"{objType:^15}"
                varFormatted=f"{varType:^15}"
                weightFormatted=f"{weight:^15.2f}"
                
                lineStr=""
                for line in readLines:
                    lineStr+=str(line[0])+"-"+str(line[1])+" "
                readLineFormatted=f"{lineStr:<30}"
                
                verboseInfos.append(f"{objFormatted}||{serIDFormatted}||{rchFormatted}||{objTypeFormatted}||{varFormatted}||{weightFormatted}||{readLineFormatted}")
        
        # verboseInfos.append("="*len(title))
        return verboseInfos
        
    def outputParaInfo(self):
        
        TUNEMODE={0: "relative", 1: "value", 2: "add"}
        
        verboseInfos=[]
        
        title="Model Information"
        spacing=int((self.verboseWidth-len(title))/2)-1
        verboseInfos.append("="*spacing+title+"="*spacing)
        nameFormatted=f"{'Parameter name':^20}"
        modeFormatted=f"{'Mode':^10}"
        lbFormatted=f"{'Lower Bound':^15}"
        ubFormatted=f"{'Upper Bound':^15}"
        sub_hruFormatted=f"{'HRU ID or Sub_HRU ID':^20}"
        head=f"{nameFormatted}||{modeFormatted}||{lbFormatted}||{ubFormatted}||{sub_hruFormatted}"
        
        verboseInfos.append(head)
        
        for param in self.paraInfos:
            nameFormatted=f"{param[0]:^20}"
            modeFormatted=f"{TUNEMODE[param[2]]:^10}"
            lbFormatted=f"{float(param[3]):^15.2f}"
            ubFormatted=f"{float(param[4]):^15.2f}"
            sub_hruFormatted=f"{param[5]:^20}"
            verboseInfos.append(f"{nameFormatted}||{modeFormatted}||{lbFormatted}||{ubFormatted}||{sub_hruFormatted}")
        
        return verboseInfos
    
    
class ReadWorker(QObject):
    
    INT_MODE={0: 'r', 1: 'v', 2: 'a'}; MODE_INT={'r': 0, 'v': 1, 'a': 2}
    INT_OBJTYPE={0: 'NSE', 1: 'RMSE', 2: 'PCC', 3: 'Pbias', 4: 'KGE'}; OBJTYPE_INT={'NSE': 0, 'RMSE':1, 'PCC':2, 'Pbias':3, 'KGE':4}
    INT_VAR={0: 'FLOW', 1: 'ORGN', 2: 'ORGP', 3: 'NO3', 4: 'NH4', 5: 'NO2', 6: 'TOTN', 7: 'TOTP'}
    VAR_INT={'FLOW': 0, 'ORGN': 1, 'ORGP': 2, 'NO3': 3, 'NH4': 4, 'NO2': 5, 'TOTN': 6, 'TOTP': 7}
    
    def readObjFile(self, path):
        
        objInfos={}
        with open(path, 'r') as f:
            lines=f.readlines()
        
        patternObj=re.compile(r'OBJ_(\d+)\s+')
        patternSer=re.compile(r'SER_(\d+)\s+')
        patternRch=re.compile(r'REACH_(\d+)\s+')
        patternType=re.compile(r'TYPE_(\d+)\s+')
        patternVar=re.compile(r'VAR_(\d+)\s+')
        patternWeight=re.compile(r'(\d+\.?\d*)')
        patternNum=re.compile(r'(\d+)')
        
        patternValue=re.compile(r'(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+\.?\d*)')
        
        i=2
        
        while i<len(lines):
            
            line=lines[i]
            
            match=patternObj.match(line)
            
            if match:
                
                objID=int(match.group(1))
                objInfos.setdefault(objID, [])
                
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
                    index, year, month ,day, value=int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), float(match.group(5))
                    data.append((index, year, month, day, value))
                    
                    if n==num:
                        break
                    else:
                        i+=1
                
                objInfos[objID].append({"objID": objID, "serID": serID, "reachID": reachID, "objType": objType, "varType": varType, "weight": weight, "observeData": data})
            
            i+=1
            
        return objInfos
    
    def readParaFile(self, path, modelInfos):
        
        paraInfos=[]
        
        with open(path, 'r') as f:
            
            lines=f.readlines()
            
            for line in lines:
                
                content=line.split()
                
                name=content[0]
                
                ext=modelInfos['totalParaList'].loc[name, 'file_name']
                
                mode=self.MODE_INT[content[1]]
                
                lb=content[2]; ub=content[3]
                position=" ".join(content[4:])
                paraInfo=[name, ext, mode, lb, ub, position]

                paraInfos.append(paraInfo)
        
        return paraInfos

class SaveWorker(QObject):
        
    def saveProFile(self, objInfos):
        
        objDict={}
        
        for objInfo in objInfos:
            
            objID=objInfo['objID']
            objDict.setdefault(objID, [])
   
            series={}
            series['objID']=objInfo['objID']
            series['serID']=objInfo['serID']
            series['reachID']=objInfo['reachID']
            series['objType']=objInfo['objType']
            series['varType']=objInfo['varType']
            series['weight']=objInfo['weight']
            series['observeData']=objInfo['observeData']
            objDict[objID].append(series)
        
        numObj=len(list(objDict.keys()))
        numSer=len(objInfos)
        
        lines=[]
        
        lines.append(f"{numSer:d}     : Number of observed variables series\n")
        lines.append(f"{numObj:d}     : The numbers of objective functions\n")
        lines.append("\n")
        
        for objID, series in objDict.items():
            for ser in series:
                
                serID=ser['serID']
                reachID=ser['reachID']
                objType=ser['objType']
                varType=ser['varType']
                weight=ser['weight']
                observedDate=ser['observeData']
                
                lines.append(f"OBJ_{objID} : ID of objective function\n")
                lines.append(f"SER_{serID} : ID of series data\n")
                lines.append(f"REACH_{reachID} : ID of reach\n")
                lines.append(f"TYPE_{objType} : Type of objective function\n")
                lines.append(f"VAR_{varType} : Type of variable\n")
                lines.append(f"{float(weight):.2f} : Weight of objective function\n")
                lines.append(f"{len(observedDate):d} : Number of data points for this variable as it follows below\n")
                lines.append("\n")
                
                for row in observedDate:
                    lines.append(f"{int(row[0]):d} {int(row[1]):d} {int(row[2]):d} {int(row[3]):d} {float(row[4]):.4f}\n")
                lines.append('\n')
                
        return lines
            
class InitWorker(QObject):
    
    result = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

    def initQThread(self, projectInfos, modelInfos, paraInfos, objInfos, runInfos):
        
        defaultVar=self.recordDefault(projectInfos, paraInfos, modelInfos, runInfos)
        
        problemInfos=self.initProblem(paraInfos)
        
        problemInfos['name']=projectInfos['projectName']
        
        problemInfos['nOutput']=len(list(objInfos.keys()))
        
        problemInfos['defaultVar']=defaultVar
        
        runInfos=self.generateTempPath(projectInfos, runInfos)
        
        objInfos=self.initObj(objInfos, modelInfos)
        
        self.result.emit({"problemInfos": problemInfos, 'runInfos': runInfos, 'objInfos': objInfos})

    def generateTempPath(self, projectInfos, runInfos):
        
        swatPath=projectInfos['swatPath']
        numParallel=runInfos['numParallel']
        tempPath=runInfos['tempPath']
        tempSwatDirs=[]
        
        if not os.path.exists(tempPath):
            os.makedirs(tempPath)
        
        now_time=datetime.now().strftime("%m%d_%H%M%S")
        tempPath=os.path.join(tempPath, now_time)
        os.makedirs(tempPath)
        runInfos['tempPath']=tempPath
        
        for i in range(numParallel):
            
            path=os.path.join(tempPath, f"instance_{i}")
            
            tempSwatDirs.append(path)
            
        runInfos['tempSwatDirs']=tempSwatDirs
        
        with ThreadPoolExecutor(max_workers=runInfos['numParallel']) as executor:
            futures = [executor.submit(copy_origin_to_tmp, swatPath, work_temp) for work_temp in tempSwatDirs]
        
        for future in as_completed(futures):
            future.result()    
        
        return runInfos
        
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
        modelInfos["nRch"]=len(modelInfos["subList"])
        
        with path(GUI.data, "SWAT_paras_files.csv") as para_path:
            
            totalParaList=pd.read_csv(para_path, index_col=0)
        
        modelInfos["totalParaList"]=totalParaList
        
        para_file={}
        for index, row in totalParaList.iterrows():
            para_name=index
            file_name=row['file_name']
            para_file.setdefault(file_name, [])
            para_file[file_name].append(para_name)
        
        modelInfos['para_file']=para_file
        
        return modelInfos
    
    def initObj(self, objInfos, modelInfos):
        
        infos={}
        
        for objID, series in objInfos.items():
            infos.setdefault(objID, [])
            
            temp={}
            
            for ser in series:
                serID=ser['serID']
                temp.setdefault(serID, [])
                temp[serID].append(ser)
            
            for serID, ser in temp.items():
                readLines=[]
                dataList=[]
                timeList=[]
                for s in ser:
                    observeData=s['observeData']
                    beginIndex=observeData[0][0]
                    endIndex=observeData[-1][0]
                    lines=self._generate_data_lines(beginIndex, endIndex, modelInfos)
                    readLines+=lines
                    dataList.append(np.array(observeData)[:, 4])
                    timeList.append(np.array(observeData, dtype=np.int32)[:, 1:4])
                    
                s['dataList']=np.concatenate(dataList, axis=0) #TODO
                s['timeList']=np.concatenate(timeList, axis=0)
                s['readLines']=readLines
                infos[objID].append(s)
            
        return infos
            
    def _generate_data_lines(self, start, end, modelInfos):
        
        printFlag=modelInfos["printFlag"]
        nRch=modelInfos["nRch"]

        lines=[]
        if printFlag==0:
            begin_month=modelInfos["beginRecord"].month
            first_period=12-begin_month
            if start<=first_period:
                if end<=first_period:
                    end_in_year=end
                    lines.append([10+nRch*start, 9+nRch*(end_in_year+1)])
                    return lines
                else:
                    end_in_year=first_period
                lines.append([10+nRch*start, 9+nRch*(end_in_year+1)])
            else:
                years=start//12
                start_in_year=start
                end_in_year=years*12+11
                if end<end_in_year:
                    lines.append([10+nRch*start_in_year+nRch*years, 9+nRch*(end+1)+nRch*years])
                    return lines
                else:
                    lines.append([10+nRch*start_in_year, 9+nRch*(end_in_year+1)+nRch*years])
            while True:
                start_in_year=end_in_year+1
                end_in_year=start_in_year+11
                years=(start_in_year-first_period)//12+1
                if end_in_year>=end:
                    lines.append([10+nRch*start_in_year+nRch*years, 9+nRch*(end+1)+nRch*years])
                    break
                else:
                    lines.append([10+nRch*start_in_year, 9+nRch*(end_in_year+1)+nRch*years])
            return lines 
        elif printFlag==1:
            lines=[[10+nRch*start, 9+nRch*(end+1)]]
            return lines
    
    def initProblem(self, paraInfos):
        
        problemInfos={}
        
        lb=[]
        ub=[]
        xLabels=[]
        
        for paraInfo in paraInfos:
            xLabels.append(paraInfo[0])
            lb.append(float(paraInfo[3]))
            ub.append(float(paraInfo[4]))
                    
        lb=np.array(lb).reshape(1, -1)
        ub=np.array(ub).reshape(1, -1)
        
        problemInfos["xLabels"]=xLabels
        problemInfos["nInput"]=len(xLabels)
        problemInfos["lb"]=lb
        problemInfos['ub']=ub
        
        return problemInfos
        
    def recordDefault(self, projectInfos, paraInfos, modelInfos, runInfos):
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
                
                if mode==1:
                    file_var[file]["mode"].append(0)
                elif mode==0:
                    file_var[file]["mode"].append(1)
                elif mode==2:
                    file_var[file]["mode"].append(2)
                
                file_var[file]["name"].append(name)
                file_var[file]["position"].append(position)
                file_var[file]["type"].append(data_type_)
         
        with ThreadPoolExecutor(max_workers=runInfos["numThreads"]) as executor:
            futures=[]
            for file_name, infos in file_var.items():
                futures.append(executor.submit(read_value_swat, projectInfos["swatPath"], file_name, infos["name"], infos["position"], 1))
        
        for future in as_completed(futures):
            res=future.result()
            for key, items in res.items():
                values=' '.join(str(value) for value in items)
                paraName, file_name=key.split('|')
                file_var[file_name].setdefault("default", {})
                file_var[file_name]["default"][paraName]=values
        return file_var

from UQPyL.utility.metrics import r_square
from scipy.stats import pearsonr

def func_NSE_inverse(true_values, sim_values):
    return -1*r_square(true_values.reshape(-1,1), sim_values.reshape(-1,1))

def func_RMSE(true_values, sim_values):
    return np.sqrt(np.mean(np.square(true_values-sim_values)))

def func_PCC_inverse(true_values, sim_values):
    return -1*np.corrcoef(true_values.ravel(), sim_values.ravel())[0,1]

def func_Pbias(true_values, sim_values):
    return np.sum(np.abs(true_values-sim_values)/true_values)*100

def func_KGE_inverse(true_values, sim_values):
    true_values=true_values.ravel()
    sim_values=sim_values.ravel()
    r, _ = pearsonr(true_values, sim_values)
    beta = np.std(sim_values) / np.std(true_values)
    gamma = np.mean(sim_values) / np.mean(true_values)
    kge = 1 - np.sqrt((r - 1)**2 + (beta - 1)**2 + (gamma - 1)**2)
    return -1*kge

def func_SUM(true_values, sim_values):
    
    return np.sum(sim_values)

def func_MEAN(true_values, sim_values):
    
    return np.mean(sim_values)

class RunWorker(QObject):
    
    VAR_COL={0 : 7, 1: 14, 2: 16, 3: 18, 4: 20, 5: 22, 6: 42, 7: 44}
    
    OBJTYPE_FUNC={0 : func_NSE_inverse, 1: func_RMSE, 2: func_PCC_inverse, 3: func_Pbias, 4: func_KGE_inverse, 5: func_SUM, 6: func_MEAN}
    
    updateProcess=pyqtSignal(float)
    result=pyqtSignal(object)
    unfinished=pyqtSignal()
    start=pyqtSignal(object)
    stop=False
    
    def __init__(self, modelInfos, paraInfos, objInfos, problemInfos, runInfos):
        
        self.modelInfos=modelInfos
        self.paraInfos=paraInfos
        self.objInfos=objInfos
        self.runInfos=runInfos
        
        self.numParallel=runInfos['numParallel']
        self.numThreads=runInfos['numThreads']
        swatDirs=runInfos['tempSwatDirs']
        self.file_var=problemInfos['defaultVar']
        self.swatExe=runInfos['swatExe']
        self.objInfos=objInfos
        self.nRch=modelInfos['nRch']
        self.nOutput=problemInfos['nOutput']
        
        self.workPath=queue.Queue()
        for dir in swatDirs:
            self.workPath.put(dir)
        
        self.count=0
        
        super().__init__()
        
        self.start.connect(self.evaluate)
        
    def _subprocess(self, x, id):
        
        if not self.stop:
            workPath=self.workPath.get()
            self.setValues(workPath, x)
            
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE


            subprocess.run(
                [os.path.join(workPath, self.swatExe)],
                cwd=workPath,
                stdout=subprocess.PIPE, 
                stderr=subprocess.DEVNULL, 
                stdin=subprocess.DEVNULL,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW, 
                startupinfo=startupinfo  
            )

            objs=[]
            
            for obj, series in self.objInfos.items():
                vObj=0
                for ser in series:
                
                    reachID=ser['reachID']
                    readLines=ser['readLines']
                    varType=ser['varType']
                    objType=ser['objType']
                    weight=ser['weight']
                    
                    simValueList=[]
                    for line in readLines:
                        
                        startLine, endLine=line[0], line[1]
                        subValue=np.array(read_simulation(os.path.join(workPath, "output.rch"), self.VAR_COL[varType] , reachID, self.nRch, startLine, endLine))
                        simValueList.append(subValue)
                
                    simValue=np.concatenate(simValueList, axis=0)
                    obValue=ser['dataList']
                    vObj+=weight*self.OBJTYPE_FUNC[objType](obValue, simValue)
                
                objs.append(vObj)
            
            self.workPath.put(workPath)
            return id, objs
        
        
    def setValues(self, path, x):
                
        with ThreadPoolExecutor(max_workers=self.numThreads) as executor:
            futures=[]
            for file_name, infos in self.file_var.items():
                future = executor.submit(write_value_to_file, path, file_name, 
                                            infos["name"], infos["default"], 
                                            infos["index"], infos["mode"],  infos["position"], infos["type"],
                                            x.ravel())
                futures.append(future)
            
            for future in as_completed(futures):
                res=future.result()
    
    def singleEvaluate(self, x):
        
        x=x.ravel()
        if not self.stop:
            workPath=self.workPath.get()
            self.setValues(workPath, x)
            

            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            
            subprocess.run(
                [os.path.join(workPath, self.swatExe)],
                cwd=workPath,
                stdout=subprocess.PIPE, 
                stderr=subprocess.DEVNULL, 
                stdin=subprocess.DEVNULL,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                startupinfo=startupinfo 
            )

            objs=[]
            simData={}
            for obj, series in self.objInfos.items():
                
                vObj=0
                simData.setdefault(obj, [])
                
                for ser in series:
                    
                    reachID=ser['reachID']
                    readLines=ser['readLines']
                    varType=ser['varType']
                    objType=ser['objType']
                    weight=ser['weight']
                    
                    simValueList=[]
                    for line in readLines:
                        
                        startLine, endLine=line[0], line[1]
                        subValue=np.array(read_simulation(os.path.join(workPath, "output.rch"), self.VAR_COL[varType] , reachID, self.nRch, startLine, endLine))
                        simValueList.append(subValue)
                
                    simValue=np.concatenate(simValueList, axis=0)
                    obValue=ser['dataList']
                    vObj+=weight*self.OBJTYPE_FUNC[objType](obValue, simValue)
                    
                    simData[obj].append(simValue)
                    
                objs.append(vObj)

            self.workPath.put(workPath)
            
            self.result.emit((objs, simData))
            
    def evaluate(self, X):
    
        n = X.shape[0]
        
        Y = np.full((n, self.nOutput), np.inf)
        
        self.updateProcess.emit(self.count)
        
        with ThreadPoolExecutor(max_workers=self.numParallel) as executor:
            
            futures = [executor.submit(self._subprocess, X[i, :], i) for i in range(n)]
            
            for future in as_completed(futures):
                
                if not self.stop:
                    idx, obj_value = future.result()
                    
                    for i, value in enumerate(obj_value):
                        Y[idx, i] = value
                
                self.count += 1
                self.updateProcess.emit(self.count) 
        if not self.stop:
            self.result.emit(Y)
        else:
            self.unfinished.emit()
            
        return Y
class EvaluateThread(QThread):
    
    def __init__(self, worker, X):
        super().__init__()
        self.worker = worker
        self.X = X

    def run(self):
        
        self.worker.evaluate(self.X)

class SingleEvaluateThread(QThread):
    
    def __init__(self, worker, x):
        super().__init__()
        self.worker = worker
        self.x = x
    
    def run(self):
        
        self.worker.singleEvaluate(self.x)

class OptimizeThread(QThread):
    errorOccur=pyqtSignal(str)
    def __init__(self, worker, optimizer, problemInfos):
        super().__init__()
        self.worker = worker
        self.optimizer = optimizer
        
        nInput=problemInfos['nInput']
        nOutput=problemInfos['nOutput']
        lb=problemInfos['lb']
        ub=problemInfos['ub']
        xLabels=problemInfos['xLabels']
        self.problem=PracticalProblem(self.worker.evaluate, nInput=nInput, nOutput=nOutput, lb=lb, ub=ub, x_labels=xLabels, name=problemInfos['name'])
    
    # def run1(self):
        
    #     self.optimizer.run(self.problem)
    
    def run(self):
        try:
            self.optimizer.run(self.problem)
        except Exception as e:
            self.errorOccur.emit(str(e))
        
class NewThread(QThread):
    
    occurError=pyqtSignal(str)
    
    accept=pyqtSignal()
    
    def __init__(self, worker, projectInfos):
        super().__init__()
        self.worker=worker
        self.projectInfos=projectInfos
        self.modelInfos=None
        
    def run(self):
        
        try:
            
            self.modelInfos=self.worker.initModel(self.projectInfos)
            
            self.accept.emit()
            
        except Exception as e:
            
            self.occurError.emit("There are some error in model file, please check!")

class InitThread(QThread):
    errorOccur=pyqtSignal(str)
    def __init__(self, worker, projectInfos,  modelInfos , paraInfos, objInfos, runInfos):
        super().__init__()
        self.worker=worker
        self.projectInfos=projectInfos
        self.modelInfos=modelInfos
        self.paraInfos=paraInfos
        self.objInfos=objInfos
        self.runInfos=runInfos
        
    def run(self):
        try:
            self.worker.initQThread(self.projectInfos, self.modelInfos, self.paraInfos, self.objInfos, self.runInfos)
        except Exception as e:
            self.errorOccur.emit(str(e))

class IterEmit(QObject):
    
    iterCount=0
    iterSend=pyqtSignal(int)
    iterStop=pyqtSignal()
    iterFinished=pyqtSignal()
    def __init__(self, parent=None):
        
        super().__init__(parent)
    
    def send(self):
        
        self.iterSend.emit(self.iterCount)
        self.iterCount+=1
        
    def unfinished(self):
        
        self.iterStop.emit()
    
    def finished(self):
        
        self.iterFinished.emit()
    
class VerboseEmit(QObject):
    
    verboseSend=pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def send(self, txt):
        
        self.verboseSend.emit(txt)
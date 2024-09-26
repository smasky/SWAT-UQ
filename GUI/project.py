import os
import re
import glob
import GUI.data
import numpy as np
import itertools
from importlib.resources import path
from datetime import datetime, timedelta
from .swat_uq_core import SWAT_UQ_Flow
#C++ Module
from .pyd.swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation
class Project:
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
    
    TUNEMODE={"r": 0, "v": 1, "a":2}; INVERSETUNEMODE={0: "r", 1: "v", 2: "a"}
    OBJTYPE={ 0: "NSE", 1: "RMSE", 2: "PCC", 3: "Pbias", 4: "KGE" }
    VARIABLE={ 0 : "Flow" }
    paraInfos=[];bsnInfos={};bsnFile={};modelInfos={}
    
    btnSets=[]
    @classmethod
    def loadParaList(cls):
        with path(GUI.data, "parameter_list.txt") as para_list_path:
            with open(str(para_list_path), 'r') as f:
                lines=f.readlines()
                for line in lines:
                    txt=line.split()
                    cls.paraList.setdefault(txt[0], []).append(txt[1])
                    cls.inverseParaList[txt[1]]=txt[0]
    
    @classmethod
    def initialize(cls):
        
        cls.readHRUInfos()
        cls.readFigCio()
        
    @classmethod
    def readFigCio(cls):
        
        paras=["IPRINT", "NBYR", "IYR", "IDAF", "IDAL", "NYSKIP"]
        pos=["default"]*len(paras)
        dict_values=read_value_swat(cls.swatPath, "file.cio", paras, pos, 0)
        begin_date=datetime(int(dict_values["IYR"][0]), 1, 1)+timedelta(int(dict_values['IDAF'][0])-1)
        end_date=datetime(int(dict_values["IYR"][0])+int(dict_values['NBYR'][0])-1, 1, 1)+timedelta(int(dict_values['IDAL'][0])-1)
        simulation_days=(end_date-begin_date).days+1
        output_skip_years=int(dict_values["NYSKIP"][0])
        output_skip_days=(datetime(int(dict_values["IYR"][0])+output_skip_years, 1, 1)+timedelta(int(dict_values['IDAF'][0])-1)-begin_date).days
        begin_record=begin_date+timedelta(output_skip_days)
        
        cls.modelInfos["print_flag"]=int(dict_values["IPRINT"][0])
        cls.modelInfos["beginDate"]=begin_date
        cls.modelInfos["endDate"]=end_date
        cls.modelInfos["output_skip_years"]=output_skip_years
        cls.modelInfos["simulation_days"]=simulation_days
        cls.modelInfos["recordDate"]=begin_record
    
    @classmethod
    def importProFromFile(cls, path):
        Infos={}
        cls.proPath=path
        with open(path, 'r') as f:
            lines=f.readlines()
            
        pattern_id=re.compile(r'REACH_(\d+)\s+')
        pattern_ser=re.compile(r'SER_(\d+)\s+')
        pattern_col=re.compile(r'VAR_(\d+)\s+')
        pattern_type=re.compile(r'TYPE_(\d+)\s+')
        pattern_obj=re.compile(r'OBJ_(\d+)\s+')
        pattern_weight=re.compile(r'(\d+\.?\d*)')
        pattern_num=re.compile(r'(\d+)')
        
        pattern_value=re.compile(r'(\d+)\s+(\d+)\s+(\d+\.?\d*)')
        
        total_series=int(re.search(r'\d+', lines[0]).group()) #read the num of reaches
        num_objs=int(re.search(r'\d+', lines[1]).group())
                    
        i=2; series_id=0
        
            
        while i<len(lines):
            line=lines[i]
            match_obj= pattern_obj.match(line)
            
            if match_obj:
                series_id+=1
                
                objID=int(match_obj.group(1)); Infos.setdefault(objID, [])
                serID=int(pattern_ser.match(lines[i+1]).group(1))
                reachID=int(pattern_id.match(lines[i+2]).group(1))
                objType=int(pattern_type.match(lines[i+3]).group(1))
                varType=int(pattern_col.match(lines[i+4]).group(1))
                weight=float(pattern_weight.match(lines[i+5]).group(1))
                num=int(pattern_num.match(lines[i+6]).group(1))
                
                i=i+7
                
                line=lines[i]
                while pattern_value.match(line) is None:
                    i+=1
                    line=lines[i]
                    
                n=0; data=[]
                
                while True:
                    line=lines[i];n+=1
                    match_data=pattern_value.match(line)
                    year, index, value=match_data.group(1), match_data.group(2), match_data.group(3)
                    data.append([year, index, value])
                    
                    if n==num:
                        break
                    else:
                        i+=1
                
                Infos[objID].append({"objID": objID, "serID": serID, "reachID": reachID, "objType": cls.OBJTYPE[objType], "varType": cls.VARIABLE[varType],"weight": weight, "observeData": np.array(data)})
            i+=1
        return Infos
                        
    @classmethod
    def importParaFromFile(cls, path):
        Infos=[]
        cls.paraPath=path
        with open(path, 'r') as f:
            lines=f.readlines()
            for line in lines:
                content=line.split()
                
                name=content[0]
                ext=cls.inverseParaList[name]
                mode=cls.TUNEMODE[content[1]]
                
                lb=content[2]; ub=content[3]
                
                position=" ".join(content[4:])
                
                paraInfo=[name, ext, mode, lb, ub, position]

                Infos.append(paraInfo)
        return Infos
    
    @classmethod
    def saveParaFile(cls, path):
        
        with open(path, 'w') as f:
            lines=[" ".join(info)+"\n" for info in cls.paraInfos]
            f.writelines(lines)
    
    @classmethod
    def saveProFile(cls, path, lines):
        
        with open(path, 'w') as f:
            f.writelines(lines)
    
    @classmethod
    def readHRUInfos(cls):
        
        basin_hru={}
        
        if cls.swatPath is None:
            return
        
        with open(os.path.join(cls.swatPath, "fig.fig"), "r") as f:
            lines=f.readlines()
            for line in lines:
                match = re.search(r'(\d+)\.sub', line)
                if match:
                    cls.bsnFile[match.group(1)]=[]
                    basin_hru[match.group(1)]=[]

        for sub in cls.bsnFile:
            file_name=sub+".sub"
            cls.bsnInfos[str(int(sub[:5]))]=[]
            with open(os.path.join(cls.swatPath, file_name), "r") as f:
                lines=f.readlines()
                for line in lines:
                    match = re.search(r'(\d+)\.mgt', line)
                    if match:
                        basin_hru[sub].append(match.group(1))
                        cls.bsnFile[sub].append(match.group(1)[-4:])
                        cls.bsnInfos[str(int(sub[:5]))].append(str(int(match.group(1)[-4:])))
                        
        cls.modelInfos["basinList"]=list(basin_hru.keys())
        cls.modelInfos["nBsn"]=len(cls.modelInfos["basinList"])
        cls.modelInfos["hruList"]=list(itertools.chain.from_iterable(basin_hru.values()))
        cls.modelInfos["nHru"]=len(cls.modelInfos["hruList"])
        cls.modelInfos["bsn_hru"]=basin_hru
        cls.modelInfos['nRch']=len(cls.modelInfos['hruList'])
        
    @classmethod
    def checkParaFile(cls):
        
        par_files = glob.glob(os.path.join(cls.projectPath, "*.par"))
        # par_files = glob.glob(os.path.join(cls.projectPath, "**", "*.par"), recursive=True)
        files=[os.path.basename(file_path) for file_path in par_files]
        return files
    
    @classmethod
    def checkProFile(cls):
        
        
        # pro_files = glob.glob(os.path.join(cls.projectPath, "**", "*.pro"), recursive=True)
        pro_files=glob.glob(os.path.join(cls.projectPath, "*.pro"))
        files=[os.path.basename(file_path) for file_path in pro_files]
        
        return files
    
    @classmethod
    def checkSwatExe(cls):
        
        if cls.swatPath!='':
            # exe_name = glob.glob(os.path.join(cls.swatPath, "**", "*.exe"), recursive=True)
            exe_name= glob.glob(os.path.join(cls.swatPath, "*.exe"))
            name=[os.path.basename(file_path) for file_path in exe_name]
            return name
        else:
            return []
    
    @classmethod
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
    
    @classmethod
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
        
        return swat_cup.verbose
import os
import re
import GUI.data
from importlib.resources import path
from datetime import datetime, timedelta
from .pyd.swat_utility import read_value_swat
class Project:
    swatPath=""
    projectPath=""
    projectName=""
    parameters={}
    objs={}
    paraList={}
    inverseParaList={}
    
    TUNEMODE={"r": 0, "v": 1, "a":2}; INVERSETUNEMODE={0: "r", 1: "v", 2: "a"}
    
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
        cls.modelInfos["begin_date"]=begin_date
        cls.modelInfos["end_date"]=end_date
        cls.modelInfos["output_skip_years"]=output_skip_years
        cls.modelInfos["simulation_days"]=simulation_days
        cls.modelInfos["begin_record"]=begin_record
    
    @classmethod
    def importParaFromFile(cls, path):
        Infos=[]
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
    def readHRUInfos(cls):
        
        if cls.swatPath is None:
            return
        
        with open(os.path.join(cls.swatPath, "fig.fig"), "r") as f:
            lines=f.readlines()
            for line in lines:
                match = re.search(r'(\d+)\.sub', line)
                if match:
                    cls.bsnFile[match.group(1)]=[]

        for sub in cls.bsnFile:
            file_name=sub+".sub"
            cls.bsnInfos[str(int(sub[:5]))]=[]
            with open(os.path.join(cls.swatPath, file_name), "r") as f:
                lines=f.readlines()
                for line in lines:
                    match = re.search(r'(\d+)\.mgt', line)
                    if match:
                        cls.bsnFile[sub].append(match.group(1)[-4:])
                        cls.bsnInfos[str(int(sub[:5]))].append(str(int(match.group(1)[-4:])))
        
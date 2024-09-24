import GUI.data
from importlib.resources import path

class Project:
    swatPath=None
    projectPath=None
    projectName=None
    parameters={}
    objs={}
    paraList={}
    inverseParaList={}
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
    def importParaFromFile(cls, path):
        with open(path, 'r') as f:
            lines=f.readlines()
            for line in lines:
                content=line.split()
                
                name=content[0]
                ext=cls.inverseParaList[name]
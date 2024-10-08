import os
import glob
import numpy as np
import sys
from importlib.resources import path
from datetime import datetime, timedelta
from PyQt5.QtWidgets import QApplication
from .woker import (InitWorker, ReadWorker, SaveWorker, InitThread,
                    VerboseWorker, RunWorker, EvaluateThread)
#C++ Module
from .pyd.swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation
from UQPyL.DoE import LHS, FFD, Morris_Sequence, FAST_Sequence, Sobol_Sequence, Random
from UQPyL.sensibility import Sobol, Delta_Test, FAST, RBD_FAST, Morris, RSA
from UQPyL.problems import PracticalProblem
from UQPyL.utility.scalers import StandardScaler
from PyQt5.QtCore import QThread, Qt, QDate
class Project:
    
    INT_MODE={0: 'r', 1: 'v', 2: 'a'}; MODE_INT={'r': 0, 'v':1, 'a':2}
    INT_OBJTYPE={0: 'NSE', 1: 'RMSE', 2: 'PCC', 3: 'Pbias', 4: 'KGE'}; OBJTYPE_INT={'NSE': 0, 'RMSE':1, 'PCC':2, 'Pbias':3, 'KGE':4}
    INT_VAR={0: 'Flow'}; VAR_INT={'Flow': 0}
    
    SA_METHOD={'Sobol': 'Sobol', 'Delta Test': 'Delta_Test', 'FAST': 'FAST', 'RBD-FAST': 'RBD_FAST', 'Morris': 'Morris', 'RSA': 'RSA'}
    SAMPLE_METHOD={'Full Factorial Design': 'FFD', 'Latin Hyper Sampling': 'LHS', 'Random': 'Random', 'Fast Sequence': 'FAST_Sequence', 'Morris Sequence': 'Morris_Sequence', 'Sobol Sequence': 'Sobol_Sequence'}
    SOP_METHOD={'Genetic Algorithm (GA)': 'GA', 'Particle Swarm Optimization (PSO)': 'PSO', 'Differential Evolution (DE)': 'DE', 'Artificial Bee Colony (ABC)': 'ABC', 'Cooperation Search Algorithm (CSA)': 'CSA', 'Shuffled Complex Evolution-UA (SCE-UA)':'SCE_UA'}
    MOP_METHOD={'Reference Vector guided Evolutionary Algorithm (RVEA)': 'RVEA', 'Non-dominated Sorting Genetic Algorithm II (NSGA-II)': 'NSGAII', 'MultiObjective Evolutionary Algorithm based on Decomposition (MOEA/D)' : 'MOEAD'}
    
    SA_SAMPLE={'Sobol': ['Sobol Sequence'], 'Delta Test': ['any'], 'FAST': ['Fast Sequence'], 'RBD-FAST': ['any'], 'Morris': ['Morris Sequence'], 'RSA': ['any']}
    
    SA_HYPER={'Sobol': {'Z-score':{'type':'bool', 'class': 'Sobol', 'method': '__init__' ,'default': ''}, 'calSecondOrder':{'type':'bool', 'class': 'Sobol','method': '__init__', 'default': '0'}}, 
              'Delta Test': {'Z-score':{'decs':'Z-score' , 'class': 'Delta_Test','method': '__init__', 'type':'bool', 'default': '0'}, 'nNeighbors':{'type':'int', 'class': 'Delta_Test','method': '__init__','default': '2'}},
              'FAST': {'Z-score':{'type':'bool', 'method': '__init__', 'class': 'FAST','default': ''}},
              'RBD-FAST': {'Z-score':{'type':'bool', 'class': 'RBD_FAST','method': '__init__', 'default': ''}, 'M':{'type':'int', 'method': '__init__', 'class': 'RBD_FAST', 'default': '4'}},
              'Morris': {'Z-score':{'type':'bool', 'method': '__init__', 'class' : 'Morris','default': ''}},
              'RSA': {'Z-score':{'type':'bool', 'method': '__init__', 'class': 'RSA', 'default': ''}, 'nRegion':{'type':'int','method': '__init__', 'class': 'RSA', 'default': '20'}}}
    
    SAMPLE_HYPER={'Full Factorial Design': {'levels': {'dec': 'Number of Factors *', 'method': '__init__', 'class': 'FFD','type': 'int', 'related': '*','default': '5'}},
              'Latin Hyper Sampling' : {'nt': {'dec': 'Number for sampling *', 'method' : 'sample', 'type': 'int', 'class' : 'LHS', 'related': '*', 'default': '500'}},
              'Random' : {'nt': {'dec': 'Number for sampling *', 'class' : 'Random', 'method' : 'sample', 'type': 'int', 'related' : '*','default': '500'}},
              'Fast Sequence' : { 'M' : {'dec': 'M', 'class' : 'FAST_Sequence' ,'method': '__init__', 'type': 'int', 'default': '5'},
                                  'nt' : {'dec': 'The number for sampling *', 'class' : 'FAST_Sequence','method': 'sample', 'type': 'int', 'related' : '*' ,'default': '500'}
                                },
              'Morris Sequence' : { 'num_levels': {'dec': 'Number of Level', 'class' : 'Morris_Sequence','method': '__init__', 'type': 'int', 'default': '5'},
                                    'nt' : {'dec': 'Number of Trajectory *', 'class' : 'Morris_Sequence', 'method' : 'sample', 'type': 'int', 'related' : '*','default': '100'}
                                  },
              'Sobol Sequence' : {'nt': { 'dec': 'Number for sampling *', 'class' : 'Sobol_Sequence', 'method': 'sample', 'type': 'int', 'related' : '*', 'default': '100'},
                                  'skipValue' : {'dec': 'Skip Values', 'class' : 'Sobol_Sequence', 'method': '__init__', 'type': 'int', 'default': '5'},
                                  'scramble' : {'dec' : 'Scramble', 'class' : 'Sobol_Sequence', 'method': '__init__', 'type': 'bool', 'default': 'False'}
                                  }
            }
    
    SOP_HYPER={'Artificial Bee Colony (ABC)': {'employedRate' : {'dec':'Employed Rate', 'class' : 'ABC', 'method': '__init__', 'type': 'float', 'default': '0.3'}},
               'Cooperation Search Algorithm (CSA)' : {'alpha' : {'dec':'Alpha', 'class' : 'CSA', 'method': '__init__', 'type': 'float', 'default': '0.5'}, 'beta' : {'dec':'Beta', 'class' : 'CSA', 'method': '__init__', 'type': 'float', 'default': '0.3'}, 'M' : {'dec':'M', 'class' : 'CSA', 'method': '__init__', 'type': 'int', 'default': '3'}},
               'Differential Evolution (DE)': {'cr': {'dec':'cr', 'class': 'DE', 'method': '__init__', 'type': 'float', 'default': '0.9'}, 'f': {'dec':'f', 'class': 'DE', 'method': '__init__', 'type': 'float', 'default': '0.5'}},
               'Genetic Algorithm (GA)': {'proC': {'dec': 'proC', 'class': 'GA', 'method': '__init__', 'type': 'float', 'default': '1'}, 'proM': {'dec': 'proM', 'class': 'GA', 'method': '__init__', 'type': 'float', 'default': '1'}, 'disC': {'dec': 'disC', 'class': 'GA', 'method': '__init__', 'type': 'int', 'default': '20'}, 'disM': {'dec': 'disM', 'class': 'GA', 'method': '__init__', 'type': 'int', 'default': '20'}},
               'Particle Swarm Optimization (PSO)': {'w': {'dec': 'w', 'class': 'PSO', 'method': '__init__', 'type': 'float', 'default': '0.1'}, 'c1': {'dec': 'c1', 'class': 'PSO', 'method': '__init__', 'type': 'float', 'default': '0.5'}, 'c2': {'dec': 'c2', 'class': 'PSO', 'method': '__init__', 'type': 'float', 'default': '0.5'}},
               'Shuffled Complex Evolution-UA (SCE-UA)': {'ngs': {'dec': 'ngs', 'class': 'SCE_UA', 'method': '__init__', 'type': 'int', 'default': '3'}, 'npg': {'dec': 'npg', 'class': 'SCE_UA', 'method': '__init__', 'type': 'int', 'default': '7'}, 'nps': {'dec': 'nps', 'class': 'SCE_UA', 'method': '__init__', 'type': 'int', 'default': '4'}, 'nspl': {'dec':'nspl', 'class':'SCE_UA', 'method': '__init__', 'type':'int', 'default': '7'}},
            }
    
    MOP_HYPER={'Reference Vector guided Evolutionary Algorithm (RVEA)' : {'alpha': {'dec': 'alpha', 'class': 'RVEA', 'method': '__init__', 'type': 'float', 'default': '2.0'}, 'fr': {'dec': 'fr', 'class': 'RVEA', 'method': '__init__', 'type': 'float', 'default': '0.1'}},
               'Non-dominated Sorting Genetic Algorithm II (NSGA-II)' : {'proC': {'dec': 'proC', 'class': 'GA', 'method': '__init__', 'type': 'float', 'default': '1'}, 'proM': {'dec': 'proM', 'class': 'GA', 'method': '__init__', 'type': 'float', 'default': '1'}, 'disC': {'dec': 'disC', 'class': 'GA', 'method': '__init__', 'type': 'int', 'default': '20'}, 'disM': {'dec': 'disM', 'class': 'GA', 'method': '__init__', 'type': 'int', 'default': '20'}}, 
    }
    
    FORMULA={'Full Factorial Design' : 'nInput**levels',
             'Latin Hyper Sampling' : 'nt',
             'Random' : 'nt',
             'Fast Sequence' : 'nt*nInput',  
             'Morris Sequence' : 'nt*(nInput+1)',
             'Sobol Sequence' : '(nt+2)*nInput'
             }
    
    projectInfos=None; modelInfos=None; paraInfos=None; proInfos=None; objInfos=None
    problemInfos=None; SAInfos=None; SAResult=None; OPInfos=None
    
    btnSets=[]
    @classmethod
    def openProject(cls, projectName, projectPath, swatPath):
        
        projectInfos={}
        projectInfos["projectName"]=projectName
        projectInfos["projectPath"]=projectPath
        projectInfos['swatPath']=swatPath
        projectInfos['tempPath']=os.path.join(projectPath, 'temp')
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
        
        cls.worker.moveToThread(cls.thread)
        cls.worker.result.connect(accept, Qt.QueuedConnection)
        cls.thread.started.connect(run)
        cls.thread.start()
        
    @classmethod
    def calDate(cls, observeDate):
        
        _, beginY, beginM, beginD, _= observeDate[0]
        _, endY, endM, endD, _= observeDate[-1]
        printFlag=cls.modelInfos["printFlag"]
        
        if printFlag==1:
            startDate=datetime(beginY, beginM, beginD)
            endDate=datetime(endY, endM, endD)
        else:
            startDate=datetime(beginY, beginM, 1)
            endDate=datetime(endY, endM, 1)
        
        return startDate, endDate
    
    @classmethod
    def calDateIndex(cls, beginDate, delta):
        
        printFlag=cls.modelInfos["printFlag"]
        beginRecord=cls.modelInfos['beginRecord']
        baseDate=QDate(beginRecord.year, beginRecord.month, beginRecord.day)
        # baseDate=QDate(beginDate.year(), 1, 1)
        
        if printFlag==1:
            nowDate=beginDate.addDays(delta)
            index=baseDate.daysTo(nowDate)+1
            return index, nowDate.year(), nowDate.month(), nowDate.day()
        else:
            nowDate=beginDate.addMonths(delta)
            index=nowDate.month()-baseDate.month()+1
            return index, nowDate.year(), nowDate.month(), 1 
         
    @classmethod 
    def importProFromFile(cls, path):
        
        cls.worker=ReadWorker()
        infos=cls.worker.readObjFile(path)
        
        return infos
                        
    @classmethod
    def importParaFromFile(cls, path):
        
        infos=[]
        worker=ReadWorker()
        infos=worker.readParaFile(path, cls.modelInfos)
                
        return infos
    
    @classmethod
    def saveParaFile(cls, infos, path):
        
        with open(path, 'w') as f:
            lines=[" ".join(info)+"\n" for info in infos]
            f.writelines(lines)
        
    @classmethod
    def saveProFile(cls, path, objInfos):
        
        worker=SaveWorker()
        
        lines=worker.saveProFile(objInfos)
        
        with open(path, 'w') as f:
            f.writelines(lines)
        
    @classmethod
    def findParaFile(cls):
        
        par_files = glob.glob(os.path.join(cls.projectInfos['projectPath'], "*.par"))
        files=[os.path.basename(file_path) for file_path in par_files]
        return files
    
    @classmethod
    def findProFile(cls):
        
        pro_files=glob.glob(os.path.join(cls.projectInfos['projectPath'], "*.pro"))
        files=[os.path.basename(file_path) for file_path in pro_files]
        return files
    
    @classmethod#TODO find
    def findSwatExe(cls):
        swatPath=cls.projectInfos['swatPath']
        exe_name= glob.glob(os.path.join(swatPath, "*.exe"))
        name=[os.path.basename(file_path) for file_path in exe_name]

        return name
    
    @classmethod
    def sampling(cls):
        
        SAInfos=cls.SAInfos
        paraInfos=cls.paraInfos
        
        lb=np.array([float(para[3]) for para in paraInfos])
        ub=np.array([float(para[4]) for para in paraInfos])
        
        smName=SAInfos['smClass']
        smHyper=SAInfos['smHyper']
        initHyper={}
        sampleHyper={}
        
        for hyper in smHyper:
            name=hyper['name']
            func=hyper['method']
            value=hyper['value']
            
            if func=="__init__":
                initHyper[name]=value
            else:
                sampleHyper[name]=value
        
        sampleHyper['nx']=len(paraInfos)
        
        sampler=eval(smName)(**initHyper)
        
        X=sampler.sample(**sampleHyper)
        
        X=X*(ub-lb)+lb
        
        cls.SAResult={}
        cls.SAResult['X']=X
    
    @classmethod #TODO
    def simulation(cls, processBar, finish):
        
        def update_progress(value):
            processBar.setValue(value)
        
        def accept(Y):
            cls.SAResult['Y']=Y
        
        cls.worker=RunWorker(cls.projectInfos, cls.modelInfos, cls.paraInfos, cls.objInfos, cls.problemInfos)
        cls.worker.result.connect(accept)
        cls.thread=EvaluateThread(cls.worker, cls.SAResult['X'])
        cls.worker.updateProcess.connect(update_progress)
        cls.thread.finished.connect(cls.thread.deleteLater)  # 确保线程完成后被清理
        cls.thread.finished.connect(finish)
        cls.thread.start()
    
    @classmethod
    def initProject(cls, verboseWidget, btn):
        
        cls.projectInfos["numThreads"]=12 #TODO
    
        cls.worker = InitWorker()
        cls.worker.initQThread(cls.projectInfos, cls.modelInfos, cls.paraInfos, cls.objInfos)
        cls.thread = InitThread(cls.worker, cls.projectInfos, cls.modelInfos, cls.paraInfos, cls.objInfos)
        
        def accept(infos):
            
            cls.problemInfos=infos["problemInfos"]
            cls.projectInfos=infos['projectInfos']
            cls.objInfos=infos['objInfos']
            cls.thread.quit()
            cls.thread.deleteLater()
            
            worker=VerboseWorker(cls.projectInfos, cls.modelInfos, cls.paraInfos, cls.objInfos)
            
            verbose=worker.outputVerbose()
            
            text="\n".join(verbose)
            
            verboseWidget.setText(text)
            verboseWidget.verticalScrollBar().setValue(verboseWidget.verticalScrollBar().maximum())

            btn.setEnabled(True)
            
        cls.worker.result.connect(accept)
        cls.thread.start()
    
    @classmethod
    def sensibility_analysis(cls, verboseWidget):
        SAInfos=cls.SAInfos
        initHyper={}
        analyzeHyper={}
        saClass=SAInfos['saClass']
        saHyper=SAInfos['saHyper']
        
        for hyper in saHyper:
            name=hyper['name']
            func=hyper['method']
            value=hyper['value']
            
            if name=="Z-score":
                if value:
                    value=(StandardScaler(0,1), StandardScaler(0,1))
                else:
                    value=(None, None)
                initHyper["scalers"]=value
                continue
            
            if func=="__init__":
                initHyper[name]=value
            else:
                analyzeHyper[name]=value
        
        initHyper['verbose']=True
        sa=eval(saClass)(**initHyper)
        
        analyzeHyper['X']=cls.SAResult['X']
        analyzeHyper['Y']=cls.SAResult['Y']
        
        ub=cls.problemInfos['ub']
        lb=cls.problemInfos['lb']
        nInput=cls.problemInfos['nInput']
        xLabels=cls.problemInfos['xLabels']
        problem=PracticalProblem(None, nInput, 1, ub, lb, x_labels=xLabels)
        
        verbose=[]
        def write_verbose(text):
            verbose.append(text)
        
        def flush():
            pass
        
        origin=sys.stdout
        sys.stdout.write = write_verbose
        sys.stdout.flush = flush
        
        sa.analyze(problem=problem, **analyzeHyper)
        
        sys.stdout=origin
        
        verboseWidget.append("".join(verbose))
        
        
        
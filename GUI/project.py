import os
import glob
import numpy as np
import h5py
import shutil
from datetime import datetime
from .worker import (InitWorker, ReadWorker, SaveWorker, InitThread, OptimizeThread, IterEmit, VerboseEmit, NewThread,
                    VerboseWorker, RunWorker, EvaluateThread, SingleEvaluateThread)
#C++ Module
from .pyd.swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation
from UQPyL.DoE import LHS, FFD, Morris_Sequence, FAST_Sequence, Sobol_Sequence, Random, Saltelli_Sequence
from UQPyL.sensibility import Sobol, Delta_Test, FAST, RBD_FAST, Morris, RSA
from UQPyL.optimization import GA, DE, SCE_UA, PSO, ABC, CSA
from UQPyL.optimization import NSGAII, RVEA
from UQPyL.problems import PracticalProblem
from UQPyL.utility.scalers import StandardScaler
from UQPyL.utility.verbose import Verbose
from PyQt5.QtCore import QDate, Qt
from .component.info_bar import InfoBar_ as InfoBar, InfoBarPosition
from .component.message_box import MessageBox
class Project:

    INT_MODE={0: 'r', 1: 'v', 2: 'a'}; MODE_INT={'r': 0, 'v':1, 'a':2}
    INT_OBJTYPE={0: 'NSE', 1: 'RMSE', 2: 'PCC', 3: 'PBIAS', 4: 'KGE', 5: 'SUM', 6: 'MEAN'}; OBJTYPE_INT={'NSE': 0, 'RMSE': 1, 'PCC': 2, 'PBIAS': 3, 'KGE': 4, 'SUM': 5, 'MEAN': 6}
    INT_VAR={0: 'FLOW', 1: 'ORGN', 2: 'ORGP', 3: 'NO3', 4: 'NH4', 5: 'NO2', 6: 'TOTN', 7: 'TOTP'}
    VAR_INT={'FLOW': 0, 'ORGN': 1, 'ORGP': 2, 'NO3': 3, 'NH4': 4, 'NO2': 5, 'TOTN': 6, 'TOTP': 7}
    
    SA_METHOD={'Sobol': 'Sobol', 'FAST': 'FAST', 'RBD-FAST': 'RBD_FAST', 'Morris': 'Morris', 'RSA': 'RSA'}
    SAMPLE_METHOD={'Full Factorial Design': 'FFD', 'Latin Hyper Sampling': 'LHS', 'Random': 'Random', 'Fast Sequence': 'FAST_Sequence', 'Morris Sequence': 'Morris_Sequence', 'Saltelli Sequence': 'Saltelli_Sequence'}
    SOP_METHOD={'Genetic Algorithm (GA)': 'GA', 'Particle Swarm Optimization (PSO)': 'PSO', 'Differential Evolution (DE)': 'DE', 'Artificial Bee Colony (ABC)': 'ABC', 'Cooperation Search Algorithm (CSA)': 'CSA', 'Shuffled Complex Evolution-UA (SCE-UA)':'SCE_UA'}
    MOP_METHOD={'Reference Vector guided Evolutionary Algorithm (RVEA)': 'RVEA', 'Non-dominated Sorting Genetic Algorithm II (NSGA-II)': 'NSGAII', 'MultiObjective Evolutionary Algorithm based on Decomposition (MOEA/D)' : 'MOEAD'}
    
    SA_SAMPLE={'Sobol': ['Saltelli Sequence'], 'FAST': ['Fast Sequence'], 'RBD-FAST': ['any'], 'Morris': ['Morris Sequence'], 'RSA': ['any']}
    
    SA_HYPER={'Sobol': {'Z-score':{'type':'bool', 'class': 'Sobol', 'method': '__init__' ,'default': ''}}, 
            #   'Delta Test': {'Z-score':{'decs':'Z-score' , 'class': 'Delta_Test','method': '__init__', 'type':'bool', 'default': '0'}, 'nNeighbors':{'type':'int', 'class': 'Delta_Test','method': '__init__','default': '2'}},
              'FAST': {'Z-score':{'type':'bool', 'method': '__init__', 'class': 'FAST','default': ''}},
              'RBD-FAST': {'Z-score':{'type':'bool', 'class': 'RBD_FAST','method': '__init__', 'default': ''}, 'M':{'type':'int', 'method': '__init__', 'class': 'RBD_FAST', 'default': '4'}},
              'Morris': {'Z-score':{'type':'bool', 'method': '__init__', 'class' : 'Morris','default': ''}},
              'RSA': {'Z-score':{'type':'bool', 'method': '__init__', 'class': 'RSA', 'default': ''}, 'nRegion':{'type':'int','method': '__init__', 'class': 'RSA', 'default': '20'}}}
    
    SAMPLE_HYPER={'Full Factorial Design': {'levels': {'dec': 'Number of Factors *', 'method': '__init__', 'class': 'FFD','type': 'int', 'related': '*','default': '5'}},
              'Latin Hyper Sampling' : {'nt': {'dec': 'Number for sampling *', 'method' : 'sample', 'type': 'int', 'class' : 'LHS', 'related': '*', 'default': '500'}},
              'Random' : {'nt': {'dec': 'Number for sampling *', 'class' : 'Random', 'method' : 'sample', 'type': 'int', 'related' : '*','default': '500'}},
              'Fast Sequence' : { 'M' : {'dec': 'M', 'class' : 'FAST_Sequence', 'method' : '__init__', 'type': 'int', 'default': '5', 'share': '__init__'},
                                  'nt' : {'dec': 'Number for sampling *', 'class' : 'FAST_Sequence','method': 'sample', 'type': 'int', 'related' : '*' ,'default': '500'}
                                },
              'Morris Sequence' : { 'numLevels': {'dec': 'Number of Level', 'class' : 'Morris_Sequence','method': '__init__', 'type': 'int', 'default': '5', 'share' : '__init__'},
                                    'nt' : {'dec': 'Number of Trajectory *', 'class' : 'Morris_Sequence', 'method' : 'sample', 'type': 'int', 'related' : '*','default': '100'}
                                  },
              'Saltelli Sequence' : {'nt': { 'dec': 'Number for sampling *', 'class' : 'Saltelli_Sequence', 'method': 'sample', 'type': 'int', 'related' : '*', 'default': '100'},
                                  'skipValue' : {'dec': 'Skip Values', 'class' : 'Saltelli_Sequence', 'method': '__init__', 'type': 'int', 'default': '5'},
                                  'scramble' : {'dec' : 'Scramble', 'class' : 'Saltelli_Sequence', 'method': '__init__', 'type': 'bool', 'default': 'False'},
                                  'calSecondOrder' : {'dec': 'SecondOrder', 'class': 'Saltelli_Sequence', 'method': '__init__', 'type': 'bool', 'default': 'False', 'share': '__init__', 'related' : '*'}
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
    
    FORMULA={'Full Factorial Design' : 'levels**nInput',
             'Latin Hyper Sampling' : 'nt',
             'Random' : 'nt',
             'Fast Sequence' : 'nt*nInput',  
             'Morris Sequence' : 'nt*(nInput+1)',
             'Saltelli Sequence' : '(2*nt+2)*nInput if calSecondOrder else (nt+2)*nInput'
             }
    
    W=None
    
    #Basic Infos
    projectInfos=None; modelInfos=None
    paraInfos=None; objInfos=None; problemInfos=None
    
    #Sensibility Analysis
    SA_paraInfos={}; SA_runInfos={}; SA_objInfos={}; SA_problemInfos={}
    SA_result={}; SA_infos={}
    
    #Optimization
    OP_paraInfos={}; OP_runInfos={}; OP_objInfos={}; OP_problemInfos={}
    OP_result={}; OP_infos={}
    
    #Validation
    Val_paraInfos={}; Val_runInfos={}; Val_objInfos={}; Val_problemInfos={}
    Val_result={}
    
    btnSets=[]
    
    @classmethod
    def openProject(cls, projectName, projectPath, swatPath, close, activate):
        
        try:
            projectInfos={}
            projectInfos['projectName']=projectName
            projectInfos['projectPath']=projectPath
            projectInfos['swatPath']=swatPath
            projectInfos['tempPath']=os.path.join(projectInfos['projectPath'], 'temp')
            
            projectFile=f"{projectName}.prj"
            
            cls.projectInfos=projectInfos
            
        except Exception as e:
            cls.showError(error=f"Some errors occur in project file, please check!\n The error is {str(e)}.")
            close(500)
            return
        
        def writeProjectFile():
            
            with open(os.path.join(projectPath, projectFile), 'w') as f:
                f.write(f"projectName: {projectName}\n")
                f.write(f"projectPath: {projectInfos['projectPath']}\n")
                f.write(f"swatPath: {projectInfos['swatPath']}\n")
                f.write(f"tempPath: {projectInfos['tempPath']}\n")

        cls.loadModel(close, activate, writeProjectFile)
        
    @classmethod
    def loadModel(cls, close, activate, writeProjectFile):
        
        cls.worker=InitWorker()
        
        cls.thread=NewThread(cls.worker, cls.projectInfos)
        
        def accept():
            
            cls.modelInfos=cls.thread.modelInfos
            close(2000)
            activate()
            writeProjectFile()
            
        def reject(error):
            
            close(500)
            cls.projectInfos=None
            cls.showError(error=error)
        
        cls.thread.accept.connect(accept)
        cls.thread.finished.connect(cls.thread.deleteLater)
        cls.thread.occurError.connect(reject)
        cls.thread.start()
    
    @classmethod
    def loadSAFile(cls, path):
        
        def h5_to_dict(h5_obj):
            result = {}
            for key, item in h5_obj.items():
                if isinstance(item, h5py.Dataset):
                    result[key] = item[()]
                elif isinstance(item, h5py.Group):
                    result[key] = h5_to_dict(item)
            return result
        
        path=os.path.join(cls.projectInfos['projectPath']+"\\Result\\Data", path)
        
        with h5py.File(path, 'r') as file:
            
            SAData= h5_to_dict(file)
        
        return SAData
    
    @classmethod
    def loadOPFile(cls, path):
        
        def h5_to_dict(h5_obj):
            result = {}
            for key, item in h5_obj.items():
                if isinstance(item, h5py.Dataset):
                    result[key] = item[()]
                elif isinstance(item, h5py.Group):
                    result[key] = h5_to_dict(item)
            return result
        
        path=os.path.join(cls.projectInfos['projectPath']+"\\Result\\Data", path)
        
        with h5py.File(path, 'r') as file:
            
            OPData= h5_to_dict(file)
        
        return OPData
    
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
        
        if printFlag==1:
            nowDate=beginDate.addDays(delta)
            index=baseDate.daysTo(nowDate)
            return index, nowDate.year(), nowDate.month(), nowDate.day()
        else:
            nowDate=beginDate.addMonths(delta)
            index=nowDate.month()-baseDate.month()+1
            return index, nowDate.year(), nowDate.month(), 1 
        
    @classmethod 
    def importObjFromFile(cls, path):
        
        try:
            cls.worker=ReadWorker()
            infos=cls.worker.readObjFile(path)
            return infos, True
                
        except Exception as e:
            cls.showError(error=f"There exists some errors in objective file, please check! \n The error is {str(e)}.")
            return {}, False   
   
    @classmethod
    def importParaFromFile(cls, path):
        
        try:
            infos=[]
            worker=ReadWorker()
            infos=worker.readParaFile(path, cls.modelInfos)
            return infos, True
        
        except Exception as e:
            cls.showError(error=f"There are some error in parameter file, please check! \n The error is {str(e)}.")
            return {}, False
        
    @classmethod
    def saveParaFile(cls, infos, path):
        
        with open(path, 'w') as f:
            lines=[" ".join(info)+"\n" for info in infos]
            f.writelines(lines)
        
    @classmethod
    def saveObjFile(cls, path, objInfos):
        
        worker=SaveWorker()
        
        lines=worker.saveProFile(objInfos)
        
        with open(path, 'w') as f:
            f.writelines(lines)
    
    @classmethod
    def findSOPResultFile(cls):
        
        path=os.path.join(cls.projectInfos['projectPath'], "Result\\Data")
        res_files=glob.glob(os.path.join(path, "*.hdf"))
        files=[os.path.basename(file_path) for file_path in res_files]
        
        SOP_List=list(cls.SOP_METHOD.values())
        
        sop_files=[]
        for file in files:
            for name in SOP_List:
                if name in file:
                    sop_files.append(file)
                    break
            
        return sop_files
    
    @classmethod
    def findMOPResultFile(cls):
        pass
    
    @classmethod
    def findSAResultFile(cls):
        
        path=os.path.join(cls.projectInfos['projectPath'], "Result\\Data")
        res_files=glob.glob(os.path.join(path, "*.hdf"))
        files=[os.path.basename(file_path) for file_path in res_files]
        
        SA_List=list(cls.SA_METHOD.values())
        
        sa_files=[]
        for file in files:
            for name in SA_List:
                if name in file:
                    sa_files.append(file)
                    break
            
        return sa_files        
    
    @classmethod
    def findParaFile(cls):
        
        par_files = glob.glob(os.path.join(cls.projectInfos['projectPath'], "*.par"))
        files=[os.path.basename(file_path) for file_path in par_files]
        
        return files
    
    @classmethod
    def findObjFile(cls):
        
        pro_files=glob.glob(os.path.join(cls.projectInfos['projectPath'], "*.obj"))
        files=[os.path.basename(file_path) for file_path in pro_files]
        
        return files
    
    @classmethod
    def findSwatExe(cls):
        
        swatPath=cls.projectInfos['swatPath']
        exe_name= glob.glob(os.path.join(swatPath, "*.exe"))
        name=[os.path.basename(file_path) for file_path in exe_name]

        return name
    
    ##############sensibility analysis####################
    @classmethod
    def initSA(cls, verboseWidget, btn):
        
        cls.SA_runInfos["numThreads"]=12 

        cls.worker = InitWorker()
        cls.thread = InitThread(cls.worker, cls.projectInfos, cls.modelInfos, cls.SA_paraInfos, cls.SA_objInfos, cls.SA_runInfos)
        
        Verbose.workDir=cls.projectInfos['projectPath']
        Verbose.total_width=verboseWidget.property('totalWidth')
        
        def accept(infos):
            
            cls.SA_problemInfos=infos["problemInfos"]
            cls.SA_runInfos=infos["runInfos"]
            cls.SA_objInfos=infos['objInfos']
            cls.thread.quit()
            cls.thread.deleteLater()
            
            worker=VerboseWorker(cls.projectInfos, cls.modelInfos, cls.SA_paraInfos, cls.SA_objInfos, cls.SA_runInfos)
            
            verbose=worker.outputVerbose()
            
            text="\n".join(verbose)
            
            verboseWidget.setText(text)
            verboseWidget.verticalScrollBar().setValue(verboseWidget.verticalScrollBar().maximum())

            btn.setEnabled(True)
            
        def showError(infos):
            
            cls.showError(title="Error in Sensitivity Analysis", error=f"There exists some errors. \n {infos} \n If you can't solve this problem, please contact the developer!")
        
        cls.thread.errorOccur.connect(showError)
        cls.worker.result.connect(accept)
        cls.thread.start()
    
    @classmethod
    def sampling(cls):
        
        SAInfos=cls.SA_infos
        paraInfos=cls.SA_paraInfos
        
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
        
        try:
            
            X=sampler.sample(**sampleHyper) 
            X=X*(ub-lb)+lb
            cls.SA_result['X']=X
            
            return True
        
        except Exception as e:
            
            cls.showError(error=f"Sampling failed, please check the hyperparameters! \n The error is {e}.")
            
            return False
        
    @classmethod 
    def simulation(cls, processBar, statistics, finish, unfinish):
        
        tolN=cls.SA_result['X'].shape[0]
        
        def update_progress(value):
            
            percent=value/tolN*100
            statistics.setText(f"{int(value)}/{tolN} FEs")
            processBar.setValue(percent)
        
        def accept(Y):
            
            cls.SA_result['Y']=abs(Y)

            try:
                tempPath=cls.SA_runInfos['tempPath']
                shutil.rmtree(tempPath)
            except Exception as e:
                cls.showError(error=f"Failed to delete temporary files, please remove them by yourself. \n The error is {str(e)}.")
            
        cls.SA_worker=RunWorker(cls.modelInfos, cls.SA_paraInfos, cls.SA_objInfos, cls.SA_problemInfos, cls.SA_runInfos)
        cls.SA_worker.result.connect(accept)
        cls.SA_worker.result.connect(finish)
        cls.SA_worker.unfinished.connect(unfinish)
        
        cls.SA_thread=EvaluateThread(cls.SA_worker, cls.SA_result['X'])
        cls.SA_worker.updateProcess.connect(update_progress)
        cls.SA_thread.finished.connect(cls.SA_thread.deleteLater)
        
        cls.SA_thread.start()
    
    @classmethod
    def sensibility_analysis(cls, verboseWidget):
        
        SAInfos=cls.SA_infos
        initHyper={}
        analyzeHyper={}
        saClass=SAInfos['saClass']
        saHyper=SAInfos['saHyper']
        smHyper=SAInfos['smHyper']
        
        for hyper in smHyper:
            if 'share' in hyper:
                name=hyper['name']
                func=hyper['share']
                value=hyper['value']
                if func=="__init__":
                    initHyper[name]=value
                else:
                    analyzeHyper[name]=value
                     
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
        initHyper['saveFlag']=True
        
        sa=eval(saClass)(**initHyper)
        
        analyzeHyper['X']=cls.SA_result['X']
        analyzeHyper['Y']=cls.SA_result['Y']
        
        ub=cls.SA_problemInfos['ub']
        lb=cls.SA_problemInfos['lb']
        nInput=cls.SA_problemInfos['nInput']
        xLabels=cls.SA_problemInfos['xLabels']
        
        problem=PracticalProblem(None, nInput, 1, ub, lb, x_labels=xLabels, name=cls.SA_problemInfos['name'])
        #TODO
        problem.workDir=cls.projectInfos['projectPath']
        problem.totalWidth=cls.SA_runInfos['verboseWidth']
        problem.GUI=True

        try:
            sa.analyze(problem=problem, **analyzeHyper)
            verboseWidget.append("\n".join(sa.problem.logLines))
        except Exception as e:
            cls.showError(title="Error in sensibility analysis", error=f"The error is {e}. \n If you can't solve this problem, please contact the developer!")
        
    #################################################
    @classmethod
    def initOP(cls, verboseWidget, btn):
        
        cls.OP_runInfos["numThreads"]=12 

        cls.worker = InitWorker()
        cls.thread = InitThread(cls.worker, cls.projectInfos, cls.modelInfos, cls.OP_paraInfos, cls.OP_objInfos, cls.OP_runInfos)
        
        Verbose.workDir=cls.projectInfos['projectPath']
        Verbose.total_width=verboseWidget.property('totalWidth')
        
        def accept(infos):
            
            cls.OP_problemInfos=infos["problemInfos"]
            cls.OP_runInfos=infos["runInfos"]
            cls.OP_objInfos=infos['objInfos']
            cls.thread.quit()
            cls.thread.deleteLater()
            
            worker=VerboseWorker(cls.projectInfos, cls.modelInfos, cls.OP_paraInfos, cls.OP_objInfos, cls.OP_runInfos)
            
            verbose=worker.outputVerbose()
            
            text="\n".join(verbose)
            
            verboseWidget.setText(text)
            verboseWidget.verticalScrollBar().setValue(verboseWidget.verticalScrollBar().maximum())

            btn.setEnabled(True)
            
        def showError(infos):
            cls.showError(title="Error in Optimization", error=f"{infos}.\n If you can't solve this problem, please contact the developer!")
        
        cls.thread.errorOccur.connect(showError)
        cls.worker.result.connect(accept)
        cls.thread.start()
    
    ##################################################
    
    @classmethod
    def cancelSA(cls):
        
        cls.SA_worker.stop=True
    
    @classmethod
    def cancelOpt(cls):
        
        cls.OP_worker.stop=True
        cls.OP_thread.problem.isStop=True
    
    @classmethod
    def optimizing(cls, FEsBar, itersBar, FEsLabel, itersLabel, verbose, finish, unfinish):
        
        cls.OP_result={}
        cls.OP_result['verbose']=[]
        
        opInfos=cls.OP_infos
        
        opClass=opInfos['opClass']
        opHyper=opInfos['opHyper']
        
        initHyper={}
        
        for hyper in opHyper:
            name=hyper['name']
            func=hyper['method']
            value=hyper['value']
            
            if func=="__init__":
                initHyper[name]=value
        
        initHyper['verboseFreq']=1
        initHyper['verbose']=True
        initHyper['saveFlag']=True
        
        optimizer=eval(opClass)(**initHyper)
        
        maxFEs=initHyper['maxFEs']
        maxIterTimes=initHyper['maxIterTimes']
        
        def update_FEsBar(value):
            
            percent=value/maxFEs*100
            FEsBar.setValue(percent)
            FEsLabel.setText(f"{int(value)}/{maxFEs} FEs")
        
        def update_itersBar(value):
            
            percent=value/maxIterTimes*100
            itersBar.setValue(percent)
            itersLabel.setText(f"{int(value)}/{maxIterTimes} iters")
            
        def update_verbose(txt):
            
            cls.OP_result['verbose'].append(txt+'\n')
            verbose.append(txt+'\n')
             
        def saveResult():
            
            cls.OP_result['bestDec']=optimizer.result.bestDec
            cls.OP_result['bestObj']=optimizer.result.bestObj
            cls.OP_result['historyBestDecs']=optimizer.result.historyBestDecs
            cls.OP_result['historyBestObjs']=optimizer.result.historyBestObjs
        
        def showError(infos):
            
            cls.showError(title="Error in Optimization", content=f"The error is {infos}. \n If you cannot solve this problem, please contact the developer!")
        
        def deleteTempFiles():
            
            try:
                tempPath=cls.OP_runInfos['tempPath']
                shutil.rmtree(tempPath)
            except Exception as e:
                cls.showError(error=f"Failed to delete temporary files, please remove them by yourself.\n The error is {str(e)}.")
        
        iterEmit=IterEmit()
        verboseEmit=VerboseEmit()
        
        cls.OP_worker=RunWorker(cls.modelInfos, cls.OP_paraInfos, cls.OP_objInfos, cls.OP_problemInfos, cls.OP_runInfos)
        cls.OP_worker.updateProcess.connect(update_FEsBar)
        
        iterEmit.iterSend.connect(update_itersBar)
        verboseEmit.verboseSend.connect(update_verbose)

        cls.OP_thread=OptimizeThread(cls.OP_worker, optimizer, cls.OP_problemInfos)
        cls.OP_thread.errorOccur.connect(showError)
        cls.OP_thread.problem.GUI=True
        cls.OP_thread.problem.iterEmit=iterEmit
        cls.OP_thread.problem.verboseEmit=verboseEmit
        cls.OP_thread.problem.isStop=False
        cls.OP_thread.problem.totalWidth=cls.OP_runInfos['verboseWidth']
        cls.OP_thread.problem.workDir=cls.projectInfos['projectPath']
        
        cls.OP_thread.finished.connect(cls.OP_thread.deleteLater)
        iterEmit.iterFinished.connect(finish)
        iterEmit.iterStop.connect(unfinish)
        
        iterEmit.iterFinished.connect(deleteTempFiles)
        iterEmit.iterStop.connect(deleteTempFiles)
        cls.OP_thread.finished.connect(saveResult)
    
        cls.OP_thread.start()
        
    ################################
    
    @classmethod
    def initVal(cls, verboseWidget, btn):
        
        cls.Val_runInfos["numThreads"]=12 

        cls.Val_worker = InitWorker()
        cls.Val_thread = InitThread(cls.Val_worker, cls.projectInfos, cls.modelInfos, cls.Val_paraInfos, cls.Val_objInfos, cls.Val_runInfos)
        
        Verbose.workDir=cls.projectInfos['projectPath']
        Verbose.total_width=verboseWidget.property('totalWidth')
        
        def accept(infos):
            
            cls.Val_problemInfos=infos["problemInfos"]
            cls.Val_runInfos=infos["runInfos"]
            cls.Val_objInfos=infos['objInfos']
            cls.Val_thread.quit()
            cls.Val_thread.deleteLater()
            
            worker=VerboseWorker(cls.projectInfos, cls.modelInfos, cls.Val_paraInfos, cls.Val_objInfos, cls.Val_runInfos)
            
            verbose=worker.outputVerbose()
            
            text="\n".join(verbose)
            
            verboseWidget.setText(text)
            verboseWidget.verticalScrollBar().setValue(verboseWidget.verticalScrollBar().maximum())

            btn.setEnabled(True)
            
        def showError(infos):
            
            cls.showError(title="Error in Validation", error=f"{infos}.\n If you can't solve this problem, please contact the developer!")
        
        cls.Val_thread.errorOccur.connect(showError)
        cls.Val_worker.result.connect(accept)
        cls.Val_thread.start()
        
    @classmethod
    def singleSim(cls, x, finish):
        
        cls.worker=RunWorker(cls.modelInfos, cls.Val_paraInfos, cls.Val_objInfos, cls.Val_problemInfos, cls.Val_runInfos)
        cls.thread=SingleEvaluateThread(cls.worker, x)
        
        def accept(res):
            cls.Val_result=res
        
        cls.worker.result.connect(accept)
        cls.worker.result.connect(finish)
        cls.thread.finished.connect(cls.thread.deleteLater)
        cls.thread.start()
    
    @classmethod
    def showError(cls, title="Errors Occur", error=""):
        
        box=MessageBox(title=title, content=error, parent=cls.W)
        box.show()
        
    @classmethod
    def clearAll(cls):
        
        btnSets=Project.btnSets
        
        for btn in btnSets[1:]:
            btn.setEnabled(False)
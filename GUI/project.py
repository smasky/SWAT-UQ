import os
import glob
import numpy as np
import sys
import h5py
from datetime import datetime
from .worker import (InitWorker, ReadWorker, SaveWorker, InitThread, OptimizeThread, IterEmit, VerboseEmit, NewThread,
                    VerboseWorker, RunWorker, EvaluateThread, SingleEvaluateThread)
#C++ Module
from .pyd.swat_utility import read_value_swat, copy_origin_to_tmp, write_value_to_file, read_simulation
from UQPyL.DoE import LHS, FFD, Morris_Sequence, FAST_Sequence, Sobol_Sequence, Random, Saltelli_Sequence
from UQPyL.sensibility import Sobol, Delta_Test, FAST, RBD_FAST, Morris, RSA
from UQPyL.optimization import GA, DE, SCE_UA, PSO
from UQPyL.problems import PracticalProblem
from UQPyL.utility.scalers import StandardScaler
from UQPyL.utility.verbose import Verbose
from PyQt5.QtCore import QDate, Qt
from .component.info_bar import InfoBar_ as InfoBar, InfoBarPosition

class Project:

    INT_MODE={0: 'r', 1: 'v', 2: 'a'}; MODE_INT={'r': 0, 'v':1, 'a':2}
    INT_OBJTYPE={0: 'NSE', 1: 'RMSE', 2: 'PCC', 3: 'Pbias', 4: 'KGE'}; OBJTYPE_INT={'NSE': 0, 'RMSE':1, 'PCC':2, 'Pbias':3, 'KGE':4}
    INT_VAR={0: 'Flow'}; VAR_INT={'Flow': 0}
    
    SA_METHOD={'Sobol': 'Sobol', 'Delta Test': 'Delta_Test', 'FAST': 'FAST', 'RBD-FAST': 'RBD_FAST', 'Morris': 'Morris', 'RSA': 'RSA'}
    SAMPLE_METHOD={'Full Factorial Design': 'FFD', 'Latin Hyper Sampling': 'LHS', 'Random': 'Random', 'Fast Sequence': 'FAST_Sequence', 'Morris Sequence': 'Morris_Sequence', 'Saltelli Sequence': 'Saltelli_Sequence'}
    SOP_METHOD={'Genetic Algorithm (GA)': 'GA', 'Particle Swarm Optimization (PSO)': 'PSO', 'Differential Evolution (DE)': 'DE', 'Artificial Bee Colony (ABC)': 'ABC', 'Cooperation Search Algorithm (CSA)': 'CSA', 'Shuffled Complex Evolution-UA (SCE-UA)':'SCE_UA'}
    MOP_METHOD={'Reference Vector guided Evolutionary Algorithm (RVEA)': 'RVEA', 'Non-dominated Sorting Genetic Algorithm II (NSGA-II)': 'NSGAII', 'MultiObjective Evolutionary Algorithm based on Decomposition (MOEA/D)' : 'MOEAD'}
    
    SA_SAMPLE={'Sobol': ['Saltelli Sequence'], 'Delta Test': ['any'], 'FAST': ['Fast Sequence'], 'RBD-FAST': ['any'], 'Morris': ['Morris Sequence'], 'RSA': ['any']}
    
    SA_HYPER={'Sobol': {'Z-score':{'type':'bool', 'class': 'Sobol', 'method': '__init__' ,'default': ''}}, 
              'Delta Test': {'Z-score':{'decs':'Z-score' , 'class': 'Delta_Test','method': '__init__', 'type':'bool', 'default': '0'}, 'nNeighbors':{'type':'int', 'class': 'Delta_Test','method': '__init__','default': '2'}},
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
    
    window=None; projectInfos=None; modelInfos=None; paraInfos=None; proInfos=None; objInfos=None
    problemInfos=None; SAInfos=None; SAResult=None; OPInfos=None; OPResult=None
    ValResult=None
    
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
            
            with open(os.path.join(projectPath, projectFile), 'w') as f:
                f.write(f"projectName: {projectName}\n")
                f.write(f"projectPath: {projectInfos['projectPath']}\n")
                f.write(f"swatPath: {projectInfos['swatPath']}\n")
                f.write(f"tempPath: {projectInfos['tempPath']}\n")
            
            cls.projectInfos=projectInfos
            
        except Exception as e:
            
            cls.showError("Some errors occur in project file, please check!")

            return
        cls.loadModel(close, activate)

    @classmethod
    def loadModel(cls, close, activate):
        
        cls.worker=InitWorker()
        cls.thread=NewThread(cls.worker, cls.projectInfos)
        
        def accept():
            cls.modelInfos=cls.thread.modelInfos
            close()
            activate()
        
        def reject(error):
            cls.showError(error)
        
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
    def findResultFile(cls):
        
        path=os.path.join(cls.projectInfos['projectPath'], "Result\\Data")
        res_files=glob.glob(os.path.join(path, "*.hdf"))
        
        files=[os.path.basename(file_path) for file_path in res_files]
        
        return files
    
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
        
        try:
            
            X=sampler.sample(**sampleHyper) 
            X=X*(ub-lb)+lb
            cls.SAResult={}
            cls.SAResult['X']=X
            
            return True
        
        except Exception as e:
            
            cls.showError(f"Sampling failed, please check the hyperparameters!\n The error is {e}")
            
            return False
    
    @classmethod
    def singleSim(cls, x, finish):
        
        
        cls.worker=RunWorker(cls.projectInfos, cls.modelInfos, cls.paraInfos, cls.objInfos, cls.problemInfos)
        cls.thread=SingleEvaluateThread(cls.worker, x)
        
        
        def accept(res):
            
            cls.ValResult=res
        
        cls.worker.result.connect(accept)
        cls.worker.result.connect(finish)
        cls.thread.finished.connect(cls.thread.deleteLater)
        cls.thread.start()
    
    
    @classmethod 
    def simulation(cls, processBar, statistics, finish, unfinish):
        
        tolN=cls.SAResult['X'].shape[0]
        
        def update_progress(value):
            
            percent=value/tolN*100
            statistics.setText(f"{int(value)}/{tolN} FEs")
            processBar.setValue(percent)
        
        def accept(Y):
            
            cls.SAResult['Y']=abs(Y)
        
        cls.worker=RunWorker(cls.projectInfos, cls.modelInfos, cls.paraInfos, cls.objInfos, cls.problemInfos)
        cls.worker.result.connect(accept)
        cls.worker.result.connect(finish)
        cls.worker.unfinished.connect(unfinish)
        cls.thread=EvaluateThread(cls.worker, cls.SAResult['X'])
        cls.worker.updateProcess.connect(update_progress)
        cls.thread.finished.connect(cls.thread.deleteLater)  # 确保线程完成后被清理
        
        cls.thread.start()
    
    @classmethod
    def cancelSA(cls):
        
        cls.worker.stop=True
    
    @classmethod
    def cancelOpt(cls):
        
        cls.worker.stop=True
        Verbose.isStop=True
    
    @classmethod
    def optimizing(cls, FEsBar, itersBar, FEsLabel, itersLabel, verbose, finish, unfinish):
        
        cls.OPResult={}
        cls.OPResult['verbose']=[]
        
        opInfos=cls.OPInfos
        
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
            
            cls.OPResult['verbose'].append(txt+'\n')
            verbose.append(txt+'\n')
        
        def reset():
            
            Verbose.isStop=False
            Verbose.iterEmit=None
            Verbose.verboseEmit=None
        
        def saveResult():
            
            cls.OPResult['bestDec']=optimizer.result.bestDec
            cls.OPResult['bestObj']=optimizer.result.bestObj
            cls.OPResult['historyBestDecs']=optimizer.result.historyBestDecs
            cls.OPResult['historyBestObjs']=optimizer.result.historyBestObjs
        
        iterEmit=IterEmit()
        verboseEmit=VerboseEmit()
        cls.worker=RunWorker(cls.projectInfos, cls.modelInfos, cls.paraInfos, cls.objInfos, cls.problemInfos)
        cls.worker.updateProcess.connect(update_FEsBar)
        iterEmit.iterSend.connect(update_itersBar)
        Verbose.iterEmit=iterEmit
        Verbose.verboseEmit=verboseEmit

        verboseEmit.verboseSend.connect(update_verbose)
        cls.thread=OptimizeThread(cls.worker, optimizer, cls.problemInfos)
        cls.thread.finished.connect(cls.thread.deleteLater)
        iterEmit.iterFinished.connect(finish)
        iterEmit.iterStop.connect(unfinish)
        cls.thread.finished.connect(reset)
        cls.thread.finished.connect(saveResult)
        cls.thread.start()
        
    @classmethod
    def initProject(cls, verboseWidget, btn):
        
        cls.projectInfos["numThreads"]=12 

        cls.worker = InitWorker()
        cls.thread = InitThread(cls.worker, cls.projectInfos, cls.modelInfos, cls.paraInfos, cls.objInfos)
        
        Verbose.workDir=cls.projectInfos['projectPath']
        
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
        
    @classmethod
    def showError(cls, error):
         
        InfoBar.error(
                title='Error',
                content=error,
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=20000,
                parent=cls.window
                )
    
    @classmethod
    def clearAll(cls):
        
        cls.window=None
        cls.projectInfos=None
        cls.modelInfos=None
        cls.paraInfos=None
        cls.proInfos=None
        cls.objInfos=None
        cls.problemInfos=None
        cls.SAInfos=None
        cls.SAResult=None
        cls.OPInfos=None
        cls.OPResult=None

        btnSets=Project.btnSets
        
        for btn in btnSets[1:]:
            btn.setEnabled(False)
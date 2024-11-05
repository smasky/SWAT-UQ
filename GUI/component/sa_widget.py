from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, QFormLayout, QGridLayout,
                             QStackedWidget, QWidget,  QFileDialog)
from PyQt5.QtCore import  Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics
from qfluentwidgets import (BodyLabel,
                             SpinBox,TextEdit,
                             PrimaryPushButton, LineEdit)
import os
import copy
import GUI.qss
import GUI.data
from importlib.resources import path
from UQPyL.utility import Verbose
from .process_widget import ProcessWidget
from .button_group import ButtonGroup
from .hyper_widget import hyperWidget
from .combox_ import ComboBox_ as ComboBox
from ..project import Project as Pro
from .progress_bar import ProgressBar_ as ProgressBar
from .utility import setFont, Normal, Medium, MediumSize
class SAWidget(QFrame):
    INDEX=0
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        
        ##########################Process Widget########################
        processWidget=ProcessWidget(self)
        processWidget.addStep(0, "Setup")
        processWidget.addStep(1, "Simulation")
        processWidget.addStep(2, "Analysis")
        self.processWidget=processWidget
        vBoxLayout.addWidget(processWidget)
        #################################################################
        
        contentWidget=QStackedWidget(self)
        contentWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        contentWidget.setObjectName("contentWidget")
        vBoxLayout.addWidget(contentWidget)
        
        #################################################################
        
        self.setupWidget=SetupWidget(self)
        
        contentWidget.addWidget(self.setupWidget)
        self.simulationWidget=SimulationWidget(self)
        contentWidget.addWidget(self.simulationWidget)
        self.analysisWidget=AnalysisWidget(self)
        contentWidget.addWidget(self.analysisWidget)
        contentWidget.setCurrentIndex(0)
        self.contentWidget=contentWidget
        ##################################################################
        
        self.nextButton=PrimaryPushButton("Next", self)
        self.nextButton.setEnabled(False)
        setFont(self.nextButton)
        self.nextButton.setMinimumWidth(150)
        
        self.resetBtn=PrimaryPushButton("Reset", self)
        self.resetBtn.setMinimumWidth(150)
        self.resetBtn.clicked.connect(self.reset)
        setFont(self.resetBtn)
        
        h=QHBoxLayout();h.addStretch(1);h.addWidget(self.nextButton);h.addSpacing(20);h.addWidget(self.resetBtn) ;h.addStretch(1)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        #connect
        self.nextButton.clicked.connect(self.nextPage)
        self.setupWidget.nextBtn.connect(self.nextButton.setEnabled)
        self.simulationWidget.nextBtn.connect(self.nextButton.setEnabled)
        self.simulationWidget.resetBtn.connect(self.resetBtn.setEnabled)
        
        #qss
        with path(GUI.qss, "sa_widget.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        
    def updateUI(self):
        self.setupWidget.updateUI()
    
    def reset(self):
        
        Pro.SA_objInfos={}
        Pro.SA_paraInfos={}
        Pro.SA_problemInfos={}
        Pro.SA_result={}
        Pro.SA_runInfos={}
        Pro.SA_infos={}
        
        self.contentWidget.setCurrentIndex(0)
        self.setupWidget.reset()
        self.simulationWidget.reset()
        self.processWidget.reset()
        self.INDEX=0
        
    def nextPage(self):
        
        if self.INDEX==0:
            widget=self.setupWidget
            hyper=self.setupWidget.hyperStack.widget(1).returnHyper()

            sa=widget.SA_METHOD[widget.saBtnGroup.currentIndex]
            sm=widget.SAMPLE_METHOD[widget.smBtnGroup.currentIndex]
            Pro.SA_infos={'saName': sa, 'saClass': Pro.SA_METHOD[sa],'saHyper': hyper[Pro.SA_METHOD[sa]],
                         'smName': sm,'smClass' : Pro.SAMPLE_METHOD[sm],'smHyper': hyper[Pro.SAMPLE_METHOD[sm]]}
            
        self.INDEX+=1
        self.contentWidget.setCurrentIndex(self.INDEX)
        self.contentWidget.currentWidget().updateUI()
        self.processWidget.on_button_clicked(self.INDEX)
        
        self.nextButton.setEnabled(False)

class SetupWidget(QWidget):
    nextBtn=pyqtSignal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0,15,0,0)
        contentWidget=QWidget(self)
        #######################Parameter Path############################
        gridLayout=QGridLayout(contentWidget)
        gridLayout.setVerticalSpacing(10)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        ####
        label=BodyLabel("Parameter File:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 0, 1, Qt.AlignmentFlag.AlignVCenter)
        
        
        self.paraEdit=ComboBox(self )
        self.paraEdit.currentIndexChanged.connect(self.loadParaFile)
        self.paraEdit.currentIndexChanged.connect(self.activateSABtn)
        self.paraEdit._showComboMenu=self.dynamicShowPara
        setFont(self.paraEdit)
        self.paraEdit.setPlaceholderText("Click to select parameter file")
        gridLayout.addWidget(self.paraEdit, 0, 2, Qt.AlignmentFlag.AlignVCenter)
        ##########
        label=BodyLabel("Number of Parameters:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 0, 4, Qt.AlignmentFlag.AlignVCenter)
        self.numPara=LineEdit(self); self.numPara.setEnabled(False)
        setFont(self.numPara)
        gridLayout.addWidget(self.numPara, 0, 5, Qt.AlignmentFlag.AlignVCenter)
        
        ######################Objective Path###########################
        label=BodyLabel("Objective File:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        
        self.objLine=ComboBox(self)
        setFont(self.objLine)
        self.objLine._showComboMenu=self.dynamicShowObj
        self.objLine.setPlaceholderText("Click to select objective file")
     
        gridLayout.addWidget(self.objLine, 1, 2, Qt.AlignmentFlag.AlignVCenter)
        self.objLine.currentIndexChanged.connect(self.loadObjFile)
        self.objLine.currentIndexChanged.connect(self.activateSABtn)
        
        label=BodyLabel("Selection of Objectives:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 1, 4, Qt.AlignmentFlag.AlignVCenter)
        
        self.objEdit=ComboBox(self)
        self.objEdit.setEnabled(True)
        setFont(self.objEdit)
        self.objEdit.currentIndexChanged.connect(self.ensureObj)
        gridLayout.addWidget(self.objEdit, 1, 5, Qt.AlignmentFlag.AlignVCenter)
        
        index=[ 1, 2, 3, 4, 5]
        width=[210, 310, 50, 210, 270]
        for i, w in zip(index, width):
            qw=QWidget();qw.setFixedHeight(10);qw.setFixedWidth(w)
            gridLayout.addWidget(qw, 2, i)
        
        for i in range(2):
            qw=QWidget();qw.setFixedHeight(45)
            gridLayout.addWidget(qw, i, 0)

        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setColumnStretch(2, 1)
        gridLayout.setColumnStretch(3, 1)
        gridLayout.setColumnStretch(4, 1)
        gridLayout.setColumnStretch(5, 1)
        gridLayout.setColumnStretch(6, 1)
       
        label=BodyLabel("Sensibility Analysis:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        
        self.saBtnGroup=ButtonGroup(Pro.SA_METHOD.keys(), False, self)
        self.SA_METHOD=list(Pro.SA_METHOD.keys())
        gridLayout.addWidget(self.saBtnGroup, 3, 2, 1, 4, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Sampling Method:")
        
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 4, 1, Qt.AlignmentFlag.AlignVCenter)
        
        self.smBtnGroup=ButtonGroup(Pro.SAMPLE_METHOD.keys(), False, self)
        self.SAMPLE_METHOD=list(Pro.SAMPLE_METHOD.keys())
        gridLayout.addWidget(self.smBtnGroup, 4, 2, 1, 4, Qt.AlignmentFlag.AlignVCenter)
        
        vBoxLayout.addWidget(contentWidget)
        vBoxLayout.addSpacing(10)
        
        self.hyperStack=QStackedWidget(self)
        self.hyperStack.setContentsMargins(0, 0, 0, 0)
        vBoxLayout.addWidget(self.hyperStack)
        w=QWidget(); w.setFixedHeight(10)
        self.hyperStack.addWidget(w)
        self.hyperStack.setCurrentIndex(0)
        
        vBoxLayout.addStretch(1)
        
        conclusionWidget=QWidget(self)
        conclusionWidget.setObjectName("conclusionWidget")
        h=QHBoxLayout(conclusionWidget)
        labelC=BodyLabel('The total number of sampling points is:')
        setFont(labelC)
        lineC=LineEdit(self); lineC.setEnabled(False);lineC.setToolTip("Please select the Sensitivity Analysis and Sampling Method first.")
        self.numLine=lineC; self.numLine.setMinimumWidth(150)
        setFont(lineC)
        h.addSpacing(50); h.addWidget(labelC); h.addWidget(lineC);h.addStretch(1)
        h.setContentsMargins(0, 10, 0, 10)
        
        vBoxLayout.addWidget(conclusionWidget)
        
        self.saBtnGroup.group.idClicked.connect(self.enableSampling)
        self.saBtnGroup.group.idClicked.connect(self.updateHyper)
        self.smBtnGroup.group.idClicked.connect(self.updateHyper)
        self.saBtnGroup.group.buttonClicked.connect(self.updateNextButton)
        
        # self.reset()
        
    def activateSABtn(self):
        
        i=self.paraEdit.currentIndex()
        j=self.objLine.currentIndex()
        
        if(i>=0 and j>=0):
            self.saBtnGroup.setEnabled_(True)
            btn=self.saBtnGroup.group.buttons()[0]
            btn.click()
        else:
            self.saBtnGroup.setEnabled_(False)
            self.hyperStack.setCurrentIndex(0)
            self.smBtnGroup.setEnabled_(False)
            self.nextBtn.emit(False)
    
    def updateHyper(self):
        
        num=self.hyperStack.count()
        if num>1:
            widget=self.hyperStack.widget(1)
            self.hyperStack.removeWidget(widget)
        
        I_SA=self.saBtnGroup.currentIndex
        I_SM=self.smBtnGroup.currentIndex
        
        options=copy.deepcopy(Pro.SA_HYPER[self.SA_METHOD[I_SA]])
        options.update(Pro.SAMPLE_HYPER[self.SAMPLE_METHOD[I_SM]])
        
        hyper=hyperWidget(options)
        self.hyperStack.addWidget(hyper)
        self.hyperStack.setCurrentIndex(1)
        hyper.changed.connect(self.updateNumSampling)
        hyper.changed.emit()
        
        self.nextBtn.emit(True)
        
    def updateNumSampling(self):
        
        widget=self.sender()
        related=widget.returnRelated()
        
        add={'nInput': int(self.numPara.text())}
        related.update(add)
        
        I_SM=self.smBtnGroup.currentIndex
        formula=Pro.FORMULA[self.SAMPLE_METHOD[I_SM]]
        
        num=eval(formula, related)
        self.numLine.setText(str(num))
    
    def dynamicShowPara(self):
        
        self.paraEdit.clear()
        self.numPara.clear()
        self.paraEdit.addItems(Pro.findParaFile())
        # self.paraEdit.setCurrentIndex(0)
        super(ComboBox, self.paraEdit)._showComboMenu()
        

    def dynamicShowObj(self):
        
        self.objLine.clear()
        self.objEdit.clear()
        self.objLine.addItems(Pro.findObjFile())
        # self.objLine.setCurrentIndex(0)
        super(ComboBox, self.objLine)._showComboMenu()

    def reset(self):
        
        self.objLine.clear()
        self.objLine.setPlaceholderText("Click to select objective file")
        self.paraEdit.clear()
        self.paraEdit.setPlaceholderText("Click to select parameter file")
        self.objEdit.clear()
        self.numPara.clear()
        self.numLine.clear()
        
        self.saBtnGroup.setEnabled_(False)
        self.smBtnGroup.setEnabled_(False)
        self.hyperStack.setCurrentIndex(0)
        
    def updateUI(self):
        pass
    
    def loadParaFile(self):
        
        path=self.paraEdit.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], path)
        infos, res=Pro.importParaFromFile(path)
        
        if res:
            
            self.numPara.setText(str(len(infos)))
            
            Pro.SA_paraInfos=infos
            Pro.SA_runInfos['paraPath']=path
            
        else:
            
            self.paraEdit.setCurrentIndex(-1)
        
    def loadObjFile(self):
        
        path=self.objLine.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], path)
        infos, res=Pro.importObjFromFile(path)
        
        if res:
            
            self.objInfos=infos
            self.objEdit.clear()
            self.objEdit.addItems([f"obj {i : d}" for i in list(infos.keys())])
            self.objEdit.setCurrentIndex(0)
            
            Pro.SA_runInfos['objPath']=path
        
        else:
            
            self.objLine.setCurrentIndex(-1)
            
    def ensureObj(self):
        
        objID=int(self.objEdit.text().split()[1])
        Pro.SA_objInfos={objID: self.objInfos[objID]}
      
    def updateNextButton(self):
        
        selectedSA=self.saBtnGroup.group.checkedButton()
        selectedSampling=self.smBtnGroup.group.checkedButton()
        
        if selectedSA and selectedSampling:
            self.nextBtn.emit(True)
        else:
            self.nextBtn.emit(False)
            
    def enableSampling(self, i):
        saName=self.SA_METHOD[i]
        options=Pro.SA_SAMPLE[saName]
        if options[0]=='any':
            index=range(len(self.SAMPLE_METHOD))
        else:
            index=[]
            for option in options:
                index.append(self.SAMPLE_METHOD.index(option))
        self.smBtnGroup.setEnables(index)
        
class SimulationWidget(QWidget):
    
    nextBtn=pyqtSignal(bool)
    resetBtn=pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.currentValue=0
                
        vBoxLayout=QVBoxLayout(self); vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.processBar=ProgressBar(self)
        self.processBar.setValue(self.currentValue)
        Pro.processBar=self.processBar
        
        h1=QHBoxLayout()
        
        self.statistics=BodyLabel("NA/NA FEs")
        setFont(self.statistics, MediumSize, Medium)
        
        h1.addStretch(1)
        h1.addWidget(self.statistics); h1.addSpacing(20)
        
        h2=QHBoxLayout(); h2.addSpacing(20)
        h2.addWidget(self.processBar); h2.addSpacing(20)
        v=QVBoxLayout()
        v.addLayout(h2); v.addLayout(h1)
        
        vBoxLayout.addLayout(v)

        ##############################
        formLayout=QFormLayout()
        formLayout.setContentsMargins(20, 0, 0, 0)
        formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        label=BodyLabel("SWAT Execution:")
        label.setMinimumWidth(100)
        setFont(label)
        
        self.swatEdit=ComboBox(self)
        self.swatEdit.setMaximumWidth(400)
        self.swatEdit._showComboMenu=self.dynamicShowExe
        setFont(self.swatEdit, MediumSize, Normal)
        self.swatEdit.currentIndexChanged.connect(self.swatChanged)
        
        formLayout.addRow(label, self.swatEdit)
        
        ##################################

        label=BodyLabel("SWAT Parallel:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        
        self.parallelEdit=SpinBox(self); self.parallelEdit.setValue(1)
        setFont(self.parallelEdit, MediumSize, Normal)
        self.parallelEdit.setMaximumWidth(400)
        formLayout.addRow(label, self.parallelEdit)
        
        label=BodyLabel("Problem Name:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.problemEdit=LineEdit(self)
        setFont(self.problemEdit, MediumSize, Normal)
        self.problemEdit.setMaximumWidth(400)
        
        formLayout.addRow(label, self.problemEdit)
        
        vBoxLayout.addLayout(formLayout)
        
        #################Verbose################
        
        h=QHBoxLayout()
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        font = QFont("Consolas", pointSize=12)
        font.setStyleHint(QFont.Monospace) 
        self.verbose.setFont(font)
        self.verbose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        h.addSpacing(10); h.addWidget(self.verbose); h.addSpacing(10)
        vBoxLayout.addLayout(h)
        
        ######################################
        btnWidget=QWidget(self); btnWidget.setObjectName("btnWidget")
        btnWidget.setStyleSheet("#btnWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);border-bottom: 1px solid rgba(0, 0, 0, 0.15);}")
        h=QHBoxLayout(btnWidget); h.setContentsMargins(0, 5, 0, 5)
        self.initializeBtn=PrimaryPushButton("Initialize"); self.initializeBtn.clicked.connect(self.initialize)
        setFont(self.initializeBtn)
        self.samplingBtn=PrimaryPushButton("Sampling"); self.samplingBtn.clicked.connect(self.sampling)
        setFont(self.samplingBtn)
        self.simBtn=PrimaryPushButton("Simulate"); self.simBtn.clicked.connect(self.simulation)
        setFont(self.simBtn)
        self.cancelBtn=PrimaryPushButton("Break"); self.cancelBtn.clicked.connect(self.cancel)
        self.cancelBtn.setEnabled(False)
        setFont(self.cancelBtn)
        
        self.samplingBtn.setEnabled(False); self.simBtn.setEnabled(False)
        h.addStretch(1);h.addWidget(self.initializeBtn);h.addSpacing(30);h.addWidget(self.samplingBtn);h.addSpacing(30);h.addWidget(self.simBtn); h.addSpacing(30); h.addWidget(self.cancelBtn); h.addStretch(1)
        vBoxLayout.addWidget(btnWidget)
    
    def dynamicShowExe(self):
        
        self.swatEdit.clear()
        self.swatEdit.addItems(Pro.findSwatExe())
        self.swatEdit.setCurrentIndex(0)
        super(ComboBox, self.swatEdit)._showComboMenu()
    
    def reset(self):
        
        self.swatEdit.setEnabled(True)
        self.parallelEdit.setEnabled(True)
        self.problemEdit.setEnabled(True)
        self.initializeBtn.setEnabled(True)
        self.simBtn.setEnabled(False)
        self.samplingBtn.setEnabled(False)
        self.cancelBtn.setEnabled(False)
        self.verbose.clear()
        self.parallelEdit.setValue(1)
        self.statistics.setText("NA/NA FEs")
        self.processBar.setValue(0)
        
    def updateUI(self):
        
        self.swatEdit.addItems(Pro.findSwatExe())
        self.swatEdit.setCurrentIndex(0)
        self.problemEdit.setText(Pro.projectInfos['projectName'])
        
    def swatChanged(self):
        
        Pro.SA_runInfos['swatExe']=self.swatEdit.currentText()
    
    def initialize(self):
        #
        textWidth = self.verbose.viewport().width()
        fontMetrics = QFontMetrics(self.verbose.font())
        averWidth = fontMetrics.averageCharWidth()
        nChars=textWidth // averWidth
        self.verbose.setProperty('totalWidth', nChars)
        Pro.SA_runInfos['verboseWidth']=nChars
        #
        Pro.SA_runInfos['window']=self.parent().parent().parent()
        Pro.window=self.parent().parent().parent()
        # Verbose.total_width=self.verbose.document().idealWidth()
        
        numParallel=int(self.parallelEdit.value())
        
        Pro.SA_runInfos['numParallel']=numParallel
        Pro.SA_runInfos['tempPath']=os.path.join(Pro.projectInfos['projectPath'], 'temp')
        
        self.swatEdit.setEnabled(False)
        self.parallelEdit.setEnabled(False)
        self.initializeBtn.setEnabled(False)
        self.problemEdit.setEnabled(False)
        
        self.verbose.append("Initializing ... Please wait!\n")
        Pro.initSA(self.verbose, self.samplingBtn)
        
    def sampling(self):
        
        Pro.SA_problemInfos['name']=self.problemEdit.text()
        
        success=Pro.sampling()
        
        if success:
            self.verbose.append("Sampling Done. Please start simulation!\n")
            
            self.samplingBtn.setEnabled(False)
            self.simBtn.setEnabled(True)

    def simulation(self):
        
        self.verbose.append("Model Simulating ... Please Waiting!\n")
        self.simBtn.setEnabled(False)
        self.resetBtn.emit(False)
        self.cancelBtn.setEnabled(True)
        Pro.simulation(self.processBar, self.statistics, self.finish, self.unfinish)

    def unfinish(self):
        
        self.cancelBtn.setEnabled(False)
        self.initializeBtn.setEnabled(True)
        self.resetBtn.emit(True)
        self.processBar.setValue(0)
        self.statistics.setText("NA/NA FEs")
        self.verbose.append("Simulation has been canceled by user.\n")
        
        self.swatEdit.setEnabled(True)
        self.parallelEdit.setEnabled(True)
        self.problemEdit.setEnabled(True)
    
    def cancel(self):

        Pro.cancelSA()
        self.verbose.append("Canceling... Please wait!\n")
        
    def finish(self):
        self.cancelBtn.setEnabled(False)
        self.verbose.append("Simulation Done. Please click the next to execute analysis!\n")
        self.nextBtn.emit(True)
        self.resetBtn.emit(True)

class AnalysisWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        vBoxLayout=QVBoxLayout(self)
        
        self.textWidget=TextEdit(self); self.textWidget.setReadOnly(True)
        font = QFont("Consolas", pointSize=12)  
        font.setStyleHint(QFont.Monospace) 
        self.textWidget.setFont(font)
        vBoxLayout.addWidget(self.textWidget)
        
        self.btnWidget=QWidget(self); self.btnWidget.setObjectName("btnWidget")
        self.btnWidget.setStyleSheet("#btnWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);border-bottom: 1px solid rgba(0, 0, 0, 0.15);}")
        
        h=QHBoxLayout(self.btnWidget); h.setContentsMargins(0, 5, 0, 5)
        self.executeBtn=PrimaryPushButton("Execute Analysis")
        self.executeBtn.clicked.connect(self.execute)
        setFont(self.executeBtn)

        h.addStretch(1); h.addWidget(self.executeBtn); h.addSpacing(20);  h.addStretch(1)
        vBoxLayout.addWidget(self.btnWidget)
        
    def updateUI(self):
        
        SAInfos=Pro.SA_infos
        
        saName=SAInfos['saName']
        smName=SAInfos['smName']
        self.textWidget.append(f"Sensibility Analysis you selected: {saName}\n")
        self.textWidget.append(f"The used data set is sampled by {smName}\n")
        
        result=Pro.SA_result
        
        self.textWidget.append(f"The size of the data set is {result['Y'].size}\n")
        
        self.textWidget.append(f"Please click the execute button to do sensibility analysis.\n")
        
    def execute(self):
        
        self.textWidget.append("Sensibility Analysis is running ... \n")
        
        Pro.sensibility_analysis(self.textWidget)
        
        
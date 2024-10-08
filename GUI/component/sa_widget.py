from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, 
                             QStackedWidget, QWidget, QButtonGroup, QFileDialog, QTextEdit)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QFont
from qfluentwidgets import (BodyLabel, ComboBox, 
                            RadioButton, SpinBox, DoubleSpinBox, TextEdit,
                            CheckBox, PrimaryPushButton, LineEdit, ProgressBar)
import os
import copy
import GUI.qss
import GUI.data
from importlib.resources import path
from .process_widget import ProcessWidget
from .button_group import ButtonGroup
from .hyper_widget import hyperWidget
from ..project import Project as Pro
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
        
        self.nextButton.setMinimumWidth(300)
        h=QHBoxLayout();h.addStretch(1);h.addWidget(self.nextButton);h.addStretch(1)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
         
        #connect
        self.nextButton.clicked.connect(self.nextPage)
        
        #qss
        with path(GUI.qss, "sa_widget.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())

    def updateUI(self):
        self.setupWidget.updateUI()
        
    def nextPage(self):
        
        if self.INDEX==0:
            widget=self.setupWidget
            hyper=self.setupWidget.hyperStack.widget(1).returnHyper()

            sa=widget.SA_METHOD[widget.saBtnGroup.currentIndex]
            sm=widget.SAMPLE_METHOD[widget.smBtnGroup.currentIndex]
            Pro.SAInfos={'saName': sa, 'saClass': Pro.SA_METHOD[sa],'saHyper': hyper[Pro.SA_METHOD[sa]],
                         'smName': sm,'smClass' : Pro.SAMPLE_METHOD[sm],'smHyper': hyper[Pro.SAMPLE_METHOD[sm]]}
            
        self.INDEX+=1
        self.contentWidget.setCurrentIndex(self.INDEX)
        self.contentWidget.currentWidget().updateUI()
        self.processWidget.on_button_clicked(self.INDEX)
        # self.nextButton.setEnabled(False)

class SetupWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        #######################Parameter Path############################
        h0=QHBoxLayout()
        label0=BodyLabel("Parameter File:")
        self.paraEdit=ComboBox(self); self.paraEdit.setMinimumWidth(300)
        self.paraEdit.currentIndexChanged.connect(self.loadParaFile)
        
        label1=BodyLabel("Number of Parameters:")
        self.numPara=LineEdit(self); self.numPara.setEnabled(False)
        
        h0.addSpacing(50);h0.addWidget(label0); h0.addWidget(self.paraEdit);h0.addSpacing(50) 
        h0.addWidget(label1); h0.addWidget(self.numPara)
        h0.addStretch(1)
        vBoxLayout.addLayout(h0)
        ######################Objective Path###########################
        h0=QHBoxLayout()
        label0=BodyLabel("Objective File:")
        self.objLine=ComboBox(self); self.objLine.setMinimumWidth(300)
        
        label1=BodyLabel("Selection of Objectives:"); self.objEdit=ComboBox(self)
        self.objEdit.setEnabled(True); self.objEdit.setMinimumWidth(50)
        self.objLine.currentIndexChanged.connect(self.loadObjFile)
        self.objEdit.currentIndexChanged.connect(self.ensureObj)
        
        h0.addSpacing(50);h0.addWidget(label0); h0.addWidget(self.objLine);h0.addSpacing(50)
        h0.addWidget(label1); h0.addWidget(self.objEdit)
        h0.addStretch(1)
        vBoxLayout.addLayout(h0)

        #######################SA Combobox#############################
        h1=QHBoxLayout()
        label1=BodyLabel("Sensibility Analysis:"); line1=ButtonGroup(Pro.SA_METHOD.keys(), True, self)
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(line1)
        self.saBtnGroup=line1; self.SA_METHOD=list(Pro.SA_METHOD.keys())
        vBoxLayout.addLayout(h1)
        
        ########################Sampling Method#################################
        h2=QHBoxLayout()
        label2=BodyLabel("Sampling Method:"); line2=ButtonGroup(Pro.SAMPLE_METHOD.keys(), False, self)
        h2.addSpacing(50); h2.addWidget(label2); h2.addWidget(line2)
        self.smBtnGroup=line2; self.SAMPLE_METHOD=list(Pro.SAMPLE_METHOD.keys())
        vBoxLayout.addLayout(h2)
        
        self.hyperStack=QStackedWidget(self)
        vBoxLayout.addWidget(self.hyperStack)
        self.hyperStack.addWidget(QWidget())
        self.hyperStack.setCurrentIndex(0)
        
        vBoxLayout.addStretch(1)
        
        conclusionWidget=QWidget(self)
        conclusionWidget.setObjectName("conclusionWidget")
        h=QHBoxLayout(conclusionWidget)
        labelC=BodyLabel('The total number of sampling points is:')
        lineC=LineEdit(self); lineC.setEnabled(False);lineC.setToolTip("Please select the Sensitivity Analysis and Sampling Method first.")
        self.numLine=lineC; self.numLine.setMinimumWidth(150)
        h.addSpacing(50); h.addWidget(labelC); h.addWidget(lineC);h.addStretch(1)
        h.setContentsMargins(0, 10, 0, 10)
        vBoxLayout.addWidget(conclusionWidget)
        
        self.saBtnGroup.group.idClicked.connect(self.enableSampling)
        self.saBtnGroup.group.idClicked.connect(self.updateHyper)
        self.smBtnGroup.group.idClicked.connect(self.updateHyper)
        self.saBtnGroup.group.buttonClicked.connect(self.updateNextButton)
        
        vBoxLayout.setContentsMargins(0,0,0,0)
    
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
        
    def updateNumSampling(self):
        
        widget=self.sender()
        related=widget.returnRelated()
        
        add={'nInput': int(self.numPara.text())}
        related.update(add)
        
        I_SM=self.smBtnGroup.currentIndex
        formula=Pro.FORMULA[self.SAMPLE_METHOD[I_SM]]
        
        num=eval(formula, related)
        
        self.numLine.setText(str(num))
        
    def updateUI(self):
        
        self.paraEdit.clear()
        self.objLine.clear()
        self.paraEdit.addItems(Pro.findParaFile())
        self.objLine.addItems(Pro.findProFile())
        self.paraEdit.setCurrentIndex(0)
        self.objLine.setCurrentIndex(0)
        self.loadParaFile()
        self.loadObjFile()
    
    def loadParaFile(self):
        
        path=self.paraEdit.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], path)
        infos=Pro.importParaFromFile(path)
        self.numPara.setText(str(len(infos)))
        
        Pro.paraInfos=infos
        Pro.projectInfos['paraPath']=path
     
    def loadObjFile(self):
        
        path=self.objLine.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], path)
        infos=Pro.importProFromFile(path)
        self.objInfos=infos
        
        self.objEdit.clear()
        self.objEdit.addItems([f"obj {i : d}" for i in list(infos.keys())])

        
        Pro.projectInfos['objPath']=path
    
    def ensureObj(self):
        
        objID=int(self.objEdit.text().split()[1])
        Pro.objInfos={objID: self.objInfos[objID]}
        
    def openParaDialog(self):
        
        path, success=QFileDialog.getOpenFileName(self, "Open File", "", "Parameter Files (*.par)")
        if success:
            self.paraEdit.setText(path)
            self.paraBtn.setEnabled(True)
     
    def openProDialog(self):
        
        path, success=QFileDialog.getOpenFileName(self, "Open File", "", "Objective Files (*.obj)")
        
        if success:
            self.objLine.setText(path)
            self.proBtn.setEnabled(True)        

    def updateNextButton(self):
        
        selectedSA=self.saBtnGroup.group.checkedButton()
        selectedSampling=self.smBtnGroup.group.checkedButton()
        if selectedSA and selectedSampling:
            self.parent().parent().nextButton.setEnabled(True)
        else:
            self.parent().parent().nextButton.setEnabled(False)
            
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.currentValue=0
                
        vBoxLayout=QVBoxLayout(self); vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.processBar=ProgressBar(self)
        self.processBar.setValue(self.currentValue)
        Pro.processBar=self.processBar
        
        h=QHBoxLayout(); h.addSpacing(20)
        h.addWidget(self.processBar); h.addSpacing(20)
        
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)

        ##############################
        h=QHBoxLayout(); h.addSpacing(20)
        self.label=BodyLabel("SWAT Execution:")
        self.swatEdit=ComboBox(self); self.swatEdit.setMinimumWidth(400)
        
        self.swatEdit.currentIndexChanged.connect(self.swatChanged)
        h.addWidget(self.label); h.addWidget(self.swatEdit); h.addStretch(1)
        vBoxLayout.addLayout(h)
        ##################################
        h=QHBoxLayout(); h.addSpacing(20)
        self.label2=BodyLabel("SWAT Parallel:")
        self.parallelEdit=SpinBox(self); self.parallelEdit.setValue(5)
        h.addWidget(self.label2); h.addWidget(self.parallelEdit); h.addStretch(1)
        vBoxLayout.addLayout(h)
        #################Verbose################
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        font = QFont("Consolas")  # 或者使用 "Courier New"
        font.setStyleHint(QFont.Monospace)  # 确保字体为等宽字体
        self.verbose.setFont(font)
        self.verbose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vBoxLayout.addWidget(self.verbose)
        ######################################
        btnWidget=QWidget(self); btnWidget.setObjectName("btnWidget")
        btnWidget.setStyleSheet("#btnWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);border-bottom: 1px solid rgba(0, 0, 0, 0.15);}")
        h=QHBoxLayout(btnWidget); h.setContentsMargins(0, 5, 0, 5)
        self.initializeBtn=PrimaryPushButton("Initialize"); self.initializeBtn.clicked.connect(self.initialize)
        self.samplingBtn=PrimaryPushButton("Sampling"); self.samplingBtn.clicked.connect(self.sampling)
        self.simBtn=PrimaryPushButton("Simulate"); self.simBtn.clicked.connect(self.simulation)
        self.samplingBtn.setEnabled(False); self.simBtn.setEnabled(False)
        h.addStretch(1);h.addWidget(self.initializeBtn);h.addSpacing(30);h.addWidget(self.samplingBtn);h.addSpacing(30);h.addWidget(self.simBtn); h.addStretch(1)
        
        vBoxLayout.addWidget(btnWidget)
        
        
    def updateUI(self):
        self.swatEdit.addItems(Pro.findSwatExe())
        
    def swatChanged(self):
        Pro.projectInfos['swatExe']=self.swatEdit.currentText()
    
    def initialize(self):
        
        numParallel=int(self.parallelEdit.value())
        Pro.projectInfos['numParallel']=numParallel
        
        self.swatEdit.setEnabled(False)
        self.parallelEdit.setEnabled(False)
        
        self.initializeBtn.setEnabled(False)
        
        Pro.initProject(self.verbose, self.samplingBtn)
        
    def sampling(self):
        
        Pro.sampling()
        self.verbose.append("Sampling Done. Please start simulation!\n")
        
        self.samplingBtn.setEnabled(False)
        self.simBtn.setEnabled(True)

    def simulation(self):
        
        self.verbose.append("Model Simulating ... Please Waiting!\n")
        self.simBtn.setEnabled(False)
        Pro.simulation(self.processBar, self.finish)
    
    def finish(self):
        
        self.verbose.append("Simulation Done. Please click the next to execute analysis!\n")
        self.parent().parent().nextButton.setEnabled(True)

class AnalysisWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        vBoxLayout=QVBoxLayout(self)
        
        self.textWidget=TextEdit(self); self.textWidget.setReadOnly(True)
        font = QFont("Consolas")  # 或者使用 "Courier New"
        font.setStyleHint(QFont.Monospace)  # 确保字体为等宽字体
        self.textWidget.setFont(font)
        vBoxLayout.addWidget(self.textWidget)
        
        self.btnWidget=QWidget(self); self.btnWidget.setObjectName("btnWidget")
        self.btnWidget.setStyleSheet("#btnWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);border-bottom: 1px solid rgba(0, 0, 0, 0.15);}")
        h=QHBoxLayout(self.btnWidget); h.setContentsMargins(0, 5, 0, 5)
        self.executeBtn=PrimaryPushButton("Execute Analysis")
        self.executeBtn.clicked.connect(self.execute)
        h.addStretch(1); h.addWidget(self.executeBtn); h.addStretch(1)
        vBoxLayout.addWidget(self.btnWidget)
        
    def updateUI(self):
        
        SAInfos=Pro.SAInfos
        
        saName=SAInfos['saName']
        smName=SAInfos['smName']
        self.textWidget.append(f"Sensibility Analysis you selected: {saName}\n")
        self.textWidget.append(f"The used data set is sampled by {smName}\n")
        
        result=Pro.SAResult
        
        self.textWidget.append(f"The size of the data set is {result['Y'].size}\n")
        
        self.textWidget.append(f"Please click the execute button to do sensibility analysis.\n")
        
    def execute(self):
        
        self.textWidget.append("Sensibility Analysis is running ... \n")
        
        Pro.sensibility_analysis(self.textWidget)
        
        
from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, 
                             QStackedWidget, QWidget, QButtonGroup, QFileDialog)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from qfluentwidgets import (BodyLabel, ComboBox, 
                            RadioButton, SpinBox, DoubleSpinBox, TextEdit,
                            CheckBox, PrimaryPushButton, LineEdit, ProgressBar)
import math
import GUI.qss
import GUI.data
from importlib.resources import path
from .process_widget import ProcessWidget
from ..project import Project as Pro
class SAWidget(QFrame):
    INDEX=0
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        
        ##########################Process Widget########################
        proWidget=ProcessWidget(self)
        proWidget.addStep(0, "Setup")
        proWidget.addStep(1, "Simulation")
        proWidget.addStep(2, "Analysis")
        proWidget.addStep(3, "Report")
        self.proWidget=proWidget
        vBoxLayout.addWidget(proWidget)
        #################################################################
        
        contentWidget=QStackedWidget(self)
        contentWidget.setObjectName("contentWidget")
        vBoxLayout.addWidget(contentWidget)
        
        #################################################################
        
        self.setupWidget=SetupWidget(self)
        contentWidget.addWidget(self.setupWidget)
        self.simulationWidget=SimulationWidget(self)
        contentWidget.addWidget(self.simulationWidget)
        contentWidget.setCurrentIndex(0)
        self.contentWidget=contentWidget
        ##################################################################
        # vBoxLayout.addStretch(1)
        self.nextButton=PrimaryPushButton("Next", self)
        self.nextButton.setEnabled(False) #TODO
        self.nextButton.clicked.connect(self.nextPage)
        self.nextButton.setMinimumWidth(300)
        h=QHBoxLayout();h.addStretch(1);h.addWidget(self.nextButton);h.addStretch(1)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(20)
        
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        with path(GUI.qss, "sa_widget.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())

    def updateUI(self):
        self.setupWidget.updateUI()
        
    def nextPage(self):
        self.INDEX+=1
        self.contentWidget.setCurrentIndex(self.INDEX)
        self.contentWidget.currentWidget().updateUI()
        self.proWidget.on_button_clicked(self.INDEX)
        self.nextButton.setEnabled(False)
        
    
class SetupWidget(QWidget):
    
    SAMPLE={ 0:[5], 1: [], 2: [3], 3: [], 4: [4], 5: []}
    scenarioInfos={}
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        #######################Parameter Path############################
        h0=QHBoxLayout()
        label0=BodyLabel("Parameter File:")
        self.paraLine=ComboBox(self); self.paraLine.setMinimumWidth(300)
        self.paraLine.addItems(Pro.checkParaFile()); 
        self.paraLine.currentIndexChanged.connect(self.loadParaFile)
        self.paraLine.currentIndexChanged.connect(self.updateSamplingStack)
        
        label1=BodyLabel("Number of Parameters:")
        self.numPara=LineEdit(self); self.numPara.setEnabled(False)
        
        h0.addSpacing(50);h0.addWidget(label0); h0.addWidget(self.paraLine);h0.addSpacing(50) 
        h0.addWidget(label1); h0.addWidget(self.numPara)
        h0.addStretch(1)
        vBoxLayout.addLayout(h0)
        ######################Objective Path###########################
        h0=QHBoxLayout()
        label0=BodyLabel("Objective File:")
        self.objLine=ComboBox(self); self.objLine.setMinimumWidth(300)
        self.objLine.addItems(Pro.checkProFile())
        
        label1=BodyLabel("Selection of Objectives:"); self.objEdit=ComboBox(self)
        self.objEdit.setEnabled(True); self.objEdit.setMinimumWidth(50)
        self.objLine.currentIndexChanged.connect(self.loadProFile)
        
        h0.addSpacing(50);h0.addWidget(label0); h0.addWidget(self.objLine);h0.addSpacing(50)
        h0.addWidget(label1); h0.addWidget(self.objEdit)
        h0.addStretch(1)
        vBoxLayout.addLayout(h0)

        #######################SA Combobox#############################
        h1=QHBoxLayout()
        label1=BodyLabel("Sensibility Analysis:"); line1=ButtonGroup(['Sobol', 'Delta Test', 'FAST', 'RBD-FAST', 'Morris', 'RSA'], True, self)
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(line1);h1.addStretch(10)
        self.btnGroup1=line1
        vBoxLayout.addLayout(h1); 
        ########################Sampling Method#################################
        h2=QHBoxLayout()
        label2=BodyLabel("Sampling Method:"); line2=ButtonGroup(['Full Factorial Design', 'Latin Hyper Sampling', 'Random', 'Fast Sequence', 'Morris Sequence', 'Sobol Sequence'], False, self)
        h2.addSpacing(50); h2.addWidget(label2); h2.addWidget(line2);h2.addStretch(10)
        self.btnGroup2=line2
        vBoxLayout.addLayout(h2)
        
        #########################################################
        hyperStack=QStackedWidget(self)
        vBoxLayout.addWidget(hyperStack)
        hyperStack.setObjectName("hyperStack")
        hyperStack.addWidget(hyperWidget({'Z-score':{'type':'bool', 'default': 0}, 'Cal_Second_Order':{'type':'bool', 'default': 0}}))
        hyperStack.addWidget(hyperWidget({'Z-score':{'type':'bool', 'default': 0}, 'nNeighbors':{'type':'int', 'default': 2}}))
        hyperStack.addWidget(hyperWidget({'Z-score':{'type':'bool', 'default': 0}}))
        hyperStack.addWidget(hyperWidget({'Z-score':{'type':'bool', 'default': 0}, 'M':{'type':'int', 'default': 4}}))
        hyperStack.addWidget(hyperWidget({'Z-score':{'type':'bool', 'default': 0}, 'numLevels':{'type':'int', 'default': 4}}))
        hyperStack.addWidget(hyperWidget({'Z-score':{'type':'bool', 'default': 0}, 'nRegion':{'type':'int', 'default': 20}}))
        hyperStack.addWidget(QWidget())
        hyperStack.setCurrentIndex(6)
        self.hyperStack=hyperStack
        self.btnGroup1.group.idClicked.connect(self.displayPage1)
        self.btnGroup1.group.idClicked.connect(self.enableSampling)
        ############################################################
        
        samplingStack=QStackedWidget(self)
        vBoxLayout.addWidget(samplingStack)
        samplingStack.setObjectName("samplingStack")
        samplingStack.addWidget(FFDWidget(self))
        samplingStack.addWidget(LHSWidget(self))
        samplingStack.addWidget(RandomWidget(self)) 
        samplingStack.addWidget(FastSamplingWidget(self))
        samplingStack.addWidget(MorrisWidget(self))
        samplingStack.addWidget(SobolWidget(self))
        samplingStack.addWidget(QWidget(self))
        self.samplingStack=samplingStack; self.samplingStack.setCurrentIndex(6)
        self.btnGroup2.group.idClicked.connect(self.displayPage2)
        self.btnGroup2.group.buttonClicked.connect(self.updateSamplingStack)
        
        self.btnGroup1.group.buttonClicked.connect(self.updateNextButton)
        self.btnGroup2.group.buttonClicked.connect(self.updateNextButton)
        
        vBoxLayout.addStretch(1)
        vBoxLayout.setContentsMargins(0,0,0,0)

    def updateUI(self):
        
        self.loadParaFile()
        self.loadProFile()
    
    def updateCombobox(self):
        self.objLine.clear()
        self.objLine.addItems(Pro.checkProFile())
        self.paraLine.clear()
        self.paraLine.addItems(Pro.checkParaFile)
        
    def loadParaFile(self):
        if Pro.projectPath!="":
            path=self.paraLine.currentText()
            infos=Pro.importParaFromFile(path)
            self.numPara.setText(str(len(infos)))
            Pro.paraInfos=infos
            
    def loadProFile(self):
        if Pro.projectPath!="":
            path=self.objLine.currentText()
            infos=Pro.importProFromFile(path)
            self.objEdit.clear()
            self.objEdit.addItems([str(i) for i in list(infos.keys())])

    def openParaDialog(self):
        path, success=QFileDialog.getOpenFileName(self, "Open File", "", "Parameter Files (*.par)")
        if success:
            self.paraLine.setText(path)
            self.paraBtn.setEnabled(True)
            
    def openProDialog(self):
        path, success=QFileDialog.getOpenFileName(self, "Open File", "", "Objective Files (*.obj)")
        
        if success:
            self.objLine.setText(path)
            self.proBtn.setEnabled(True)
    
    def displayPage1(self, index):
        self.hyperStack.setCurrentIndex(index)

    def updateNextButton(self):
        selectedSA=self.btnGroup1.group.checkedButton()
        selectedSampling=self.btnGroup2.group.checkedButton()
        if selectedSA and selectedSampling:
            self.parent().parent().nextButton.setEnabled(True)
        else:
            self.parent().parent().nextButton.setEnabled(False)
            
    def updateSamplingStack(self):
        if self.samplingStack.currentIndex()<6:
            self.samplingStack.currentWidget().updateUI()
    
    def displayPage2(self, index):
        self.samplingStack.setCurrentIndex(index)
            
    
    def enableSampling(self, index):
        self.btnGroup2.setEnables(self.SAMPLE[index])
    
class FFDWidget(QWidget):
    HYPER={}
    
    def __init__(self, parent=None):
        super().__init__(parent)
            
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        h1=QHBoxLayout()
        label1=BodyLabel("Number of Factors(*):"); self.line1=SpinBox(self); self.line1.setValue(5)
        self.line1.setProperty('Name', 'numFactors')
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(self.line1); h1.addStretch(1)
        ##################################
        
        conclusionWidget=QFrame(self); conclusionWidget.setObjectName("conclusionWidget")
        hC=QHBoxLayout(conclusionWidget); hC.setContentsMargins(0, 20, 0, 0)
        lC=BodyLabel("Number of Sampling Points: "); self.lC=LineEdit(self); self.lC.setEnabled(False)
        hC.addSpacing(50); hC.addWidget(lC); hC.addWidget(self.lC); hC.addStretch(1)
        
        conclusionWidget.setStyleSheet("#conclusionWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);}")
        
        ######
        vBoxLayout.addLayout(h1)
        vBoxLayout.addWidget(conclusionWidget)
        vBoxLayout.addStretch(1)

        #########connect#########
        self.line1.valueChanged.connect(self.recordNumFactors)
        self.recordNumFactors()
        
    def recordNumFactors(self):
        
        self.HYPER['numFactors']=self.line1.value()
        value=int(math.pow(self.line1.value(),len(Pro.paraInfos)))
        self.lC.setText(f"{value:d}")
    
    def updateUI(self):
        self.recordNumFactors()
class LHSWidget(QWidget):
    
    HYPER={}
        
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("N(*):"); self.line1=SpinBox(self); self.line1.setValue(5)
        self.line1.setProperty('Name', 'numSampling')
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(self.line1); h1.addStretch(1)

        conclusionWidget=QFrame(self); conclusionWidget.setObjectName("conclusionWidget")
        hC=QHBoxLayout(conclusionWidget); hC.setContentsMargins(0, 20, 0, 0)
        lC=BodyLabel("Based your setting, the total number of sampling point is: "); self.lC=LineEdit(self); self.lC.setEnabled(False)
        hC.addSpacing(50); hC.addWidget(lC); hC.addWidget(self.lC); hC.addStretch(1)
        
        conclusionWidget.setStyleSheet("#conclusionWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);}")
        
        
        vBoxLayout.addLayout(h1)
        vBoxLayout.addWidget(conclusionWidget)
        vBoxLayout.addStretch(1)

        #########connect#########
        self.line1.valueChanged.connect(self.recordNumFactors)
        self.recordNumFactors()
        
    def recordNumFactors(self):
        
        self.HYPER['numSampling']=self.line1.value()
        self.lC.setText(str(self.line1.value()))

    def updateUI(self):
        
        self.recordNumFactors()
    
class RandomWidget(QWidget):
    
    HYPER={}
        
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("N(*):"); self.line1=SpinBox(self); self.line1.setValue(5)
        self.line1.setProperty('Name', 'numSampling')
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(self.line1); h1.addStretch(1)

        conclusionWidget=QFrame(self); conclusionWidget.setObjectName("conclusionWidget")
        hC=QHBoxLayout(conclusionWidget); hC.setContentsMargins(0, 20, 0, 0)
        lC=BodyLabel("Number of Sampling Points: "); self.lC=LineEdit(self); self.lC.setEnabled(False)
        hC.addSpacing(50); hC.addWidget(lC); hC.addWidget(self.lC); hC.addStretch(1)
        
        conclusionWidget.setStyleSheet("#conclusionWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);}")
        
        
        vBoxLayout.addLayout(h1)
        vBoxLayout.addWidget(conclusionWidget)
        vBoxLayout.addStretch(1)

        #########connect#########
        self.line1.valueChanged.connect(self.recordNumFactors)
        self.recordNumFactors()
        
    def recordNumFactors(self):
        
        self.HYPER['numSampling']=self.line1.value()
        self.lC.setText(str(self.line1.value()))

    def updateUI(self):
        
        self.recordNumFactors()
    
class  FastSamplingWidget(QWidget):
    
    HYPER={}
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("M:"); self.line1=SpinBox(self); self.line1.setValue(5)
        self.line1.setProperty('Name', 'M')
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(self.line1); h1.addStretch(1)

        h2=QHBoxLayout()
        label2=BodyLabel("N(*):"); self.line2=SpinBox(self); self.line2.setValue(50)
        self.line2.setProperty('Name', 'N')
        h2.addSpacing(50); h2.addWidget(label2); h2.addWidget(self.line2); h2.addStretch(1)
        
        conclusionWidget=QFrame(self); conclusionWidget.setObjectName("conclusionWidget")
        hC=QHBoxLayout(conclusionWidget); hC.setContentsMargins(0, 20, 0, 0)
        lC=BodyLabel("Number of Sampling Points: "); self.lC=LineEdit(self); self.lC.setEnabled(False)
        hC.addSpacing(50); hC.addWidget(lC); hC.addWidget(self.lC); hC.addStretch(1)
        
        conclusionWidget.setStyleSheet("#conclusionWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);}")
        
        
        vBoxLayout.addLayout(h1)
        vBoxLayout.addLayout(h2)
        vBoxLayout.addWidget(conclusionWidget)
        vBoxLayout.addStretch(1)

        #########connect#########
        self.line1.valueChanged.connect(self.recordNumFactors)
        self.line2.valueChanged.connect(self.recordNumFactors)
        self.recordNumFactors()
        
    def recordNumFactors(self):
        
        self.HYPER['N']=self.line2.value()
        
        self.lC.setText(str(self.HYPER['N']*len(Pro.paraInfos)))

    def updateUI(self):
        
        self.recordNumFactors()
    
    
class MorrisWidget(QWidget):
        
    HYPER={}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("N(*):"); self.line1=SpinBox(self); self.line1.setValue(5)
        self.line1.setProperty('Name', 'N')
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(self.line1); h1.addStretch(1)

        conclusionWidget=QFrame(self); conclusionWidget.setObjectName("conclusionWidget")
        hC=QHBoxLayout(conclusionWidget); hC.setContentsMargins(0, 20, 0, 0)
        lC=BodyLabel("Number of Sampling Points: "); self.lC=LineEdit(self); self.lC.setEnabled(False)
        hC.addSpacing(50); hC.addWidget(lC); hC.addWidget(self.lC); hC.addStretch(1)
        
        conclusionWidget.setStyleSheet("#conclusionWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);}")
        
        
        vBoxLayout.addLayout(h1)
        vBoxLayout.addWidget(conclusionWidget)
        vBoxLayout.addStretch(1)

        #########connect#########
        self.line1.valueChanged.connect(self.recordNumFactors)
        self.recordNumFactors()
        
    def recordNumFactors(self):
        
        self.HYPER['N']=self.line1.value()
        self.lC.setText(str(self.HYPER['N']*(len(Pro.paraInfos)+1))) #TODO

    def updateUI(self):
        
        self.recordNumFactors()
class SobolWidget(QWidget):
    
    HYPER={}
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("N(*):"); self.line1=SpinBox(self); self.line1.setValue(5)
        self.line1.setProperty('Name', 'N')
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(self.line1); h1.addStretch(1)
        
        h2=QHBoxLayout()
        label2=BodyLabel("Skip Values"); self.line2=SpinBox(self); self.line2.setValue(5)
        self.line2.setProperty('Name', 'SkipValues')
        h2.addSpacing(50); h2.addWidget(label2); h2.addWidget(self.line2); h2.addStretch(1)

        conclusionWidget=QFrame(self); conclusionWidget.setObjectName("conclusionWidget")
        hC=QHBoxLayout(conclusionWidget); hC.setContentsMargins(0, 20, 0, 0)
        lC=BodyLabel("Number of Sampling Points: "); self.lC=LineEdit(self); self.lC.setEnabled(False)
        hC.addSpacing(50); hC.addWidget(lC); hC.addWidget(self.lC); hC.addStretch(1)
        
        conclusionWidget.setStyleSheet("#conclusionWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);}")
        
        
        vBoxLayout.addLayout(h1)
        vBoxLayout.addLayout(h2)
        vBoxLayout.addWidget(conclusionWidget)
        vBoxLayout.addStretch(1)

        #########connect#########
        self.line1.valueChanged.connect(self.recordNumFactors)
        self.recordNumFactors()
        
    def recordNumFactors(self):
        
        self.HYPER['N']=self.line1.value()
        self.lC.setText(str(self.HYPER['N']))

    def updateUI(self):
        
        self.recordNumFactors()
    
    
class ButtonGroup(QWidget):
    def __init__(self, contents, bool, parent=None):
        super().__init__(parent)
        self.btns=[]
        self.group=QButtonGroup(self)
        layout=QHBoxLayout(self)
        layout.setSpacing(25)
        
        for i, content in enumerate(contents):
            btn=RadioButton(content, self)
            self.btns.append(btn)
            self.group.addButton(btn, i)
            layout.addWidget(btn)
            btn.setEnabled(bool)
            
    def setEnables(self, indexes):
        
        for btn in self.btns:
                btn.setEnabled(False)
                btn.setChecked(False)
                
        for index in indexes:
            self.btns[index].setEnabled(True)
        
        if len(indexes)==0:
            for btn in self.btns:
                btn.setEnabled(True)
            
            self.btns[0].click()
        else:
            self.btns[indexes[0]].click()


class hyperWidget(QWidget):
    def __init__(self, dicts, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.addSpacing(20)
        vBoxLayout.setSpacing(20)
        for name, contents in dicts.items():
            h=QHBoxLayout()
            label=BodyLabel(name+":")
            
            type=contents['type']
            value=contents['default']
            if type=="int":
                line=SpinBox()
                line.setMaximum(5000)
                line.setValue(value)
            elif type=="float":
                line=DoubleSpinBox()
                line.setValue(value)
            elif type=="bool":
                line=CheckBox()
                line.setChecked(value)
            
            h.addSpacing(50); h.addWidget(label); h.addWidget(line);h.addStretch(10)
            vBoxLayout.addLayout(h)
        vBoxLayout.setContentsMargins(0,0,0,0)
        vBoxLayout.addStretch(1)
                
class PathLine(LineEdit):
    
    focusReceived = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isSelected = False
        
    def focusInEvent(self, e):
        
        if self.isSelected is False:
            self.isSelected=True
            self.focusReceived.emit()
            self.isSelected=False
            self.clearFocus()

       
       
class SimulationWidget(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.currentValue=40
        
        self.setFixedHeight(300)
                
        vBoxLayout=QVBoxLayout(self)
        self.processBar=ProgressBar(self)
        self.processBar.setValue(self.currentValue)
        
        vBoxLayout.addWidget(self.processBar)
        vBoxLayout.addSpacing(30)

        ##############################
        h=QHBoxLayout()
        self.label=BodyLabel("SWAT Execution:")
        self.swatEdit=ComboBox(self); self.swatEdit.setMinimumWidth(400)
        
        self.swatEdit.currentIndexChanged.connect(self.swatChanged)
        h.addWidget(self.label); h.addWidget(self.swatEdit); h.addStretch(1)
        vBoxLayout.addLayout(h)
        ##################################
        h=QHBoxLayout()
        self.label2=BodyLabel("SWAT Parallel:")
        self.parallelEdit=SpinBox(self); self.parallelEdit.setValue(5)
        h.addWidget(self.label2); h.addWidget(self.parallelEdit); h.addStretch(1)
        vBoxLayout.addLayout(h)
        #################Verbose################
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        self.verbose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        vBoxLayout.addWidget(self.verbose)
        ######################################
        h=QHBoxLayout()
        self.initializeBtn=PrimaryPushButton("Initialize"); self.initializeBtn.clicked.connect(self.initialize)
        self.samplingBtn=PrimaryPushButton("Sampling")
        self.simBtn=PrimaryPushButton("Simulate")
        h.addStretch(1);h.addWidget(self.initializeBtn);h.addWidget(self.samplingBtn); h.addWidget(self.simBtn); h.addStretch(1)
        
        vBoxLayout.addLayout(h)
        
    def updateUI(self):
        self.swatEdit.addItems(Pro.checkSwatExe())
        
    def swatChanged(self):
            
        Pro.swatExe=self.swatEdit.currentText()
    
    def initialize(self):
        
        lines=Pro.createSwatUQ()
        self.verbose.setText("\n".join(lines))
        
        
        
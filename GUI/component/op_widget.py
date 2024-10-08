from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, 
                             QStackedWidget, QWidget, QButtonGroup, QFileDialog, QTextEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from qfluentwidgets import (BodyLabel, ComboBox, CheckBox,
                            RadioButton, SpinBox, DoubleSpinBox, TextEdit,
                            CheckBox, PrimaryPushButton, LineEdit, ProgressBar)
import os
import copy
import GUI.qss
import GUI.data
from importlib.resources import path

from .button_group import ButtonGroup
from .process_widget import ProcessWidget
from .hyper_widget import hyperWidget
from ..project import Project as Pro

class OPWidget(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.INDEX=0
        
        vBoxLayout=QVBoxLayout(self)
        
        processWidget=ProcessWidget(self)
        processWidget.addStep(0, "Setup")
        processWidget.addStep(1, "Optimization")
        processWidget.addStep(2, "Conclusion")
        self.processWidget=processWidget
        vBoxLayout.addWidget(processWidget)
        
        self.contentWidget=QStackedWidget(self)
        self.contentWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.contentWidget.setObjectName("contentWidget")
        vBoxLayout.addWidget(self.contentWidget)
        ##############################################
        
        self.setupWidget=SetupWidget(self)
        self.setupWidget.next.connect(self.updateNext)
        self.opWidget=OptimizationWidget(self)
        
        self.contentWidget.addWidget(self.setupWidget)
        self.contentWidget.addWidget(self.opWidget)
        
        ###############################################
        self.nextButton=PrimaryPushButton("Next", self)
        self.nextButton.setEnabled(False)
        self.nextButton.clicked.connect(self.nextPage)
        self.nextButton.setMinimumWidth(300)
        h=QHBoxLayout();h.addStretch(1);h.addWidget(self.nextButton);h.addStretch(1)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)
        
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        #qss
        with path(GUI.qss, "op_widget.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())

    def nextPage(self):
        
        if self.INDEX==0:
            widget=self.setupWidget
            hyper=self.setupWidget.hyperStack.widget(1).returnHyper()

            if widget.objType=="SOP":
                op=widget.SOP_METHOD[widget.sopBtnGroup.currentIndex]
                Pro.OPInfos={'opName': op, 'opClass': Pro.SOP_METHOD[op], 'opHyper': hyper[Pro.SOP_METHOD[op]]}
            else:
                op=widget.MOP_METHOD[widget.mopBtnGroup.currentIndex]
                Pro.OPInfos={'opName': op, 'opClass': Pro.MOP_METHOD[op], 'opHyper': hyper[Pro.MOP_METHOD[op]]}
            
            
            # sa=widget.SA_METHOD[widget.saBtnGroup.currentIndex]
            # sm=widget.SAMPLE_METHOD[widget.smBtnGroup.currentIndex]
            # Pro.SAInfos={'saName': sa, 'saClass': Pro.SA_METHOD[sa],'saHyper': hyper[Pro.SA_METHOD[sa]],
            #              'smName': sm,'smClass' : Pro.SAMPLE_METHOD[sm],'smHyper': hyper[Pro.SAMPLE_METHOD[sm]]}
            
        self.INDEX+=1
        self.contentWidget.setCurrentIndex(self.INDEX)
        self.contentWidget.currentWidget().updateUI()
        self.processWidget.on_button_clicked(self.INDEX)
        self.nextButton.setEnabled(False)
    
    def updateUI(self):
        
        self.setupWidget.updateUI()
    
    def updateNext(self):
        
        self.nextButton.setEnabled(True)
        
class SetupWidget(QWidget):
    
    next=pyqtSignal()
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        
        self.objType=None
        
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
        
        ########################Objective Path#######################
        
        h0=QHBoxLayout()
        label0=BodyLabel("Objective File:")
        self.objLine=ComboBox(self); self.objLine.setMinimumWidth(300)
        
        label1=BodyLabel("Selection of Optimization Objectives:"); self.objEdit=RadioWidget([])
        self.objEdit.setEnabled(True); self.objEdit.setMinimumWidth(50)
        self.objLine.currentIndexChanged.connect(self.loadObjFile)
        # self.objEdit.currentIndexChanged.connect(self.ensureObj)
        
        h0.addSpacing(50);h0.addWidget(label0); h0.addWidget(self.objLine);h0.addSpacing(50)
        h0.addWidget(label1); h0.addWidget(self.objEdit)
        h0.addStretch(1)
        vBoxLayout.addLayout(h0)
        #######################Optimization Method###########################
        h1=QHBoxLayout()
        label1=BodyLabel("SOP Method:"); line1=ButtonGroup(Pro.SOP_METHOD.keys(), False, self)
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(line1)
        self.sopBtnGroup=line1; self.SOP_METHOD=list(Pro.SOP_METHOD.keys())
        vBoxLayout.addLayout(h1)
        
        h2=QHBoxLayout()
        label2=BodyLabel("MOP Method:"); line2=ButtonGroup(Pro.MOP_METHOD.keys(), False, self)
        h2.addSpacing(50); h2.addWidget(label2); h2.addWidget(line2)
        self.mopBtnGroup=line2; self.MOP_METHOD=list(Pro.MOP_METHOD.keys())
        vBoxLayout.addLayout(h2)
        
        self.sopBtnGroup.group.buttonClicked.connect(self.updateHyper)
        self.mopBtnGroup.group.buttonClicked.connect(self.updateHyper)
        self.sopBtnGroup.group.buttonClicked.connect(self.nextEmit)
        self.objEdit.sop.connect(self.showSOP)
        self.objEdit.mop.connect(self.showMOP)
        self.objEdit.clearBtn.connect(self.clearMethod)
        self.objEdit.sop.connect(self.ensureObj)
        self.objEdit.mop.connect(self.ensureObj)
        ############################hyperWidget##########################################
        
        self.hyperStack=QStackedWidget(self)
        vBoxLayout.addWidget(self.hyperStack)
        self.hyperStack.addWidget(QWidget())
        self.hyperStack.setCurrentIndex(0)

        vBoxLayout.addStretch(1)
    
    def nextEmit(self):
        self.next.emit()
    
    def clearHyper(self):
        
        num=self.hyperStack.count()
        if num>1:
            widget=self.hyperStack.widget(1)
            self.hyperStack.removeWidget(widget)
        self.hyperStack.setCurrentIndex(0)
    
    def updateHyper(self):
        
        num=self.hyperStack.count()
        if num>1:
            widget=self.hyperStack.widget(1)
            self.hyperStack.removeWidget(widget)
        
        if self.objType=='SOP':
            I_op=self.sopBtnGroup.currentIndex
            method=self.SOP_METHOD[I_op]
            options=copy.deepcopy(Pro.SOP_HYPER[method])
        else:
            I_op=self.mopBtnGroup.currentIndex
            method=self.MOP_METHOD[I_op]
            options=copy.deepcopy(Pro.MOP_HYPER[method])
        
        hyper=hyperWidget(options)
        self.hyperStack.addWidget(hyper)
        self.hyperStack.setCurrentIndex(1)
    
    def clearMethod(self):
        
        self.sopBtnGroup.clearBtn()
        self.mopBtnGroup.clearBtn()
        self.clearHyper()
        
    def showSOP(self):
        
        self.objType='SOP'
        self.sopBtnGroup.setEnabled_(True)
        
    def showMOP(self):
        
        self.objType='MOP'
        self.sopBtnGroup.setEnabled_(True)
        
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
        objs=[f"obj {i : d}" for i in list(infos.keys())]
        self.objEdit.addObjs(objs)

        Pro.projectInfos['objPath']=path
        
    def ensureObj(self):
        
        objIDs=self.objEdit.selectID
        objInfos=[]
        for objID in objIDs:
            objInfos.append(self.objInfos[objID])
        
        Pro.objInfos=objInfos

class OptimizationWidget(QWidget):
    
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
        
        ########################
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
        self.optimizationBtn=PrimaryPushButton("Optimization"); self.optimizationBtn.clicked.connect(self.optimizing)
        self.optimizationBtn.setEnabled(False)
        h.addStretch(1);h.addWidget(self.initializeBtn);h.addSpacing(30);h.addWidget(self.optimizationBtn); h.addStretch(1)
        
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
        
        Pro.initProject(self.verbose, self.optimizationBtn)
        
    def optimizing(self):
        
        Pro.sampling()
        # self.verbose.append("Sampling Done. Please start simulation!\n")
        
        # self.samplingBtn.setEnabled(False)
        # self.simBtn.setEnabled(True)

    # def simulation(self):
        
    #     self.verbose.append("Model Simulating ... Please Waiting!\n")
    #     self.simBtn.setEnabled(False)
    #     Pro.simulation(self.processBar, self.finish)
    
    # def finish(self):
        
    #     self.verbose.append("Simulation Done. Please click the next to execute analysis!\n")
    #     self.parent().parent().nextButton.setEnabled(True)
        

class RadioWidget(QWidget):
    
    sop=pyqtSignal()
    mop=pyqtSignal()
    clearBtn=pyqtSignal()
    
    def __init__(self, objs, parent=None):
        
        self.selectID=[]
        
        super().__init__(parent)
        
        self.radios=[]
        
        self.hBoxLayout=QHBoxLayout(self)
        
        for obj in objs:
            radio=CheckBox(obj, self)
            self.radios.append(radio)
            radio.stateChanged.connect(self.ensureType)
            self.hBoxLayout.addWidget(radio)
        
        self.hBoxLayout.addStretch(1)
        
        
    def clear(self):
        
        if self.hBoxLayout is not None:
            while self.hBoxLayout.count():
                child = self.hBoxLayout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
        
        self.radios=[]       

    def addObjs(self, objs):
        
        for obj in objs:
            radio=CheckBox(obj, self)
            radio.setChecked(False)
            radio.toggled.connect(self.ensureType)
            self.radios.append(radio)
            self.hBoxLayout.addWidget(radio)
    
    def ensureType(self):
        count=0
        for radio in self.radios:
            if radio.isChecked():
                count+=1
                
                ID=radio.text().split()[1]
                self.selectID.append(int(ID))
                
        if count==0:
            self.clearBtn.emit()
        elif count==1:
            self.clearBtn.emit()
            self.sop.emit()
        else:
            self.clearBtn.emit()
            self.mop.emit()
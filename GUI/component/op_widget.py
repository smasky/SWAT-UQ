from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, QFormLayout, QGridLayout,
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
        self.setupWidget.objEdit.nextBtn.connect(self.updateNext)
        self.opWidget=OptimizationWidget(self)
        self.opWidget.nextBtn.connect(self.updateNext)
        self.conWidget=ConclusionWidget(self)
        
        self.contentWidget.addWidget(self.setupWidget)
        self.contentWidget.addWidget(self.opWidget)
        self.contentWidget.addWidget(self.conWidget)
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
                op=widget.SOP_METHOD[widget.sopComBox.currentIndex()]
                Pro.OPInfos={'opName': op, 'opClass': Pro.SOP_METHOD[op], 'opHyper': hyper[Pro.SOP_METHOD[op]]}
            else:
                op=widget.MOP_METHOD[widget.mopComBox.currentIndex()]
                Pro.OPInfos={'opName': op, 'opClass': Pro.MOP_METHOD[op], 'opHyper': hyper[Pro.MOP_METHOD[op]]}
            
        self.INDEX+=1
        self.contentWidget.setCurrentIndex(self.INDEX)
        self.contentWidget.currentWidget().updateUI()
        self.processWidget.on_button_clicked(self.INDEX)
        self.nextButton.setEnabled(False) #TODO
    
    def updateUI(self):
        
        self.setupWidget.updateUI()
    
    def updateNext(self, bool):
        
        self.nextButton.setEnabled(bool)
        
class SetupWidget(QWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        
        self.objType=None
        
        #######################Parameter Path############################
        gridLayout=QGridLayout()
        
        self.paraEdit=ComboBox(self); self.paraEdit.setMinimumWidth(300)
        self.paraEdit.currentIndexChanged.connect(self.loadParaFile)
        self.paraEdit._showComboMenu=self.dynamicShowPara
        self.paraEdit.setPlaceholderText("Click to select parameter file")
        gridLayout.addWidget(BodyLabel("Parameter File:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        gridLayout.addWidget(self.paraEdit, 0, 1)
        
        gridLayout.addWidget(BodyLabel("Number of Parameters:"), 0, 3, Qt.AlignmentFlag.AlignRight)
        self.numPara=LineEdit(self); self.numPara.setEnabled(False); self.numPara.setMaximumWidth(50)
        gridLayout.addWidget(self.numPara, 0, 4)
        
        ########################Objective Path#######################
        
        gridLayout.addWidget(BodyLabel("Objective File:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.objLine=ComboBox(self); self.objLine.setFixedWidth(300)
        self.objLine._showComboMenu=self.dynamicShowObj
        self.objLine.setPlaceholderText("Click to select objective file")
        gridLayout.addWidget(self.objLine, 1, 1)
        
        gridLayout.addWidget(BodyLabel("Selection of Optimization Objectives:"), 1, 3, Qt.AlignmentFlag.AlignRight)
        self.objEdit=RadioWidget([])
        self.objEdit.setEnabled(True)
        self.objLine.currentIndexChanged.connect(self.loadObjFile)
        gridLayout.addWidget(self.objEdit, 1, 4)
        self.objEdit.sop.connect(self.ensureObj)
        self.objEdit.mop.connect(self.ensureObj)
        
        gridLayout.addWidget(QWidget(), 0, 2)
        gridLayout.addWidget(QWidget(), 1, 2)
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setColumnStretch(2, 0.7)
        gridLayout.setColumnStretch(3, 1)
        gridLayout.setColumnStretch(4, 1)
        # h=QHBoxLayout()
        # h.addStretch(1);h.addLayout(gridLayout);h.addStretch(1)
        
        vBoxLayout.addLayout(gridLayout)
        vBoxLayout.addSpacing(10)
        
        #######################Optimization Method###########################
        gridLayout=QGridLayout()
        gridLayout.addWidget(BodyLabel("SOP Method:"), 0, 0, Qt.AlignmentFlag.AlignRight)
        self.sopComBox=ComboBox(self)
        self.sopComBox.addItems(Pro.SOP_METHOD.keys())
        self.SOP_METHOD=list(Pro.SOP_METHOD.keys())
        self.sopComBox.setEnabled(False)
        self.sopComBox.setFixedWidth(600)
        gridLayout.addWidget(self.sopComBox, 0, 1)
        
        gridLayout.addWidget(BodyLabel("MOP Method:"), 1, 0, Qt.AlignmentFlag.AlignRight)
        self.mopComBox=ComboBox(self)
        self.mopComBox.addItems(Pro.MOP_METHOD.keys())
        self.MOP_METHOD=list(Pro.MOP_METHOD.keys())
        self.mopComBox.setFixedWidth(600)
        self.mopComBox.setEnabled(False)
        gridLayout.addWidget(self.mopComBox, 1, 1)
        gridLayout.addWidget(QWidget(), 0 , 2)
        gridLayout.addWidget(QWidget(), 1 , 2)
        vBoxLayout.addLayout(gridLayout)
        
        self.objEdit.sop.connect(self.showSOP)
        self.objEdit.mop.connect(self.showMOP)
        self.objEdit.clearBtn.connect(self.clearMethod)
        self.objEdit.sop.connect(self.ensureObj)
        self.objEdit.mop.connect(self.ensureObj)
        self.mopComBox.currentIndexChanged.connect(self.updateHyper)
        self.sopComBox.currentIndexChanged.connect(self.updateHyper)
        
        vBoxLayout.addSpacing(20)
        ############################hyperWidget##########################################
        
        self.hyperStack=QStackedWidget(self)
        vBoxLayout.addWidget(self.hyperStack)
        self.hyperStack.addWidget(QWidget())
        self.hyperStack.setCurrentIndex(0)

        vBoxLayout.addStretch(1)
    
    def dynamicShowPara(self):
        
        self.paraEdit.clear()
        self.paraEdit.addItems(Pro.findParaFile())
        super(ComboBox, self.paraEdit)._showComboMenu()
    
    def dynamicShowObj(self):
        
        self.objLine.clear()
        self.objLine.addItems(Pro.findProFile())
        super(ComboBox, self.objLine)._showComboMenu()
    
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
            I_op=self.sopComBox.currentIndex()
            method=self.SOP_METHOD[I_op]
            options=copy.deepcopy(Pro.SOP_HYPER[method])
        else:
            I_op=self.mopComBox.currentIndex()
            method=self.MOP_METHOD[I_op]
            options=copy.deepcopy(Pro.MOP_HYPER[method])
        
        className=Pro.SOP_METHOD[method] if self.objType=='SOP' else Pro.MOP_METHOD[method]
        if className !="SCE_UA":
            options['nInit']={'dec': 'nInit', 'class': className, 'method': '__init__', 'type': 'int', 'default': '50'}
            options['nPop']={'dec': 'nPop', 'class': className, 'method': '__init__', 'type': 'int', 'default': '50'}
        
        options['maxFEs']={'dec': 'maxFEs', 'class': className, 'method': '__init__', 'type': 'int', 'default': '50000'}
        options['maxIterTimes']={'dec': 'maxIterTimes', 'class': className, 'method': '__init__', 'type': 'int', 'default': '1000'}
        
        hyper=hyperWidget(options)
        self.hyperStack.addWidget(hyper)
        self.hyperStack.setCurrentIndex(1)
    
    def clearMethod(self):
        
        self.sopComBox.setEnabled(False)
        self.mopComBox.setEnabled(False)
        self.clearHyper()
        
    def showSOP(self):
        
        self.objType='SOP'
        self.sopComBox.setEnabled(True)
        self.updateHyper()
        
    def showMOP(self):
        
        self.objType='MOP'
        self.sopComBox.setEnabled(True)
        self.updateHyper()
        
    def updateUI(self):
        
        pass
        # self.paraEdit.clear()
        # self.objLine.clear()
        # self.paraEdit.addItems(Pro.findParaFile())
        # self.objLine.addItems(Pro.findProFile())
        # self.paraEdit.setCurrentIndex(0)
        # self.objLine.setCurrentIndex(0)
        # self.loadParaFile()
        # self.loadObjFile()
    
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
        objInfos={}
        for objID in objIDs:
            objInfos[objID]=self.objInfos[objID]
        
        Pro.objInfos=objInfos

class OptimizationWidget(QWidget):
    
    nextBtn=pyqtSignal(bool)
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
                
        vBoxLayout=QVBoxLayout(self); vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ##################################Process Bar#####################################
        formLayout=QFormLayout()
        formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        self.FEsBar=ProgressBar(self)
        self.FEsBar.setValue(0)
        formLayout.addRow(BodyLabel("Function Evaluations:"), self.FEsBar)
    
        self.iterBar=ProgressBar(self)
        self.iterBar.setValue(0)
        formLayout.addRow(BodyLabel("Iterations:"), self.iterBar)
        
        h=QHBoxLayout()
        h.addSpacing(20);h.addLayout(formLayout);h.addSpacing(20)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)

        ###################################################
        h=QHBoxLayout(); h.addSpacing(20)
        self.label=BodyLabel("SWAT Execution:")
        self.swatEdit=ComboBox(self); self.swatEdit.setMinimumWidth(400)
        
        self.swatEdit.currentIndexChanged.connect(self.swatChanged)
        h.addWidget(self.label); h.addWidget(self.swatEdit); h.addStretch(1)
        vBoxLayout.addLayout(h)
        ######################################################
        h=QHBoxLayout(); h.addSpacing(20)
        self.label2=BodyLabel("SWAT Parallel:")
        self.parallelEdit=SpinBox(self); self.parallelEdit.setValue(5)
        h.addWidget(self.label2); h.addWidget(self.parallelEdit); h.addStretch(1)
        vBoxLayout.addLayout(h)
        
        #################Verbose################
        h=QHBoxLayout()
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        font = QFont("Consolas")  
        font.setStyleHint(QFont.Monospace)  
        self.verbose.setFont(font)
        self.verbose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        h.addSpacing(10);h.addWidget(self.verbose);h.addSpacing(10)
        vBoxLayout.addLayout(h)
        ######################################
        btnWidget=QWidget(self); btnWidget.setObjectName("btnWidget")
        btnWidget.setStyleSheet("#btnWidget{border-top: 1px solid rgba(0, 0, 0, 0.15);border-bottom: 1px solid rgba(0, 0, 0, 0.15);}")
        h=QHBoxLayout(btnWidget); h.setContentsMargins(0, 5, 0, 5)
        self.initializeBtn=PrimaryPushButton("Initialize"); self.initializeBtn.clicked.connect(self.initialize)
        self.optimizationBtn=PrimaryPushButton("Optimizing"); self.optimizationBtn.clicked.connect(self.optimizing)
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
        
        self.optimizationBtn.setEnabled(False)
        Pro.optimizing(self.FEsBar, self.iterBar, self.verbose, self.finish)
    
    def finish(self):
        
        self.verbose.append("Optimization Finished! Please click the next button to proceed.")
        self.nextBtn.emit(True)

class ConclusionWidget(QWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
                
        vBoxLayout=QVBoxLayout(self); vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ######################################
        
        h=QHBoxLayout()
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        font = QFont("Consolas")  
        font.setStyleHint(QFont.Monospace)  
        self.verbose.setFont(font)
        self.verbose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        h.addSpacing(10);h.addWidget(self.verbose);h.addSpacing(10)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)
        ############################
        
        h=QHBoxLayout()
        self.applyBtn=PrimaryPushButton("Apply optimal parameters to SWAT")
        h.addStretch(1); h.addWidget(self.applyBtn); h.addStretch(1)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)
        
    def updateUI(self):
        
        self.verbose.setText("")
        # Pro.OPResult['verbose']=[]
        self.verbose.setText("".join(Pro.OPResult['verbose']))
            
class RadioWidget(QWidget):
    
    sop=pyqtSignal()
    mop=pyqtSignal()
    clearBtn=pyqtSignal()
    nextBtn=pyqtSignal(bool)
    
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
        self.selectID=[]
        for radio in self.radios:
            if radio.isChecked():
                count+=1
                ID=radio.text().split()[1]
                self.selectID.append(int(ID))
                
        if count==0:
            self.clearBtn.emit()
            self.nextBtn.emit(False)
        elif count==1:
            self.clearBtn.emit()
            self.sop.emit()
            self.nextBtn.emit(True)
        else:
            self.clearBtn.emit()
            self.mop.emit()
            self.nextBtn.emit(True)


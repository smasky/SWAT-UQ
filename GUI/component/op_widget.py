from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, QFormLayout, QGridLayout,
                             QStackedWidget, QWidget)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics
from qfluentwidgets import (BodyLabel,
                             SpinBox,  TextEdit,
                             PrimaryPushButton, LineEdit)
import os
import copy
import GUI.qss
import GUI.data
from importlib.resources import path

from .process_widget import ProcessWidget
from .hyper_widget import hyperWidget
from .utility import setFont, getFont, MediumSize, Medium, Normal
from ..project import Project as Pro
from .check_box import CheckBox_
from .combox_ import ComboBox_ as ComboBox
from .progress_bar import ProgressBar_ as ProgressBar
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
        setFont(self.nextButton)
        self.nextButton.clicked.connect(self.nextPage)
        self.nextButton.setMinimumWidth(150)
        
        self.resetBtn=PrimaryPushButton("Reset", self)
        self.resetBtn.setMinimumWidth(150)
        self.resetBtn.clicked.connect(self.reset)
        setFont(self.resetBtn)
        
        h=QHBoxLayout();h.addStretch(1);h.addWidget(self.nextButton);h.addSpacing(20);h.addWidget(self.resetBtn);h.addStretch(1)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        #qss
        with path(GUI.qss, "op_widget.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
                
        #connect
        self.opWidget.resetChange.connect(self.resetBtn.setEnabled)
                
    def reset(self):
        
        Pro.OP_infos={}
        Pro.OP_result={}
        Pro.OP_paraInfos={}
        Pro.OP_problemInfos={}
        Pro.OP_objInfos={}
        
        self.contentWidget.setCurrentIndex(0)
        self.setupWidget.reset()
        self.opWidget.reset()
        self.processWidget.reset()
        self.INDEX=0
        
    def nextPage(self):
        
        if self.INDEX==0:
            widget=self.setupWidget
            hyper=self.setupWidget.hyperStack.widget(1).returnHyper()

            if widget.objType=="SOP":
                op=widget.SOP_METHOD[widget.sopComBox.currentIndex()]
                Pro.OP_infos={'opName': op, 'opClass': Pro.SOP_METHOD[op], 'opHyper': hyper[Pro.SOP_METHOD[op]]}
            else:
                op=widget.MOP_METHOD[widget.mopComBox.currentIndex()]
                Pro.OP_infos={'opName': op, 'opClass': Pro.MOP_METHOD[op], 'opHyper': hyper[Pro.MOP_METHOD[op]]}
            
        self.INDEX+=1
        self.contentWidget.setCurrentIndex(self.INDEX)
        self.contentWidget.currentWidget().updateUI()
        self.processWidget.on_button_clicked(self.INDEX)
        self.nextButton.setEnabled(False) #TODO
    
    def updateUI(self):
        
        self.setupWidget.updateUI()
    
    def updateNext(self, b):
        
        self.nextButton.setEnabled(b)
        
class SetupWidget(QWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 15, 0, 0)
        self.objType=None
        contentWidget=QWidget(self)
        #######################Parameter Path############################
        gridLayout=QGridLayout(contentWidget)
        gridLayout.setVerticalSpacing(10)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        
        label=BodyLabel("Parameter File:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 0, 1, Qt.AlignmentFlag.AlignVCenter)
    
        self.paraEdit=ComboBox(self)
        self.paraEdit.currentIndexChanged.connect(self.loadParaFile)
        self.paraEdit._showComboMenu=self.dynamicShowPara
        self.paraEdit.setPlaceholderText("Click to select parameter file")
        setFont(self.paraEdit)
        gridLayout.addWidget(self.paraEdit, 0, 2, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Number of Parameters:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 0, 4, Qt.AlignmentFlag.AlignVCenter)
        
        self.numPara=LineEdit(self); self.numPara.setEnabled(False)
        setFont(self.numPara)
        gridLayout.addWidget(self.numPara, 0, 5, Qt.AlignmentFlag.AlignVCenter)
        
        ########################Objective Path#######################
        
        label=BodyLabel("Objective File:"); label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 1, 1, Qt.AlignmentFlag.AlignVCenter)
        
        self.objLine=ComboBox(self)
        setFont(self.objLine)
        self.objLine._showComboMenu=self.dynamicShowObj
        self.objLine.setPlaceholderText("Click to select objective file")
        gridLayout.addWidget(self.objLine, 1, 2, Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("Optimization Objectives:"); label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 1, 4, Qt.AlignmentFlag.AlignVCenter)
        
        self.objEdit=RadioWidget([])
        self.objEdit.setEnabled(True)
        self.objLine.currentIndexChanged.connect(self.loadObjFile)
        gridLayout.addWidget(self.objEdit, 1, 5, Qt.AlignmentFlag.AlignVCenter)
        self.objEdit.sop.connect(self.ensureObj)
        self.objEdit.mop.connect(self.ensureObj)
        
        gridLayout.setColumnStretch(0, 1)
        gridLayout.setColumnStretch(1, 1)
        gridLayout.setColumnStretch(2, 1)
        gridLayout.setColumnStretch(3, 1)
        gridLayout.setColumnStretch(4, 1)
        gridLayout.setColumnStretch(5, 1)
        gridLayout.setColumnStretch(6, 1)
        
        index=[1, 2, 3, 4, 5]
        width=[210, 310, 50, 270, 210]
        for i, w in zip(index, width):
            qw=QWidget();qw.setFixedHeight(20);qw.setFixedWidth(w)
            gridLayout.addWidget(qw, 2, i)
            
        label=BodyLabel("SOP Method:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        gridLayout.addWidget(label, 3, 1, Qt.AlignmentFlag.AlignVCenter)
        
        self.sopComBox=ComboBox(self)
        setFont(self.sopComBox)
        self.sopComBox.addItems(Pro.SOP_METHOD.keys())
        self.SOP_METHOD=list(Pro.SOP_METHOD.keys())
        self.sopComBox.setEnabled(False)
        gridLayout.addWidget(self.sopComBox, 3, 2, 1, 3 ,Qt.AlignmentFlag.AlignVCenter)
        
        label=BodyLabel("MOP Method:")
        setFont(label)
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        gridLayout.addWidget(label, 4, 1, Qt.AlignmentFlag.AlignVCenter)
        
        self.mopComBox=ComboBox(self)
        setFont(self.mopComBox)
        self.mopComBox.addItems(Pro.MOP_METHOD.keys())
        self.MOP_METHOD=list(Pro.MOP_METHOD.keys())
        self.mopComBox.setEnabled(False)
        gridLayout.addWidget(self.mopComBox, 4, 2, 1, 3 ,Qt.AlignmentFlag.AlignVCenter)
        vBoxLayout.addWidget(contentWidget)
        vBoxLayout.addSpacing(10)
        
        #######################Connect###########################
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
        self.paraEdit.setCurrentIndex(0)
        super(ComboBox, self.paraEdit)._showComboMenu()
    
    def dynamicShowObj(self):
        
        self.objLine.clear()
        self.objLine.addItems(Pro.findObjFile())
        self.objLine.setCurrentIndex(0)
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
        self.sopComBox.setCurrentIndex(-1)
        self.mopComBox.setCurrentIndex(-1)
        self.sopComBox.setPlaceholderText("")
        self.mopComBox.setPlaceholderText("")
        self.clearHyper()
        
    def showSOP(self):
        
        self.objType='SOP'
        self.sopComBox.setEnabled(True)
        self.sopComBox.setCurrentIndex(-1)
        self.sopComBox.setPlaceholderText("Click here to select algorithm")
        
    def showMOP(self):
        
        self.objType='MOP'
        self.mopComBox.setEnabled(True)
        self.mopComBox.setCurrentIndex(-1)
        self.mopComBox.setPlaceholderText("Click here to select algorithm")
        
    def updateUI(self):
        
        pass
    
    def loadParaFile(self):
        
        path=self.paraEdit.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], path)
        infos, res=Pro.importParaFromFile(path)
        
        if res:
            self.numPara.setText(str(len(infos)))
            Pro.OP_paraInfos=infos
            Pro.OP_runInfos['paraPath']=path
    
    def loadObjFile(self):
        
        path=self.objLine.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], path)
        infos, res=Pro.importObjFromFile(path)
        if res:
            self.objInfos=infos
            
            self.objEdit.clear()
            objs=[f"obj {i : d}" for i in list(infos.keys())]
            self.objEdit.addObjs(objs)

            Pro.OP_runInfos['objPath']=path
        
    def ensureObj(self):
        
        objIDs=self.objEdit.selectID
        objInfos={}
        for objID in objIDs:
            objInfos[objID]=self.objInfos[objID]
        
        Pro.OP_objInfos=objInfos

    def reset(self):
        
        self.objLine.clear()
        self.paraEdit.clear()
        self.objEdit.clear()
        self.numPara.clear()
        
        self.objLine.setPlaceholderText("Click to select objective file")
        self.paraEdit.setPlaceholderText("Click to select parameter file")
        
        self.sopComBox.setCurrentIndex(-1)
        self.sopComBox.setPlaceholderText("")
        self.sopComBox.setEnabled(False)
        self.mopComBox.setCurrentIndex(-1)
        self.mopComBox.setPlaceholderText("")
        self.mopComBox.setEnabled(False)
        self.hyperStack.setCurrentIndex(0)
        
class OptimizationWidget(QWidget):
    
    nextBtn=pyqtSignal(bool)
    resetChange=pyqtSignal(bool)
    def __init__(self, parent=None):
        
        super().__init__(parent)
                
        vBoxLayout=QVBoxLayout(self); vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ##################################Process Bar#####################################
        h=QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        self.FEsBar=ProgressBar(self)
        self.FEsBar.setValue(0)
        h.setContentsMargins(20, 0, 20, 0)
        h.addWidget(self.FEsBar)
        vBoxLayout.addLayout(h)
        
        self.FEsLabel=BodyLabel("NA/NA FEs")
        self.FEsLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(self.FEsLabel)
        h=QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.addStretch(1);h.addWidget(self.FEsLabel);h.addSpacing(20)
        vBoxLayout.addLayout(h)
        
        h=QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        self.itersBar=ProgressBar(self)
        self.itersBar.setValue(0)
        h.setContentsMargins(20, 0, 20, 0)
        h.addWidget(self.itersBar)
        vBoxLayout.addLayout(h)
           
        self.itersLabel=BodyLabel("NA/NA Iters")
        self.itersLabel.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(self.itersLabel)
        h=QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        h.addStretch(1);h.addWidget(self.itersLabel);h.addSpacing(20)
        vBoxLayout.addLayout(h)
        
        ############################################################
        
        formLayout=QFormLayout()
        formLayout.setContentsMargins(20, 0, 0, 0)
        formLayout.setSpacing(5)
        formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        label=BodyLabel("SWAT Execution:")
        label.setMinimumWidth(100)
        setFont(label)
      
        self.swatEdit=ComboBox(self)
        setFont(self.swatEdit)
        self.swatEdit.setMaximumWidth(400)
        setFont(self.swatEdit, MediumSize, Normal)
        self.swatEdit.currentIndexChanged.connect(self.swatChanged)
        formLayout.addRow(label, self.swatEdit)
        
        ##############################################################
        
        label=BodyLabel("SWAT Parallel:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.parallelEdit=SpinBox(self); self.parallelEdit.setValue(1)
        setFont(self.parallelEdit, MediumSize, Normal)
        self.parallelEdit.setMaximumWidth(400)
        formLayout.addRow(label, self.parallelEdit)
        
        ###############################################################
        
        label=BodyLabel("Problem Name:")
        label.setAlignment(Qt.AlignmentFlag.AlignRight)
        setFont(label)
        self.problemEdit=LineEdit(self)
        self.problemEdit.setMaximumWidth(400)
        setFont(self.problemEdit, MediumSize, Normal)
        
        formLayout.addRow(label, self.problemEdit)
        
        vBoxLayout.addLayout(formLayout)
        #################Verbose################
        
        h=QHBoxLayout(); h.setContentsMargins(0, 0, 0, 0)
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        font = QFont("Consolas", pointSize=12)  
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
        setFont(self.initializeBtn)
        self.optimizationBtn=PrimaryPushButton("Optimizing"); self.optimizationBtn.clicked.connect(self.optimizing)
        setFont(self.optimizationBtn)
        self.optimizationBtn.setEnabled(False)
        self.cancelBtn=PrimaryPushButton("Break")
        setFont(self.cancelBtn)
        self.cancelBtn.setEnabled(False)
        self.cancelBtn.clicked.connect(self.cancel)
        
        h.addStretch(1);h.addWidget(self.initializeBtn);h.addSpacing(30);h.addWidget(self.optimizationBtn); h.addSpacing(30);h.addWidget(self.cancelBtn);h.addStretch(1)
        
        vBoxLayout.addWidget(btnWidget)
        
    def updateUI(self):
        
        self.swatEdit.clear()
        self.swatEdit.addItems(Pro.findSwatExe())
        self.swatEdit.setCurrentIndex(0)
        self.problemEdit.setText(Pro.projectInfos['projectName'])
        
    def swatChanged(self):
        
        Pro.OP_runInfos['swatExe']=self.swatEdit.currentText()
    
    def initialize(self):
        #
        textWidth = self.verbose.viewport().width()
        fontMetrics = QFontMetrics(self.verbose.font())
        averWidth = fontMetrics.averageCharWidth()
        nChars=textWidth // averWidth
        self.verbose.setProperty('totalWidth', nChars)
        Pro.OP_runInfos['verboseWidth']=nChars
        #
        numParallel=int(self.parallelEdit.value())
        Pro.OP_runInfos['numParallel']=numParallel
        Pro.OP_runInfos['tempPath']=os.path.join(Pro.projectInfos['projectPath'], 'temp')
        
        self.initializeBtn.setEnabled(False)
        
        self.swatEdit.setEnabled(False)
        self.parallelEdit.setEnabled(False)
        self.problemEdit.setEnabled(False)
        
        Pro.initOP(self.verbose, self.optimizationBtn)
        
        self.verbose.append("Initializing... Please wait!\n")
        
    def optimizing(self):
        
        Pro.OP_problemInfos['name']=self.problemEdit.text()
        
        self.resetChange.emit(False)
        self.optimizationBtn.setEnabled(False)
        self.cancelBtn.setEnabled(True)
        
        Pro.optimizing(self.FEsBar, self.itersBar, self.FEsLabel, self.itersLabel, self.verbose, self.finish, self.unfinish)

    def unfinish(self):
        
        self.itersLabel.setText("NA/NA Iters")
        self.FEsLabel.setText("NA/NA FEs")
        self.initializeBtn.setEnabled(True)
        self.cancelBtn.setEnabled(False)
        self.FEsBar.setValue(0)
        self.itersBar.setValue(0)
        self.swatEdit.setEnabled(True)
        self.parallelEdit.setEnabled(True)
        self.problemEdit.setEnabled(True)
        self.resetChange.emit(True)
        self.verbose.append("Simulation has been canceled by user.\n")

    def reset(self):
        
        self.itersLabel.setText("NA/NA Iters")
        self.FEsLabel.setText("NA/NA FEs")
        self.initializeBtn.setEnabled(True)
        self.cancelBtn.setEnabled(False)
        self.FEsBar.setValue(0)
        self.itersBar.setValue(0)
        self.swatEdit.setEnabled(True)
        self.parallelEdit.setEnabled(True)
        self.problemEdit.setEnabled(True)
        self.parallelEdit.setValue(1)
        self.verbose.clear()
        
    def cancel(self):
        
        self.cancelBtn.setEnabled(False)
        Pro.cancelOpt()
        self.verbose.append("Canceling... Please wait!\n")
        
    def finish(self):
        
        self.verbose.append("Optimization Finished! Please click the next button to proceed.")
        self.nextBtn.emit(True)
        self.cancelBtn.setEnabled(False)
        self.resetChange.emit(True)

class ConclusionWidget(QWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
                
        vBoxLayout=QVBoxLayout(self); vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ######################################
        h=QHBoxLayout()
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        font = QFont("Consolas", pointSize=12)  
        font.setStyleHint(QFont.Monospace)  
        self.verbose.setFont(font)
        self.verbose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        h.addSpacing(10);h.addWidget(self.verbose);h.addSpacing(10)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(10)
        ############################
        
    def updateUI(self):
        
        self.verbose.append("")
        self.verbose.append("".join(Pro.OP_result['verbose']))
        
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
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        for obj in objs:
            radio=CheckBox_(obj, self)
            self.radios.append(radio)
            radio.stateChanged.connect(self.ensureType)
            self.hBoxLayout.addWidget(radio)
              
    def clear(self):
        
        if self.hBoxLayout is not None:
            while self.hBoxLayout.count():
                child = self.hBoxLayout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()
        
        self.radios=[]       

    def addObjs(self, objs):
        
        for obj in objs:
            radio=CheckBox_(obj, self)
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
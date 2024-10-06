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
from ..project import Project as Pro

class OPWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        
        processWidget=ProcessWidget(self)
        processWidget.addStep(0, "Setup")
        processWidget.addStep(1, "Optimization")
        processWidget.addStep(2, "Conclusion")
        self.processWidget=processWidget
        vBoxLayout.addWidget(processWidget)
        
        contentWidget=QStackedWidget(self)
        contentWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        contentWidget.setObjectName("contentWidget")
        vBoxLayout.addWidget(contentWidget)
        ##############################################
        
        self.setupWidget=SetupWidget(self)
        contentWidget.addWidget(self.setupWidget)
        
        vBoxLayout.addStretch(1)
        
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        #qss
        with path(GUI.qss, "op_widget.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())

    def updateUI(self):
        
        self.setupWidget.updateUI()
    
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
        
        ########################Objective Path#######################
        
        h0=QHBoxLayout()
        label0=BodyLabel("Objective File:")
        self.objLine=ComboBox(self); self.objLine.setMinimumWidth(300)
        
        label1=BodyLabel("Selection of Objectives:"); self.objEdit=RadioWidget([])
        self.objEdit.setEnabled(True); self.objEdit.setMinimumWidth(50)
        self.objLine.currentIndexChanged.connect(self.loadObjFile)
        # self.objEdit.currentIndexChanged.connect(self.ensureObj)
        
        h0.addSpacing(50);h0.addWidget(label0); h0.addWidget(self.objLine);h0.addSpacing(50)
        h0.addWidget(label1); h0.addWidget(self.objEdit)
        h0.addStretch(1)
        vBoxLayout.addLayout(h0)
        #######################Optimization Method###########################
        h1=QHBoxLayout()
        label1=BodyLabel("SOP Method:"); line1=ButtonGroup(Pro.SOP_METHOD.keys(), True, self)
        h1.addSpacing(50); h1.addWidget(label1); h1.addWidget(line1);h1.addStretch(10)
        self.smBtnGroup=line1; self.OP_METHOD=list(Pro.SOP_METHOD.keys())
        vBoxLayout.addLayout(h1)
        
        

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

class RadioWidget(QWidget):
    def __init__(self, objs, parent=None):
        
        super().__init__(parent)
        
        radios=[]
        
        self.hBoxLayout=QHBoxLayout(self)
        
        for obj in objs:
            radio=CheckBox(obj, self)
            radios.append(radio)
            self.hBoxLayout.addWidget(radio)
        
        self.hBoxLayout.addStretch(1)
    
    def clear(self):
        
        if self.hBoxLayout is not None:
            while self.hBoxLayout.count():
                child = self.hBoxLayout.takeAt(0)
                if child.widget() is not None:
                    child.widget().deleteLater()

    def addObjs(self, objs):
        
        for obj in objs:
            radio=CheckBox(obj, self)
            radio.setChecked(True)
            self.hBoxLayout.addWidget(radio)
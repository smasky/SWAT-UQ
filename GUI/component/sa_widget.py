from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout, QSizePolicy, 
                             QStackedWidget, QWidget, QButtonGroup, QSplitter)
from PyQt5.QtCore import Qt
from qfluentwidgets import BodyLabel, RadioButton, SpinBox, DoubleSpinBox, CheckBox, PrimaryPushButton, LineEdit

import GUI.qss
import GUI.data
from importlib.resources import path
from .process_widget import ProcessWidget
class SAWidget(QFrame):
    INDEX=0
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        
        proWidget=ProcessWidget(self)
        proWidget.addStep(0, "Setup")
        proWidget.addStep(1, "Simulation")
        proWidget.addStep(2, "Analysis")
        proWidget.addStep(3, "Report")
        self.proWidget=proWidget
        # proWidget.buttonClicked.connect(self.displayPage)
        vBoxLayout.addWidget(proWidget)
        
        
        contentWidget=QStackedWidget(self)
        contentWidget.setObjectName("contentWidget")
        vBoxLayout.addWidget(contentWidget)
        
        contentWidget.addWidget(SetupWidget(self))
        contentWidget.setCurrentIndex(0)
        self.contentWidget=contentWidget
        
        vBoxLayout.addStretch(1)
        nextButton=PrimaryPushButton("Next", self)
        nextButton.clicked.connect(self.nextPage)
        nextButton.setMinimumWidth(300)
        h=QHBoxLayout();h.addStretch(1);h.addWidget(nextButton);h.addStretch(1)
        vBoxLayout.addLayout(h)
        vBoxLayout.addSpacing(20)
        
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        with path(GUI.qss, "sa_widget.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
    
    def nextPage(self):
        self.INDEX+=1
        # self.contentWidget.setCurrentIndex(self.INDEX)
        self.proWidget.on_button_clicked(self.INDEX)

    
class SetupWidget(QWidget):
    
    SAMPLE={ 0:[5], 1: [], 2: [3], 3: [], 4: [4], 5: []}
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
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
        samplingStack.addWidget(FFDWidget())
        samplingStack.addWidget(LHSWidget())
        samplingStack.addWidget(RandomWidget()) 
        samplingStack.addWidget(FastSamplingWidget())
        samplingStack.addWidget(MorrisWidget())
        samplingStack.addWidget(SobolWidget())
        samplingStack.addWidget(QWidget())
        self.samplingStack=samplingStack; self.samplingStack.setCurrentIndex(6)
        self.btnGroup2.group.idClicked.connect(self.displayPage2)
        
        vBoxLayout.addStretch(1)
        vBoxLayout.setContentsMargins(0,0,0,0)

    def displayPage1(self, index):
        self.hyperStack.setCurrentIndex(index)

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
        label1=BodyLabel("Number of Factors:"); self.line1=SpinBox(self); self.line1.setValue(5)
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
        self.lC.setText(str(self.line1.value())) #TODO

class LHSWidget(QWidget):
    
    HYPER={}
        
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("N:"); self.line1=SpinBox(self); self.line1.setValue(5)
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
        self.lC.setText(str(self.line1.value())) #TODO

class RandomWidget(QWidget):
    
    HYPER={}
        
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("N:"); self.line1=SpinBox(self); self.line1.setValue(5)
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
        self.lC.setText(str(self.line1.value())) #TODO

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
        label2=BodyLabel("N:"); self.line2=SpinBox(self); self.line2.setValue(50)
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
        
        self.HYPER['N']=self.line1.value()
        
        self.lC.setText(str(self.HYPER['N'])) #TODO

class MorrisWidget(QWidget):
        
    HYPER={}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("N:"); self.line1=SpinBox(self); self.line1.setValue(5)
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
        self.lC.setText(str(self.HYPER['N'])) #TODO

class SobolWidget(QWidget):
    
    HYPER={}
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        ########################
        h1=QHBoxLayout()
        label1=BodyLabel("N:"); self.line1=SpinBox(self); self.line1.setValue(5)
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
        self.lC.setText(str(self.HYPER['N'])) #TODO

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
                
        

        
        
        
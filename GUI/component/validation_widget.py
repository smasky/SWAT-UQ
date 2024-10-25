
from typing import List
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QFrame, QWidget,QFormLayout, QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy, QTreeWidgetItem

from qfluentwidgets import TextEdit, TableWidget, BodyLabel, PrimaryPushButton, FluentStyleSheet, getStyleSheet, TreeWidget

import os
import numpy as np
from .utility import setFont, getFont, Medium, substitute, MediumSize, Normal
from .combox_ import ComboBox
# from .tree_widget import TreeWidget_ as TreeWidget
from ..project import Project as Pro
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

class ValidationWidget(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)

        vMainLayout=QVBoxLayout(self)
        
        topHLayout=QHBoxLayout()
        leftLayout=QVBoxLayout()
        formLayout=QFormLayout()
        formLayout.setContentsMargins(10, 10, 0, 0)
        formLayout.setSpacing(20)
        formLayout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        
        label=BodyLabel("Result File:", self)
        setFont(label)
        self.resultFileBox=ComboBox(self)
        setFont(self.resultFileBox)
        self.resultFileBox.setFixedWidth(300)
        self.resultFileBox._showComboMenu=self.dynamicShowResultFile
        
        formLayout.addRow(label, self.resultFileBox)
        
        label=BodyLabel("Parameter File:")
        setFont(label)
        self.paraFileBox=ComboBox(self)
        setFont(self.paraFileBox)
        self.paraFileBox.setFixedWidth(300)
        self.paraFileBox._showComboMenu=self.dynamicShowParFile
        
        formLayout.addRow(label, self.paraFileBox)
        
        label=BodyLabel("Objective File:")
        setFont(label)
        self.objFileBox=ComboBox(self)
        setFont(self.objFileBox)
        self.objFileBox.setFixedWidth(300)
        self.objFileBox._showComboMenu=self.dynamicShowObjFile
        
        formLayout.addRow(label, self.objFileBox)
        
        label=BodyLabel("SWAT Execution:")
        setFont(label)
        self.swatBox=ComboBox(self)
        setFont(self.swatBox)
        self.swatBox.setFixedWidth(300)
        self.swatBox._showComboMenu=self.dynamicShowSwat
        
        formLayout.addRow(label, self.swatBox)
        
        w=QWidget()
        h=QHBoxLayout(w); h.setContentsMargins(0, 0, 0, 0)
        self.loadBtn=PrimaryPushButton("Load", self)
        self.loadBtn.setFixedWidth(100)
        self.loadBtn.clicked.connect(self.loadFile)
        setFont(self.loadBtn)
        
        self.resetBtn=PrimaryPushButton("Reset", self)
        self.resetBtn.setFixedWidth(100)
        setFont(self.resetBtn)
        self.resetBtn.setEnabled(False)
        self.resetBtn.clicked.connect(self.reset)
        
        h.addWidget(self.loadBtn); h.addSpacing(10); h.addWidget(self.resetBtn)
        
        formLayout.addRow("", w)
        
        formLayout.setAlignment(w, Qt.AlignRight)
        
        leftLayout.addLayout(formLayout)
        
        topHLayout.addLayout(leftLayout)
        topHLayout.addSpacing(20)
        
        w=QWidget(self)
        w.setObjectName("Container")
        h=QHBoxLayout(w)
        self.leftTreeWidget=TreeWidgetVal(self)
        h.addWidget(self.leftTreeWidget)
        h.setContentsMargins(0 ,0 ,0 ,0 )
        w.setStyleSheet(""" #Container { border: 1px solid rgba(0, 0, 0, 0.15); border-radius:15px; } """)
      
        topHLayout.addWidget(w)
        
        vMainLayout.addLayout(topHLayout)
        
        vMainLayout.addSpacing(10)
        
        self.table=TableWidgetVal(self)
        
        vMainLayout.addWidget(self.table)
        
        self.verbose=TextEdit(self);self.verbose.setReadOnly(True)
        font = QFont("Consolas", pointSize=8)
        font.setStyleHint(QFont.Monospace) 
        self.verbose.setFont(font)
        self.verbose.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        vMainLayout.addWidget(self.verbose)
        
        self.applyBtn=PrimaryPushButton("Apply", self)
        self.applyBtn.setFixedWidth(100)
        self.applyBtn.setEnabled(False)
        setFont(self.applyBtn)
        self.simBtn=PrimaryPushButton("Simulate", self)
        self.simBtn.setFixedWidth(100)
        self.simBtn.setEnabled(False)
        setFont(self.simBtn)
        self.visualBtn=PrimaryPushButton("Visualize", self)
        self.visualBtn.setFixedWidth(100)
        self.visualBtn.setEnabled(False)
        setFont(self.visualBtn)
        
        h=QHBoxLayout()
        h.addStretch(1)
        h.addWidget(self.applyBtn); h.addSpacing(20)
        h.addWidget(self.simBtn); h.addSpacing(20)
        h.addWidget(self.visualBtn); h.addSpacing(20)
        h.addStretch(1)
        
        vMainLayout.addLayout(h)
        
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setStyleSheet("""ValidationWidget {
                                    border: 1px solid rgba(0, 0, 0, 0.15);
                                    border-radius:15px;
                                    background-color: rgba(249, 249, 249, 0.75);
                                }
                           """)

        #connect
        self.leftTreeWidget.itemIndex.connect(self.setDecsToTable)
        self.applyBtn.clicked.connect(self.apply)
        self.simBtn.clicked.connect(self.simulate)
    
    def dynamicShowSwat(self):
        
        self.swatBox.clear()
        self.swatBox.addItems(Pro.findSwatExe())
        self.swatBox.setCurrentIndex(0)
        super(ComboBox, self.swatBox)._showComboMenu()
    
    def dynamicShowResultFile(self):
        
        self.resultFileBox.clear()
        self.resultFileBox.addItems(Pro.findResultFile())
        self.resultFileBox.setCurrentIndex(0)
        super(ComboBox, self.resultFileBox)._showComboMenu()
    
    def dynamicShowObjFile(self):
        
        self.objFileBox.clear()
        self.objFileBox.addItems(Pro.findProFile())
        self.objFileBox.setCurrentIndex(0)
        super(ComboBox, self.objFileBox)._showComboMenu()
        
    def dynamicShowParFile(self):
        
        self.paraFileBox.clear()
        self.paraFileBox.addItems(Pro.findParaFile())
        self.paraFileBox.setCurrentIndex(0)
        super(ComboBox, self.paraFileBox)._showComboMenu()
    
    def loadFile(self):
        
        fileName=self.resultFileBox.currentText()
        self.OPData=Pro.loadOPFile(fileName)
        data=self.OPData['History_Best']
        
        self.data=[]
        
        self.leftTreeWidget.clear()
        
        for key, items in data.items():
            
            bestObj, bestDecs=items['Best Objectives'].tolist(), items['Best Decisions'].tolist()
            
            self.data.append(bestDecs)
            
            text_decs = ",".join([f"{num:.2f}" for num in bestDecs])
            text_objs = ",".join([f"{num:.2f}" for num in bestObj])
            
            description=f"Objs: {text_objs} | Decs: {text_decs}"
            self.leftTreeWidget.addItem_(key, description)
        self.leftTreeWidget.scrollToBottom()
        
        paraFile=self.paraFileBox.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], paraFile)
        infos=Pro.importParaFromFile(path)
        
        self.table.setRowCount(0)
        for info in infos:
            self.table.addRows_(info)
            
        Pro.paraInfos=infos #TODO
        Pro.projectInfos['paraPath']=path
        
        objFile=self.objFileBox.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], objFile)
        infos=Pro.importProFromFile(path)
      
        Pro.objInfos=infos #TODO
        Pro.projectInfos['objPath']=path
        
        Pro.projectInfos['numParallel']=1
        Pro.projectInfos['tempPath']=os.path.join(Pro.projectInfos['projectPath'], 'validation') #TODO
        Pro.projectInfos['swatExe']=self.swatBox.currentText()

        self.resetBtn.setEnabled(True)
        self.loadBtn.setEnabled(False)
        
    def reset(self):
        
        self.table.setRowCount(0)
        self.leftTreeWidget.clear()
        
        self.resetBtn.setEnabled(False)
        self.loadBtn.setEnabled(True)
        
        self.applyBtn.setEnabled(False)
        self.simBtn.setEnabled(False)
        self.visualBtn.setEnabled(False)
        
    def setDecsToTable(self, index):
        
        decs=self.data[index]
        self.table.setColValue(decs)
        self.decs=np.array(decs).reshape(1, -1)
        
        if self.applyBtn.isEnabled()==False:
            self.applyBtn.setEnabled(True)
        
    def apply(self):
        
        Pro.initProject(self.verbose, self.simBtn)
        
    def simulate(self):
        
        objs, data=Pro.singleSim(self.decs)
        
        a=1
    
    
    
class TreeWidgetVal(TreeWidget):
    
    itemIndex=pyqtSignal(int)
    
    def __init__(self, parent=None):
            
        super().__init__(parent)
        
        self.initUI()
        self.lastCheckedItem=None
        
    def initUI(self):
        
        self.setHeaderLabels(["Optimization Iters", "Best Obj Value"])
        qss=getStyleSheet(FluentStyleSheet.TREE_VIEW)
        qss=substitute(qss, {'QHeaderView::section':{'font': " 18px 'Segoe UI', 'Microsoft YaHei'", 'font-weight': '500'}})
        self.setStyleSheet(qss)
        self.header().setStyleSheet("QHeaderView::section { color: black; }")
        self.header().setSectionResizeMode(0, QHeaderView.Fixed)
        self.setColumnWidth(0, 200) 
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents) 
        self.itemClicked.connect(self.handleItemClicked)
    
    def clear(self):
        
        self.lastCheckedItem=None
        
        return super().clear()
    
    def addItem_(self, key, description):
        
        iterItems= QTreeWidgetItem(self, [key, description])
        iterItems.setFont(0, getFont(18, Medium))
        iterItems.setFont(1, getFont(18, Medium))
        iterItems.setToolTip(1, description)
        iterItems.setFlags(iterItems.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
        iterItems.setCheckState(0, Qt.Unchecked)
    
    def handleItemClicked(self, item, column):
        
        if self.lastCheckedItem and self.lastCheckedItem is not item:
            self.lastCheckedItem.setCheckState(0, Qt.Unchecked) 
        
        item.setCheckState(0, Qt.Checked)
        self.lastCheckedItem = item 
        
        index=self.indexOfTopLevelItem(item)
        
        self.itemIndex.emit(index)
    
class TableWidgetVal(TableWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        qss=getStyleSheet(FluentStyleSheet.TABLE_VIEW)
        qss=substitute(qss, {'QTableView': { 'font': " 16px 'Segoe UI', 'Microsoft YaHei'"}, 'QHeaderView::section':{'font': " 18px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'", 'font-weight': ' 500'}})
        self.setStyleSheet(qss)

        self.initUI()
        
    def initUI(self):
        
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        self.horizontalHeader().setVisible(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setColumnCount(7)
        
        self.setHorizontalHeaderLabels([
            str('Parameter Name'), str('File Extension'), str('Tuning Mode'),
            str('Lower Bound'), str('Upper Bound'), str('Position'), str('Value')])
        self.setFixedHeight(200)
        self.horizontalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; }}")
        self.verticalHeader().setVisible(False)
        
    def addRows_(self, data):
        
        row=self.rowCount()
        col=0
        
        self.insertRow(row)
        self.setRowHeight(row, 35) 
        
        for i, value in enumerate(data):
            if i==2:
                value=Pro.INT_MODE[value]
            
            item=QTableWidgetItem(value); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            setFont(item, weight=Normal)
            self.setItem(row, col, item)
            col+=1
    
    def setColValue(self, decs):
        
        for i, v in enumerate(decs):
            
            item=QTableWidgetItem(f"{float(v):.4f}");item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            setFont(item)

            self.setItem(i, 6, item)

        
        
        
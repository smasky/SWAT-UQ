
from typing import List
from PyQt5.QtWidgets import QHeaderView, QTableWidgetItem, QFrame, QWidget,QFormLayout, QGridLayout, QVBoxLayout, QHBoxLayout, QSizePolicy, QTreeWidgetItem

from qfluentwidgets import TableWidget, BodyLabel, PrimaryPushButton, FluentStyleSheet, getStyleSheet, TreeWidget

import os
from .utility import setFont, getFont, Medium, substitute, MediumSize, Normal
from .combox_ import ComboBox
# from .tree_widget import TreeWidget_ as TreeWidget
from ..project import Project as Pro
from PyQt5.QtCore import Qt

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
        
        self.loadBtn=PrimaryPushButton("Load", self)
        self.loadBtn.setFixedWidth(150)
        self.loadBtn.clicked.connect(self.loadFile)
        setFont(self.loadBtn)
        
        formLayout.addRow("", self.loadBtn)
        formLayout.setAlignment(self.loadBtn, Qt.AlignRight)
        
        leftLayout.addLayout(formLayout)
        
        topHLayout.addLayout(leftLayout)
        topHLayout.addSpacing(20)
        
        w=QWidget(self)
        w.setObjectName("Container")
        h=QHBoxLayout(w)
        self.leftTreeWidget=TreeWidget(self)
        self.leftTreeWidget.setHeaderLabels(["Optimization Iters", "Best Obj Value"])
        qss=getStyleSheet(FluentStyleSheet.TREE_VIEW)
        qss=substitute(qss, {'QHeaderView::section':{'font': " 18px 'Segoe UI', 'Microsoft YaHei'", 'font-weight': '500'}})
        self.leftTreeWidget.setStyleSheet(qss)
        self.leftTreeWidget.header().setStyleSheet("QHeaderView::section { color: black; }")
        self.leftTreeWidget.header().setSectionResizeMode(0, QHeaderView.Fixed)
        self.leftTreeWidget.setColumnWidth(0, 200) 
        self.leftTreeWidget.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)  
        
        h.addWidget(self.leftTreeWidget)
        h.setContentsMargins(0 ,0 ,0 ,0 )
        w.setStyleSheet(""" #Container { border: 1px solid rgba(0, 0, 0, 0.15); border-radius:15px; } """)
      
        topHLayout.addWidget(w)
        
        vMainLayout.addLayout(topHLayout)
        
        vMainLayout.addSpacing(10)
        
        self.table=TableWidgetVal(self)
        
        vMainLayout.addWidget(self.table)
        
        vMainLayout.addStretch(1)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.setStyleSheet("""ValidationWidget {
                                    border: 1px solid rgba(0, 0, 0, 0.15);
                                    border-radius:15px;
                                    background-color: rgba(249, 249, 249, 0.75);
                                }
                           """)
    
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
        self.data=self.OPData['History_Best']
        
        for i, (key, items) in enumerate(self.data.items()):
            
            bestObj, bestDecs=items['Best Objectives'].tolist(), items['Best Decisions'].tolist()
            
            text_decs = ",".join([f"{num:.2f}" for num in bestDecs])
            text_objs = ",".join([f"{num:.2f}" for num in bestObj])
            
            description=f"Objs: {text_objs} | Decs: {text_decs}"
            
            iterItems= QTreeWidgetItem(self.leftTreeWidget, [key, description])
            iterItems.setFont(0, getFont(18, Medium))
            iterItems.setFont(1, getFont(18, Medium))
            iterItems.setToolTip(1, description)
            iterItems.setFlags(iterItems.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
            iterItems.setCheckState(0, Qt.Unchecked)
        
        paraFile=self.paraFileBox.currentText()
        path=os.path.join(Pro.projectInfos['projectPath'], paraFile)
        infos=Pro.importParaFromFile(path)
        
        for info in infos:
            self.table.addRows_(info)
        
        a=1


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
        self.setFixedHeight(300)
        self.horizontalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; }}")
        self.verticalHeader().setVisible(False)
    def addRows_(self, data):
        
        row=self.rowCount()
        col=0
        
        self.insertRow(row)
        self.setRowHeight(row, 35) 
        
        for value in data:
            
            item=QTableWidgetItem(str(value));item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            setFont(item, weight=Normal)
            self.setItem(row, col, item)
            col+=1
    
    
        
        
        
        
        
from qfluentwidgets import StrongBodyLabel, PrimaryToolButton, FluentIcon, PrimaryPushButton

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QHeaderView, QFrame
from PyQt5.QtCore import Qt

import GUI.qss
import GUI.data
from importlib.resources import path

from .table_widget_pro import TableWidgetPro
from .add_para_widget import AddParaWidget

class ParaTable(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        self.loadParaList()
        
        self.vBoxLayout=QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        
        label=StrongBodyLabel("Parameter List")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        importButton=PrimaryPushButton("Import From File", self); importButton.setFixedHeight(24); 
        self.importButton=importButton
        
        addButton=PrimaryToolButton(FluentIcon.ADD, self); addButton.setFixedHeight(24); 
        self.addButton=addButton; addButton.clicked.connect(self.addPara)
        
        hBoxLayout=QHBoxLayout(); hBoxLayout.addWidget(importButton);hBoxLayout.addStretch(2)
        hBoxLayout.addWidget(label);hBoxLayout.addStretch(3);hBoxLayout.addWidget(addButton)
        
        self.vBoxLayout.addLayout(hBoxLayout)
        
        self.table=TableWidgetPro(self); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setObjectName("contentTable")
        self.vBoxLayout.addWidget(self.table)
        
        self.table.verticalHeader()
        self.table.setBorderRadius(8)
        self.table.setBorderVisible(True)

        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            self.tr('Par. Name'), self.tr('File Ext.'), self.tr('Tuning Mode'),
            self.tr('Lower Bound'), self.tr('Upper Bound'), self.tr('   Position (SUB-HRU)   '), self.tr('Operation')])
        
        self.generateButton=PrimaryPushButton("Generate Para. File (.par)", self)
        self.generateButton.setMaximumWidth(500)
        self.vBoxLayout.addWidget(self.generateButton)
        
        self.vBoxLayout.setAlignment(self.generateButton, Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        with path(GUI.qss, "para_table.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { color: black; }")
        
    def addPara(self):
        dialog=AddParaWidget(self.paraList, self)
        dialog.exec()
        
        selected=dialog.selected
        
        for key, values in selected.items():
            for paraName in values:
                text=[paraName, key]
                self.table.addRow(text)
        
        self.table.repaint()
                
    def loadParaList(self):
        self.paraList={}
        with path(GUI.data, "parameter_list.txt") as para_list_path:
            with open(str(para_list_path), 'r') as f:
                lines=f.readlines()
                for line in lines:
                    txt=line.split()
                    self.paraList.setdefault(txt[0], []).append(txt[1])
        
        
from qfluentwidgets import StrongBodyLabel, PrimaryToolButton, FluentIcon, PrimaryPushButton

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QHeaderView, QFrame, QFileDialog
from PyQt5.QtCore import Qt

import GUI.qss
import GUI.data
from importlib.resources import path

from .table_widget_para import TableWidgetPara
from .add_para_widget import AddParaWidget
from ..project import Project as Pro
class ParaTable(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.vBoxLayout=QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        
        label=StrongBodyLabel("Parameter Information List")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        importButton=PrimaryPushButton("Import From File", self); importButton.setFixedHeight(30); 
        self.importButton=importButton; self.importButton.clicked.connect(self.importParaFile)
        
        addButton=PrimaryToolButton(FluentIcon.ADD, self); addButton.setFixedHeight(30); 
        self.addButton=addButton; addButton.clicked.connect(self.addPara)
        
        hBoxLayout=QHBoxLayout(); hBoxLayout.addWidget(importButton);hBoxLayout.addStretch(2)
        hBoxLayout.addWidget(label);hBoxLayout.addStretch(3);hBoxLayout.addWidget(addButton)
        
        self.vBoxLayout.addLayout(hBoxLayout)
        
        self.table=TableWidgetPara(self); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setObjectName("contentTable")
        self.vBoxLayout.addWidget(self.table)
        
        # self.table.verticalHeader()
        self.table.setBorderRadius(8)
        self.table.setBorderVisible(True)

        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            self.tr('Parameter Name'), self.tr('File Extension'), self.tr('Tuning Mode'),
            self.tr('Lower Bound'), self.tr('Upper Bound'), self.tr('   Position (SUB-HRU)   '), self.tr('Operation')])
        
        self.generateButton=PrimaryPushButton("Save To Parameter File (.par)", self)
        self.generateButton.setMaximumWidth(500); self.generateButton.clicked.connect(self.saveParFile)
        self.vBoxLayout.addWidget(self.generateButton)
        
        self.vBoxLayout.setAlignment(self.generateButton, Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        with path(GUI.qss, "para_table.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { color: black; }")
        
    def addPara(self):
        dialog=AddParaWidget(Pro.paraList, parent=self)
        dialog.exec()
        
        selected=dialog.selected
        
        for key, values in selected.items():
            for paraName in values:
                text=[paraName, key]
                self.table.addRow(text)
        
        self.table.repaint()
    
    def importParaFile(self):
        
        path, success= QFileDialog.getOpenFileName(self, "Import Parameter File", "", "Parameter File (*.par)")
        
        if success:
            Infos=Pro.importParaFromFile(path)
        
            for paraInfo in Infos:
                self.table.addRow(paraInfo)
                self.table.repaint()

    def saveParFile(self):
        Infos=[]
        
        rows=self.table.rowCount()
        for i in range(rows):
            paraName=self.table.item(i, 0).text()
            # fileExtension=self.table.item(i, 1).text()
            tuningMode=Pro.INVERSETUNEMODE[self.table.cellWidget(i, 2).core.currentIndex()]
            lowerBound=str(self.table.cellWidget(i, 3).core.value())
            upperBound=str(self.table.cellWidget(i, 4).core.value())
            position=self.table.cellWidget(i, 5).core.text()
            Infos.append([paraName, tuningMode, lowerBound, upperBound, position])

        Pro.paraInfos=Infos
        path, success= QFileDialog.getSaveFileName(self, "Save Parameter File", Pro.projectPath, "Parameter File (*.par)")
        if success:
            
            Pro.saveParaFile(path)
            
    
        
        
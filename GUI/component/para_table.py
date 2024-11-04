from qfluentwidgets import (SubtitleLabel,
                            PrimaryPushButton, InfoBar, InfoBarPosition)

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSizePolicy, QHeaderView, QFrame, QFileDialog
from PyQt5.QtCore import Qt

import GUI.qss
import GUI.data
from importlib.resources import path

from .table_widget_para import TableWidgetPara
from .add_para_widget import AddParaWidget
from .info_bar import InfoBar_ as InfoBar
from .utility import  setFont, MediumSize
from .message_box import MessageBox
from ..project import Project as Pro
class ParaTable(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.vBoxLayout=QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        
        label=SubtitleLabel("Parameter Information List")
        setFont(label, 25)
        
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        
        addButton=PrimaryPushButton("Add", self); addButton.setFixedHeight(30)
        setFont(addButton)
        
        self.addButton=addButton; addButton.clicked.connect(self.addPara)
        
        hBoxLayout=QHBoxLayout();hBoxLayout.addStretch(3)
        hBoxLayout.addWidget(label);hBoxLayout.addStretch(3);hBoxLayout.addWidget(addButton)
        
        self.vBoxLayout.addLayout(hBoxLayout)
        
        self.table=TableWidgetPara(self); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setObjectName("contentTable")
        self.vBoxLayout.addWidget(self.table)
        
        self.table.setBorderRadius(8)
        self.table.setBorderVisible(True)

        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            str('Parameter Name'), str('File Extension'), str('Tuning Mode'),
            str('Lower Bound'), str('Upper Bound'), str('Position'), str('Operation')])
        
        
        hBoxLayout=QHBoxLayout()
        importButton=PrimaryPushButton("Import Existing File", self); importButton.setFixedSize(300, 40); 
        self.importButton=importButton; self.importButton.clicked.connect(self.importParaFile)
        setFont(importButton)
        
        clearButton=PrimaryPushButton("Clear All", self); clearButton.setFixedSize(300, 40)
        setFont(clearButton)
        self.clearButton=clearButton; self.clearButton.clicked.connect(self.clearAll)
        
        
        self.generateButton=PrimaryPushButton("Save Current Parameters", self)
        self.generateButton.setFixedSize(300, 40); 
        self.generateButton.clicked.connect(self.saveParFile)
        setFont(self.generateButton)
        
        hBoxLayout.setSpacing(30)
        hBoxLayout.addStretch(1);hBoxLayout.addWidget(self.importButton); 
        hBoxLayout.addWidget(self.generateButton); hBoxLayout.addWidget(self.clearButton)
        hBoxLayout.addStretch(1)
        
        self.vBoxLayout.addLayout(hBoxLayout)
        
        self.vBoxLayout.setAlignment(self.generateButton, Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        
        with path(GUI.qss, "para_table.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
                
        self.table.horizontalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; }}")
        self.table.verticalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; text-align: center; }}")
        self.table.verticalHeader().setFixedWidth(30)

    def addPara(self):
        
        modelInfos=Pro.modelInfos
        dialog=AddParaWidget(modelInfos['para_file'], [], parent=self)
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
            
            Pro.window=self.parent()
            Infos, res=Pro.importParaFromFile(path)
            
            if res:
                for paraInfo in Infos:
                    self.table.addRow(paraInfo)
                self.table.repaint()

    def saveParFile(self):
        
        infos=[]
        rows=self.table.rowCount()
        
        if rows>0:
            
            path, success= QFileDialog.getSaveFileName(self, "Save Parameter File", Pro.projectInfos["projectPath"], "Parameter File (*.par)")
            
            if not success:
                return
            
            for i in range(rows):
                paraName=self.table.item(i, 0).text()
                tuningMode=Pro.INT_MODE[self.table.cellWidget(i, 2).core.currentIndex()]
                lowerBound=str(self.table.cellWidget(i, 3).core.value())
                upperBound=str(self.table.cellWidget(i, 4).core.value())
                position=self.table.cellWidget(i, 5).core.text()
                infos.append([paraName, tuningMode, lowerBound, upperBound, position])

            Pro.saveParaFile(infos, path)
            self.saveSuccess(path)
        
        else:
        #     InfoBar.warning(
        #     title=f"Error",
        #     content=f"There is no parameter information to save.",
        #     position=InfoBarPosition.TOP_RIGHT,
        #     duration=2000,
        #     parent=self.parent()
        # )
            box=MessageBox(title="Warning", content=f"There is no parameter information to save.", parent=self.window())
            box.show()
            
    def saveSuccess(self, path): 
        InfoBar.success(
            title=f"Save Success",
            content=f"Parameter setting file have been save to {path}",
            position=InfoBarPosition.TOP_RIGHT,
            duration=2000,
            parent=self.parent()
        )
    
    def clearAll(self):
        
        self.table.setRowCount(0)
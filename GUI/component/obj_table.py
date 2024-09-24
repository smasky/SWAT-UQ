from qfluentwidgets import StrongBodyLabel, PrimaryToolButton, FluentIcon, PrimaryPushButton

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSizePolicy, 
                             QHeaderView, QFrame, QTableWidgetItem, QWidget)
from PyQt5.QtCore import Qt

import GUI.qss
import GUI.data
from importlib.resources import path

from .table_widget_pro import TableWidgetPro
from .add_pro_widget import AddProWidget

OBJ_TYPE={ "NSE":0, "RMSE":1, "PCC":2, "Pbias":3, "KGE":4 }
VARIABLE={ "Flow":0 }
class ObjTable(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        #########Data###########
        self.objs=[]
        self.default={'objID':1, 'seriesID':1,'reachID':1, "objType": 0, "variable": 0, "weight":1.0}
        #########################
        self.vBoxLayout=QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        
        label=StrongBodyLabel("Objective Information List")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        importButton=PrimaryPushButton("Import From File", self); importButton.setFixedHeight(24); 
        self.importButton=importButton
        
        addButton=PrimaryToolButton(FluentIcon.ADD, self); addButton.setFixedHeight(24); 
        self.addButton=addButton; addButton.clicked.connect(self.addPro)
        
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
            self.tr('Obj ID'), self.tr('Series ID'), self.tr('Reach ID'), 
            self.tr('Obj Type'), self.tr('Variable'), self.tr('Weight'), 
            self.tr('Operation')])
        
        self.generateButton=PrimaryPushButton("Generate Objective File (.obj)", self)
        self.generateButton.setMaximumWidth(500)
        self.vBoxLayout.addWidget(self.generateButton)
        
        self.vBoxLayout.setAlignment(self.generateButton, Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        
        with path(GUI.qss, "obj_table.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
                
    def addPro(self):
        
        dialog=AddProWidget(self.default, self)
        dialog.exec()
        
        data=dialog.data
        objID=int(dialog.line1.text())
        seriesID=int(dialog.line2.text())
        reachID=int(dialog.line3.text())
        objType=dialog.line4.currentText()
        variable=dialog.line5.currentText()
        weight=float(dialog.line6.text())

        obj={"objID":objID, "seriesID":seriesID, "reachID":reachID, "objType":OBJ_TYPE[objType], "variable":VARIABLE[variable], "weight":weight, "data": data}
        self.objs.append(obj)
        self.default['objID']=objID
        self.default['seriesID']=seriesID+1
        self.default['reachID']=reachID
        
        text=[objID, seriesID, reachID, objType, variable, weight]
        self.addRow(text)
        
    def addRow(self, text):
        
        row=self.table.rowCount()
        self.table.insertRow(row)
        
        item=QTableWidgetItem(f"{text[0]:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, item)
        
        item=QTableWidgetItem(f"{text[1]:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, item)
        
        item=QTableWidgetItem(f"{text[2]:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, item)
        
        item=QTableWidgetItem(text[3]); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, item)
        
        item=QTableWidgetItem(text[4]); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 4, item)
        
        item=QTableWidgetItem(f"{text[5]:f}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 5, item)
        self.table.setCellWidget(row, 6, self.addOperation(row))
    
    def changeRow(self, row, text):
        item=QTableWidgetItem(f"{text[0]:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, item)
        
        item=QTableWidgetItem(f"{text[1]:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, item)
        
        item=QTableWidgetItem(f"{text[2]:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, item)
        
        item=QTableWidgetItem(text[3]); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, item)
        
        item=QTableWidgetItem(text[4]); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 4, item)
        
        item=QTableWidgetItem(f"{text[5]:f}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 5, item)
        self.table.setCellWidget(row, 6, self.addOperation(row))

        self.addOperation(row)
        
    def addOperation(self, row):
        
        operation=QWidget()
        
        hBoxLayout=QHBoxLayout(operation)
        editButton=PrimaryToolButton(FluentIcon.EDIT)
        editButton.setFixedSize(24,24)
        editButton.setProperty('row', row)
        editButton.clicked.connect(self.editPro)
        hBoxLayout.addWidget(editButton)
        
        delButton=PrimaryToolButton(FluentIcon.DELETE)
        delButton.setFixedSize(24,24)
        delButton.setProperty('row', row)
        hBoxLayout.addWidget(delButton)
        
        return operation
    
    def editPro(self):
        
        btn=self.sender()
        row=btn.property('row')
        obj=self.objs[row]
        
        dialog=AddProWidget(obj, self)
        dialog.exec()
        
        data=dialog.data
        objID=int(dialog.line1.text())
        seriesID=int(dialog.line2.text())
        reachID=int(dialog.line3.text())
        objType=dialog.line4.currentText()
        variable=dialog.line5.currentText()
        weight=float(dialog.line6.text())
        
        obj={"objID":objID, "seriesID":seriesID, "reachID":reachID, "objType":OBJ_TYPE[objType], "variable":VARIABLE[variable], "weight":weight, "data": data}
        self.objs[row]=obj
        
        text=[objID, seriesID, reachID, objType, variable, weight]
        
        self.changeRow(row, text)
        
        
        
        
        
        
        
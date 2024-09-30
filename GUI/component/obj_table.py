from qfluentwidgets import StrongBodyLabel, PrimaryToolButton, FluentIcon, PrimaryPushButton

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSizePolicy, QFileDialog,
                             QHeaderView, QFrame, QTableWidgetItem, QWidget, QDialog)
from PyQt5.QtCore import Qt, QDate

import GUI.qss
import GUI.data
from importlib.resources import path

from .table_widget_pro import TableWidgetPro
from .add_pro_widget import AddProWidget
from ..project import Project as Pro
OBJTYPE={ "NSE":0, "RMSE":1, "PCC":2, "Pbias":3, "KGE":4 }
VARIABLE={ "Flow":0 }
class ObjTable(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        #########Data###########
        self.observedData={}
        self.objs=[]
        self.default={'objID':1, 'serID':1,'reachID':1, "objType": "NSE", "varType": "Flow", "weight":1.0}
        #########################
        self.vBoxLayout=QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        
        label=StrongBodyLabel("Objective Information List")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        importButton=PrimaryPushButton("Import From File", self); importButton.setFixedHeight(24); 
        self.importButton=importButton; self.importButton.clicked.connect(self.importProFile)
        
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
        
        self.generateButton=PrimaryPushButton("Save to Objective File (.obj)", self)
        self.generateButton.setMaximumWidth(500)
        self.generateButton.clicked.connect(self.saveProFile)
        self.vBoxLayout.addWidget(self.generateButton)
        
        self.vBoxLayout.setAlignment(self.generateButton, Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        
        #qss
        with path(GUI.qss, "obj_table.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        self.table.horizontalHeader().setStyleSheet("QHeaderView::section { color: black; }")
    
    def importProFile(self):
        
        path, success= QFileDialog.getOpenFileName(self, "Open Parameter File", Pro.projectPath, "Parameter File (*.pro)")
        
        if not success:
            return
        
        # objs={}
        infos=Pro.importProFromFile(path)
        for _, series in infos.items():
            for s in series:
                self.addRow(s)
        
    def saveProFile(self):
        
        path, success= QFileDialog.getSaveFileName(self, "Save Parameter File", Pro.projectPath, "Parameter File (*.pro)")
        
        if not success:
            return
        
        lines=[]
        
        numObj=len(self.objs)
        numSer=self.table.rowCount()
        lines.append(f"{numSer:d}     : Number of observed variables series\n")
        lines.append(f"{numObj:d}     : The numbers of objective functions\n")
        lines.append("\n")
        
        for i in range(numSer):
            obj=self.objs[i]
            
            objID=obj['objID']
            serID=obj['serID']
            reachID=obj['reachID']
            objType=obj['objType']
            varType=obj['varType']
            weight=obj['weight']
            observedDate=obj['observeData']
            
            lines.append(f"OBJ_{objID} : ID of objective function\n")
            lines.append(f"SER_{serID} : ID of series data\n")
            lines.append(f"REACH_{reachID} : ID of reach\n")
            lines.append(f"TYPE_{OBJTYPE[objType]} : Type of objective function\n")
            lines.append(f"VAR_{VARIABLE[varType]} : Type of variable\n")
            lines.append(f"{float(weight):.2f} : Weight of objective function\n")
            lines.append(f"{observedDate.shape[0]:d} : Number of data points for this variable as it follows below\n")
            lines.append("\n")
            
            for row in observedDate:
                lines.append(f"{int(row[0]):d} {int(row[1]):d} {float(row[2]):.4f}\n")
            lines.append("\n")
        
            Pro.saveProFile(path, lines)
        
    def addPro(self):
        
        dialog=AddProWidget(self.default, self)
        res=dialog.exec()
        
        if res:
            data=dialog.data            
            self.default['objID']=data['objID']
            self.default['seriesID']=data['serID']+1
            self.default['reachID']=data['reachID']
            
            self.addRow(data)
        
    def addRow(self, text):
        
        row=self.table.rowCount()
        self.table.insertRow(row)
        
        item=QTableWidgetItem(f"{text['objID']:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, item)
        
        item=QTableWidgetItem(f"{text['serID']:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 1, item)
        
        item=QTableWidgetItem(f"{text['reachID']:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, item)
        
        item=QTableWidgetItem(f"{Pro.INT_OBJTYPE[text['objType']]}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 3, item)
        
        item=QTableWidgetItem(f"{Pro.INT_VAR[text['varType']]}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 4, item)
        
        item=QTableWidgetItem(f"{text['weight']:.2f}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 5, item)
        self.table.setCellWidget(row, 6, self.addOperation(row))

        self.observedData[text['serID']]=text['data']
        
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
        res=dialog.exec()
        
        if res:
            data=dialog.data
            objID=int(data['objID'])
            seriesID=int(data['serID'])
            reachID=int(data['reachID'])
            objType=data['objType']
            variable=data['varType']
            weight=float(data['weight'])

            self.objs[row]=data
            
            self.default['objID']=objID
            self.default['seriesID']=seriesID+1
            self.default['reachID']=reachID
            
            text=[objID, seriesID, reachID, objType, variable, weight]
        
            self.changeRow(row, text)
        
        
        
        
        
        
        
from qfluentwidgets import SubtitleLabel,PrimaryToolButton, FluentIcon, PrimaryPushButton, InfoBarPosition

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QSizePolicy, QFileDialog,
                             QHeaderView, QFrame, QTableWidgetItem, QWidget, QDialog)
from PyQt5.QtCore import Qt

import GUI.qss
import GUI.data
from importlib.resources import path

from .table_widget_pro import TableWidgetPro
from .add_pro_widget import AddProWidget
from ..project import Project as Pro
from .info_bar import InfoBar_ as InfoBar
from .utility import setFont, Medium, MediumSize, Normal
from .message_box import MessageBox
OBJTYPE={ "NSE":0, "RMSE":1, "PCC":2, "Pbias":3, "KGE":4 }
VARIABLE={ "Flow":0 }
class ObjTable(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        #########Data###########
        self.objInfos=[]
        self.default={'objID':1, 'serID':1,'reachID':1, "objType": 0, "varType": 0, "weight":1.0}
        #########################
        self.vBoxLayout=QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        
        label=SubtitleLabel("Objective Information List")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        setFont(label, 25, Medium)
        
        addButton=PrimaryPushButton("Add", self); addButton.setFixedHeight(30); 
        self.addButton=addButton; addButton.clicked.connect(self.addPro)
        setFont(addButton, 18, Medium)
        
        hBoxLayout=QHBoxLayout(); hBoxLayout.addStretch(3)
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
        
        importButton=PrimaryPushButton("Import Existing File", self); importButton.setFixedSize(300, 40)
        setFont(importButton, 18, Medium)
        self.importButton=importButton; self.importButton.clicked.connect(self.importObjFile)
        
        self.generateButton=PrimaryPushButton("Save Current File", self)
        self.generateButton.setFixedSize(300, 40)
        self.generateButton.clicked.connect(self.saveObjFile)
        setFont(self.generateButton, 18, Medium)
        
        self.clearButton=PrimaryPushButton("Clear All", self); self.clearButton.setFixedSize(300, 40)
        setFont(self.clearButton)
        
        hBoxLayout=QHBoxLayout(); hBoxLayout.addStretch(1);hBoxLayout.addWidget(self.importButton); hBoxLayout.setSpacing(30)
        hBoxLayout.addWidget(self.generateButton); hBoxLayout.addWidget(self.clearButton); hBoxLayout.addStretch(1)
        self.vBoxLayout.addLayout(hBoxLayout)
        
        self.vBoxLayout.setAlignment(self.generateButton, Qt.AlignCenter)
        self.vBoxLayout.setContentsMargins(10, 10, 10, 10)
        
        #qss
        with path(GUI.qss, "obj_table.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        
        self.table.horizontalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; }}")
        self.table.verticalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; text-align: center; }}")
        self.table.verticalHeader().setFixedWidth(30)
        
    def importObjFile(self):
        
        path, success= QFileDialog.getOpenFileName(self, "Open Parameter File", Pro.projectInfos['projectPath'], "Parameter File (*.obj)")
        
        if not success:
            return
        
        infos, res=Pro.importObjFromFile(path)
        if res:
            for _, series in infos.items():
                for s in series:
                    self.addRow(s)
                    self.objInfos.append(s)

            self.default['serID']=self.default['serID']+len(series)
        
    def saveObjFile(self):
        
        keys=['reachID', 'objType', 'varType', 'weight']
        
        if len(self.objInfos)>0:
            temp={}
            sign=True
            signID=None
            for series in self.objInfos:
                
                serID=series['serID']
                
                if serID not in temp:
                    temp[serID]=series
                else:
                    for key in keys:
                        if temp[serID][key] != series[key]:
                            sign=False
                            signID=serID
                            break
                
                if not sign:
                    break
            
            if not sign:
                
                box=MessageBox(title="Error", content=f"The series ID {signID} have different attributes, please check.", parent=self.window())
                box.show()
                
            else:
            
                path, success= QFileDialog.getSaveFileName(self, "Save Parameter File", Pro.projectInfos['projectPath'], "Objective File (*.obj)")
                if not success:
                    return
                
                Pro.saveObjFile(path, self.objInfos)
            
        else:
            
            box=MessageBox(title="Warning", content=f"There is no objective information to save.", parent=self.window())
            box.show()
        
    def addPro(self):
        
        dialog=AddProWidget(self.default, self)
        res=dialog.exec()
        
        if res:
            data=dialog.data            
            self.default['objID']=data['objID']
            self.default['seriesID']=data['serID']+1
            self.default['reachID']=data['reachID']
            self.addRow(data)
            
            self.objInfos.append(data)
        
    def addRow(self, text):
        
        row=self.table.rowCount()
        self.table.insertRow(row)
        
        item=QTableWidgetItem(f"{text['objID']:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        setFont(item, MediumSize, Normal)
        self.table.setItem(row, 0, item)
        
        item=QTableWidgetItem(f"{text['serID']:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        setFont(item, MediumSize, Normal)
        self.table.setItem(row, 1, item)
        
        item=QTableWidgetItem(f"{text['reachID']:d}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        setFont(item, MediumSize, Normal)
        self.table.setItem(row, 2, item)
        
        item=QTableWidgetItem(f"{Pro.INT_OBJTYPE[text['objType']]}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        setFont(item, MediumSize, Normal)
        self.table.setItem(row, 3, item)
        
        item=QTableWidgetItem(f"{Pro.INT_VAR[text['varType']]}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        setFont(item, MediumSize, Normal)
        self.table.setItem(row, 4, item)
        
        item=QTableWidgetItem(f"{text['weight']:.2f}"); item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(item.flags() & ~Qt.ItemIsEditable)
        setFont(item, MediumSize, Normal)
        self.table.setItem(row, 5, item)
        self.table.setCellWidget(row, 6, self.addOperation(row))
        
    def changeRow(self, row, text):
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

        self.addOperation(row)
        
    def addOperation(self, row):
        
        operation=QWidget()
        
        hBoxLayout=QHBoxLayout(operation)

        editButton=PrimaryToolButton(FluentIcon.EDIT)
        editButton.setFixedSize(24,24)
        editButton.setProperty('row', row)
        editButton.clicked.connect(self.editPro)
        hBoxLayout.addWidget(editButton, Qt.AlignmentFlag.AlignCenter)
        
        delButton=PrimaryToolButton(FluentIcon.DELETE)
        delButton.setFixedSize(24,24)
        delButton.setProperty('row', row)
        hBoxLayout.addWidget(delButton, Qt.AlignmentFlag.AlignCenter)
        operation.delBtn=delButton
        delButton.clicked.connect(self.delete_row)
        
        operation.setFixedHeight(30)
        hBoxLayout.setContentsMargins(0,0,0,0)
        return operation
    
    def editPro(self):
        
        btn=self.sender()
        row=btn.property('row')
        obj=self.objInfos[row]
        
        dialog=AddProWidget(obj, self)
        res=dialog.exec()
        
        if res:
            data=dialog.data
        
            self.objInfos[row]=data
            
            self.default['objID']=data['objID']
            self.default['seriesID']=data['serID']+1
            self.default['reachID']=data['reachID']
            
            self.changeRow(row, data)
            
    def delete_row(self):
        
        button = self.sender() 
        row = button.property('row') 
        
        if row is not None:
    
            self.table.removeRow(row)
            del self.objInfos[row]
            self.update_button_row_properties()

    def update_button_row_properties(self):
        
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 6)  
            if widget:
                widget.delBtn.setProperty('row', row)
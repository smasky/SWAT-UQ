from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, PushButton, PrimaryPushButton, PushButton,
                            SpinBox, ComboBox, DoubleSpinBox, TableWidget)

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt

from .double_tree_widget import DoubleTreeWidget

import numpy as np

class AddProWidget(FramelessDialog):
    
    def __init__(self, default, parent=None):
        
        super().__init__(parent)
        self.vBoxLayout=QVBoxLayout(self)
        label=BodyLabel(self.tr("Problem Define"), self)
        self.vBoxLayout.addWidget(label)
        
        # Content
        self.contentWidget=QWidget(self)
        self.vBoxLayout.addWidget(self.contentWidget)
        hBoxLayout=QHBoxLayout(self.contentWidget)
        
        vBoxLayout=QVBoxLayout()
        hBoxLayout.addLayout(vBoxLayout)
        
        #initial data table
        self.initDataWidget(hBoxLayout)
        

        h1=QHBoxLayout()
        label1=BodyLabel(self.tr("Objective ID"), self); line1=SpinBox(self)
        self.line1=line1; self.line1.setValue(int(default['objID']))
        h1.addWidget(label1); h1.addWidget(line1)
        vBoxLayout.addLayout(h1)
        
        h2=QHBoxLayout()
        label2=BodyLabel(self.tr("Series ID"), self); line2=SpinBox(self)
        self.line2=line2; self.line2.setValue(int(default['seriesID']))
        h2.addWidget(label2); h2.addWidget(line2)
        vBoxLayout.addLayout(h2)
        
        h3=QHBoxLayout()
        label3=BodyLabel(self.tr("Reach ID"), self); line3=SpinBox(self)
        self.line3=line3; self.line3.setValue(int(default['reachID']))
        h3.addWidget(label3); h3.addWidget(line3)
        vBoxLayout.addLayout(h3)
        
        h4=QHBoxLayout()
        label4=BodyLabel(self.tr("Obj Type"), self); line4=ComboBox(self)
        self.line4=line4; self.line4.setCurrentIndex(int(default['objType']))
        line4.addItems(["NSE", "RMSE", "PCC", "Pbias", "KGE"])
        h4.addWidget(label4); h4.addWidget(line4)
        vBoxLayout.addLayout(h4)
        
        h5=QHBoxLayout()
        label5=BodyLabel(self.tr("Variable"), self); line5=ComboBox(self)
        self.line5=line5; self.line5.setCurrentIndex(int(default['variable']))
        line5.addItems(["Flow", "Tol_N", "Tol_P"])
        h5.addWidget(label5); h5.addWidget(line5)
        vBoxLayout.addLayout(h5)
        
        h6=QHBoxLayout()
        label6=BodyLabel(self.tr("Weight"), self);  line6=DoubleSpinBox(self)
        self.line6=line6; self.line6.setValue(float(default['weight']))
        h6.addWidget(label6); h6.addWidget(line6)
        vBoxLayout.addLayout(h6)
        
        vBoxLayout.addStretch(1)
        
        if 'data' in default:
            self.data=default['data']
            self.inputData()
        
        self.buttonGroup=QWidget(self)
        self.vBoxLayout.addWidget(self.buttonGroup)
        self.yesButton=PrimaryPushButton(self.tr("Confirm"), self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
        self.cancelButton=PushButton(self.tr("Cancel"), self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
        self.buttonLayout=QHBoxLayout(self.buttonGroup)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.cancelButton)
        
        self.setFixedSize(800, 400)
        self.titleBar.hide()
    
    def initDataWidget(self, layout):
        
        vBoxLayout=QVBoxLayout()
        self.dataTable=TableWidget(self); 
        self.dataTable.setBorderRadius(8); self.dataTable.setBorderVisible(True)
        self.dataTable.setColumnCount(3)
        self.dataTable.setHorizontalHeaderLabels([self.tr('Year'), 
                                                  self.tr('Index'), self.tr('Value')])
        
        vBoxLayout.addWidget(self.dataTable)
        
        hBoxLayout=QHBoxLayout()
        importButton=PrimaryPushButton(self.tr("Import Observe Data"))
        importButton.setMaximumWidth(250); importButton.clicked.connect(self.importData)
        hBoxLayout.addWidget(importButton)
        
        clearButton=PushButton(self.tr("Clear Data"))
        clearButton.setMaximumWidth(250)
        hBoxLayout.addWidget(clearButton)
        
        vBoxLayout.addLayout(hBoxLayout)
        
        layout.addLayout(vBoxLayout)
    
    def importData(self):
        
        file_path, _=QFileDialog.getOpenFileName(self, self.tr("Open File"), "", self.tr("Text Files (*.txt)"))
        data=np.loadtxt(file_path)
        self.data=data
        self.inputData()
       
    def inputData(self):
        data=self.data
        m, _=data.shape
        for i in range(m):
            self.dataTable.insertRow(i)
            item=QTableWidgetItem(f"{int(data[i, 0]):d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dataTable.setItem(i, 0, item)
            item=QTableWidgetItem(f"{int(data[i, 1]):d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dataTable.setItem(i, 1, item)
            item=QTableWidgetItem(f"{data[i, 2]:f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dataTable.setItem(i, 2, item) 
    
    
    def confirm_clicked(self):
                        
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()
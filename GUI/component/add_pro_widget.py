from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, PushButton, PrimaryPushButton, PushButton,
                            SpinBox, ComboBox, DoubleSpinBox, TableWidget, DatePicker, InfoBar, 
                            InfoBarIcon, InfoBarPosition)

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate
from ..project import Project as Pro

import numpy as np

class AddProWidget(FramelessDialog):
    
    def __init__(self, default, parent=None):
        
        super().__init__(parent)
        self.vBoxLayout=QVBoxLayout(self)
        label=BodyLabel(self.tr("Problem Define"), self)
        self.vBoxLayout.addWidget(label)
        
        self.contentWidget=QWidget(self)
        self.vBoxLayout.addWidget(self.contentWidget)
        hBoxLayout=QHBoxLayout(self.contentWidget)
        
        vBoxLayout=QVBoxLayout()
        hBoxLayout.addLayout(vBoxLayout)
        
        self.initDataWidget(hBoxLayout)
        
        OFFSET=15
        h1=QHBoxLayout()
        label1=BodyLabel(str("Objective ID:").rjust(OFFSET-1), self); line1=SpinBox(self)
        self.line1=line1; self.line1.setValue(int(default['objID']));line1.setMinimumWidth(150)
        h1.addWidget(label1); h1.addWidget(line1); h1.addStretch(1)
        vBoxLayout.addLayout(h1)
        
        h2=QHBoxLayout()
        label2=BodyLabel(str("Series ID:").rjust(OFFSET+1), self); line2=SpinBox(self)
        self.line2=line2; self.line2.setValue(int(default['seriesID']));line2.setMinimumWidth(150)
        h2.addWidget(label2); h2.addWidget(line2); h2.addStretch(1)
        vBoxLayout.addLayout(h2)
        
        h3=QHBoxLayout()
        label3=BodyLabel(str("Reach ID:").rjust(OFFSET), self); line3=SpinBox(self)
        self.line3=line3; self.line3.setValue(int(default['reachID']));line3.setMinimumWidth(150)
        h3.addWidget(label3); h3.addWidget(line3); h3.addStretch(1)
        vBoxLayout.addLayout(h3)
        
        h4=QHBoxLayout()
        label4=BodyLabel(str("Obj Type:").rjust(OFFSET), self); line4=ComboBox(self)
        self.line4=line4; self.line4.setCurrentIndex(int(default['objType']))
        line4.addItems(["NSE", "RMSE", "PCC", "Pbias", "KGE"]); line4.setMinimumWidth(150)
        h4.addWidget(label4); h4.addWidget(line4); h4.addStretch(1)
        vBoxLayout.addLayout(h4)
        
        h5=QHBoxLayout()
        label5=BodyLabel(str("Variable:").rjust(OFFSET+1), self); line5=ComboBox(self)
        self.line5=line5; self.line5.setCurrentIndex(int(default['variable']))
        line5.addItems(["Flow", "Tol_N", "Tol_P"]); line5.setMinimumWidth(150)
        h5.addWidget(label5); h5.addWidget(line5); h5.addStretch(1)
        vBoxLayout.addLayout(h5)
        
        h6=QHBoxLayout()
        label6=BodyLabel(str("Weight:").rjust(OFFSET), self); line6=DoubleSpinBox(self)
        self.line6=line6; self.line6.setValue(float(default['weight']));line6.setMinimumWidth(150)
        h6.addWidget(label6); h6.addWidget(line6); h6.addStretch(1)
        vBoxLayout.addLayout(h6)
        
        modelInfos=Pro.modelInfos
        begin_date=modelInfos['begin_record']
        end_date=modelInfos['end_date']
        
        h7=QHBoxLayout()
        label7=BodyLabel(str("Start Date:").rjust(OFFSET-1), self); line7=DatePicker(self, isMonthTight=True)
        self.line7=line7; time=QDate(begin_date.year, begin_date.month, begin_date.day); line7.setDate(time)
        h7.addWidget(label7); h7.addWidget(line7); h7.addStretch(1)
        vBoxLayout.addLayout(h7)
        
        h8=QHBoxLayout()
        label8=BodyLabel(str("End Date:").rjust(OFFSET-1), self); line8=DatePicker(self, isMonthTight=True)
        self.line8=line8; time=QDate(end_date.year, end_date.month, end_date.day); line8.setDate(time)
        h8.addWidget(label8); h8.addWidget(line8); h8.addStretch(1)
        vBoxLayout.addLayout(h8)
            
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
        num=self.calDeltaNum(self.line7.date, self.line8.date)
        n, _=data.shape

        if n!=num:
            infoBar = InfoBar(
                icon=InfoBarIcon.WARNING,
                title=self.tr('Warning'),
                content=f"The project need {num} sets of data for the project, but only {n} have been provided. Please check the data.",
                orient=Qt.Vertical,
                isClosable=True,
                duration=-1,
                position=InfoBarPosition.TOP_RIGHT,
                parent=self
            )
            infoBar.show()
            
        else:
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
    
    def calDeltaNum(self, begin, end):
        
        IPRINT=Pro.modelInfos["print_flag"]
        
        if IPRINT==1:
            return begin.daysTo(end)+1
        else:
            start_year = begin.year()
            start_month = begin.month()
            
            end_year = end.year()
            end_month = end.month()
            
            # 计算年份差和月份差
            years_diff = end_year - start_year
            months_diff = end_month - start_month
            
            # 总月数 = 年份差 * 12 + 月份差
            total_months = years_diff * 12 + months_diff+1
            
            return total_months
    
    def confirm_clicked(self):
                        
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()
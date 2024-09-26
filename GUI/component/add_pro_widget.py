from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, PushButton, PrimaryPushButton, PushButton,
                            SpinBox, ComboBox, DoubleSpinBox, TableWidget, DatePicker, InfoBar, 
                            InfoBarIcon, InfoBarPosition, LineEdit)

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTableWidgetItem
from PyQt5.QtCore import Qt, QDate
from ..project import Project as Pro

import numpy as np

OBJTYPE={"NSE":0, "RMSE":1, "PCC":2, "Pbias":3, "KGE":4}
VARTYPE={"Flow":0, "Tol_N":1, "Tol_P":2}

class AddProWidget(FramelessDialog):
    data={}
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
        label1=BodyLabel(str("Objective ID:").rjust(OFFSET-1), self); objIDEdit=SpinBox(self)
        self.objIDEdit=objIDEdit; self.objIDEdit.setValue(int(default['objID']));objIDEdit.setMinimumWidth(150)
        h1.addWidget(label1); h1.addWidget(objIDEdit); h1.addStretch(1)
        vBoxLayout.addLayout(h1)
        
        h2=QHBoxLayout()
        label2=BodyLabel(str("Series ID:").rjust(OFFSET+1), self); serIDEdit=SpinBox(self)
        self.serIDEdit=serIDEdit; self.serIDEdit.setValue(int(default['serID']));serIDEdit.setMinimumWidth(150)
        h2.addWidget(label2); h2.addWidget(serIDEdit); h2.addStretch(1)
        vBoxLayout.addLayout(h2)
        
        h3=QHBoxLayout()
        label3=BodyLabel(str("Reach ID:").rjust(OFFSET), self); reachIDEdit=SpinBox(self)
        self.reachIDEdit=reachIDEdit; self.reachIDEdit.setValue(int(default['reachID']));reachIDEdit.setMinimumWidth(150)
        h3.addWidget(label3); h3.addWidget(reachIDEdit); h3.addStretch(1)
        vBoxLayout.addLayout(h3)
        
        h4=QHBoxLayout()
        label4=BodyLabel(str("Obj Type:").rjust(OFFSET), self); objTypeEdit=ComboBox(self)
        self.objTypeEdit=objTypeEdit; self.objTypeEdit.setCurrentIndex(OBJTYPE[default['objType']])
        objTypeEdit.addItems(["NSE", "RMSE", "PCC", "Pbias", "KGE"]); objTypeEdit.setMinimumWidth(150)
        h4.addWidget(label4); h4.addWidget(objTypeEdit); h4.addStretch(1)
        vBoxLayout.addLayout(h4)
        
        h5=QHBoxLayout()
        label5=BodyLabel(str("Variable:").rjust(OFFSET+1), self); varEdit=ComboBox(self)
        self.varEdit=varEdit; self.varEdit.setCurrentIndex(VARTYPE[default['varType']])
        varEdit.addItems(["Flow", "Tol_N", "Tol_P"]); varEdit.setMinimumWidth(150)
        h5.addWidget(label5); h5.addWidget(varEdit); h5.addStretch(1)
        vBoxLayout.addLayout(h5)
        
        h6=QHBoxLayout()
        label6=BodyLabel(str("Weight:").rjust(OFFSET), self); weightEdit=DoubleSpinBox(self)
        self.weightEdit=weightEdit; self.weightEdit.setValue(float(default['weight']));weightEdit.setMinimumWidth(150)
        h6.addWidget(label6); h6.addWidget(weightEdit); h6.addStretch(1)
        vBoxLayout.addLayout(h6)
        ##############################################
        # modelInfos=Pro.modelInfos
        # begin_date=modelInfos['begin_record']
        # end_date=modelInfos['end_date']
        ###########################
        
        h7=QHBoxLayout()
        label7=BodyLabel(str("Start Date:").rjust(OFFSET-1), self); 
        beginDataEdit=DatePicker(self, isMonthTight=True)
        self.beginDataEdit=beginDataEdit
        if 'beginDate' not in default:
            beginDate=Pro.modelInfos['recordDate']
            time=QDate(beginDate.year, beginDate.month, beginDate.day)
        else:
            beginDate=default['beginDate']
            time=QDate(beginDate.year(), beginDate.month(), beginDate.day())
        
        beginDataEdit.setDate(time)
        beginDataEdit.dateChanged.connect(self.reCalNum)
        h7.addWidget(label7); h7.addWidget(beginDataEdit); h7.addStretch(1)
        vBoxLayout.addLayout(h7)
        #################################
        h8=QHBoxLayout()
        label8=BodyLabel(str("End Date:").rjust(OFFSET-1), self); 
        endDataEdit=DatePicker(self, isMonthTight=True)
        self.endDataEdit=endDataEdit
        if 'endDate' not in default:
            endDate=Pro.modelInfos['endDate']
            time=QDate(endDate.year, endDate.month, endDate.day)
        else:
            endDate=default['endDate']
            time=QDate(endDate.year(), endDate.month(), endDate.day())
        endDataEdit.setDate(time)
        endDataEdit.dateChanged.connect(self.reCalNum)
        h8.addWidget(label8); h8.addWidget(endDataEdit); h8.addStretch(1)
        vBoxLayout.addLayout(h8)
        ########################################
        h9=QHBoxLayout()
        label9=BodyLabel(str("Number of Observe Data to Load:").rjust(OFFSET-1), self)
        self.numDisplay=LineEdit(self); self.numDisplay.setEnabled(False)
        self.numDisplay.setText(str(self.calDeltaNum(self.beginDataEdit.date, self.endDataEdit.date)))
        h9.addWidget(label9); h9.addWidget(self.numDisplay); h9.addStretch(1)
        
        vBoxLayout.addLayout(h9)
        ####################################
        
        vBoxLayout.addStretch(1)
        
        if 'observeData' in default:
            data=default['observeData']
            self.inputData(data)
        
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
        num=self.calDeltaNum(self.beginDataEdit.date, self.endDataEdit.date)
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
            self.inputData(data)
       
    def inputData(self, data):
        m, _=data.shape
        for i in range(m):
            self.dataTable.insertRow(i)
            item=QTableWidgetItem(f"{int(data[i, 0]):d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dataTable.setItem(i, 0, item)
            item=QTableWidgetItem(f"{int(data[i, 1]):d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dataTable.setItem(i, 1, item)
            item=QTableWidgetItem(f"{float(data[i, 2]):f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dataTable.setItem(i, 2, item) 
        self.observeData=data
        
    def calDeltaNum(self, begin, end):
        
        IPRINT=Pro.modelInfos["print_flag"]
        
        if IPRINT==1:
            return begin.daysTo(end)+1
        else:
            start_year = begin.year()
            start_month = begin.month()
            
            end_year = end.year()
            end_month = end.month()
            
            years_diff = end_year - start_year
            months_diff = end_month - start_month
            
            total_months = years_diff * 12 + months_diff+1
            
            return total_months
    
    def reCalNum(self):
        
        num=self.calDeltaNum(self.beginDataEdit.date, self.endDataEdit.date)
        
        self.numDisplay.setText(str(num))
    
    def confirm_clicked(self):
        
        objID=self.objIDEdit.text()
        serID=self.serIDEdit.text()
        reachID=self.reachIDEdit.text()
        objType=self.objTypeEdit.currentText()
        varType=self.varEdit.currentText()
        weight=self.weightEdit.text()
        beginDate=self.beginDataEdit.date
        endDate=self.endDataEdit.date
        observeData=self.getObserveData()
        
        self.data['objID']=objID
        self.data['serID']=serID
        self.data['reachID']=reachID
        self.data['objType']=objType
        self.data['varType']=varType
        self.data['weight']=weight
        self.data['beginDate']=beginDate
        self.data['endDate']=endDate
        self.data['observeData']=observeData
        self.accept()
        
    def getObserveData(self):
        rows=self.dataTable.rowCount()
        data=[]
        for i in range(rows):
            data.append([int(self.dataTable.item(i, 0).text()),int(self.dataTable.item(i, 1).text()), float(self.dataTable.item(i, 2).text())])

        return np.array(data)
        
    def cancel_clicked(self):
        
        self.reject()
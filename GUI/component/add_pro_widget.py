from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, PushButton, PrimaryPushButton, PushButton,FluentStyleSheet, getStyleSheet,
                            SpinBox, ComboBox, DoubleSpinBox, TableWidget, DatePicker, InfoBar, 
                            InfoBarIcon, InfoBarPosition, LineEdit)

from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QWidget,  QFileDialog,
                             QTableWidgetItem, QFormLayout, QSizePolicy)
from PyQt5.QtCore import Qt, QDate
from ..project import Project as Pro
from .combox_ import ComboBox_
from .utility import setFont, Medium, MediumSize, substitute, Normal
import numpy as np
class AddProWidget(FramelessDialog):
    
    data={}
    
    def __init__(self, default, parent=None):
        
        super().__init__(parent)
        self.vBoxLayout=QVBoxLayout(self)
        
        ################Problem Define##################
        label=BodyLabel(str("Problem Define"), self)
        setFont(label, 20)
        self.vBoxLayout.addWidget(label)
        
        self.contentWidget=QWidget(self)
        self.vBoxLayout.addWidget(self.contentWidget)
        
        hBoxLayout=QHBoxLayout(self.contentWidget)
        
        formLayout=QFormLayout()
        hBoxLayout.addLayout(formLayout, 3)
        self.initDataWidget(hBoxLayout)
        
        formLayout.setLabelAlignment(Qt.AlignRight)
        
        self.serIDEdit=SpinBox(self)
        self.serIDEdit.setValue(int(default['serID']))
        self.serIDEdit.setMaximumWidth(200)
        setFont(self.serIDEdit, MediumSize, Normal)
        label=BodyLabel("Series ID:"); setFont(label)
        formLayout.addRow(label, self.serIDEdit)
        
        self.objIDEdit=SpinBox(self)
        self.objIDEdit.setValue(int(default['objID']))
        self.objIDEdit.setMaximumWidth(200)
        setFont(self.objIDEdit, MediumSize, Normal)
        
        label=BodyLabel("Objective ID:"); setFont(label)
        formLayout.addRow(label, self.objIDEdit)
        
        self.reachIDEdit=SpinBox(self)
        self.reachIDEdit.setValue(int(default['reachID']))
        self.reachIDEdit.setMaximumWidth(200)
        setFont(self.reachIDEdit, MediumSize, Normal)
        
        label=BodyLabel("Reach ID:"); setFont(label)
        formLayout.addRow(label, self.reachIDEdit)
        
        self.objTypeEdit=ComboBox_(self)
        self.objTypeEdit.addItems(list(Pro.OBJTYPE_INT.keys()))
        self.objTypeEdit.setCurrentIndex(default['objType'])
        self.objTypeEdit.setMaximumWidth(200)
        setFont(self.objTypeEdit, MediumSize, Normal)
        label=BodyLabel("Objective Type:"); setFont(label)
        formLayout.addRow(label, self.objTypeEdit)
        
        self.varEdit=ComboBox_(self)
        self.varEdit.addItems(list(Pro.VAR_INT.keys()))
        self.varEdit.setCurrentIndex(default['varType'])
        self.varEdit.setMaximumWidth(200)
        setFont(self.varEdit, MediumSize, Normal)
        
        label=BodyLabel("Variable:"); setFont(label)
        formLayout.addRow(label, self.varEdit)
        
        self.weightEdit=DoubleSpinBox(self)
        self.weightEdit.setValue(float(default['weight']))
        self.weightEdit.setSingleStep(0.1)
        self.weightEdit.setRange(0.0, 10.0)
        self.weightEdit.setMaximumWidth(200)
        setFont(self.weightEdit, MediumSize, Normal)
        label=BodyLabel("Weight:"); setFont(label)
        formLayout.addRow(label, self.weightEdit)
        
        lbDate=Pro.modelInfos['beginRecord']
        ubDate=Pro.modelInfos['endDate']
        lbQDate=QDate(lbDate.year, lbDate.month, lbDate.day)
        ubQDate=QDate(ubDate.year, ubDate.month, ubDate.day)
        
        if 'observeData' in default:
            beginDate, endDate = Pro.calDate(default['observeData'])
            beginQDate=QDate(beginDate.year, beginDate.month, beginDate.day)
            endQDate=QDate(endDate.year, endDate.month, endDate.day)
        else:
            beginQDate=lbQDate
            endQDate=ubQDate
        
        self.beginDataEdit=DatePicker_(self, isMonthTight=True)
        self.beginDataEdit.setDate(beginQDate)
        self.beginDataEdit.dateChanged.connect(self.reCalNum)
        self.beginDataEdit.setMaximumWidth(100)
        label=BodyLabel("Start Date:"); setFont(label, MediumSize, Medium)
        formLayout.addRow(label, self.beginDataEdit)
        
        self.endDataEdit=DatePicker_(self, isMonthTight=True)
        self.endDataEdit.setDate(endQDate)
        self.endDataEdit.dateChanged.connect(self.reCalNum)
        self.endDataEdit.setMaximumWidth(100)
        label=BodyLabel("End Date:"); setFont(label, MediumSize, Medium)
        formLayout.addRow(label, self.endDataEdit)
        
        self.numDisplay=LineEdit(self); self.numDisplay.setEnabled(False)
        self.numDisplay.setText(str(self.calDeltaNum(self.beginDataEdit.date, self.endDataEdit.date)))
        self.numDisplay.setMaximumWidth(100)
        setFont(self.numDisplay)
        label=BodyLabel("Size of Data required:"); setFont(label, MediumSize, Medium)
        formLayout.addRow(label, self.numDisplay)
        
        if 'observeData' in default:
            data=default['observeData']
            self.inputData(data)
        
        self.buttonGroup=QWidget(self)
        self.vBoxLayout.addWidget(self.buttonGroup)
        self.yesButton=PrimaryPushButton("Confirm", self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
        setFont(self.yesButton)
        self.cancelButton=PushButton("Cancel", self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
        setFont(self.cancelButton)
        self.buttonLayout=QHBoxLayout(self.buttonGroup)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.cancelButton)
        
        self.setFixedSize(1200, 600)
        self.titleBar.hide()
    
    def createRightLabel(self, text):
        
        widget=QWidget()
        hLayout=QHBoxLayout(widget)
        hLayout.addStretch(1)
        hLayout.addWidget(BodyLabel(text))

        return widget
    
    def initDataWidget(self, layout):
        
        vBoxLayout=QVBoxLayout()
        self.dataTable=TableWidget_(self); 
        self.dataTable.setBorderRadius(8); self.dataTable.setBorderVisible(True)
        self.dataTable.setColumnCount(5)
        self.dataTable.setHorizontalHeaderLabels([self.tr('Index'), self.tr('Year'), self.tr('Month'), 
                                                  self.tr('Day'), self.tr('Value')])
        
        self.dataTable.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.dataTable.horizontalHeader().setVisible(True)
        self.dataTable.horizontalHeader().setStyleSheet("QHeaderView::section { color: black; }")
        self.dataTable.verticalHeader().setVisible(True)
        self.dataTable.setRowCount(1)
        
        self.dataTable.horizontalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; }}")
        self.dataTable.verticalHeader().setStyleSheet(f"QHeaderView::section {{ color: black; font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; text-align: center; }}")
        self.dataTable.verticalHeader().setFixedWidth(30)
        
        vBoxLayout.addWidget(self.dataTable)
        
        hBoxLayout=QHBoxLayout()
        importButton=PrimaryPushButton(self.tr("Import Observe Data"))
        importButton.setMaximumWidth(250); importButton.clicked.connect(self.importData)
        setFont(importButton)
        hBoxLayout.addWidget(importButton)
        
        clearButton=PushButton(self.tr("Clear Data"))
        clearButton.setMaximumWidth(250)
        clearButton.clicked.connect(self.clearAndResetTable)
        setFont(clearButton)
        hBoxLayout.addWidget(clearButton)
        
        for column in range(0, self.dataTable.columnCount()):
            self.dataTable.setColumnWidth(column, 110)  # 默认宽度
            self.dataTable.horizontalHeader().setMinimumSectionSize(50)  # 最小宽度
            self.dataTable.horizontalHeader().setMaximumSectionSize(110)  # 最大宽度

        vBoxLayout.addLayout(hBoxLayout)
        
        layout.addLayout(vBoxLayout, 4)
    
    def clearAndResetTable(self):
        
        self.dataTable.clearContents()
       
        self.dataTable.setRowCount(1)
    
    def importData(self):
        
        file_path, _=QFileDialog.getOpenFileName(self, self.tr("Open File"), "", self.tr("Text Files (*.txt)"))
        data=np.loadtxt(file_path)
        num=self.calDeltaNum(self.beginDataEdit.date, self.endDataEdit.date)
        n = data.shape[0]

        observeData=[]

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
            for i in range(n):
                index, year, month, day=Pro.calDateIndex(self.beginDataEdit.date, i)
                observeData.append([int(index), int(year), int(month), int(day), float(data[i])])
                
            for i in range(self.dataTable.rowCount()):
                self.dataTable.removeRow(0)
            self.inputData(observeData)

    def inputData(self, data):
        
        m = len(data)
        
        n = self.dataTable.rowCount()
        
        for i in range(m):
            index, year, month, day, value = data[i]
            
            if i>=n:  
                self.dataTable.insertRow(i)
                
            item=QTableWidgetItem(f"{index:d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            setFont(item, MediumSize, Normal)
            self.dataTable.setItem(i, 0, item)
            item=QTableWidgetItem(f"{year:d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.dataTable.setItem(i, 1, item)
            setFont(item, MediumSize, Normal)
            item=QTableWidgetItem(f"{month:d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.dataTable.setItem(i, 2, item)
            setFont(item, MediumSize, Normal)
            item=QTableWidgetItem(f"{day:d}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.dataTable.setItem(i, 3, item)
            setFont(item, MediumSize, Normal)
            item=QTableWidgetItem(f"{value:.2f}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.dataTable.setItem(i, 4, item)
            setFont(item, MediumSize, Normal)
             
        self.observeData=data
        
    def calDeltaNum(self, begin, end):
        
        IPRINT=Pro.modelInfos["printFlag"]
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
        observeData=self.getObserveData()
        
        self.data['objID']=int(objID)
        self.data['serID']=int(serID)
        self.data['reachID']=int(reachID)
        self.data['objType']=Pro.OBJTYPE_INT[objType]
        self.data['varType']=Pro.VAR_INT[varType]
        self.data['weight']=float(weight)
        self.data['observeData']=observeData
        self.accept()
        
    def getObserveData(self):
        
        rows=self.dataTable.rowCount()
        data=[]
        
        for i in range(rows):
            data.append((int(self.dataTable.item(i, 0).text()), int(self.dataTable.item(i, 1).text()), int(self.dataTable.item(i, 2).text()), int(self.dataTable.item(i, 3).text()),float(self.dataTable.item(i, 4).text())))

        return data
        
    def cancel_clicked(self):
        
        self.reject()
        
class DatePicker_(DatePicker):
    MM_DD_YYYY = 0
    YYYY_MM_DD = 1
    def __init__(self, parent=None, format=MM_DD_YYYY, isMonthTight=True):
        super().__init__(parent, format, isMonthTight)
        
        qss=getStyleSheet(FluentStyleSheet.TIME_PICKER)
        replace={'ItemMaskWidget': {'font': f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'"},
                 'PickerBase' : {'font': f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'"},
                 'pickerButton' : {'font': f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'"}
                 }
        qss=substitute(qss, replace)
        
        self.setStyleSheet(qss)
        

class TableWidget_(TableWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        qss=getStyleSheet(FluentStyleSheet.TABLE_VIEW)
        qss=substitute(qss, {'QTableView': { 'font': " 18px 'Segoe UI', 'Microsoft YaHei'"}, 'QHeaderView::section':{'font': " 18px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'", 'font-weight': ' 500'}})
        self.setStyleSheet(qss)
        
        
from qfluentwidgets import (TableWidget, PrimaryToolButton, FluentIcon, DoubleSpinBox,
                            FluentStyleSheet, getStyleSheet)

from PyQt5.QtWidgets import QTableWidgetItem, QSizePolicy, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

from .line_box import LineBox
from ..project import Project as Pro
from .utility import setFont, substitute, MediumSize, Normal
from .combox_ import ComboBox_

class TableWidgetPara(TableWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        qss=getStyleSheet(FluentStyleSheet.TABLE_VIEW)
        qss=substitute(qss, {'QTableView': { 'font': f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei';"}, 'QHeaderView::section':{'font': f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'", 'font-weight': ' 500'}})
        self.setStyleSheet(qss)
        
    def addRow(self, content):
        
        row=self.rowCount()
        col=0
        
        self.insertRow(row)
        self.setRowHeight(row, 35) 
        for _, value in enumerate(content[:2]):
            
            item=QTableWidgetItem(str(value));item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            setFont(item, weight=Normal)
            self.setItem(row, col, item)
            col+=1
        
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        tuneType=ComboBox_(); tuneType.addItems(['Relative', 'Value', 'Add'])
        setFont(tuneType, weight=Normal)
        tuneType.setCurrentIndex(1)
        tuneType.setFixedHeight(30)
        
        layout.addWidget(tuneType, Qt.AlignmentFlag.AlignHCenter); widget.core=tuneType
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        lowerBox=DoubleSpinBox(self); lowerBox.setMaximum(1000); lowerBox.setFixedHeight(30)
        setFont(lowerBox, weight=Normal)
        lowerBox.setRange(-100, 1000)
        layout.addWidget(lowerBox, Qt.AlignmentFlag.AlignHCenter); widget.core=lowerBox
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        upperBox=DoubleSpinBox(self); upperBox.setMaximum(1000); upperBox.setFixedHeight(30)
        setFont(upperBox, weight=Normal)
        upperBox.setRange(-100, 10000)
        layout.addWidget(upperBox, Qt.AlignmentFlag.AlignHCenter); widget.core=upperBox
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget = QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        hruSuffix=["chm", "gw", "hru", "mgt", "sdr", "sep", "sol"]
        subBasinSuffix=["pnd", "rte", "sub", "swq", "wgn", "wus"]
        
        if len(content)>2:
            options={}
            items=content[5].split()
            for item in items:
                t=item.split("(")
                if len(t)==1:
                    options[t[0]]=[]
                else:
                    options[t[0]]=t[1][:-1].split(",")
        else:
            options=[]
        
        if content[1] in hruSuffix:
            line2 = LineBox(Pro.modelInfos["sub_hru_simply"], options, self)
            
        elif content[1] in subBasinSuffix:
            sub={}
            for key in Pro.modelInfos["sub_hru_simply"].keys():
                sub[key]=[]
            line2 = LineBox(sub, self)
        else:
            line2 = LineBox({'bsn':[]}, self)
        
        setFont(line2, weight=Normal)
        line2.setFixedHeight(30)
        line2.setMinimumWidth(50)
        line2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(line2, Qt.AlignmentFlag.AlignHCenter); widget.core=line2
        
        self.setCellWidget(row, col, widget)
        col+=1
        
        #DeleteButton
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        button=PrimaryToolButton(FluentIcon.DELETE, self); button.clicked.connect(self.delete_row)
        button.setProperty('row', row); widget.btn=button
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        button.setFixedSize(25, 25)
        widget.setFixedHeight(30)
        layout.addStretch(1);layout.addWidget(button, Qt.AlignmentFlag.AlignVCenter);layout.addStretch(1)
        
        self.setCellWidget(row, col, widget)
        
        if len(content)>2:
            tuneType.setCurrentIndex(int(content[2]))
            lowerBox.setValue(float(content[3]))
            upperBox.setValue(float(content[4]))
            line2.setText(content[5])
        else:
            line2.setText("all")

    def delete_row(self):
        
        button = self.sender() 
        row = button.property('row') 
        
        if row is not None:
    
            self.removeRow(row)  
            self.update_button_row_properties()

    def update_button_row_properties(self):
        
        for row in range(self.rowCount()):
            widget = self.cellWidget(row, 6)  
            if widget:
                widget.btn.setProperty('row', row)



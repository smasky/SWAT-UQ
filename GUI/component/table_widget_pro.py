from qfluentwidgets import TableWidget, PrimaryToolButton, FluentIcon, LineEdit, LineEditButton

from PyQt5.QtWidgets import QTableWidgetItem, QSizePolicy, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

from .checkable_combo_box import CheckableComboBox
from .line_box import LineBox

class TableWidgetPro(TableWidget):
    
    rowCount=0
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def addRow(self, content):
        
        row=self.rowCount
        col=0
        
        self.insertRow(row)
        
        for value in content:
            item=QTableWidgetItem(str(value));item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, col, item)
            col+=1
        #sub_basin_id combobox
        widget = QWidget()
        layout=QHBoxLayout(widget)
        line2 = LineBox(["1", "2", "3", "4"], self)
        line2.setFixedHeight(24)
        line2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(line2)
        
        self.setCellWidget(row, col, widget)
        col+=1
        
        #DeleteButton
        widget=QWidget()
        layout=QHBoxLayout(widget)
        button=PrimaryToolButton(FluentIcon.DELETE, self)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        button.setFixedSize(24, 24)
        layout.addStretch(1);layout.addWidget(button);layout.addStretch(1)
        self.setCellWidget(row, col, widget)
        
        
        
        self.rowCount+=1
    
    
    
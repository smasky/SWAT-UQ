from qfluentwidgets import TableWidget, PrimaryToolButton, FluentIcon, DoubleSpinBox, ComboBox

from PyQt5.QtWidgets import QTableWidgetItem, QSizePolicy, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

from .checkable_combo_box import CheckableComboBox
from .line_box import LineBox
from ..project import Project as Pro

class TableWidgetPara(TableWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        
    def addRow(self, content):
        
        row=self.rowCount()
        col=0
        
        self.insertRow(row)
        
        for _, value in enumerate(content[:2]):
            
            item=QTableWidgetItem(str(value));item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.setItem(row, col, item)
            col+=1
        
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        tuneType=ComboBox(); tuneType.addItems(['Relative', 'Value', 'Add'])
        tuneType.setCurrentIndex(1)
        tuneType.setFixedHeight(30)
        layout.addWidget(tuneType); widget.core=tuneType
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        lowerBox=DoubleSpinBox(self); lowerBox.setMaximum(1000); lowerBox.setFixedHeight(30)
        layout.addWidget(lowerBox); widget.core=lowerBox
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        upperBox=DoubleSpinBox(self); upperBox.setMaximum(1000); upperBox.setFixedHeight(30)
        layout.addWidget(upperBox); widget.core=upperBox
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget = QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        line2 = LineBox(Pro.bsnInfos, self)
        line2.setFixedHeight(30)
        line2.setMinimumWidth(50)
        line2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(line2); widget.core=line2
        
        self.setCellWidget(row, col, widget)
        col+=1
        
        #DeleteButton
        widget=QWidget()
        layout=QHBoxLayout(widget)
        button=PrimaryToolButton(FluentIcon.DELETE, self); button.clicked.connect(self.delete_row)
        button.setProperty('row', row); widget.btn=button
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) 
        button.setFixedSize(24, 24)
        layout.addStretch(1);layout.addWidget(button);layout.addStretch(1)
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
            del Pro.paraInfos[row]
            self.removeRow(row)  
            
            self.update_button_row_properties()

    def update_button_row_properties(self):
        
        for row in range(self.rowCount()):
            widget = self.cellWidget(row, 6)  
            if widget:
                widget.btn.setProperty('row', row)
    
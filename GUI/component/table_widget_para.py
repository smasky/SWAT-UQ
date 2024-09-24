from qfluentwidgets import TableWidget, PrimaryToolButton, FluentIcon, DoubleSpinBox, ComboBox

from PyQt5.QtWidgets import QTableWidgetItem, QSizePolicy, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

from .checkable_combo_box import CheckableComboBox
from .line_box import LineBox

class TableWidgetPara(TableWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def addRow(self, content):
        
        row=self.rowCount()
        col=0
        
        self.insertRow(row)
        
        for _, value in enumerate(content):
            
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
        layout.addWidget(tuneType)
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        lowerBox=DoubleSpinBox(self); lowerBox.setMaximum(1000); lowerBox.setFixedHeight(30)
        layout.addWidget(lowerBox)
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget=QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        upperBox=DoubleSpinBox(self); upperBox.setMaximum(1000); upperBox.setFixedHeight(30)
        layout.addWidget(upperBox)
        self.setCellWidget(row, col, widget)
        col+=1
        
        widget = QWidget()
        layout=QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        options={"1":["2", "3", "4"], "2":["3", "4", "5"], "3":[]} #TODO
        
        line2 = LineBox(options, self)
        line2.setFixedHeight(30)
        line2.setMinimumWidth(50)
        line2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(line2)
        
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
        
    def delete_row(self):
        button = self.sender()  # 获取发出信号的按钮
        row = button.property('row')  # 获取按钮的行号属性
        if row is not None:
            self.removeRow(row)  # 删除对应的行
            # 更新之后行号信息，以免出现错位
            self.update_button_row_properties()

    def update_button_row_properties(self):
        # 更新所有按钮的行号属性，避免删除行后行号错位
        for row in range(self.rowCount()):
            widget = self.cellWidget(row, 6)  # 获取当前行的按钮
            if widget:
                widget.btn.setProperty('row', row)  # 更新行号属性
    
    
    
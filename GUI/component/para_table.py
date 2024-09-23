from qfluentwidgets import TableWidget, StrongBodyLabel

from PyQt5.QtWidgets import QVBoxLayout, QSizePolicy, QHeaderView, QFrame
from PyQt5.QtCore import Qt

import GUI.qss
from importlib.resources import path

from .table_widget_pro import TableWidgetPro

class ParaTable(QFrame):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.vBoxLayout=QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)
        
        label=StrongBodyLabel("Parameter List")
        self.vBoxLayout.addWidget(label)
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        self.table=TableWidgetPro(self); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setObjectName("contentTable")
        self.vBoxLayout.addWidget(self.table)
        
        
        self.table.verticalHeader()
        self.table.setBorderRadius(8)
        self.table.setBorderVisible(True)

        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            self.tr('Parameter'), self.tr('Position'), self.tr('Tuning Type'),
            self.tr('Lower Bound'), self.tr('Upper Bound'), self.tr('HRU ID'), self.tr('Sub Basin ID'), self.tr('Operation')
        ])
        
        self.table.addRow(["1", "2", "3", "4", "5","6"])
        
        with path(GUI.qss, "para_table.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        
        
        
        
        
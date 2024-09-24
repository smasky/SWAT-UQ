from qfluentwidgets import TableWidget, PrimaryToolButton, FluentIcon, DoubleSpinBox, ComboBox

from PyQt5.QtWidgets import QTableWidgetItem, QSizePolicy, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt

from .checkable_combo_box import CheckableComboBox
from .line_box import LineBox

class TableWidgetPro(TableWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    
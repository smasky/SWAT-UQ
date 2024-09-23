from qfluentwidgets import LineEdit, Dialog
from PyQt5.QtWidgets import QListWidget, QListWidgetItem, QComboBox
from PyQt5.QtCore import Qt

from .open_project import OpenProject

class LineBox(LineEdit):
    
    def __init__(self, options, parent=None):
        super().__init__(parent)
        self.options = options
        self.isSelected = False
        self.setPlaceholderText("Click to select Sub")
    def focusInEvent(self, event):
        """当 QLineEdit 获得焦点时显示 QComboBox 并展开"""
        # super().focusInEvent(event)
        if self.isSelected is False:
            self.isSelected=True
            dialog=OpenProject(self)
            dialog.exec()
            self.isSelected=False
            self.clearFocus()
        


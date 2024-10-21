
from qfluentwidgets import CheckBox, FluentStyleSheet, getStyleSheet

from .utility import  MediumSize, substitute

class CheckBox_(CheckBox):
    fontSize=MediumSize
    def __init__(self, text=None, parent=None):
        super().__init__(parent)
        self.setText(text)

        self.setFont_()
        
    def setFont_(self):
        qss=getStyleSheet(FluentStyleSheet.CHECK_BOX)
        qss=substitute(qss, {'CheckBox' : {'min-width': ' 35px', 'min-height': ' 35px', 'font': f" {self.fontSize}px 'Segoe UI', 'Microsoft YaHei'"}})
        self.setStyleSheet(qss)
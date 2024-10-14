
from qfluentwidgets import CheckBox, FluentStyleSheet, getStyleSheet

from .utility import  MediumSize, substitute

class CheckBox_(CheckBox):
    
    def __init__(self, text=None, parent=None):
        super().__init__(parent)
        self.setText(text)
        
        qss=getStyleSheet(FluentStyleSheet.CHECK_BOX)
        qss=substitute(qss, {'CheckBox' : {'min-width': ' 35px', 'min-height': ' 35px', 'font': f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei'"}})
        self.setStyleSheet(qss)
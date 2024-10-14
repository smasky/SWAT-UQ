from PyQt5.QtWidgets import QFrame,QButtonGroup
from qfluentwidgets import RadioButton, FluentStyleSheet, getStyleSheet
from qfluentwidgets import FlowLayout

import GUI.data
from importlib.resources import path
from .utility import substitute, MediumSize, Medium
class ButtonGroup(QFrame):
    currentIndex=None
    def __init__(self, contents, bool, parent=None):
        super().__init__(parent)
        self.btns=[]
        self.group=QButtonGroup(self)
        layout=FlowLayout(self)
        layout.setContentsMargins(0, 10, 0, 10)
        for i, content in enumerate(contents):
            btn=RadioButton_(content, self)
            self.btns.append(btn)
            self.group.addButton(btn, i)
            layout.addWidget(btn)
            btn.setEnabled(bool)
            
        self.group.idClicked.connect(self.setCurrentIndex)
    def reset(self):
        
        for btn in self.group.buttons():
            self.group.removeButton(btn)
            btn.setChecked(False)
        
        for i, btn in enumerate(self.group.buttons()):
            self.group.addButton(btn, i)
    
    def clearBtn(self):
        
        for btn in self.group.buttons():
            btn.setAutoExclusive(False)
            btn.setChecked(False)
            btn.setEnabled(False)
        
    def setCurrentIndex(self, i):
        
        self.currentIndex=i
    
    def setEnabled_(self, bool):
        
        for btn in self.btns:
            btn.setEnabled(bool)
    
    def setEnables(self, indexes):
        
        for btn in self.btns:
                btn.setEnabled(False)
                btn.setChecked(False)
                
        for index in indexes:
            self.btns[index].setEnabled(True)
        
        self.btns[indexes[0]].click()

class RadioButton_(RadioButton):
    
    def __init__(self, content, parent=None):
        super().__init__(parent)
        self.setText(content)
        qss=getStyleSheet(FluentStyleSheet.BUTTON)
        qss=substitute(qss, {'RadioButton' : {'font': f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'",'font-weight': '450'}})
        self.qss=qss
        # qss+="RadioButton:hover\n { font-weight : 500;}\n" +"QRadioButton:hover\n { font-weight : 500;}\n"
        self.setStyleSheet(qss)
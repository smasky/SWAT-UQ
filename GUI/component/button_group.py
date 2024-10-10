from PyQt5.QtWidgets import QWidget, QButtonGroup, QHBoxLayout, QSizePolicy, QGridLayout
from PyQt5.QtCore import Qt
from qfluentwidgets import RadioButton, PushButton
from qfluentwidgets import FlowLayout
import GUI.qss
import GUI.data
from importlib.resources import path

class ButtonGroup(QWidget):
    currentIndex=None
    def __init__(self, contents, bool, parent=None):
        super().__init__(parent)
        self.btns=[]
        self.group=QButtonGroup(self)
        layout=QHBoxLayout(self)
        

        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        for i, content in enumerate(contents):
            btn=RadioButton(content, self)
            self.btns.append(btn)
            self.group.addButton(btn, i)
            layout.addWidget(btn, Qt.AlignmentFlag.AlignCenter)
            btn.setEnabled(bool)
        layout.addStretch(1)
        self.group.idClicked.connect(self.setCurrentIndex)
        
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
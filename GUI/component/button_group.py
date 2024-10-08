from PyQt5.QtWidgets import QWidget, QButtonGroup, QHBoxLayout, QSizePolicy
from qfluentwidgets import RadioButton, PushButton
from qfluentwidgets import FlowLayout

class ButtonGroup(QWidget):
    currentIndex=None
    def __init__(self, contents, bool, parent=None):
        super().__init__(parent)
        self.btns=[]
        self.group=QButtonGroup(self)
        layout=FlowLayout(self)
        # layout.setSpacing(25)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        for i, content in enumerate(contents):
            btn=RadioButton(content, self)
            self.btns.append(btn)
            self.group.addButton(btn, i)
            layout.addWidget(btn)
            btn.setEnabled(bool)

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
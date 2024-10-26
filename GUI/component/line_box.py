from qfluentwidgets import LineEdit, Dialog, BodyLabel, PrimaryPushButton, PushButton
from qframelesswindow import FramelessDialog

from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from .utility import setFont, getFont, Medium
from .double_tree_widget import DoubleTreeWidget
class LineBox(LineEdit):
    
    def __init__(self, leftOptions, rightOptions, parent=None):
        super().__init__(parent)
        self.leftOptions = leftOptions
        self.rightOptions = rightOptions
        self.data=None
        self.isSelected = False
        self.setPlaceholderText("all or click to change")
        self.setToolTip("") 
        if isinstance(rightOptions, dict) and 'all' in rightOptions:
            self.rightOptions=[]
    
    def enterEvent(self, event):
        
        self.setToolTip(self.text())
        super().enterEvent(event)

    def leaveEvent(self, event):
        
        self.setToolTip("") 
        super().leaveEvent(event)
    
    def focusInEvent(self, event):
        
        if self.isSelected is False:
            
            self.isSelected=True
            
            dialog=PositionWidget(self.leftOptions, self.rightOptions, self.data, self)
            res=dialog.exec()
            
            if res==Dialog.Accepted:
                
                if dialog.isAll or len(dialog.selected)==0:
                    self.setText("all")
                    
                else:
                    
                    text=self.generateText(dialog.selected)
                    self.setText(text)
                    text=self.text()
                    
            self.isSelected=False
            
            self.clearFocus()
      
    def generateText(self, selected):
        
        tmp=[]
        for key, values in selected.items():
            if len(values)>0:
                tmp.append(key+"("+",".join(values)+")")
            else:
                tmp.append(key)
        text=" ".join(tmp)
        return text

class PositionWidget(FramelessDialog):
    
    isAll=False
    def __init__(self, leftOptions, rightOptions, selected=None, parent=None):
        
        super().__init__(parent)
        self.selected={}
        self.vBoxLayout=QVBoxLayout(self)
        
        label=BodyLabel(self.tr("Position Generation"), self)
        setFont(label, 18, Medium)
        
        self.vBoxLayout.addWidget(label)
        
        self.contentWidget=DoubleTreeWidget(leftOptions, rightOptions, selected, self)
        self.vBoxLayout.addWidget(self.contentWidget)
        
        self.buttonGroup=QWidget(self)
        self.vBoxLayout.addWidget(self.buttonGroup)
        
        self.yesButton=PrimaryPushButton(self.tr("Confirm"), self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
        setFont(self.yesButton, 18, Medium)
        
        self.setButton=PushButton(self.tr("Set all"), self.buttonGroup); self.setButton.clicked.connect(self.setAll)
        setFont(self.setButton, 18, Medium)
        
        self.cancelButton=PushButton(self.tr("Cancel"), self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
        setFont(self.cancelButton, 18, Medium)
        
        self.buttonLayout=QHBoxLayout(self.buttonGroup)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.setButton)
        self.buttonLayout.addWidget(self.cancelButton)
        
        self.setFixedSize(1000, 600)
        self.titleBar.hide()
    
    def confirm_clicked(self):
        
        targetRoot=self.contentWidget.targetTree.invisibleRootItem()
        
        for i in range(targetRoot.childCount()):
            topChild=targetRoot.child(i)
            topName=topChild.text(0)
            self.selected.setdefault(topName, [])
            for j in range(topChild.childCount()):
                child=topChild.child(j)
                paraName=child.text(0)
                self.selected[topName].append(paraName)
                        
        self.accept()
    
    def setAll(self):
        
        self.ifAll=True
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()
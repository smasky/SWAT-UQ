from qframelesswindow import FramelessDialog
from qfluentwidgets import BodyLabel, PushButton, LineEdit, PrimaryToolButton, FluentIcon, PrimaryPushButton
from qfluentwidgets import TreeWidget
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from PyQt5.QtCore import Qt

from .double_tree_widget import DoubleTreeWidget

class AddParaWidget(FramelessDialog):
    
    
    
    def __init__(self, options, parent=None):
        
        super().__init__(parent)
        self.selected={}
        self.vBoxLayout=QVBoxLayout(self)
        label=BodyLabel(self.tr("Parameter Selection"), self)
        self.vBoxLayout.addWidget(label)
        
        # options={"hru": ['1', '2', '3'], "rte": ['2', '3', '4']}
        self.contentWidget=DoubleTreeWidget(options, self)
        self.vBoxLayout.addWidget(self.contentWidget)
        
        self.buttonGroup=QWidget(self)
        self.vBoxLayout.addWidget(self.buttonGroup)
        self.yesButton=PrimaryPushButton(self.tr("Confirm"), self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
        self.cancelButton=PushButton(self.tr("Cancel"), self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
        self.buttonLayout=QHBoxLayout(self.buttonGroup)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.cancelButton)
        
        self.setFixedSize(800, 400)
        self.titleBar.hide()
    
    def confirm_clicked(self):
        
        targetRoot=self.contentWidget.targetTree.invisibleRootItem()
        
        for i in range(targetRoot.childCount()):
            topChild=targetRoot.child(i)
            topName=topChild.text(0)
            for j in range(topChild.childCount()):
                child=topChild.child(j)
                paraName=child.text(0)
                self.selected.setdefault(topName, []).append(paraName)
                        
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()
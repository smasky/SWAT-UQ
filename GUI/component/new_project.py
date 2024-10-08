from PyQt5.QtCore import Qt
from qframelesswindow import FramelessDialog
from qfluentwidgets import BodyLabel, PushButton, LineEdit, PrimaryToolButton, FluentIcon, PrimaryPushButton, IndeterminateProgressRing

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QFormLayout
from ..project import Project as Pro
class NewProject(FramelessDialog):
    projectName=None
    projectPath=None
    swatPath=None
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.vBoxLayout=QVBoxLayout(self)
        label=BodyLabel(self.tr("New UQ Project"), self)
        self.vBoxLayout.addWidget(label)
        self.vBoxLayout.addStretch(1)
        
        self.contentWidget=QWidget(self)
        self.contentLayout=QFormLayout(self.contentWidget)
        self.contentLayout.setLabelAlignment(Qt.AlignRight)
        self.vBoxLayout.addWidget(self.contentWidget)
        
        self.nameEdit=LineEdit(self.contentWidget)
        self.nameEdit.setMaximumWidth(400)
        self.contentLayout.addRow(BodyLabel("UQ Project Name:"), self.nameEdit)
        
        self.pathEdit=LineEditWithPath(self.contentWidget)
        self.contentLayout.addRow(BodyLabel("UQ Project Path:"), self.pathEdit)
        
        self.swatPathEdit=LineEditWithPath(self.contentWidget)
        self.contentLayout.addRow(BodyLabel("SWAT Project Path:"), self.swatPathEdit)
        
        self.vBoxLayout.addStretch(1)
        self.buttonGroup=QWidget(self)
        self.vBoxLayout.addWidget(self.buttonGroup)
        self.yesButton=PrimaryPushButton(self.tr("Confirm"), self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
        self.cancelButton=PushButton(self.tr("Cancel"), self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
        self.buttonLayout=QHBoxLayout(self.buttonGroup)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.cancelButton)
        
        self.setFixedSize(618, 250)
        self.titleBar.hide()
        
    def confirm_clicked(self):
        
        projectName=self.nameEdit.text()
        projectPath=self.pathEdit.text
        swatPath=self.swatPathEdit.text
        
        Pro.openProject(projectName, projectPath, swatPath)
        
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()

class LineEditWithPath(QWidget):
    
    text=None
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        hBoxLayout=QHBoxLayout(self)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        self.LineEdit=LineEdit(self)
        self.LineEdit.setMinimumWidth(400)
        self.btn=PrimaryToolButton(FluentIcon.FOLDER, self)
        self.btn.clicked.connect(self.setText)

        hBoxLayout.addWidget(self.LineEdit)
        hBoxLayout.addWidget(self.btn)
        hBoxLayout.addStretch(1)
        
    def setText(self):
        
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.LineEdit.setText(folder_path)
        self.text=folder_path 
from PyQt5.QtCore import Qt
from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, IndeterminateProgressRing, PushButton, ComboBox,
                            LineEdit, PrimaryToolButton, FluentIcon, MessageBoxBase, SubtitleLabel,
                            PrimaryPushButton, IndeterminateProgressRing)
import glob
import os
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QFormLayout, QSizePolicy
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
        
        self.projectName=self.nameEdit.text()
        self.projectPath=self.pathEdit.text.replace('/', '\\')
        self.swatPath=self.swatPathEdit.text.replace('/', '\\')
                
        
        full_files=glob.glob(os.path.join(self.projectPath, "*.prj"))
        files = [os.path.basename(file) for file in full_files]
        
        if files:
            dialog=AskForExistingProject(files, self.window())
            res=dialog.exec()

            if res:
                self.projectPath=os.path.join(self.projectPath, dialog.comBox.currentText())
                self.ifOpenExistingProject=True
            else:
                self.ifOpenExistingProject=False
            
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()
        
class AskForExistingProject(MessageBoxBase):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        
        self.titleLabel=SubtitleLabel("There are existing projects in this directory.", self)
        self.contentLabel=BodyLabel("Do you want to open an existing project or click continue?", self)
        
        self.comBox=ComboBox(self)
        self.comBox.addItems(files)
        
        self.yesButton.setText("Open existing project")
        self.yesButton.clicked.connect(self.open_existing_project)
        self.cancelButton.setText("Continue to create")
        self.cancelButton.clicked.connect(self.continue_to_create)
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        self.viewLayout.addWidget(self.comBox)
    
    def open_existing_project(self):
        self.accept()
    
    def continue_to_create(self):
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
from PyQt5.QtCore import Qt
from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel,  PushButton,
                            LineEdit, PrimaryToolButton, FluentIcon, MessageBoxBase, SubtitleLabel,
                            PrimaryPushButton)
import glob
import os
from importlib.resources import path
import GUI.qss
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QFormLayout, QSizePolicy
from PyQt5.QtGui import QFont
from .utility import getFont, setFont, Normal, MediumSize, substitute
from .combox_ import ComboBox_
class NewProject(FramelessDialog):
    
    projectName=None
    projectPath=None
    swatPath=None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.vMainLayout=QVBoxLayout(self)
        titleLabel=BodyLabel(self.tr("New SWAT-UQ Project"), self)
        titleLabel.setFont(getFont(20, QFont.Medium))
        self.vMainLayout.addWidget(titleLabel)
        self.vMainLayout.addStretch(1)
        
        self.contentWidget=QWidget(self)
        self.contentWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.contentLayout=QFormLayout(self.contentWidget)
        self.contentLayout.setLabelAlignment(Qt.AlignRight)
        self.vMainLayout.addWidget(self.contentWidget)
        
        self.nameEdit=LineEdit(self.contentWidget)
        self.nameEdit.setMaximumWidth(400)
        self.nameEdit.textChanged.connect(self.checkNull)
        setFont(self.nameEdit, MediumSize, Normal)
        
        label=BodyLabel(self.tr("Project Name:"))
        setFont(label)
        self.contentLayout.addRow(label, self.nameEdit)
        
        self.pathEdit=LineEditWithPath(self.contentWidget)
        self.pathEdit.LineEdit.textChanged.connect(self.checkNull)
        # setFont(self.pathEdit, MediumSize, Normal)
        
        label=BodyLabel(self.tr("Project Path:"))
        setFont(label)
        self.contentLayout.addRow(label, self.pathEdit)
        
        self.swatPathEdit=LineEditWithPath(self.contentWidget)
        self.swatPathEdit.LineEdit.textChanged.connect(self.checkNull)
        # setFont(self.swatPathEdit, MediumSize, Normal)
        
        label=BodyLabel(self.tr("SWAT File Path:"))
        setFont(label)
        self.contentLayout.addRow(label, self.swatPathEdit)
        
        self.vMainLayout.addStretch(1)
        self.buttonGroup=QWidget(self)
        self.vMainLayout.addWidget(self.buttonGroup)
        self.yesButton=PrimaryPushButton(self.tr("Confirm"), self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
        self.yesButton.setEnabled(False); setFont(self.yesButton)
        self.cancelButton=PushButton(self.tr("Cancel"), self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
        setFont(self.cancelButton)
        
        self.buttonLayout=QHBoxLayout(self.buttonGroup)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.cancelButton)
        
        self.setFixedSize(700, 400)
        self.titleBar.hide()
    
    def checkNull(self):
        
        text1=self.nameEdit.text()
        text2=self.pathEdit.LineEdit.text()
        text3=self.swatPathEdit.LineEdit.text()
        
        all_filled = bool(text1) and bool(text2) and bool(text3)
        
        self.yesButton.setEnabled(all_filled)
    
    def confirm_clicked(self):
        
        self.projectName=self.nameEdit.text()
        self.projectPath=self.pathEdit.text.replace('/', '\\')
        self.swatPath=self.swatPathEdit.text.replace('/', '\\')
                
        full_files=glob.glob(os.path.join(self.projectPath, "*.prj"))
        files = [os.path.basename(file) for file in full_files]
        self.ifOpenExistingProject=False
        
        if files:
            dialog=AskForExistingProject(files, self.window())
            res=dialog.exec()

            if res:
                self.projectPath=os.path.join(self.projectPath, dialog.comBox.currentText())
                self.ifOpenExistingProject=True
            
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()
        
class AskForExistingProject(MessageBoxBase):
    def __init__(self, files, parent=None):
        
        super().__init__(parent)
        
        self.titleLabel=SubtitleLabel("There are existing projects in this directory.", self)
        setFont(self.titleLabel)
        self.contentLabel=BodyLabel("Do you want to open a following existing project or continue?", self)
        setFont(self.contentLabel, MediumSize, Normal)
        
        self.comBox=ComboBox_(self)
        self.comBox.setFixedHeight(40)
        self.comBox.addItems(files)
        self.comBox.setCurrentIndex(0)
        setFont(self.comBox)
        
        self.yesButton.setText("Open existing project")
        self.yesButton.clicked.connect(self.open_existing_project)
        setFont(self.yesButton)
        self.yesButton.setFixedHeight(40)
        
        self.buttonLayout.removeWidget(self.cancelButton)
        self.cancelButton=PushButton(self.tr("Continue to create"), self.buttonGroup)
        self.cancelButton.clicked.connect(self.reject)
        self.cancelButton.setFixedHeight(40)
        self.buttonLayout.addWidget(self.cancelButton)
        setFont(self.cancelButton)
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        self.viewLayout.addWidget(self.comBox)
        
        with path(GUI.qss, "messagebox.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        
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
        setFont(self.LineEdit, MediumSize, Normal)
        self.btn=PrimaryToolButton(FluentIcon.FOLDER, self)
        self.btn.clicked.connect(self.setText)

        hBoxLayout.addWidget(self.LineEdit)
        hBoxLayout.addWidget(self.btn)
        hBoxLayout.addStretch(1)
        
    def setText(self):
        
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.LineEdit.setText(folder_path)
        self.text=folder_path 
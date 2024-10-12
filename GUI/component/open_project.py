from qframelesswindow import FramelessDialog
from qfluentwidgets import (BodyLabel, PushButton, LineEdit, PrimaryToolButton, SubtitleLabel, ComboBox,
                            FluentIcon, PrimaryPushButton, setFont, getFont, MessageBoxBase)

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
from PyQt5.QtGui import QFont
import glob
import os
from importlib.resources import path
import GUI.qss
class OpenProject(FramelessDialog):
    
    projectPath=None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.vBoxLayout=QVBoxLayout(self)
        label=BodyLabel(self.tr("Open Existing SWAT-UQ Project"), self)
        label.setFont(getFont(18, QFont.Medium))
        self.vBoxLayout.addWidget(label)
        self.vBoxLayout.addStretch(1)
        
        self.contentWidget=QWidget(self)
        self.contentLayout=QVBoxLayout(self.contentWidget)
        self.vBoxLayout.addWidget(self.contentWidget)
 
        hBoxLayout=QHBoxLayout()
        pathLabel=BodyLabel(self.tr(str("SWAT-UQ Project Path:").rjust(21)), self.contentWidget)
        pathEdit=LineEdit(self.contentWidget); pathEdit.setMinimumWidth(400); self.pathEdit=pathEdit
        self.pathEdit.setFont(getFont(18, 60))
        self.pathEdit.textChanged.connect(self.checkNull)
        
        fileButton=PrimaryToolButton(FluentIcon.FOLDER, self.contentWidget); fileButton.clicked.connect(self.open_folder_dialog)
        hBoxLayout.addWidget(pathLabel); hBoxLayout.addWidget(pathEdit);hBoxLayout.addWidget(fileButton);hBoxLayout.addStretch(1)
        self.contentLayout.addLayout(hBoxLayout)
        
        self.vBoxLayout.addStretch(1)
        self.buttonGroup=QWidget(self)
        self.vBoxLayout.addWidget(self.buttonGroup)
        self.yesButton=PrimaryPushButton(self.tr("Confirm"), self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
        self.yesButton.setEnabled(False)
        self.yesButton.setFont(getFont(18, QFont.Medium))
        self.cancelButton=PushButton(self.tr("Cancel"), self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
        self.cancelButton.setFont(getFont(18, QFont.Medium))
        
        self.buttonLayout=QHBoxLayout(self.buttonGroup)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.cancelButton)
        
        self.setFixedSize(718, 250)
        self.titleBar.hide()

    def checkNull(self):
        
        if not self.pathEdit.text()=="":
            self.yesButton.setEnabled(True)
    
    def open_folder_dialog(self):
        
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        self.pathEdit.setText(folder_path)
    
    def confirm_clicked(self):
        
        self.projectPath=self.pathEdit.text()
        
        full_files=glob.glob(os.path.join(self.projectPath, "*.prj"))
        files = [os.path.basename(file) for file in full_files]
        
        self.projectFile=None
        if len(files)>1:
            dialog=SelctProject(files, self.window())
            res=dialog.exec()
            if res:
                self.projectFile=dialog.comBox.currentText()
            else:
                self.reject()
        elif len(files)==1:
            self.projectFile=files[0]
        
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()

class SelctProject(MessageBoxBase):
    def __init__(self, files, parent=None):
        super().__init__(parent)
        
        self.titleLabel=SubtitleLabel("There exists more than one project files in this directory.", self)
        self.contentLabel=BodyLabel("You should select one to apply", self)
        
        self.comBox=ComboBox(self)
        self.comBox.setFixedHeight(40)
        self.comBox.addItems(files)
        self.comBox.setFont_(18, QFont.Medium)
        
        self.yesButton.setText("Open")
        self.yesButton.clicked.connect(self.open_existing_project)
        self.yesButton.setFont(getFont(18, QFont.Medium))
        self.yesButton.setFixedHeight(50)
        
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.continue_to_create)
        self.cancelButton.setFont(getFont(18, QFont.Medium))
        self.cancelButton.setFixedHeight(50)
        
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

class ReOpenWidget(MessageBoxBase):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.titleLabel=SubtitleLabel("A project has been opened now", self)
        self.contentLabel=BodyLabel("Do you want to create or open another project?", self)

        self.yesButton.setText("Yes")
        self.yesButton.clicked.connect(self.accept)
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
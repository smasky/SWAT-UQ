from qframelesswindow import FramelessDialog
from qfluentwidgets import BodyLabel, PushButton, LineEdit, PrimaryToolButton, FluentIcon, PrimaryPushButton, IndeterminateProgressRing

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QFileDialog
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
        self.contentLayout=QVBoxLayout(self.contentWidget)
        self.vBoxLayout.addWidget(self.contentWidget)
        
        hBoxLayout=QHBoxLayout()
        nameLabel=BodyLabel(self.tr(str("UQ Project Name:").rjust(19)), self.contentWidget)
        nameEdit=LineEdit(self.contentWidget); nameEdit.setMinimumWidth(400);self.nameEdit=nameEdit
        hBoxLayout.addWidget(nameLabel); hBoxLayout.addWidget(nameEdit);hBoxLayout.addStretch(1)
        self.contentLayout.addLayout(hBoxLayout)
        
        hBoxLayout=QHBoxLayout()
        pathLabel=BodyLabel(self.tr(str("UQ Project Path:").rjust(21)), self.contentWidget)
        pathEdit=LineEdit(self.contentWidget); pathEdit.setMinimumWidth(400); self.pathEdit=pathEdit
        fileButton=PrimaryToolButton(FluentIcon.FOLDER, self.contentWidget); fileButton.clicked.connect(self.open_folder_dialog)
        hBoxLayout.addWidget(pathLabel); hBoxLayout.addWidget(pathEdit);hBoxLayout.addWidget(fileButton);hBoxLayout.addStretch(1)
        self.contentLayout.addLayout(hBoxLayout)
        
        hBoxLayout=QHBoxLayout()
        swatPathLabel=BodyLabel(self.tr(str("SWAT Project Path:").rjust(20)), self.contentWidget)
        swatPathEdit=LineEdit(self.contentWidget);swatPathEdit.setMinimumWidth(400);self.swatPathEdit=swatPathEdit
        fileButton=PrimaryToolButton(FluentIcon.FOLDER, self.contentWidget); fileButton.clicked.connect(self.open_swat_folder_dialog)
        hBoxLayout.addWidget(swatPathLabel); hBoxLayout.addWidget(swatPathEdit);hBoxLayout.addWidget(fileButton);hBoxLayout.addStretch(1)
        self.contentLayout.addLayout(hBoxLayout)
        
        self.vBoxLayout.addStretch(1)
        self.buttonGroup=QWidget(self)
        self.vBoxLayout.addWidget(self.buttonGroup)
        self.yesButton=PrimaryPushButton(self.tr("Confirm"), self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
        self.cancelButton=PushButton(self.tr("Cancel"), self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
        self.buttonLayout=QHBoxLayout(self.buttonGroup)
        self.buttonLayout.addWidget(self.yesButton)
        self.buttonLayout.addWidget(self.cancelButton)
        
        self.setFixedSize(618, 300)
        self.titleBar.hide()

    def open_folder_dialog(self):
        
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

        self.pathEdit.setText(folder_path)
        
    def open_swat_folder_dialog(self):
        
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        
        self.swatPathEdit.setText(folder_path)
    
    def confirm_clicked(self):
        
        projectName=self.nameEdit.text()
        projectPath=self.pathEdit.text()
        swatPath=self.swatPathEdit.text()
        
        # statusBar=IndeterminateProgressRing(self.parent(), start=True)
        Pro.openProject(projectName, projectPath, swatPath)
        
        self.accept()
    
    def cancel_clicked(self):
        
        self.reject()
        
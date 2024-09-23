# from qframelesswindow import FramelessDialog

# class OpenProject(FramelessDialog):
    
#     projectPath=None
    
#     def __init__(self, parent=None):
#         super().__init__(parent)
        
#         self.vBoxLayout=QVBoxLayout(self)
#         label=BodyLabel(self.tr("Open UQ Project"), self)
#         self.vBoxLayout.addWidget(label)
#         self.vBoxLayout.addStretch(1)
        
#         self.contentWidget=QWidget(self)
#         self.contentLayout=QVBoxLayout(self.contentWidget)
#         self.vBoxLayout.addWidget(self.contentWidget)
 
#         hBoxLayout=QHBoxLayout()
#         pathLabel=BodyLabel(self.tr(str("UQ Project Path:").rjust(21)), self.contentWidget)
#         pathEdit=LineEdit(self.contentWidget); pathEdit.setMinimumWidth(400); self.pathEdit=pathEdit
#         fileButton=PrimaryToolButton(FluentIcon.FOLDER, self.contentWidget); fileButton.clicked.connect(self.open_folder_dialog)
#         hBoxLayout.addWidget(pathLabel); hBoxLayout.addWidget(pathEdit);hBoxLayout.addWidget(fileButton);hBoxLayout.addStretch(1)
#         self.contentLayout.addLayout(hBoxLayout)
        
#         self.vBoxLayout.addStretch(1)
#         self.buttonGroup=QWidget(self)
#         self.vBoxLayout.addWidget(self.buttonGroup)
#         self.yesButton=PrimaryPushButton(self.tr("Confirm"), self.buttonGroup); self.yesButton.clicked.connect(self.confirm_clicked)
#         self.cancelButton=PushButton(self.tr("Cancel"), self.buttonGroup); self.cancelButton.clicked.connect(self.cancel_clicked)
#         self.buttonLayout=QHBoxLayout(self.buttonGroup)
#         self.buttonLayout.addWidget(self.yesButton)
#         self.buttonLayout.addWidget(self.cancelButton)
        
#         self.setFixedSize(618, 300)
#         self.titleBar.hide()

#     def open_folder_dialog(self):
        
#         folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")

#         self.pathEdit.setText(folder_path)
    
#     def confirm_clicked(self):
        
#         self.projectPath=self.pathEdit.text()
        
#         self.accept()
    
#     def cancel_clicked(self):
        
#         self.reject()
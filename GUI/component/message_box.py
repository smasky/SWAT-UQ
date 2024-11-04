from qfluentwidgets import MessageBoxBase, SubtitleLabel, BodyLabel
from importlib.resources import path
from PyQt5.QtGui import QFont

import GUI.qss
from .utility import getFont

class MessageBox(MessageBoxBase):
    
    def __init__(self, title, content, parent=None):
        super().__init__(parent)
        
        self.titleLabel=SubtitleLabel(title, self)
        self.contentLabel=BodyLabel(content, self)
        
        self.yesButton.setText("Yes")
        self.yesButton.setFont(getFont(18, QFont.Medium))
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        
        self.buttonLayout.removeWidget(self.cancelButton)
        self.cancelButton=None

        with path(GUI.qss, "messagebox.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
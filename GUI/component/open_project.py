from qframelesswindow import FramelessDialog
from qfluentwidgets import TitleLabel, BodyLabel

from PyQt5.QtWidgets import QVBoxLayout, QLabel

class OpenProject(FramelessDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.vBoxLayout=QVBoxLayout(self)
        label=BodyLabel(self.tr("Open Project"), self)
        self.vBoxLayout.addWidget(label)
        self.vBoxLayout.addStretch(1)
        
        self.setFixedSize(400, 300)

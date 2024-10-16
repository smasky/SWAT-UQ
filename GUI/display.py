from qfluentwidgets import ScrollArea

from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .component import BannerWidget

from importlib.resources import path
import GUI.picture
import GUI.qss
from .component.dispaly_SA import DisplaySA

class DisplayWidget(ScrollArea):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.view=QWidget(self)
        self.view.setObjectName('view')
        vBoxLayout=QVBoxLayout(self.view)
        self.setWidget(self.view)
        
        banner=BannerWidget(self)
        
        with path(GUI.picture, "header.png") as header_path:
            banner.setPixmap(str(header_path))
        
        banner.setTitle(self.tr("Result Visualization"))
        
        vBoxLayout.addWidget(banner)
        
        displaySA=DisplaySA(self)
        banner.vBoxLayout.addWidget(displaySA)
        
        
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        self.setWidgetResizable(True)
        
        with path(GUI.qss, "display.qss") as qss_path:
            with open(qss_path, 'r') as f:
                self.setStyleSheet(f.read())
        
    def updateUI(self):
        
        pass
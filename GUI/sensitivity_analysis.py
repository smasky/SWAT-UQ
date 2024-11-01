from qfluentwidgets import ScrollArea, TableWidget

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton

from importlib.resources import path
import GUI.qss
import GUI.picture
import GUI.data

from .component import BannerWidget, SAWidget

class SenAnalysis(ScrollArea):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.view=QWidget(self)
        self.view.setObjectName('view')
        vBoxLayout=QVBoxLayout(self.view)
        self.setWidget(self.view)
        
        banner=BannerWidget(self)
        with path(GUI.picture, "header2.png") as header_path:
            banner.setPixmap(str(header_path))
            
        banner.setTitle("Sensitivity Analysis")
        vBoxLayout.addWidget(banner)
        
        self.saWidget=SAWidget()
        banner.vBoxLayout.addWidget(self.saWidget)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.setWidgetResizable(True)
        
        with path(GUI.qss, "sensitivity_analysis.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        self.setWidgetResizable(True)
        
    def updateUI(self):
        
        self.saWidget.updateUI()
from qfluentwidgets import FluentWindow
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication

from .get_start import GetStart
from .para_setting import ParaSetting

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        
        self.initWindow()

        self.get_start = GetStart(self)
        self.get_start.setObjectName("GetStart")

        self.para_setting = ParaSetting(self)
        self.para_setting.setObjectName("ParaSetting")
        
        
        self.initNavigation()
    
    def initNavigation(self):
        
        self.addSubInterface(self.get_start, FIF.HOME, self.tr('Get Start'))
        self.navigationInterface.addSeparator()
        self.addSubInterface(self.para_setting, FIF.LABEL, self.tr('Parameter Settings'))
    
    def initWindow(self):
        
        self.setWindowTitle("SWAT-UQ")
        self.resize(1200, 768)
        
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        
    
        

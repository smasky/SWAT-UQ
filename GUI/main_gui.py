from qfluentwidgets import FluentWindow
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

from .get_start import GetStart
from .para_setting import ParaSetting
from .pro_define import ProDefine
from .sensitivity_analysis import SenAnalysis

from .project import Project as Pro
class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        
        self.initWindow()

        self.get_start = GetStart(self)
        self.get_start.setObjectName("GetStart")

        self.para_setting = ParaSetting(self)
        self.para_setting.setObjectName("ParaSetting")
        
        self.pro_define = ProDefine(self)
        self.pro_define.setObjectName("ProDefine")
        
        self.sen_analysis = SenAnalysis(self)
        self.sen_analysis.setObjectName("SenAnalysis")
        
        self.initNavigation()
        
    def initNavigation(self):
        
        btn=self.addSubInterface(self.get_start, FIF.HOME, self.tr('Get Start'));Pro.btnSets.append(btn)
        self.navigationInterface.addSeparator()
        btn=self.addSubInterface(self.para_setting, FIF.LABEL, self.tr('Parameter Setting'));Pro.btnSets.append(btn); btn.setEnabled(False)
        btn=self.addSubInterface(self.pro_define, FIF.TILES, self.tr("Problem Define"));Pro.btnSets.append(btn); btn.setEnabled(False)
        self.navigationInterface.addSeparator()
        btn=self.addSubInterface(self.sen_analysis, FIF.CALENDAR, self.tr("Sensitivity Analysis"));Pro.btnSets.append(btn); btn.setEnabled(False)
        btn.clicked.connect(self.sen_analysis.updateUI)
        
    def initWindow(self):
        
        self.setWindowTitle("SWAT-UQ")
        self.resize(1200, 768)
        
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        
    
        

from qfluentwidgets import FluentWindow, getFont, FluentStyleSheet, getStyleSheet
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import QSize

from importlib.resources import path
import GUI.picture

from .component import setFont, getFont, Medium, substitute
from .get_start import GetStart
from .para_setting import ParaSetting
from .pro_define import ProDefine
from .sensitivity_analysis import SenAnalysis
from .optimization import Optimization

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
        
        self.optimization = Optimization(self)
        self.optimization.setObjectName("Optimization")
        
        self.initNavigation()
        
        qss=getStyleSheet(FluentStyleSheet.FLUENT_WINDOW)
        qss=substitute(qss, {'SplitTitleBar>QLabel#titleLabel': {'font': " 18px 'Segoe UI'"}})
        
        self.setStyleSheet(qss)
        
    def initNavigation(self):
             
        Pro.btnSets.append(self.addSubInterface(self.get_start, FIF.HOME, self.tr('Get Start')))
        
        self.navigationInterface.addSeparator()
        
        Pro.btnSets.append(self.addSubInterface(self.para_setting, FIF.LABEL, self.tr('Parameter Setting')))
        Pro.btnSets.append(self.addSubInterface(self.pro_define, FIF.TILES, self.tr('Objective Define')))
        
        self.navigationInterface.addSeparator()
        
        Pro.btnSets.append(self.addSubInterface(self.sen_analysis, FIF.CALENDAR, self.tr('Sensitivity Analysis')))
        Pro.btnSets.append(self.addSubInterface(self.optimization, FIF.ALBUM, self.tr('Problem Optimization')))
        
        for btn in Pro.btnSets:
            btn.setFont(getFont(16, QFont.Medium))
           
    def initWindow(self):
        
        self.setWindowTitle("SWAT-UQ")
        self.resize(1200, 768)
        
        with path(GUI.picture, "icon.png") as iconPath:
            self.setWindowIcon(QIcon(str(iconPath)))
        
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        
    
        

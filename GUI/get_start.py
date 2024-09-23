from qfluentwidgets import ScrollArea, FluentIcon, Dialog
from qframelesswindow import FramelessWindow, FramelessDialog
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal

from importlib.resources import path
import GUI.qss
import GUI.picture

from .component import BannerWidget, OpenProject

class GetStart(ScrollArea):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.view=QWidget(self)
        self.view.setObjectName('view')
        vBoxLayout=QVBoxLayout(self.view)
        self.setWidget(self.view)
        
        banner=BannerWidget(self)
        with path(GUI.picture, "header.png") as header_path:
            banner.setPixmap(str(header_path))
        banner.setTitle("SWAT-UQ")
        
        banner.addCard(FluentIcon.ADD,
            self.tr('New Project'),
            self.tr('Create a new project tailored for sensitivity analysis or optimization.'),
            self.click1)
        
        banner.addCard(FluentIcon.FOLDER,
                       self.tr('Open Project'),
            self.tr('open a project that you previously created and continue working on it.'),
            "http://www.uq-pyl.com/")
        
        banner.addCard(FluentIcon.BOOK_SHELF,
                       self.tr('Examples'),
                       self.tr('Review the documentation or explore examples of projects.'),
                       "http://www.uq-pyl.com/")
        
        banner.addCard(FluentIcon.HELP,
                       self.tr('Help'),
                       self.tr('Please feel free to seek assistance or report any bugs to the developers.'),
                       "http://www.uq-pyl.com/")
        
        vBoxLayout.addWidget(banner)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        with path(GUI.qss, "get_start.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        
        self.setWidgetResizable(True)

    def click1(self):
        op=OpenProject(self)
        op.setWindowModality(Qt.WindowModal)
        op.exec()

        
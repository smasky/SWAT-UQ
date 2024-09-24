from qfluentwidgets import ScrollArea, FluentIcon, Dialog
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices
from importlib.resources import path

import GUI.qss
import GUI.picture
from .component import BannerWidget, NewProject, OpenProject, LinkCardView
from .project import Project
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
        
        linkCard=LinkCardView(self); banner.vBoxLayout.addWidget(linkCard); banner.vBoxLayout.addStretch(1)
        
        linkCard.addCard(FluentIcon.ADD,
            self.tr('New Project'),
            self.tr('Create a new project tailored for sensitivity analysis or optimization.'),
            self.click_new_project)
        
        linkCard.addCard(FluentIcon.FOLDER,
                       self.tr('Open Project'),
            self.tr('open a project that you previously created and continue working on it.'),
            self.click_open_project)
        
        linkCard.addCard(FluentIcon.BOOK_SHELF,
                       self.tr('Examples'),
                       self.tr('Review the documentation or explore examples of projects.'),
                       self.click_examples)
        
        linkCard.addCard(FluentIcon.HELP,
                       self.tr('Help'),
                       self.tr('Please feel free to seek assistance or report any bugs to the developers.'),
                       self.click_help)
        
        vBoxLayout.addWidget(banner)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        with path(GUI.qss, "get_start.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        
        self.setWidgetResizable(True)

    def click_new_project(self):
        
        newPro=NewProject(self)
        newPro.setWindowModality(Qt.WindowModal)
        res=newPro.exec()
        
        if res==Dialog.Accepted:
            Project.projectName=newPro.projectName
            Project.projectPath=newPro.projectPath
            Project.swatPath=newPro.swatPath
            self.activateBtn()
    
    def click_open_project(self):
        
        openPro=OpenProject(self)
        openPro.setWindowModality(Qt.WindowModal)
        res=openPro.exec()
        
        if res==Dialog.Accepted:
            Project.projectPath=openPro.projectPath
            self.activateBtn()
            
    def click_examples(self):
        
        url=QUrl("https://github.com/smasky/SWAT-UQ")
        QDesktopServices.openUrl(url)
    
    def click_help(self):
        
        url=QUrl("https://github.com/smasky/SWAT-UQ/issues")
        QDesktopServices.openUrl(url)
        
    def activateBtn(self):
        
        btnSets=Project.btnSets
        for btn in btnSets[1:]:
            btn.setEnabled(True)
        
        

        
from qfluentwidgets import (ScrollArea, FluentIcon, Dialog, getFont, setFont,
                            InfoBarPosition, MessageBoxBase, SubtitleLabel,
                            BodyLabel,)
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QUrl, pyqtSignal, QTimer
from PyQt5.QtGui import QDesktopServices, QFont
from importlib.resources import path

import os
import GUI.qss
import GUI.picture
from .component import BannerWidget, NewProject, OpenProject, LinkCardView
from .component.info_bar import InfoBar_ as InfoBar, InfoBarPosition
from .component.message_box import MessageBox
from .project import Project
class GetStart(ScrollArea):
    
    openBox=pyqtSignal(list)
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        self.view=QWidget(self)
        self.view.setObjectName('view')
        vMainLayout=QVBoxLayout(self.view)
        self.setWidget(self.view)
        
        banner=BannerWidget(self)
        
        with path(GUI.picture, "header.png") as header_path:
            banner.setPixmap(str(header_path))
            
        banner.setTitle(self.tr("SWAT-UQ"))
        
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
                       self.tr('Review the documentation or explore more examples of SWAT-UQ projects.'),
                       self.click_examples)
        
        linkCard.addCard(FluentIcon.HELP,
                       self.tr('Help'),
                       self.tr('Please feel free to seek assistance or report any bugs to the developers.'),
                       self.click_help)
        
        vMainLayout.addWidget(banner)
        vMainLayout.setContentsMargins(0, 0, 0, 0)
        
        with path(GUI.qss, "get_start.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        
        self.setWidgetResizable(True)

        Project.window=self
        Project.W=self.window()
        
    def click_new_project(self):
        
        if Project.projectInfos:
            
            dialog=ReOpenWidget(self.window(), self.click_new_project_)
            dialog.show()
        
        else:
            
            self.click_new_project_()
    
    def click_new_project_(self):
        
        newPro=NewProject(self.window())
        res=newPro.exec()
        
        if res==Dialog.Accepted:
            
            if not newPro.ifOpenExistingProject:
                
                info=InfoBar.success(
                title=self.tr('Create Project'),
                content=self.tr("Loading and checking model, please wait..."),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=10000,
                parent=self
                )
                
                def close(time):
                    
                    QTimer.singleShot(time, info.close)
                    
                Project.openProject(newPro.projectName, newPro.projectPath, newPro.swatPath, close, self.activateBtn) #TODO
                
            else:
                
                info=InfoBar.success(
                title=self.tr('Open Project'),
                content=self.tr("Loading and checking model files, please wait..."),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP_RIGHT,
                duration=10000,
                parent=self
                )
                
                def close(time):
                    
                    QTimer.singleShot(time, info.close)
                
                dict=self.readFiles(newPro.projectPath)
                
                Project.openProject(dict['projectName'], dict['projectPath'], dict['swatPath'], close, self.activateBtn)

    def readFiles(self, path):
        
        dict={}
        
        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                key, value = line.split(': ', 1)
                key = key.strip()
                value = value.strip().replace('/', '\\')
                dict[key] = value
                
        return dict
    
    def click_open_project(self):
        
        if Project.projectInfos:
            
            dialog=ReOpenWidget(self.window(), self.click_open_project_)
            dialog.show()
        
        else:
            self.click_open_project_()
    
    def click_open_project_(self):
        
        openPro=OpenProject(self)
        openPro.setWindowModality(Qt.WindowModal)
        res=openPro.exec()
        
        if res:
            
            if openPro.projectFile==None:
                box=MessageBox(title="Errors Occur", content="There is no project file in the selected directory.", parent=self.window())
                box.show()
                return
            
            info=InfoBar.success(
                    title=self.tr('Open Project'),
                    content=self.tr("Loading and checking model files, please wait..."),
                    orient=Qt.Horizontal,
                    isClosable=True,
                    position=InfoBarPosition.TOP_RIGHT,
                    duration=10000,
                    parent=self
                )
            
            def close(time):
                    
                QTimer.singleShot(time, info.close)
            
            projectFile=openPro.projectFile
            projectPath=openPro.projectPath
            dict=self.readFiles(os.path.join(projectPath, projectFile))
            
            Project.window=self
            Project.openProject(dict['projectName'], dict['projectPath'], dict['swatPath'], close, self.activateBtn)
            
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

class ReOpenWidget(MessageBoxBase):
    
    def __init__(self, parent=None, continue_func=None):
        super().__init__(parent)
        
        self.continue_func=continue_func
        
        self.titleLabel=SubtitleLabel("A project has been opened now", self)
        self.contentLabel=BodyLabel("Do you want to create or open another project?", self)

        self.yesButton.setText("Yes")
        self.yesButton.clicked.connect(self.continue_)
        self.yesButton.setFont(getFont(18, QFont.Medium))
        self.cancelButton.setText("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        self.cancelButton.setFont(getFont(18, QFont.Medium))
        
        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.contentLabel)
        
        with path(GUI.qss, "messagebox.qss") as qss_path:
            with open(qss_path) as f:
                self.setStyleSheet(f.read())
        
    
    def continue_(self):
        
        Project.clearAll()
        
        self.continue_func()
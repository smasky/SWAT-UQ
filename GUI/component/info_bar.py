from qfluentwidgets import InfoBar, FluentStyleSheet, getStyleSheet, InfoBarPosition, InfoBarIcon
from PyQt5.QtCore import Qt
from .utility import substitute, MediumSize
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QWidget

class InfoBar_(InfoBar):
    
    def __init__(self, icon, title, content, orient=Qt.Horizontal, isClosable=True, duration=1000, position=InfoBarPosition.TOP_RIGHT, parent=None):
        super().__init__(icon, title, content, orient, isClosable, duration, position, parent)
        
        qss=getStyleSheet(FluentStyleSheet.INFO_BAR)
        qss=substitute(qss, {'#titleLabel': {'font' : f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'"}, '#contentLabel': {'font' : f" {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'"}})
        self.setStyleSheet(qss)
        
    @classmethod
    def new(cls, icon, title, content, orient=Qt.Horizontal, isClosable=True, duration=1000,
            position=InfoBarPosition.TOP_RIGHT, parent=None):
        w = InfoBar_(icon, title, content, orient,
                    isClosable, duration, position, parent)
        w.show()
        return w

    @classmethod
    def info(cls, title, content, orient=Qt.Horizontal, isClosable=True, duration=1000,
             position=InfoBarPosition.TOP_RIGHT, parent=None):
        return cls.new(InfoBarIcon.INFORMATION, title, content, orient, isClosable, duration, position, parent)

    @classmethod
    def success(cls, title, content, orient=Qt.Horizontal, isClosable=True, duration=1000,
                position=InfoBarPosition.TOP_RIGHT, parent=None):
        return cls.new(InfoBarIcon.SUCCESS, title, content, orient, isClosable, duration, position, parent)

    @classmethod
    def warning(cls, title, content, orient=Qt.Horizontal, isClosable=True, duration=1000,
                position=InfoBarPosition.TOP_RIGHT, parent=None):
        return cls.new(InfoBarIcon.WARNING, title, content, orient, isClosable, duration, position, parent)

    @classmethod
    def error(cls, title, content, orient=Qt.Horizontal, isClosable=True, duration=1000,
              position=InfoBarPosition.TOP_RIGHT, parent=None):
        return cls.new(InfoBarIcon.ERROR, title, content, orient, isClosable, duration, position, parent)

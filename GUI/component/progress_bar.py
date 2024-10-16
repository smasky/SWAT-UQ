from qfluentwidgets import ProgressBar
from math import floor

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter,  QFont, QColor

class ProgressBar_(ProgressBar):
    
    def __init__(self, parent=None, useAni=True):
        super().__init__(parent, useAni)
        
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        # draw background
        bc = QColor(128, 141, 124, 50)
        painter.setBrush(bc)
        painter.setPen(Qt.NoPen)  
        y =  floor(self.height() / 2)
        r = self.height() / 2
        painter.drawRoundedRect(0, 0, self.width(), self.height(), r, r)
        if self.minimum() >= self.maximum():
            return

        painter.setPen(Qt.NoPen)    
        painter.setBrush(self.barColor())
        w = int(self.val / (self.maximum() - self.minimum()) * self.width())
        r = self.height() / 2
        painter.drawRoundedRect(0, 0, w, self.height(), r, r)
        
        percentage = int((self.val - self.minimum()) / (self.maximum() - self.minimum()) * 100)
        text = f"{percentage}%" 
              
        if percentage>3:
            painter.setPen(Qt.white)
            font = QFont("Arial", 10, QFont.Bold)
            painter.setFont(font)
            text_width = painter.fontMetrics().width(text)
            text_height = painter.fontMetrics().height()
        
            text_x = max(0, min(w - text_width // 2, self.width() - text_width)) - 20 # 确保文本不会超出边界
            text_y = (self.height() + text_height) // 2 - 3 # 垂直居中

            painter.drawText(text_x, text_y, text)
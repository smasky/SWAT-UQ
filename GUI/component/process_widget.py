from qfluentwidgets import PillToolButton, FluentIcon, SubtitleLabel

from PyQt5.QtWidgets import QHBoxLayout, QFrame, QVBoxLayout
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QColor

from .utility import setFont
class StepWidget(QFrame):
    
    def __init__(self, content, parent=None):
        super().__init__(parent)
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        h=QHBoxLayout()
        
        self.btn=PillToolButton(FluentIcon.ACCEPT_MEDIUM, self)
        self.btn.setFixedSize(45, 35)

        h.addStretch(1);h.addWidget(self.btn);h.addStretch(1)
        vBoxLayout.addLayout(h)
        
        vBoxLayout.addSpacing(5)
        
        label=SubtitleLabel(self.tr(content), self)
        setFont(label)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vBoxLayout.addWidget(label)
        vBoxLayout.addStretch(1)
        
class ProcessWidget(QFrame):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.widgets=[]
        self.btns=[]
        self.hBoxLayout=QHBoxLayout(self)
        self.setFixedHeight(95)
        self.hBoxLayout.setContentsMargins(0, 5, 0, 0)
        
    def addStep(self, i, content):
        
        btnWidget=StepWidget(content, self)
        self.hBoxLayout.addWidget(btnWidget)
        self.widgets.append(btnWidget)
        self.btns.append(btnWidget.btn)
        btnWidget.btn.setEnabled(False)
        if len(self.widgets)==1:
            btnWidget.btn.setChecked(True)
           
    def on_button_clicked(self, index):
    
        self.btns[index].setChecked(True)
        self.update()
    
    def reset(self):
        
        for btn in self.btns:
            btn.setChecked(False)
        
        self.btns[0].setChecked(True)
        
        self.update()
    
    def paintEvent(self, event):
        
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen = QPen(QColor(0, 159, 170), 4)
        painter.setPen(pen)

        previous_widget = None  

        for widget in self.widgets:
            if widget.btn.isChecked():
                if previous_widget is not None:
                    start_x = previous_widget.mapTo(self, previous_widget.btn.pos() + QPoint(previous_widget.btn.width() // 2, previous_widget.btn.height() // 2)).x()
                    start_y = previous_widget.mapTo(self, previous_widget.btn.pos() + QPoint(previous_widget.btn.height() // 2, previous_widget.btn.height() // 2)).y()
                    end_x = widget.mapTo(self, widget.btn.pos() + QPoint(widget.btn.width() // 2, widget.btn.height() // 2)).x()
                    end_y = widget.mapTo(self, widget.btn.pos() + QPoint(widget.btn.height() // 2, widget.btn.height() // 2)).y()
                    painter.drawLine(start_x, start_y, end_x, end_y)

                previous_widget = widget
            else:
                break
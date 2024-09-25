from qfluentwidgets import PillToolButton, BodyLabel, FluentIcon, ToggleButton

from PyQt5.QtWidgets import QSizePolicy, QHBoxLayout, QFrame, QVBoxLayout, QApplication, QWidget, QPushButton

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor
class StepWidget(QFrame):
    
    def __init__(self, content, parent=None):
        super().__init__(parent)
        vBoxLayout=QVBoxLayout(self)
        vBoxLayout.setContentsMargins(0, 0, 0, 0)
        
        h=QHBoxLayout()
        
        self.btn=PillToolButton(FluentIcon.ACCEPT_MEDIUM, self)

        h.addStretch(1);h.addWidget(self.btn);h.addStretch(1)
        vBoxLayout.addLayout(h)
        
        label=BodyLabel(self.tr(content), self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vBoxLayout.addWidget(label)
        vBoxLayout.addStretch(1)
        
class ProcessWidget(QFrame):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.widgets=[]
        self.hBoxLayout=QHBoxLayout(self)
      
    def addStep(self, content):
        
        btnWidget=StepWidget(content, self)
        self.hBoxLayout.addWidget(btnWidget)
        self.widgets.append(btnWidget)
        btnWidget.btn.clicked.connect(self.handleButtonClick)
        
    def handleButtonClick(self):
        
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
    
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    window = QWidget()
    layout = QHBoxLayout(window)

    process=ProcessWidget(window)
    process.addStep("Step1")
    process.addStep("Step2")
    process.addStep("Step3")
    process.addStep("Step4")
    process.addStep("Step5")
    layout.addWidget(process)

    window.setLayout(layout)
    window.setWindowTitle('步骤进度条')
    window.show()

    window.update()
    sys.exit(app.exec_())
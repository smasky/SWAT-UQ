from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen, QColor, QIcon
from PyQt5.QtCore import Qt, QSize

class StepButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setMinimumSize(QSize(80, 80))
        if icon_path:
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(40, 40))
        self.setStyleSheet(self.default_style())

    def set_complete(self):
        self.setStyleSheet(self.complete_style())

    def set_current(self):
        self.setStyleSheet(self.current_style())

    def set_incomplete(self):
        self.setStyleSheet(self.default_style())

    def default_style(self):
        return """
        QPushButton {
            background-color: lightgrey;
            border-radius: 40px;
            border: 2px solid grey;
        }
        """

    def complete_style(self):
        return """
        QPushButton {
            background-color: green;
            border-radius: 40px;
            border: 2px solid green;
        }
        """

    def current_style(self):
        return """
        QPushButton {
            background-color: blue;
            border-radius: 40px;
            border: 2px solid blue;
        }
        """

class StepProgressWidget(QWidget):
    def __init__(self, steps, parent=None):
        super().__init__(parent)
        self.steps = steps
        self.current_step = 0
        self.init_ui()

    def init_ui(self):
        self.layout = QHBoxLayout(self)
        
        for i, step in enumerate(self.steps):
            button = StepButton(step['name'], step['icon'])
            button.clicked.connect(lambda checked, idx=i: self.on_step_clicked(idx))
            self.layout.addWidget(button)

            if i < self.current_step:
                button.set_complete()
            elif i == self.current_step:
                button.set_current()
                button.setChecked(True)
            else:
                button.set_incomplete()

        self.setLayout(self.layout)

    def on_step_clicked(self, index):
        self.current_step = index
        self.update_lines_and_buttons()

    def update_lines_and_buttons(self):
        for i in range(len(self.steps)):
            button = self.layout.itemAt(i).widget()
            if i < self.current_step:
                button.set_complete()
            elif i == self.current_step:
                button.set_current()
                button.setChecked(True)
            else:
                button.set_incomplete()
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen()
        pen.setWidth(4)

        button_positions = []
        for i in range(self.layout.count()):
            widget = self.layout.itemAt(i).widget()
            if widget:
                rect = widget.geometry()
                button_positions.append(rect.center().x())

        for i in range(1, len(button_positions)):
            if i <= self.current_step:
                pen.setColor(QColor('green'))
            else:
                pen.setColor(QColor('lightgrey'))
            painter.setPen(pen)
            painter.drawLine(button_positions[i-1], self.height()/2, button_positions[i], self.height()/2)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    steps = [
        {'name': '订单', 'icon': None},
        {'name': '购物车', 'icon': None},
        {'name': '账户信息', 'icon': None},
        {'name': '配送', 'icon': None},
        {'name': '支付', 'icon': None},
    ]

    window = QWidget()
    layout = QVBoxLayout(window)

    step_widget = StepProgressWidget(steps)
    layout.addWidget(step_widget)

    window.setLayout(layout)
    window.setWindowTitle('步骤进度条')
    window.show()

    sys.exit(app.exec_())
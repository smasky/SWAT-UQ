from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFormLayout, QSpacerItem, QSizePolicy, QRadioButton, QButtonGroup
from PyQt5.QtCore import Qt

class BodyLabel(QLabel):
    def __init__(self, text):
        super().__init__(text)

class ButtonGroup(QButtonGroup):
    def __init__(self, options, exclusive, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(parent)
        for option in options:
            button = QRadioButton(option)
            self.addButton(button)
            layout.addWidget(button)

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        vBoxLayout = QVBoxLayout()

        # 创建 QFormLayout
        h = QFormLayout()
        h.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # 添加第一个 ButtonGroup
        line1 = QButtonGroup(["Option 1", "Option 2", "Option 3"], True, self)
        self.saBtnGroup = line1
        h.addRow(QLabel("Sensibility Analysis:"), self.saBtnGroup)

        # 添加第二个 ButtonGroup
        line2 = QButtonGroup(["Method 1", "Method 2", "Method 3"], False, self)
        self.smBtnGroup = line2
        h.addRow(QLabel("Sampling Method:"), self.smBtnGroup)

        # 创建一个 QHBoxLayout 并添加左右两侧的 QSpacerItem
        hb = QHBoxLayout()
        spacer_left = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        spacer_right = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        hb.addItem(spacer_left)   # 左侧的可伸缩空白
        hb.addLayout(h)           # 中间的表单布局
        hb.addItem(spacer_right)  # 右侧的可伸缩空白

        # 将 hb 添加到 vBoxLayout
        vBoxLayout.addLayout(hb)
        self.setLayout(vBoxLayout)

if __name__ == "__main__":
    app = QApplication([])
    window = MyWidget()
    window.show()
    app.exec_()

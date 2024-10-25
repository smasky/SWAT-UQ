import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QFont, QPen
from PyQt5.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建一个 PlotWidget 对象
        self.graphWidget = pg.PlotWidget()
        self.setCentralWidget(self.graphWidget)

        # 设置背景为白色
        self.graphWidget.setBackground('w')

        # 生成一些数据
        x = np.arange(500)
        y = np.random.normal(size=(500,))

        # 设置线条样式
        pen = QPen(Qt.blue)
        pen.setWidth(0.5)  # 线条加粗为3像素宽
        self.graphWidget.plot(x, y, pen=pen)

        # 设置坐标轴边框加粗
        axisPen = QPen(Qt.black)
        axisPen.setWidth(2)  # 图框加粗为2像素宽
        self.graphWidget.getAxis('bottom').setPen(axisPen)
        self.graphWidget.getAxis('left').setPen(axisPen)

        # 设置字体为 Arial 并调整大小
        font = QFont('Arial', 14)  # 直接在创建时设置字体大小
        self.graphWidget.getAxis('bottom').setTickFont(font)
        self.graphWidget.getAxis('left').setTickFont(font)

        # 设置坐标轴标签颜色为黑色
        labelPen = QPen(Qt.black)
        self.graphWidget.getAxis('bottom').setLabel('Index', units='s', font=font, color=labelPen)
        self.graphWidget.getAxis('left').setLabel('Value', units='V', font=font, color=labelPen)

        # 设置窗口标题和大小
        self.setWindowTitle('PyQtGraph Styled Example')
        self.setGeometry(100, 100, 600, 500)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())

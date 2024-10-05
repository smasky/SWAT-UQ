import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
import pyqtgraph as pg
import numpy as np

class InteractiveBarGraph(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置窗口
        self.setWindowTitle('Interactive Bar Graph')
        self.setGeometry(100, 100, 800, 600)

        # 设置绘图小部件
        self.plot_widget = pg.PlotWidget()
        self.setCentralWidget(self.plot_widget)

        # 设置背景颜色
        self.plot_widget.setBackground('w')  # 白色背景

        # 数据
        self.x = np.array([1, 2, 3, 4, 5])
        self.y = np.random.randint(1, 20, size=5)

        # 创建柱状图，使用渐变色
        brush = pg.mkBrush(color=(100, 100, 250, 180))  # 淡蓝色，带透明度
        self.bar_graph = pg.BarGraphItem(x=self.x, height=self.y, width=0.6, brush=brush)
        self.plot_widget.addItem(self.bar_graph)

        # 设置计时器，用于动态更新数据
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # 每秒更新一次

        # 添加鼠标移动事件
        self.plot_widget.scene().sigMouseMoved.connect(self.mouseMoved)

        # 创建标签用于显示数据
        self.label = pg.TextItem("", anchor=(0.5, 0), color='black')  # 黑色字体
        self.plot_widget.addItem(self.label)

    def update_data(self):
        # 动态更新柱状图数据
        self.y = np.random.randint(1, 20, size=5)
        self.bar_graph.setOpts(height=self.y)

    def mouseMoved(self, evt):
        # 获取鼠标位置
        pos = evt
        if self.plot_widget.sceneBoundingRect().contains(pos):
            mouse_point = self.plot_widget.plotItem.vb.mapSceneToView(pos)
            index = int(mouse_point.x())
            if 0 <= index < len(self.x):
                self.label.setText(f"x: {self.x[index]}, y: {self.y[index]}")
                self.label.setPos(self.x[index], self.y[index])

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InteractiveBarGraph()
    window.show()
    sys.exit(app.exec_())
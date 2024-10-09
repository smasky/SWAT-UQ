import sys
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton, QApplication, QWidget
from PyQt5.QtGui import QMovie


class LoadingDialog(QDialog):
    def __init__(self, parent=None):
        super(LoadingDialog, self).__init__(parent)
        self.setWindowTitle("Loading...")
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)
        self.setModal(True)  # 设置为模态对话框

        layout = QVBoxLayout()
        self.label = QLabel(self)
        layout.addWidget(self.label)

        self.movie = QMovie("loading.gif")  # 使用一个转圈的GIF动画
        self.label.setMovie(self.movie)
        self.movie.start()

        self.setLayout(layout)
        self.setFixedSize(200, 200)  # 可以根据需求调整大小


class LongTask(QThread):
    task_finished = pyqtSignal()

    def run(self):
        # 模拟一个耗时任务
        import time
        time.sleep(5)
        self.task_finished.emit()


class Example(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 创建布局和按钮
        self.button = QPushButton("Start Task", self)
        self.button.clicked.connect(self.startTask)

        layout = QVBoxLayout(self)
        layout.addWidget(self.button)

        self.setLayout(layout)
        self.setWindowTitle('Loading Dialog Example')
        self.setGeometry(300, 300, 300, 200)
        self.show()

    def startTask(self):
        # 创建加载对话框
        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()

        # 启动后台任务
        self.thread = LongTask()
        self.thread.task_finished.connect(self.onTaskFinished)
        self.thread.start()

    def onTaskFinished(self):
        # 任务完成后关闭加载动画
        self.loading_dialog.accept()  # 关闭对话框
        self.button.setText("Task Finished")  # 更新主界面状态


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())

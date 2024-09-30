from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import QThread, QObject, pyqtSignal
import sys
import time

# 定义一个 Project 类来保存共享的数据
class Project:
    def __init__(self):
        self.name = "My Shared Project"
        self.data = "Some shared data"

    def set_data(self, new_data):
        self.data = new_data


# 定义一个工作线程类
class Worker(QObject):
    # 定义信号，用来通知主线程工作完成
    finished = pyqtSignal()

    def run(self):
        # 模拟一些耗时任务
        time.sleep(3)
        print("Worker 线程完成任务")
        # 发射信号通知主线程
        self.finished.emit()


# 创建一个共享的 QWidget，读取和修改 Project 中的数据
class MainWindow(QWidget):
    def __init__(self, project):
        super().__init__()
        self.project = project
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.label = QLabel(f"Project Name: {self.project.name}")
        self.data_label = QLabel(f"Data: {self.project.data}")
        self.button = QPushButton("Start Worker Thread")
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.data_label)
        self.layout.addWidget(self.button)
        self.setLayout(self.layout)

        # 按钮点击时启动线程
        self.button.clicked.connect(self.start_worker)

    def start_worker(self):
        # 创建并启动线程
        self.thread = QThread()
        self.worker = Worker()
        self.worker.moveToThread(self.thread)

        # 当 worker 完成工作后，通知主线程
        self.worker.finished.connect(self.on_worker_finished)

        # 线程启动后执行 run 函数
        self.thread.started.connect(self.worker.run)

        # 启动线程
        self.thread.start()

    def on_worker_finished(self):
        print("主线程收到完成信号，线程即将退出")
        # 确保线程完成任务后安全退出
        self.thread.quit()
        if self.thread.wait():  # 等待线程完全退出
            print("线程已退出")


# 主函数
def main():
    app = QApplication(sys.argv)

    # 创建一个共享的 Project 实例
    shared_project = Project()

    # 创建主窗口，传入共享 Project 实例
    main_window = MainWindow(shared_project)

    # 显示窗口
    main_window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
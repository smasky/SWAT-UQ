from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication
import sys

# 定义一个工作类
class Worker(QObject):
    # 定义 finished 信号
    finished = pyqtSignal()

    def run(self):
        print("任务开始执行...")
        self.task_complete()
        # QTimer.singleShot(2000, self.task_complete)  # 模拟一个耗时任务

    def task_complete(self):
        print("任务执行完成，发出 finished 信号")
        self.finished.emit()  # 发射信号，通知任务完成

# 主函数
def main():
    app = QApplication(sys.argv)

    # 创建线程
    thread = QThread()

    # 创建工作对象，并将其移动到新线程中
    worker = Worker()
    worker.moveToThread(thread)

    # 当线程开始时，启动工作任务
    thread.started.connect(worker.run)

    # 当任务完成时，线程退出
    worker.finished.connect(thread.quit)
    worker.finished.connect(lambda: print("任务完成，线程将退出"))

    # 监听线程的完成信号
    thread.finished.connect(lambda: print("线程已退出"))

    # 启动线程
    thread.start()

    # 启动应用程序事件循环
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
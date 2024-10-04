import sys
import time
import numpy as np
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QProgressBar, QPushButton, QVBoxLayout, QWidget

class Worker(QObject):
    updateProcess = pyqtSignal(float)  # 进度信号
    result = pyqtSignal(object)        # 结果信号

    def __init__(self, numParallel):
        super(Worker, self).__init__()
        self.numParallel = numParallel  # 并行数

    def _subprocess(self, data, idx):
        # 模拟耗时操作
        time.sleep(1)
        # 返回子线程的计算结果
        return idx, np.random.rand(1)[0]

    def test(self, X):
        print("Running in thread:", threading.current_thread().name)  # 打印当前线程名称
        n = X.shape[0]
        Y = np.zeros((n, 1))  # 用于存储结果
        count = 0
        
        # 使用 ThreadPoolExecutor 执行子任务
        with ThreadPoolExecutor(max_workers=self.numParallel) as executor:
            futures = [executor.submit(self._subprocess, X[i, :], i) for i in range(n)]
            
            # 等待每个任务完成并更新进度
            for future in as_completed(futures):
                idx, obj_value = future.result()  # 获取结果
                Y[idx, :] = obj_value  # 存储结果
                
                count += 1
                percent = (count / n) * 100
                self.updateProcess.emit(percent)  # 发射进度信号

        self.result.emit(Y)  # 最后发射结果信号

class WorkerThread(QThread):
    def __init__(self, worker, X):
        super().__init__()
        self.worker = worker
        self.X = X

    def run(self):
        self.worker.test(self.X)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Thread Example")

        # 创建进度条和按钮
        self.progressBar = QProgressBar(self)
        self.progressBar.setRange(0, 100)
        self.button = QPushButton("Start Test", self)
        self.button.clicked.connect(self.start_test)

        # 布局
        layout = QVBoxLayout()
        layout.addWidget(self.progressBar)
        layout.addWidget(self.button)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # 创建 worker
        self.worker = Worker(numParallel=4)  # 使用4个并行任务

        # 连接信号和槽
        self.worker.updateProcess.connect(self.update_progress)
        self.worker.result.connect(self.handle_result)

    def start_test(self):
        # 禁用按钮以防止重复点击
        self.button.setEnabled(False)
        X = np.random.rand(10, 5)  # 模拟输入

        # 创建并启动线程
        self.thread = WorkerThread(self.worker, X)
        self.thread.finished.connect(self.thread.deleteLater)  # 确保线程完成后被清理
        self.thread.start()

    def update_progress(self, value):
        self.progressBar.setValue(int(value))  # 更新进度条

    def handle_result(self, Y):
        print("Test finished, received result:", Y)
        # 任务完成后恢复按钮
        self.button.setEnabled(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

import sys
from PyQt5.QtCore import QThread, QObject, pyqtSignal,QTimer
from PyQt5.QtWidgets import QApplication
import os

class SWAT_UQ_Flow(QObject):
    finished = pyqtSignal()  # 自定义信号，表示任务完成

    # def __init__(self, work_path, paras_file_name, observed_file_name, swat_exe_name, temp_path, max_threads, num_parallel, verbose):
    #     super().__init__()
    #     # 假设你的对象有一些初始化参数
    #     self.work_path = work_path
    #     self.paras_file_name = paras_file_name
    #     self.observed_file_name = observed_file_name
    #     self.swat_exe_name = swat_exe_name
    #     self.temp_path = temp_path
    #     self.max_threads = max_threads
    #     self.num_parallel = num_parallel
    #     self.verbose = verbose

    def test(self):
        # 模拟任务执行
        print("任务正在执行...")
        
        # 模拟任务的延时操作
        # import time
        # time.sleep(2)  # 模拟一个2秒的延时任务
        
        print("任务执行完成...")
        self.emit()  # 发出任务完成信号
        print('1111')
    
    def test2(self):
        print('2222')
    
    def emit(self):
        QThread.currentThread().quit()  # 退出当前线程
        self.finished.emit()  # 发出任务完成信号
        

def main():
    # 创建 QApplication 实例
    app = QApplication(sys.argv)

    # 假设这些路径都是已经定义好的路径
    file_path = "some_path"
    temp_path = os.path.join("project_path", "temp")
    swat_exe_name = "swat_exe_name"
    observed_file_name = os.path.join("project_path", "observed_file")
    paras_file_name = os.path.join("project_path", "paras_file")

    # 创建对象
    swat_cup = SWAT_UQ_Flow()

    # 创建线程
    qThread1 = QThread()

    # 将 swat_cup 移动到 qThread1
    swat_cup.moveToThread(qThread1)

    # 任务完成后，将对象迁移回主线程
    def move_back_to_main_thread():
        print("正在将对象迁移回主线程")
        swat_cup.moveToThread(QApplication.instance().thread())
    def move():
        qThread2=QThread()
        swat_cup.moveToThread(qThread2)
        qThread2.started.connect(swat_cup.test2)
        qThread2.start()
    # 连接信号和槽
    # 连接信号和槽
    qThread1.started.connect(swat_cup.test)  # 线程开始时执行 test
    # swat_cup.finished.connect(move_back_to_main_thread)  # 任务完成时迁移回主线程
    swat_cup.finished.connect(qThread1.quit)
    swat_cup.finished.connect(lambda: print("任务完成，线程将退出"))

    # 监听线程的完成信号
    qThread1.finished.connect(lambda: print("线程已退出"))
    qThread1.finished.connect(move)
    # 启动线程
    qThread1.start()
    # def delayed_wait():
    #         print("调用 thread.wait() 等待线程完全结束...")
    #         qThread1.wait()

        # 在 thread.finished 之后，使用 QTimer 延迟调用 wait()
    # qThread1.finished.connect(lambda: QTimer.singleShot(100, delayed_wait))
    # 等待线程结束后继续
    # qThread1.wait()
    

    # 线程结束后，swat_cup 应该已经被迁移回主线程
    print(f"swat_cup 当前线程: {swat_cup.thread()}")

    # 启动主事件循环
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
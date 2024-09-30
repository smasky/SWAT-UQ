from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import sys
import os
from GUI import MainWindow

if __name__ == "__main__":
    # 设置高 DPI 缩放
    # os.environ["QT_SCALE_FACTOR"] = "0.8" 
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # 使能高 DPI 缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # 使得图片元素也遵循缩放
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    app.exec() 
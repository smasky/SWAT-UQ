from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import sys
from GUI import MainWindow
import os


if __name__ == "__main__":
    
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"  # 禁用 Qt 自动缩放
    os.environ["QT_SCALE_FACTOR"] = "1.8"  # 禁用 Qt 自动缩放
    
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # 使能高 DPI 缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # 使得图片元素也遵循缩放
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    app.exec()
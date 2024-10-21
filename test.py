from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import Qt
import sys
from GUI import MainWindow
import os


if __name__ == "__main__":
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # 使能高 DPI 缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # 使得图片元素也遵循缩放

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)  # 禁止 Qt 自动创建窗口
    
    demo = MainWindow()
    demo.show()
    app.exec_()
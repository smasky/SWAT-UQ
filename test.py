from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import Qt
import sys
from GUI import MainWindow
import os

def get_screen_scaling_factor(app):
    # 获取主屏幕
    screen = app.primaryScreen()
    
    # 获取逻辑 DPI 和物理 DPI
    logical_dpi = screen.logicalDotsPerInch()
    physical_dpi = screen.physicalDotsPerInch()
    
    # 计算缩放比例
    scaling_factor = (logical_dpi / 96)
    
    os.environ['QT_SCALING_FACTOR'] = str(scaling_factor)  # 设置环境变量 QT_SCALE_FACTOR
    
    return scaling_factor

if __name__ == "__main__":
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # 使能高 DPI 缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # 使得图片元素也遵循缩放

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)  # 禁止 Qt 自动创建窗口
    
    get_screen_scaling_factor(app)
    
    
    demo = MainWindow()
    demo.show()
    app.exec_()
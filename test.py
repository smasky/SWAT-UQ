from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import Qt
import sys
from GUI import MainWindow
import os

def calculate_scale_factor(target_width, target_height, base_width=3072, base_height=1920, base_scale=1.8):
    
    width_ratio = target_width / base_width
    height_ratio = target_height / base_height
    
    scale_ratio = min(width_ratio, height_ratio)
    
    new_scale = base_scale * scale_ratio
    return new_scale

if __name__ == "__main__":
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # 使能高 DPI 缩放
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)  # 使得图片元素也遵循缩放

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)  # 禁止 Qt 自动创建窗口

    screen = QDesktopWidget().screenGeometry()
    width = screen.width()
    height = screen.height()
    
    scaler=calculate_scale_factor(width, height)
    
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"  # 禁用 Qt 自动缩放
    os.environ["QT_SCALE_FACTOR"] = f"{scaler}"  # 禁用 Qt 自动缩放
    
    demo = MainWindow()
    demo.show()
    app.exec_()
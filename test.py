from PyQt5.QtWidgets import QApplication, QDesktopWidget
from PyQt5.QtCore import Qt
import sys
from GUI import MainWindow
import os

def get_text_scaling_factor():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # 获取主屏幕对象
    screen = app.primaryScreen()

    # 使用逻辑 DPI 和物理 DPI 计算缩放比例
    logical_dpi = screen.logicalDotsPerInch()
    base_dpi = 96  # Windows的标准基准DPI

    # 计算文本缩放系数
    scaling_factor = logical_dpi / base_dpi

    # 存储在环境变量中
    os.environ['QT_TEXT_SCALING_FACTOR'] = str(scaling_factor)

    print(f"Text Scaling Factor: {scaling_factor * 100:.0f}%")
    return scaling_factor

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

    desktop = app.desktop()
    
    # 获取主屏幕的DPI
    logical_dpi = desktop.logicalDpiX()  # 水平逻辑 DPI
    physical_dpi = desktop.physicalDpiX()  # 水平物理 DPI
    
    # 计算缩放比例
    scaling_factor = get_text_scaling_factor()
    
    # os.environ["QT_SCALING_FACTOR"] = str(scaling_factor)  # 启用 Qt 自动缩放
    
    # screen = QDesktopWidget().screenGeometry()
    # width = screen.width()
    # height = screen.height()
    
    # scaler=calculate_scale_factor(width, height)
    
    # os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"  # 禁用 Qt 自动缩放
    # os.environ["QT_SCALE_FACTOR"] = f"{scaler}"  # 禁用 Qt 自动缩放
    
    demo = MainWindow()
    demo.show()
    app.exec_()
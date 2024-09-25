from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton

class EllipseButtonDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 创建一个 QPushButton
        self.button = QPushButton("Ellipse Button", self)
        
        # 设置按钮固定大小
        self.button.setFixedSize(180, 100)  # 设置宽度为 180px, 高度为 100px
        
        # 使用样式表设置椭圆形外观
        self.button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;    /* 按钮的背景色 */
                color: white;                 /* 按钮的文字颜色 */
                border: none;                 /* 去除边框 */
                border-radius: 50px;          /* 设置圆角半径为高度的一半 */
            }
            QPushButton:pressed {
                background-color: #2980b9;    /* 按钮被按下时的背景色 */
            }
        """)

        # 设置布局
        layout = QVBoxLayout(self)
        layout.addWidget(self.button)
        self.setLayout(layout)
        self.setWindowTitle("Ellipse QPushButton Example")

# 应用的入口点
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = EllipseButtonDemo()
    window.show()
    sys.exit(app.exec_())
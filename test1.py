from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QProgressBar

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        # 创建一个 QVBoxLayout
        layout = QVBoxLayout()

        # 创建一个 QProgressBar
        progressBar = QProgressBar()
        progressBar.setValue(50)  # 设置进度值

        # 设置样式表去掉黑边
        # progressBar.setStyleSheet("""
        #     QProgressBar {
        #         border: 0px;  /* 去掉边框 */
        #         text-align: center;  /* 文本居中 */
        #         background-color: #E0E0E0;  /* 背景颜色 */
        #     }
        #     QProgressBar::chunk {
        #         background-color: #3B5998;  /* 进度条颜色 */
        #     }
        # """)

        # 添加进度条到布局
        layout.addWidget(progressBar)

        # 设置窗口布局
        self.setLayout(layout)

# 启动应用程序
app = QApplication([])
window = MyWindow()
window.show()
app.exec_()

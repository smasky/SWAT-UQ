from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QSizePolicy

# 创建应用程序实例
app = QApplication([])

# 创建主窗口
window = QWidget()

# 创建布局
layout = QVBoxLayout()

# 创建按钮并设置扩展策略
button1 = QPushButton("Button 1")
button1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 水平和垂直方向都扩展

button2 = QPushButton("Button 2")
button2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 水平和垂直方向都扩展

# 将按钮添加到布局
layout.addWidget(button1)
layout.addWidget(button2)

# 为窗口设置布局
window.setLayout(layout)

# 显示窗口
window.show()

# 进入事件循环
app.exec_()
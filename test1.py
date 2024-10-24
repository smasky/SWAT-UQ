from PyQt5.QtWidgets import QApplication, QTreeWidget, QTreeWidgetItem
import sys

# 创建应用实例
app = QApplication(sys.argv)

# 创建 QTreeWidget 对象
tree = QTreeWidget()
tree.setColumnCount(2)
tree.setHeaderLabels(['Optimization Iters', 'Best Obj Value'])

# 示例数据和对应的完整工具提示信息
data = [
    ("iter 000", "Objs: 13083.38 | Decs: 49.76, -10.79, -2.84, 30.48, 15.52, 20..."),
    ("iter 001", "Objs: 12357.52 | Decs: 10.82, -30.84, -33.01, 32.67, 35.27, 27..."),
    # 添加更多项...
]

# 添加项目并设置工具提示
for entry in data:
    item = QTreeWidgetItem(tree, [entry[0], entry[1].split("|")[0] + "..."])
    # 设置工具提示显示完整的信息
    item.setToolTip(1, entry[1])

# 显示树状结构
tree.show()

# 运行应用
sys.exit(app.exec_())

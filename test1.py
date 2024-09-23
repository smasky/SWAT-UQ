from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QTreeWidget, QTreeWidgetItem, QPushButton)
from PyQt5.QtCore import Qt


class ParameterSelectionWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # 主布局
        layout = QHBoxLayout()

        # 左侧树控件 (Source)
        self.sourceTree = QTreeWidget()
        self.sourceTree.setHeaderLabel("Source Parameters")
        self.sourceTree.setColumnCount(1)
        self.populateSourceTree()
        # 设置左侧树表头字体颜色为黑色并添加黑色边框
        self.sourceTree.header().setStyleSheet("QHeaderView::section { color: black; }")
        self.sourceTree.setStyleSheet("QTreeWidget { border: 1px solid black; }")

        # 右侧树控件 (Target)
        self.targetTree = QTreeWidget()
        self.targetTree.setHeaderLabel("Target Parameters")
        self.targetTree.setColumnCount(1)
        # 设置右侧树表头字体颜色为黑色并添加黑色边框
        self.targetTree.header().setStyleSheet("QHeaderView::section { color: black; }")
        self.targetTree.setStyleSheet("QTreeWidget { border: 1px solid black; }")

        # 中间控制按钮
        btnLayout = QVBoxLayout()
        self.btnToRight = QPushButton(">")
        self.btnToLeft = QPushButton("<")
        btnLayout.addStretch()
        btnLayout.addWidget(self.btnToRight)
        btnLayout.addWidget(self.btnToLeft)
        btnLayout.addStretch()

        self.btnToRight.clicked.connect(self.moveToRight)
        self.btnToLeft.clicked.connect(self.removeSelectedFromTarget)

        # 设置布局
        layout.addWidget(self.sourceTree)
        layout.addLayout(btnLayout)
        layout.addWidget(self.targetTree)

        self.setLayout(layout)
        self.setWindowTitle('Parameter Selection with Tree and Checkboxes')
        self.resize(800, 600)

    def populateSourceTree(self):
        """Populate the source tree with some example data"""
        parent1 = QTreeWidgetItem(self.sourceTree, ['Parent 1'])
        parent1.setFlags(parent1.flags() | Qt.ItemIsUserCheckable)
        parent1.setCheckState(0, Qt.Unchecked)
        child1 = QTreeWidgetItem(parent1, ['Child 1'])
        child1.setFlags(child1.flags() | Qt.ItemIsUserCheckable)
        child1.setCheckState(0, Qt.Unchecked)
        child2 = QTreeWidgetItem(parent1, ['Child 2'])
        child2.setFlags(child2.flags() | Qt.ItemIsUserCheckable)
        child2.setCheckState(0, Qt.Unchecked)

        parent2 = QTreeWidgetItem(self.sourceTree, ['Parent 2'])
        parent2.setFlags(parent2.flags() | Qt.ItemIsUserCheckable)
        parent2.setCheckState(0, Qt.Unchecked)
        child3 = QTreeWidgetItem(parent2, ['Child 3'])
        child3.setFlags(child3.flags() | Qt.ItemIsUserCheckable)
        child3.setCheckState(0, Qt.Unchecked)

        self.sourceTree.expandAll()

    def moveToRight(self):
        """Move selected items from source tree to target tree"""
        selectedItems = self.sourceTree.selectedItems()

        for item in selectedItems:
            if item.parent() is None:
                # 这是一级标题
                parentText = item.text(0)
                existingItems = self.targetTree.findItems(parentText, Qt.MatchExactly, 0)

                if not existingItems:
                    # 如果目标树没有这个一级标题，则创建
                    parentClone = QTreeWidgetItem(self.targetTree, [parentText])
                    parentClone.setFlags(parentClone.flags() | Qt.ItemIsUserCheckable)
                    parentClone.setCheckState(0, item.checkState(0))
                    self.copyChildren(item, parentClone)
                else:
                    # 如果已存在，则将子项加入现有的一级标题
                    existingParent = existingItems[0]
                    self.copyChildren(item, existingParent)
            else:
                # 子项需要找到对应的父项进行添加
                parentItem = item.parent()
                parentText = parentItem.text(0)
                existingParents = self.targetTree.findItems(parentText, Qt.MatchExactly, 0)

                if existingParents:
                    parentClone = existingParents[0]
                    childClone = QTreeWidgetItem(parentClone, [item.text(0)])
                    childClone.setFlags(childClone.flags() | Qt.ItemIsUserCheckable)
                    childClone.setCheckState(0, item.checkState(0))

    def copyChildren(self, sourceItem, targetItem):
        """递归复制子项"""
        for i in range(sourceItem.childCount()):
            sourceChild = sourceItem.child(i)
            existingChildren = [targetItem.child(j).text(0) for j in range(targetItem.childCount())]
            if sourceChild.text(0) not in existingChildren:
                childClone = QTreeWidgetItem(targetItem, [sourceChild.text(0)])
                childClone.setFlags(childClone.flags() | Qt.ItemIsUserCheckable)
                childClone.setCheckState(0, sourceChild.checkState(0))
                self.copyChildren(sourceChild, childClone)

    def removeSelectedFromTarget(self):
        """Remove selected items from target tree"""
        selectedItems = self.targetTree.selectedItems()
        for item in selectedItems:
            index = self.targetTree.indexOfTopLevelItem(item)
            if index != -1:
                self.targetTree.takeTopLevelItem(index)
            else:
                item.parent().removeChild(item)


if __name__ == '__main__':
    app = QApplication([])
    window = ParameterSelectionWindow()
    window.show()
    app.exec_()
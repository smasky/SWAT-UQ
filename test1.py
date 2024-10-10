from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTreeWidgetItem,
                             QPushButton, QLineEdit, QLabel, QCompleter)
from qfluentwidgets import TreeWidget, PrimaryToolButton, FluentIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

class DoubleTreeWidget(QWidget):
    
    def __init__(self, leftOptions, rightOptions, selected, parent=None):
        super().__init__(parent)
        self.leftOptions = leftOptions
        self.rightOptions = rightOptions
        self.initUI()
        
        if selected is not None:
            self.populateTree(self.targetTree, selected)
            
        self.sourceTree.header().setStyleSheet("QHeaderView::section { color: black; }")
        self.targetTree.header().setStyleSheet("QHeaderView::section { color: black; }")
        
    def initUI(self):
        layout = QVBoxLayout()

        # 添加搜索框
        searchLayout = QHBoxLayout()
        self.searchBox = QLineEdit()
        self.searchBox.setPlaceholderText("Search...")
        self.searchBox.textChanged.connect(self.filterTree)  # 连接搜索框文本变化事件

        # 添加重置按钮
        self.resetButton = QPushButton("Reset")
        self.resetButton.clicked.connect(self.resetSearch)

        # 设置自动完成器
        self.completer = QCompleter(self.getAllItems(self.leftOptions))
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.searchBox.setCompleter(self.completer)

        searchLayout.addWidget(QLabel("Search:"))
        searchLayout.addWidget(self.searchBox)
        searchLayout.addWidget(self.resetButton)

        self.sourceTree = TreeWidget()
        self.sourceTree.setHeaderLabel("Source Parameters")
        
        self.targetTree = TreeWidget()
        self.targetTree.setHeaderLabel("Target Parameters")
        
        self.populateTree(self.sourceTree, self.leftOptions)
        self.populateTree(self.targetTree, self.rightOptions)

        btnLayout = QVBoxLayout()
        self.btnToRight = PrimaryToolButton(FluentIcon.RIGHT_ARROW, self)
        self.btnToLeft = PrimaryToolButton(FluentIcon.LEFT_ARROW, self)
        btnLayout.addStretch()
        btnLayout.addWidget(self.btnToRight)
        btnLayout.addWidget(self.btnToLeft)
        btnLayout.addStretch()

        self.btnToRight.clicked.connect(self.moveToRight)
        self.btnToLeft.clicked.connect(self.removeSelectedFromTarget)

        # 添加搜索框和树控件到布局
        treeLayout = QHBoxLayout()
        treeLayout.addWidget(self.sourceTree)
        treeLayout.addLayout(btnLayout)
        treeLayout.addWidget(self.targetTree)

        layout.addLayout(searchLayout)
        layout.addLayout(treeLayout)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def getAllItems(self, content):
        """获取所有项目名称"""
        items = []
        for key, values in content.items():
            items.append(key)
            items.extend(values)
        return items

    def filterTree(self):
        searchText = self.searchBox.text().lower()
        root = self.sourceTree.invisibleRootItem()
        self.filterTreeItems(root, searchText)

    def filterTreeItems(self, item, searchText):
        hasMatchingChild = False
        for i in range(item.childCount()):
            child = item.child(i)
            childMatch = self.filterTreeItems(child, searchText)
            if childMatch:
                hasMatchingChild = True
            child.setHidden(searchText not in child.text(0).lower() and not childMatch)

        # 如果当前项目或其子项目匹配，则展开父项目
        if searchText in item.text(0).lower() or hasMatchingChild:
            item.setExpanded(True)
            return True
        else:
            item.setExpanded(False)
            return False

    def hasVisibleChildren(self, item):
        for i in range(item.childCount()):
            if not item.child(i).isHidden():
                return True
        return False

    def populateTree(self, widget, content):
        if isinstance(content, dict):
            keys = list(content.keys())
            rootItems = {}
            for key in keys:
                rootItem = QTreeWidgetItem(widget, [key])
                rootItems[key] = rootItem

            for rootItem in rootItems.values():
                rootItem.setFlags(rootItem.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                rootItem.setCheckState(0, Qt.Unchecked)

            for key, value in content.items():
                self.addChildItems(rootItems[key], value)
    
    def addChildItems(self, parent, children):
        for child in children:
            childItem = QTreeWidgetItem(parent, [child])
            childItem.setFlags(childItem.flags() | Qt.ItemIsUserCheckable)
            childItem.setCheckState(0, Qt.Unchecked)

    def moveToRight(self):
        self.copyCheckedChildItems(self.sourceTree.invisibleRootItem())
        self.uncheckAllItems(self.sourceTree.invisibleRootItem())
        self.resetSearch()

    def copyCheckedChildItems(self, sourceRoot):
        for i in range(sourceRoot.childCount()):
            sourceChild = sourceRoot.child(i)

            if sourceChild.isHidden():
                continue  # 跳过隐藏的项目

            if not self.targetTree.findItems(sourceChild.text(0), Qt.MatchExactly, 0) and sourceChild.childCount() == 0:
                if sourceChild.checkState(0) == Qt.Checked:
                    child = QTreeWidgetItem(self.targetTree, [sourceChild.text(0)])
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                    child.setCheckState(0, Qt.Unchecked)
            
            for j in range(sourceChild.childCount()):
                subChild = sourceChild.child(j)
                if subChild.isHidden():
                    continue  # 跳过隐藏的子项目

                if subChild.checkState(0) == Qt.Checked:
                    if not self.targetTree.findItems(sourceChild.text(0), Qt.MatchExactly, 0):
                        child = QTreeWidgetItem(self.targetTree, [sourceChild.text(0)])
                        child.setFlags(child.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                        child.setCheckState(0, Qt.Unchecked)
                        
                        self.addChildItems(child, [subChild.text(0)])
                        child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                        child.setCheckState(0, Qt.Unchecked)
                    else:
                        child = self.targetTree.findItems(sourceChild.text(0), Qt.MatchExactly, 0)[0]
                        self.addChildItems(child, [subChild.text(0)])
                    
                    child.setExpanded(True)

    def uncheckAllItems(self, rootItem):
        for i in range(rootItem.childCount()):
            child = rootItem.child(i)
            child.setCheckState(0, Qt.Unchecked)
            self.uncheckAllItems(child)

    def removeSelectedFromTarget(self):
        self.removeCheckedItems(self.targetTree.invisibleRootItem())

    def removeCheckedItems(self, targetRoot):
        i = 0
        while i < targetRoot.childCount():
            child = targetRoot.child(i)
            if child.checkState(0) == Qt.Checked:
                targetRoot.removeChild(child)
            else:
                self.removeCheckedItems(child)
                i += 1

    def resetSearch(self):
        
        self.searchBox.clear()
        root = self.sourceTree.invisibleRootItem()
        for i in range(root.childCount()):
            root.child(i).setHidden(False)
            root.child(i).setExpanded(False)
            self.hideAllChildren(root.child(i))

    def expandAllItems(self, item):
        item.setHidden(False)
        item.setExpanded(True)
        for i in range(item.childCount()):
            self.expandAllItems(item.child(i))

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    
    leftOptions = {
        "Category 1": ["Item 1", "Item 2"],
        "Category 2": ["Item 3", "Item 4"]
    }
    rightOptions = {
        "Category A": ["Item A1", "Item A2"],
        "Category B": ["Item B1", "Item B2"]
    }
    selected = None
    
    window = DoubleTreeWidget(leftOptions, rightOptions, selected)
    window.show()
    
    sys.exit(app.exec_())

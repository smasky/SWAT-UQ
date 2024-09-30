from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,QTreeWidgetItem,
                             QPushButton)
from qfluentwidgets import TreeWidget, PrimaryToolButton, FluentIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

class DoubleTreeWidget(QWidget):
    def __init__(self, leftOptions, rightOptions, selected, parent=None):
        super().__init__(parent)
        self.leftOptions=leftOptions
        self.rightOptions=rightOptions
        self.initUI()
        
        if selected is not None:
            self.populateTree(self.targetTree, selected)
            
        self.sourceTree.header().setStyleSheet("QHeaderView::section { color: black; }")
        self.targetTree.header().setStyleSheet("QHeaderView::section { color: black; }")
        
    def initUI(self):
        layout = QHBoxLayout()

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

        layout.addWidget(self.sourceTree)
        layout.addLayout(btnLayout)
        layout.addWidget(self.targetTree)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def populateTree(self, widget, content):
        """为 Source 树结构添加参数项目"""
        if isinstance(content, dict):
            keys=list(content.keys())
            rootItems={}
            for key in keys:
                rootItem=QTreeWidgetItem(widget, [key])
                rootItems[key]=rootItem

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

    
    def copyCheckedChildItems(self, sourceRoot):
        
        for i in range(sourceRoot.childCount()):
            sourceChild = sourceRoot.child(i)

            if not self.targetTree.findItems(sourceChild.text(0), Qt.MatchExactly, 0) and sourceChild.childCount()==0:
                if sourceChild.checkState(0) == Qt.Checked:
                    child = QTreeWidgetItem(self.targetTree, [sourceChild.text(0)])
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                    child.setCheckState(0, Qt.Unchecked)
            
            for j in range(sourceChild.childCount()):
                subChild = sourceChild.child(j)
                if subChild.checkState(0) == Qt.Checked:
                    if not self.targetTree.findItems(sourceChild.text(0), Qt.MatchExactly, 0):
                        child = QTreeWidgetItem(self.targetTree, [sourceChild.text(0)])
                        child.setFlags(child.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsTristate)
                        child.setCheckState(0, Qt.Unchecked)
                        
                        self.addChildItems(child, [subChild.text(0)])
                        child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                        child.setCheckState(0, Qt.Unchecked)
                    else:
                        child=self.targetTree.findItems(sourceChild.text(0), Qt.MatchExactly, 0)[0]
                        self.addChildItems(child, [subChild.text(0)])
                    
                    child.setExpanded(True)
                    
    def uncheckAllItems(self, rootItem):
        
        for i in range(rootItem.childCount()):
            child = rootItem.child(i)
            child.setCheckState(0, Qt.Unchecked)
            self.uncheckAllItems(child)  # 递归处理子项

    def removeSelectedFromTarget(self):
        
        self.removeCheckedItems(self.targetTree.invisibleRootItem())

    def removeCheckedItems(self, targetRoot):
        """递归地移除选中的项目"""
        i = 0
        while i < targetRoot.childCount():
            child = targetRoot.child(i)
            if child.checkState(0) == Qt.Checked:
                targetRoot.removeChild(child)
            else:
                self.removeCheckedItems(child)
                i += 1
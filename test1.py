from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QSpinBox, QComboBox, QDoubleSpinBox, QLabel, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt

class BodyLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("font-weight: bold;")

class MyForm(QWidget):
    def __init__(self, default, parent=None):
        super().__init__(parent)
        
        vBoxLayout = QVBoxLayout(self)
        
        label = BodyLabel("Problem Define", self)
        vBoxLayout.addWidget(label)
        
        contentWidget = QWidget(self)
        vBoxLayout.addWidget(contentWidget)
        hBoxLayout = QHBoxLayout(contentWidget)
        
        formLayout = QFormLayout()
        hBoxLayout.addLayout(formLayout)
        
        # 设置标签右对齐
        formLayout.setLabelAlignment(Qt.AlignRight)
        
        # 定义一个函数来创建右对齐的字段
        def create_right_aligned_field(widget):
            h_layout = QHBoxLayout()
            h_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            h_layout.addWidget(widget)
            return h_layout
        
        serIDEdit = QSpinBox(self)
        serIDEdit.setValue(int(default['serID']))
        formLayout.addRow(BodyLabel('Series ID:'), create_right_aligned_field(serIDEdit))
        
        objIDEdit = QSpinBox(self)
        objIDEdit.setValue(int(default['objID']))
        formLayout.addRow(BodyLabel("Objective ID:"), create_right_aligned_field(objIDEdit))
        
        reachIDEdit = QSpinBox(self)
        reachIDEdit.setValue(int(default['reachID']))
        formLayout.addRow(BodyLabel("Reach ID:"), create_right_aligned_field(reachIDEdit))
        
        objTypeEdit = QComboBox(self)
        objTypeEdit.setCurrentIndex(default['objType'])
        objTypeEdit.addItems(list(Pro.OBJTYPE_INT.keys()))
        formLayout.addRow(BodyLabel("Objective Type:"), create_right_aligned_field(objTypeEdit))
        
        varEdit = QComboBox(self)
        varEdit.setCurrentIndex(default['varType'])
        varEdit.addItems(list(Pro.VAR_INT.keys()))
        formLayout.addRow(BodyLabel("Variable:"), create_right_aligned_field(varEdit))
        
        weightEdit = QDoubleSpinBox(self)
        weightEdit.setValue(float(default['weight']))
        formLayout.addRow(BodyLabel("Weight:"), create_right_aligned_field(weightEdit))

# 示例默认值
default = {
    'serID': 1,
    'objID': 2,
    'reachID': 3,
    'objType': 0,  # 假设这是下拉框的默认索引
    'varType': 1,  # 假设这是另一个下拉框的默认索引
    'weight': 0.5
}

# Pro 类的模拟定义，用于提供下拉框的数据
class Pro:
    OBJTYPE_INT = {'Type1': 1, 'Type2': 2}
    VAR_INT = {'Var1': 1, 'Var2': 2}

# 创建表单实例并显示窗口
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    form = MyForm(default)
    form.show()
    sys.exit(app.exec_())
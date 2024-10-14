from qfluentwidgets import TreeWidget


from .utility import MediumSize
class TreeWidget_(TreeWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(f"QHeaderView::section {{ font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; font-weight: 500;}}")
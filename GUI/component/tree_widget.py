from qfluentwidgets import TreeWidget

class TreeWidget_(TreeWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet("""
                           QHeaderView::section { font: 18px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'; 
                                                  font-weight: 500;
                     
                           }
                           
                           """)
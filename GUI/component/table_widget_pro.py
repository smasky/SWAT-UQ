from qfluentwidgets import TableWidget, getStyleSheet, FluentStyleSheet

from .utility import substitute
class TableWidgetPro(TableWidget):
    
    def __init__(self, parent=None):
        
        super().__init__(parent)
        
        qss=getStyleSheet(FluentStyleSheet.TABLE_VIEW)
        qss=substitute(qss, {'QTableView': { 'font': " 16px 'Segoe UI', 'Microsoft YaHei'"}, 'QHeaderView::section':{'font': " 18px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC'", 'font-weight': ' 500'}})
        self.setStyleSheet(qss)
    
    
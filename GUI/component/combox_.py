from PyQt5.QtWidgets import QMenu
from qfluentwidgets import  ComboBox
from qfluentwidgets.components.widgets.combo_box import ComboBoxMenu, ComboItem
from .utility import MediumSize

class ComboBoxMenu_(ComboBoxMenu):
    
    def __init__(self, title="", parent=None):
        
        super().__init__(parent)
        size=parent.menuFontsize
        self.view.setStyleSheet(f"MenuActionListWidget {{ font: {size}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC' }}")

    
    
class ComboBox_(ComboBox):
    
    menuFontsize=MediumSize
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMaxVisibleItems(10)
    def _createComboMenu(self):
        
        return ComboBoxMenu_(parent=self)
    
    # def setMenuFontsize(self, size):
        
    #     self.menu.view.setStyleSheet(f"MenuActionListWidget {{ font: {size}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC' }}")
    
    def addItem(self, text: str, icon = None, userData=None):
        """ add item

        Parameters
        ----------
        text: str
            the text of item

        icon: str | QIcon | FluentIconBase
        """
        item = ComboItem(text, icon, userData)
        self.items.append(item)
        # if len(self.items) == 1:
        #     self.setCurrentIndex(0)
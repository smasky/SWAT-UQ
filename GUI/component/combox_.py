from qfluentwidgets import  ComboBox,FluentStyleSheet, getStyleSheet
from qfluentwidgets.components.widgets.combo_box import ComboBoxMenu, ComboItem
from .utility import getFont, setFont, Normal, MediumSize, substitute

class ComboBoxMenu_(ComboBoxMenu):
    
    def __init__(self, title="", parent=None):
        
        super().__init__(parent)
        self.view.setStyleSheet(f"MenuActionListWidget {{ font: {MediumSize}px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC' }}")

class ComboBox_(ComboBox):
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def _createComboMenu(self):
        
        return ComboBoxMenu_(self)
    
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
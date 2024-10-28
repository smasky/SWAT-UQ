from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import sys
from GUI import MainWindow


if __name__ == "__main__":
    
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    
    demo = MainWindow()
    demo.show()
    app.exec_()
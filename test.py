from PyQt5.QtWidgets import QApplication
import sys

from GUI import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = MainWindow()
    demo.show()
    app.exec()
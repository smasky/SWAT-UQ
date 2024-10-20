import sys
from PyQt5.QtWidgets import QApplication, QDialog, QPushButton, QVBoxLayout

class DialogOne(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialog One")
        layout = QVBoxLayout()
        btn = QPushButton("Close Dialog One")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)

class DialogTwo(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dialog Two")
        layout = QVBoxLayout()
        btn = QPushButton("Close Dialog Two")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)
        self.setLayout(layout)

class MainWindow:
    def __init__(self):
        self.show_dialogs()

    def show_dialogs(self):
        dialog_one = DialogOne()
        if dialog_one.exec():
            print("Dialog One Closed")
            dialog_two = DialogTwo()
            dialog_two.exec()
            print("Dialog Two Closed")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())

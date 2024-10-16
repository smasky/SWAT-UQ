import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QCheckBox, QGridLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class MplCanvas(FigureCanvas):
    def __init__(self, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setWindowTitle("Bar Chart with Selectable Parameters")

        # Create a canvas to draw the plot
        self.canvas = MplCanvas(width=5, height=4, dpi=100)

        # Generate random data for 10 parameters
        self.parameter_count = 10
        self.data = np.random.rand(self.parameter_count)  # 10 random values between 0 and 1

        # Plot all parameters initially
        self.plot_parameters([True] * self.parameter_count)

        # Create a layout and add the canvas
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)

        # Create a grid layout for checkboxes
        checkbox_layout = QGridLayout()

        # Create checkboxes for each parameter
        self.checkboxes = []
        for i in range(self.parameter_count):
            checkbox = QCheckBox(f"Parameter {i+1}")
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(self.update_plot)
            self.checkboxes.append(checkbox)
            checkbox_layout.addWidget(checkbox, i // 5, i % 5)  # Arrange in two rows

        # Add checkbox layout to the main layout
        layout.addLayout(checkbox_layout)

        # Create a central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def plot_parameters(self, show_params):
        self.canvas.axes.clear()  # Clear existing plot

        # Filter data and labels based on checkbox state
        visible_indices = [i for i, show in enumerate(show_params) if show]
        heights = [self.data[i] for i in visible_indices]
        labels = [f"P{i+1}" for i in visible_indices]

        # Fixed bar width
        bar_width = 0.5

        # Calculate positions for bars with dynamic spacing
        spacing = 1.0  # Base spacing between bars
        indices = np.arange(len(visible_indices)) * (bar_width + spacing)

        self.canvas.axes.bar(indices, heights, width=bar_width, tick_label=labels)
        self.canvas.axes.set_ylim(0, 1)  # Set y-axis range

        # Adjust x-axis limits to fit the bars and show spacing
        self.canvas.axes.set_xlim(-bar_width, max(indices) + bar_width)

        self.canvas.draw()

    def update_plot(self):
        show_params = [checkbox.isChecked() for checkbox in self.checkboxes]
        self.plot_parameters(show_params)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout, QSplitter
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.file_operations import load_files, clear_selection, select_all, select_none, confirm_selection
from backend.plot_operations import plot_data

class ADCPlotterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADCP Plotter")
        self.setGeometry(100, 100, 1000, 600)
        self.file_paths = {}
        self.parsed_data = {}
        self.metadata_keys_to_plot = ['altitude', 'vwc', 'unit_number']  # Add fields to plot here

        self.layout = QHBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel
        self.left_panel = QVBoxLayout()
        self.load_btn = QPushButton("Load Files")
        self.load_btn.clicked.connect(lambda: load_files(self))
        self.clear_btn = QPushButton("Clear Loaded Files")
        self.clear_btn.clicked.connect(lambda: clear_selection(self))
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(lambda: select_all(self))
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(lambda: select_none(self))
        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(lambda: confirm_selection(self))

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.MultiSelection)

        self.left_panel.addWidget(self.load_btn)
        self.left_panel.addWidget(self.clear_btn)
        self.left_panel.addWidget(self.select_all_btn)
        self.left_panel.addWidget(self.select_none_btn)
        self.left_panel.addWidget(self.file_list)
        self.left_panel.addWidget(self.confirm_button)

        left_widget = QWidget()
        left_widget.setLayout(self.left_panel)

        # Center panel
        self.center_panel = QVBoxLayout()
        self.collection_list = QListWidget()
        self.collection_list.setSelectionMode(QListWidget.MultiSelection)
        self.plot_button = QPushButton("Plot Selected Data")
        self.plot_button.clicked.connect(lambda: plot_data(self))
        self.center_panel.addWidget(self.collection_list)
        self.center_panel.addWidget(self.plot_button)

        center_widget = QWidget()
        center_widget.setLayout(self.center_panel)

        # Right panel (plot only)
        self.right_panel = QVBoxLayout()
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMinimumHeight(300)
        self.canvas.setMinimumWidth(600)
        self.right_panel.addWidget(self.canvas)

        right_widget = QWidget()
        right_widget.setLayout(self.right_panel)

        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(center_widget)
        self.splitter.addWidget(right_widget)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ADCPlotterGUI()
    gui.show()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout, QSplitter, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.file_operations import load_files, clear_selection, select_all, select_none, confirm_selection, export_plots
from backend.plot_operations import plot_data

class ADCPlotterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADCP Plotter")
        self.setGeometry(100, 100, 1200, 700)
        self.file_paths = {}
        self.parsed_data = {}
        self.metadata_keys_to_plot = []
        self.active_metadata_tab = 'latlong'  # default tab

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
        
        self.export_button = QPushButton("Export Plots")
        self.export_button.clicked.connect(lambda: export_plots(self))
        self.center_panel.addWidget(self.export_button)


        center_widget = QWidget()
        center_widget.setLayout(self.center_panel)

        # Right panel
        self.right_panel = QVBoxLayout()
        self.profile_figure = Figure()
        self.profile_canvas = FigureCanvas(self.profile_figure)
        self.profile_canvas.setMinimumHeight(300)

        self.metadata_tabs = QTabWidget()
        self.metadata_canvases = {}
        metadata_fields = ['latlong', 'timestamp', 'abort_status', 'actuator_error', 'temperature']

        for field in metadata_fields:
            fig = Figure()
            canvas = FigureCanvas(fig)
            self.metadata_canvases[field] = canvas
            tab = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(canvas)
            tab.setLayout(layout)
            self.metadata_tabs.addTab(tab, field.replace('_', ' ').title())

        self.metadata_tabs.currentChanged.connect(self.update_active_tab)

        self.right_panel.addWidget(self.profile_canvas)
        self.right_panel.addWidget(self.metadata_tabs)

        right_widget = QWidget()
        right_widget.setLayout(self.right_panel)
        
        # Legend panel (far right)
        self.legend_panel = QVBoxLayout()
        self.legend_list = QListWidget()
        self.legend_panel.addWidget(self.legend_list)
        legend_widget = QWidget()
        legend_widget.setLayout(self.legend_panel)

        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(center_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.addWidget(legend_widget)


        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

    def update_active_tab(self):
        index = self.metadata_tabs.currentIndex()
        self.active_metadata_tab = list(self.metadata_canvases.keys())[index]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ADCPlotterGUI()
    gui.show()
    sys.exit(app.exec_())

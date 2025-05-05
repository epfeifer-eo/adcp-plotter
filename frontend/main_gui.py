import sys
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QHBoxLayout, QSplitter, QTabWidget,
    QRadioButton, QCheckBox, QDialog, QDialogButtonBox, QLabel, QButtonGroup, QTextEdit
)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from backend.file_operations import load_files, clear_selection, select_all, select_none, confirm_selection, export_selected
from backend.plot_operations import plot_data


def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class ExportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Options")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Export format selection
        layout.addWidget(QLabel("Export format:"))
        self.format_group = QButtonGroup(self)
        self.png_radio = QRadioButton("Export as PNG files")
        self.pdf_radio = QRadioButton("Export as a combined PDF")
        self.format_group.addButton(self.png_radio)
        self.format_group.addButton(self.pdf_radio)
        self.pdf_radio.setChecked(True)
        layout.addWidget(self.png_radio)
        layout.addWidget(self.pdf_radio)

        # Metadata field checkboxes
        layout.addWidget(QLabel("Include metadata plots:"))
        self.checkboxes = {}
        fields = ['latlong', 'timestamp', 'abort_status', 'actuator_error', 'temperature']
        for field in fields:
            checkbox = QCheckBox(field.replace('_', ' ').title())
            checkbox.setChecked(True)
            self.checkboxes[field] = checkbox
            layout.addWidget(checkbox)

        # Legend checkbox
        self.include_legend_checkbox = QCheckBox("Include legend")
        self.include_legend_checkbox.setChecked(True)
        layout.addWidget(self.include_legend_checkbox)

        # Dialog buttons
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

        self.setLayout(layout)

    def get_options(self):
        return {
            'format': 'pdf' if self.pdf_radio.isChecked() else 'png',
            'metadata_fields': [key for key, cb in self.checkboxes.items() if cb.isChecked()],
            'include_legend': self.include_legend_checkbox.isChecked()
        }


class ADCPlotterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADCP Plotter")
        self.setGeometry(100, 100, 1200, 700)

        # Set custom icon
        if getattr(sys, 'frozen', False):
            base_dir = sys._MEIPASS  # special PyInstaller path
        else:
            base_dir = os.path.abspath(os.path.dirname(__file__))
        
        icon_path = os.path.join(base_dir, "adcp_icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        self.file_paths = {}
        self.parsed_data = {}
        self.metadata_keys_to_plot = []
        self.active_metadata_tab = 'latlong'

        self.layout = QHBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel: file controls
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

        # Center panel: collection and plot controls
        self.center_panel = QVBoxLayout()
        self.collection_list = QListWidget()
        self.collection_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.plot_button = QPushButton("Plot Selected Data")
        self.plot_button.clicked.connect(lambda: plot_data(self))
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.show_export_dialog)

        self.center_panel.addWidget(self.collection_list)
        self.center_panel.addWidget(self.plot_button)
        self.center_panel.addWidget(self.export_button)

        center_widget = QWidget()
        center_widget.setLayout(self.center_panel)

        # Right panel: profile plot and metadata tabs
        self.right_panel = QVBoxLayout()
        self.profile_figure = Figure(constrained_layout=True)
        self.profile_canvas = FigureCanvas(self.profile_figure)
        self.profile_canvas.setMinimumHeight(300)

        self.metadata_tabs = QTabWidget()
        self.metadata_canvases = {}
        metadata_fields = ['latlong', 'timestamp', 'abort_status', 'actuator_error', 'temperature']

        for field in metadata_fields:
            fig = Figure(constrained_layout=True)
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

        # Legend panel: scrollable list + metadata viewer
        self.legend_splitter = QSplitter(Qt.Vertical)
        self.legend_list = QListWidget()
        self.legend_list.setMinimumHeight(100)
        self.legend_splitter.addWidget(self.legend_list)

        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        self.metadata_display.setPlaceholderText("Select a collection to view metadata...")
        self.legend_splitter.addWidget(self.metadata_display)

        legend_widget = QWidget()
        legend_layout = QVBoxLayout()
        legend_layout.addWidget(self.legend_splitter)
        legend_widget.setLayout(legend_layout)

        # Combine all panels
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(center_widget)
        self.splitter.addWidget(right_widget)
        self.splitter.addWidget(legend_widget)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

    def update_active_tab(self):
        index = self.metadata_tabs.currentIndex()
        self.active_metadata_tab = list(self.metadata_canvases.keys())[index]

    def show_export_dialog(self):
        dialog = ExportDialog(self)
        if dialog.exec_():
            options = dialog.get_options()
            print("User selected export options:", options)
            from backend.file_operations import export_selected
            export_selected(self, options)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    import qdarkstyle
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    try:
        gui = ADCPlotterGUI()
    except Exception as e:
        print(f"GUI creation failed: {e}")
        sys.exit(1)

    gui.showMaximized()
    sys.exit(app.exec_())

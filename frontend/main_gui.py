from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QHBoxLayout, QTextEdit, QSplitter)
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import sys
import os

# Ensure the script can find the backend folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_parsing import load_json, load_adcp

class ADCPlotterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ADCP Plotter")
        self.setGeometry(100, 100, 1000, 600)
        self.file_paths = {}
        self.parsed_data = {}

        # Main layout with splitters
        self.layout = QHBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)

        # Left panel for file operations
        self.left_panel = QVBoxLayout()
        self.load_btn = QPushButton("Load Files")
        self.load_btn.clicked.connect(self.load_files)
        self.clear_btn = QPushButton("Clear Loaded Files")
        self.clear_btn.clicked.connect(self.clear_selection)
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)
        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_none)
        self.confirm_button = QPushButton("Confirm Selection")
        self.confirm_button.clicked.connect(self.confirm_selection)

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

        # Center panel for collection list
        self.center_panel = QVBoxLayout()
        self.collection_list = QListWidget()
        self.collection_list.setSelectionMode(QListWidget.MultiSelection)
        self.plot_button = QPushButton("Plot Selected Data")
        self.plot_button.clicked.connect(self.plot_data)
        self.center_panel.addWidget(self.collection_list)
        self.center_panel.addWidget(self.plot_button)

        center_widget = QWidget()
        center_widget.setLayout(self.center_panel)

        # Right panel for metadata and plots
        self.right_panel = QVBoxLayout()
        self.metadata_display = QTextEdit()
        self.metadata_display.setReadOnly(True)
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.right_panel.addWidget(self.metadata_display)
        self.right_panel.addWidget(self.canvas)

        right_widget = QWidget()
        right_widget.setLayout(self.right_panel)

        # Adding splitters for resize functionality
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(center_widget)
        self.splitter.addWidget(right_widget)

        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)

    def load_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "./data", "JSON and ADCP Files (*.json *.adcp)")
        if files:
            for file in files:
                file_name = os.path.basename(file)
                if file_name not in self.file_paths:
                    self.file_paths[file_name] = file
                    self.file_list.addItem(file_name)
        print("Files loaded.")

    def clear_selection(self):
        self.file_paths.clear()
        self.parsed_data.clear()
        self.file_list.clear()
        self.collection_list.clear()
        self.metadata_display.clear()
        print("Selection cleared.")

    def select_all(self):
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            item.setSelected(True)
        print("All files selected.")

    def select_none(self):
        for index in range(self.file_list.count()):
            item = self.file_list.item(index)
            item.setSelected(False)
        print("No files selected.")

    def confirm_selection(self):
        print("Confirming selected files for visualization...")
        selected_files = [self.file_list.item(i).text() for i in range(self.file_list.count()) if self.file_list.item(i).isSelected()]
        self.collection_list.clear()
        for file_name in selected_files:
            file_path = self.file_paths[file_name]
            if file_path.endswith('.json'):
                data = load_json(file_path)
            elif file_path.endswith('.adcp'):
                data = load_adcp(file_path)
            else:
                continue

            if data:
                self.parsed_data[file_name] = data
                for i, collection in enumerate(data):
                    self.collection_list.addItem(f"{file_name} - Collection {i+1}")
        print("Selection confirmed.")

    def display_metadata(self, metadata):
        self.metadata_display.clear()
        for key, value in metadata.items():
            self.metadata_display.append(f"{key}: {value}")

    def plot_data(self):
        selected_items = self.collection_list.selectedItems()
        if not selected_items:
            print("No collection selected.")
            return

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        for item in selected_items:
            try:
                file_name, collection_number = item.text().rsplit(" - Collection ", 1)
                collection_number = int(collection_number) - 1
                data = self.parsed_data[file_name][collection_number]

                if 'measurements' in data:
                    depths = [point['depth'] for point in data['measurements']]
                    values = [point['value'] for point in data['measurements']]
                elif 'data' in data:
                    depths = [point['depth'] for point in data['data']]
                    values = [point['value'] for point in data['data']]
                elif 'data' in data:
                    depths = [point['depth'] for point in data['data']]
                    values = [point['value'] for point in data['data']]
                    values = [point['value'] for point in data['data']]
                    depths = [point['depth'] for point in data['measurements']]
                    values = [point['value'] for point in data['measurements']]
                else:
                    depths = [point['depth'] for point in data.get('data', data)]
                
                metadata = data.get('metadata', {})

                ax.plot(depths, values, label=f"{file_name} - Col {collection_number + 1}")
                self.display_metadata(metadata)
            except Exception as e:
                print(f"Error plotting data for item: {item.text()}, Error: {e}")

        ax.legend(loc='upper right')
        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ADCPlotterGUI()
    gui.show()
    sys.exit(app.exec_())

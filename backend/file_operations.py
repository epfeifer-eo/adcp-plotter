import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog, QInputDialog
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_agg import FigureCanvasAgg
import matplotlib.pyplot as plt

from backend.data_parsing import load_json

def get_base_dir():
    if getattr(sys, 'frozen', False):
        # Running as.exe
        return os.path.dirname(sys.executable)
    else:
        # Running from source
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def load_files(gui):
    base_dir = get_base_dir()
    data_folder = os.path.join(base_dir, 'data')


    os.makedirs(data_folder, exist_ok=True)

    files, _ = QFileDialog.getOpenFileNames(gui, "Select Files", data_folder, "JSON Files (*.json)")
    if files:
        for file in files:
            file_name = os.path.basename(file)
            if file_name not in gui.file_paths:
                gui.file_paths[file_name] = file
                gui.file_list.addItem(file_name)

def clear_selection(gui):
    gui.file_paths.clear()
    gui.parsed_data.clear()
    gui.file_list.clear()
    gui.collection_list.clear()

    if hasattr(gui, 'legend_list'):
        gui.legend_list.clear()
        try:
            gui.legend_list.itemClicked.disconnect()
        except TypeError:
            pass

    if hasattr(gui, 'profile_figure'):
        gui.profile_figure.clear()
        gui.profile_canvas.draw()

    if hasattr(gui, 'metadata_canvases'):
        for canvas in gui.metadata_canvases.values():
            canvas.figure.clear()
            canvas.draw()

    gui.profile_lines = []
    gui.highlighted_label = None

def select_all(gui):
    for index in range(gui.file_list.count()):
        item = gui.file_list.item(index)
        item.setSelected(True)

def select_none(gui):
    for index in range(gui.file_list.count()):
        item = gui.file_list.item(index)
        item.setSelected(False)

def confirm_selection(gui):
    selected_files = [gui.file_list.item(i).text() for i in range(gui.file_list.count()) if gui.file_list.item(i).isSelected()]
    gui.collection_list.clear()
    for file_name in selected_files:
        file_path = gui.file_paths[file_name]
        data = load_json(file_path)
        if data:
            gui.parsed_data[file_name] = data
            for i, collection in enumerate(data):
                gui.collection_list.addItem(f"{file_name} - Collection {i+1}")

def export_selected(gui, options):
    base_dir = get_base_dir()
    export_folder = os.path.join(base_dir, 'plots')
    os.makedirs(export_folder, exist_ok=True)

    def export_legend_figure(filepath):
        grouped = {}
        for i in range(gui.legend_list.count()):
            item = gui.legend_list.item(i)
            info = item.data(Qt.UserRole)
    
            if not info or "file" not in info or "collection" not in info:
                continue
    
            file_part = info["file"]
            display_label = info["collection"]
            color = info["color"]
    
            grouped.setdefault(file_part, []).append((display_label, color))
    
        total_lines = sum(len(v) + 1 for v in grouped.values())
        fig_height = max(2, total_lines * 0.25)
        fig, ax = plt.subplots(figsize=(6, fig_height))
        ax.axis('off')
    
        y = 1.0
        spacing = 0.06
    
        for group, entries in grouped.items():
            ax.text(0.01, y, group, fontsize=11, fontweight='bold', verticalalignment='top')
            y -= spacing
            for entry, color in entries:
                ax.text(0.05, y, entry, color=color, fontsize=10, verticalalignment='top')
                y -= spacing
    
        fig.tight_layout()
        fig.savefig(filepath)
        plt.close(fig)



    if options['format'] == 'pdf':
        path, _ = QFileDialog.getSaveFileName(gui, "Export PDF", os.path.join(export_folder, "export.pdf"), "PDF Files (*.pdf)")
        if not path:
            return
    
        with PdfPages(path) as pdf:
            canvas = FigureCanvasAgg(gui.profile_figure)
            canvas.draw()
            pdf.savefig(gui.profile_figure)
    
            for key in options['metadata_fields']:
                canvas = FigureCanvasAgg(gui.metadata_canvases[key].figure)
                canvas.draw()
                pdf.savefig(gui.metadata_canvases[key].figure)
    
            if options['include_legend']:
                grouped = {}
                for i in range(gui.legend_list.count()):
                    item = gui.legend_list.item(i)
                    info = item.data(Qt.UserRole)
            
                    if not info or "file" not in info or "collection" not in info:
                        continue
            
                    file_part = info["file"]
                    display_label = info["collection"]
                    color = info["color"]
            
                    grouped.setdefault(file_part, []).append((display_label, color))
            
                total_lines = sum(len(v) + 1 for v in grouped.values())  # +1 for each group header
                fig_height = max(2, total_lines * 0.25)
                fig, ax = plt.subplots(figsize=(6, fig_height))
                ax.axis('off')
            
                y = 1.0
                spacing = 0.06
            
                for group, entries in grouped.items():
                    ax.text(0.01, y, group, fontsize=11, fontweight='bold', verticalalignment='top')
                    y -= spacing
                    for entry, color in entries:
                        ax.text(0.05, y, entry, color=color, fontsize=10, verticalalignment='top')
                        y -= spacing
            
                fig.tight_layout()
                pdf.savefig(fig)
                plt.close(fig)



    elif options['format'] == 'png':
        name, ok = QInputDialog.getText(gui, "File Naming", "Base filename:", text="export")
        if not ok or not name.strip():
            name = "export"
        gui.profile_figure.savefig(os.path.join(export_folder, f"{name}_profile.png"))
        for key in options['metadata_fields']:
            canvas = gui.metadata_canvases[key]
            canvas.figure.savefig(os.path.join(export_folder, f"{name}_{key}.png"))
        if options['include_legend']:
            grouped = {}
            for i in range(gui.legend_list.count()):
                item = gui.legend_list.item(i)
                info = item.data(Qt.UserRole)
        
                if not info or "file" not in info or "collection" not in info:
                    continue  # skip any broken or non-standard items
        
                file_part = info["file"]
                display_label = info["collection"]
                color = info["color"]
        
                grouped.setdefault(file_part, []).append((display_label, color))
        
            total_lines = sum(len(v) + 1 for v in grouped.values())  # +1 for each group header
            fig_height = max(2, total_lines * 0.25)
            fig, ax = plt.subplots(figsize=(6, fig_height))
            ax.axis('off')
        
            y = 1.0
            spacing = 0.06
        
            for group, entries in grouped.items():
                ax.text(0.01, y, group, fontsize=11, fontweight='bold', verticalalignment='top')
                y -= spacing
                for entry, color in entries:
                    ax.text(0.05, y, entry, color=color, fontsize=10, verticalalignment='top')
                    y -= spacing
        
            fig.tight_layout()
            fig.savefig(os.path.join(export_folder, f"{name}_legend.png"))
            plt.close(fig)

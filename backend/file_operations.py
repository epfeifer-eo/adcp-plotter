import os
from PyQt5.QtWidgets import QFileDialog
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.backends.backend_agg import FigureCanvasAgg

from backend.data_parsing import load_json

def load_files(gui):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    data_folder = os.path.join(project_root, 'data')
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
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    export_folder = os.path.join(project_root, 'plots')
    os.makedirs(export_folder, exist_ok=True)

    if options['format'] == 'pdf':
        from PyQt5.QtWidgets import QFileDialog
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
                from matplotlib.figure import Figure
                import matplotlib.pyplot as plt
                fig = Figure(figsize=(6, len(gui.legend_list) * 0.25 + 1))
                ax = fig.add_subplot(111)
                ax.axis('off')
                for i in range(gui.legend_list.count()):
                    item = gui.legend_list.item(i)
                    label = item.text()
                    color = item.foreground().color().name()
                    ax.text(0.01, 0.95 - i * 0.05, label, color=color, fontsize=10, verticalalignment='top')
                pdf.savefig(fig)

    elif options['format'] == 'png':
        from PyQt5.QtWidgets import QInputDialog
        name, ok = QInputDialog.getText(gui, "File Naming", "Base filename:", text="export")
        if not ok or not name.strip():
            name = "export"
        gui.profile_figure.savefig(os.path.join(export_folder, f"{name}_profile.png"))
        for key in options['metadata_fields']:
            canvas = gui.metadata_canvases[key]
            canvas.figure.savefig(os.path.join(export_folder, f"{name}_{key}.png"))
        if options['include_legend']:
            from matplotlib.figure import Figure
            fig = Figure(figsize=(6, len(gui.legend_list) * 0.25 + 1))
            ax = fig.add_subplot(111)
            ax.axis('off')
            for i in range(gui.legend_list.count()):
                item = gui.legend_list.item(i)
                label = item.text()
                color = item.foreground().color().name()
                ax.text(0.01, 1 - i * 0.14, label, color=color, fontsize=10, verticalalignment='top')
            fig.savefig(os.path.join(export_folder, f"{name}_legend.png"))

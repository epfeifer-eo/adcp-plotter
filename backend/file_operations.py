import os
from PyQt5.QtWidgets import QFileDialog
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

def export_plots(gui):
    from matplotlib.backends.backend_agg import FigureCanvasAgg
    from matplotlib.backends.backend_pdf import PdfPages

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    plots_folder = os.path.join(project_root, 'plots')
    os.makedirs(plots_folder, exist_ok=True)

    path, _ = QFileDialog.getSaveFileName(
        gui, "Export Plot", os.path.join(plots_folder, "export.png"), "PNG Files (*.png);;PDF Files (*.pdf)"
    )
    if not path:
        return

    try:
        if path.endswith(".pdf"):
            with PdfPages(path) as pdf:
                profile_canvas = FigureCanvasAgg(gui.profile_figure)
                profile_canvas.draw()
                pdf.savefig(gui.profile_figure)

                for key, canvas in gui.metadata_canvases.items():
                    metadata_canvas = FigureCanvasAgg(canvas.figure)
                    metadata_canvas.draw()
                    pdf.savefig(canvas.figure)
        else:
            gui.profile_figure.savefig(path.replace(".png", "_profile.png"))
            for key, canvas in gui.metadata_canvases.items():
                canvas.figure.savefig(path.replace(".png", f"_{key}.png"))

    except Exception as e:
        print(f"Export failed: {e}")

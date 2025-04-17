import os
from PyQt5.QtWidgets import QFileDialog
from backend.data_parsing import load_json

def load_files(gui):
    files, _ = QFileDialog.getOpenFileNames(gui, "Select Files", "./data", "JSON Files (*.json)")
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
    gui.metadata_display.clear()


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

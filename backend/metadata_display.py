def display_metadata(gui, file_name, collection_number, metadata):
    gui.metadata_display.clear()
    if not metadata:
        gui.metadata_display.append("No metadata available.")
        return

    gui.metadata_display.append(f"Metadata for {file_name} - Collection {collection_number + 1}:")

    if isinstance(metadata, dict) and 'metadata' in metadata:
        metadata = metadata['metadata']

    for key, value in metadata.items():
        if isinstance(value, float) and value.is_integer():
            gui.metadata_display.append(f"{key}: {int(value)}")
        else:
            gui.metadata_display.append(f"{key}: {value}")

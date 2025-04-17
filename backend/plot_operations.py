from backend.metadata_display import display_metadata
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os

def plot_data(gui):
    selected_items = gui.collection_list.selectedItems()
    if not selected_items:
        return

    gui.figure.clear()
    ax1 = gui.figure.add_subplot(211)  # Main profile plot
    ax2 = gui.figure.add_subplot(212)  # Metadata subplot

    metadata_keys_to_plot = getattr(gui, 'metadata_keys_to_plot', [])
    all_metadata = {key: [] for key in metadata_keys_to_plot}
    x_labels = []

    for item in selected_items:
        selected_collection = item.text()

        try:
            file_name, collection_number = selected_collection.split(" - Collection ")
            collection_number = int(collection_number.split()[0]) - 1

            data = gui.parsed_data.get(file_name)
            if not data or collection_number >= len(data):
                continue

            collection = data[collection_number]

            if 'measurements' in collection:
                collection_data = collection['measurements']
                metadata = collection.get('metadata', {})
            else:
                collection_data = collection.get('data') or []
                metadata = collection.get('metadata') or {k: v for k, v in collection.items() if k != 'data'}

            depths = [point['depth'] for point in collection_data]
            values = [point['value'] for point in collection_data]


            base_name = os.path.splitext(file_name)[0]
            if len(base_name) > 20:
                prefix = base_name[:12].rstrip('_')
                short_name = f"{prefix}_..."
            else:
                short_name = base_name
            label = f"{short_name} #{collection_number + 1}"
            ax1.plot(depths, values, label=label)

            x_labels.append(label)
            for key in metadata_keys_to_plot:
                all_metadata[key].append(metadata.get(key, None))

        except Exception:
            continue

    ax1.set_title("ADCP Profile Data")
    ax1.set_xlabel("Depth (in)")
    ax1.set_xlim(-2, 25)

    ax1.set_ylabel("Pressure (psi)")
    ax1.set_ylim(-100, 1100)
    ax1.legend(loc='center left', bbox_to_anchor=(1.05, 0.5), borderaxespad=0., frameon=True)

    if metadata_keys_to_plot and x_labels:
        for key in metadata_keys_to_plot:
            y_vals = all_metadata.get(key, [])
            if any(v is not None for v in y_vals):
                ax2.plot(range(len(y_vals)), y_vals, label=key)
        ax2.set_title("Metadata Overview")
        ax2.set_xlabel("Collection Index")
        ax2.set_ylabel("Metadata Value")
        ax2.set_xticks(range(len(x_labels)))
        ax2.set_xticklabels(x_labels, rotation=45, ha='right')
        ax2.legend(loc='upper right')

    gui.figure.tight_layout()
    gui.canvas.draw()

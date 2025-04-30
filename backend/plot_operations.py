from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import matplotlib.dates as mdates
import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QBrush, QFont
from PyQt5.QtWidgets import QListWidgetItem

def plot_data(gui):
    selected_items = gui.collection_list.selectedItems()
    if not selected_items:
        return

    # Clear profile plot
    gui.profile_figure.clear()
    ax1 = gui.profile_figure.add_subplot(111)
    ax1.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.3)


    # Clear legend list
    gui.legend_list.clear()

    # Shared metadata info for all tabs
    timestamps = []
    latitudes = []
    longitudes = []
    abort_statuses = []
    actuator_errors = []
    temperatures = []
    colors = []
    labels = []

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
            short_name = base_name[:12].rstrip('_') + "_..." if len(base_name) > 20 else base_name
            label = f"{short_name} #{collection_number + 1}"
            line = ax1.plot(depths, values, label=label)
            color = line[0].get_color()

            labels.append(label)
            colors.append(color)

            # Add to scrollable legend
            legend_item = QListWidgetItem(label)
            legend_item.setForeground(QBrush(QColor(color)))
            legend_item.setFont(QFont("Courier", 9))
            legend_item.setData(Qt.UserRole, {
                "file": file_name,
                "collection": f"Collection {collection_number + 1}",
                "color": color
            })
            gui.legend_list.addItem(legend_item)


            try:
                dt = datetime(
                    int(metadata['year']), int(metadata['month']), int(metadata['day']),
                    int(metadata.get('hour', 0)), int(metadata.get('minute', 0)), int(metadata.get('second', 0))
                )
                timestamps.append(dt)
            except Exception:
                timestamps.append(None)

            latitudes.append(metadata.get('latitude'))
            longitudes.append(metadata.get('longitude'))
            abort_statuses.append(metadata.get('abort_status'))
            actuator_errors.append(metadata.get('actuator_absolute_position_error'))
            val = metadata.get('adcp_internal_temp_f') or metadata.get('internal_temp')
            temperatures.append(val)

        except Exception:
            continue

    # Finalize profile plot
    ax1.set_title("ADCP Profile Data")
    ax1.set_xlabel("Depth (in)")
    ax1.set_xlim(-2, 25)
    ax1.set_ylabel("Pressure (psi)")
    ax1.set_ylim(-100, 1100)

    gui.profile_lines = ax1.get_lines()
    gui.highlighted_label = None

    def handle_legend_click(item):
        clicked_label = item.text()
    
        # Toggle highlighting
        if gui.highlighted_label == clicked_label:
            for line in gui.profile_lines:
                line.set_linewidth(1.5)
                line.set_alpha(1.0)
            gui.highlighted_label = None
            gui.metadata_display.clear()
            return
        else:
            for line in gui.profile_lines:
                if line.get_label() == clicked_label:
                    line.set_linewidth(3.0)
                    line.set_alpha(1.0)
                else:
                    line.set_linewidth(1.0)
                    line.set_alpha(0.3)
            gui.highlighted_label = clicked_label
    
        gui.profile_canvas.draw()
    
        # 🔍 Display metadata for the selected collection
        info = item.data(Qt.UserRole)
        if not info:
            gui.metadata_display.setText("No metadata available.")
            return
    
        file = info.get("file")
        try:
            index = int(info.get("collection").split()[-1]) - 1
            metadata = gui.parsed_data[file][index].get("metadata", {})
        except Exception:
            gui.metadata_display.setText("Metadata not found.")
            return
    
        if not metadata:
            gui.metadata_display.setText("No metadata found.")
        else:
            lines = [f"{key}: {value}" for key, value in metadata.items()]
            gui.metadata_display.setText("\n".join(lines))
    

    try:
        gui.legend_list.itemClicked.disconnect()
    except TypeError:
        pass
    gui.legend_list.itemClicked.connect(handle_legend_click)

    ax1.legend(loc='center left', bbox_to_anchor=(1.2, 0.5), borderaxespad=0., frameon=True, fontsize='small')
    gui.profile_canvas.draw()

    # Plot all metadata tabs
    for key, canvas in gui.metadata_canvases.items():
        fig = canvas.figure
        fig.clear()
        ax2 = fig.add_subplot(111)
        ax2.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.3)


        if key == 'latlong':
            for i in range(len(latitudes)):
                if latitudes[i] is not None and longitudes[i] is not None:
                    ax2.scatter(longitudes[i], latitudes[i], label=labels[i], color=colors[i])
            ax2.set_title("Latitude vs Longitude")
            ax2.set_xlabel("Longitude")
            ax2.set_ylabel("Latitude")

        elif key == 'timestamp':
            clean_times = [ts for ts in timestamps if ts is not None]
            if clean_times:
                ax2.plot(range(len(clean_times)), [dt.timestamp() for dt in clean_times], label="Timestamps")
                ax2.set_title("Timestamp Progression")
                ax2.set_ylabel("Epoch Time")
                ax2.set_xticks(range(len(labels)))
                ax2.set_xticklabels(labels, rotation=45, ha='right')

        elif key == 'abort_status':
            for i, val in enumerate(abort_statuses):
                if val is not None:
                    ax2.scatter(i, val, label=labels[i], color=colors[i])
            ax2.set_title("Abort Status")
            ax2.set_ylabel("Status Code")
            ax2.set_yticks([0, 1, 2])
            ax2.set_yticklabels(["No Issue", "Manual Abort", "Auto Abort"])
            ax2.set_xticks(range(len(labels)))
            ax2.set_xticklabels(labels, rotation=45, ha='right')

        elif key == 'actuator_error':
            ax2.plot(range(len(actuator_errors)), actuator_errors, label="Actuator Error")
            ax2.set_title("Actuator Error")
            ax2.set_xticks(range(len(labels)))
            ax2.set_xticklabels(labels, rotation=45, ha='right')

        elif key == 'temperature':
            ax2.plot(range(len(temperatures)), temperatures, label="Temperature")
            ax2.set_title("Internal Temperature")
            ax2.set_xticks(range(len(labels)))
            ax2.set_xticklabels(labels, rotation=45, ha='right')

        fig.tight_layout()
        canvas.draw()

import json


def load_json(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        print(f"Loaded JSON file: {filepath}")
        if 'data' in data:
            return data['data']
        else:
            print("No 'data' key found in JSON file.")
            return None
    except Exception as e:
        print(f"Error loading JSON file {filepath}: {e}")
        return None


def load_adcp(filepath):
    try:
        with open(filepath, 'r') as file:
            lines = file.readlines()

        parsed_collections = []
        current_collection = {'data': [], 'metadata': {}}
        collecting_data = False

        for line in lines:
            line = line.strip()

            # Start a new collection
            if '111111' in line:
                if current_collection['data']:
                    parsed_collections.append(current_collection)
                    current_collection = {'data': [], 'metadata': {}}
                collecting_data = True
                continue

            # End data collection and start metadata
            if '0.000000' in line:
                collecting_data = False
                continue

            # End of a collection
            if '999999' in line:
                if current_collection['data']:
                    parsed_collections.append(current_collection)
                current_collection = {'data': [], 'metadata': {}}
                continue

            # Collect data points
            if collecting_data:
                try:
                    depth, value = map(float, line.split())
                    current_collection['data'].append({'depth': depth, 'value': value})
                except ValueError:
                    print(f"Error parsing data line: {line}")
                continue

            # Collect metadata
            try:
                values = list(map(float, line.split()))
                if len(values) == 2:
                    if 'latitude' not in current_collection['metadata']:
                        current_collection['metadata']['latitude'], current_collection['metadata']['longitude'] = values
                    elif 'altitude' not in current_collection['metadata']:
                        current_collection['metadata']['altitude'], current_collection['metadata']['month'] = values
                    elif 'day' not in current_collection['metadata']:
                        current_collection['metadata']['day'], current_collection['metadata']['year'] = values
                    elif 'hour' not in current_collection['metadata']:
                        current_collection['metadata']['hour'], current_collection['metadata']['minute'] = values
                    elif 'second' not in current_collection['metadata']:
                        current_collection['metadata']['second'], current_collection['metadata']['n_satellites'] = values
                    elif 'hdop_error' not in current_collection['metadata']:
                        current_collection['metadata']['hdop_error'], current_collection['metadata']['adcp_internal_temp_f'] = values
                    elif 'abort_status' not in current_collection['metadata']:
                        current_collection['metadata']['abort_status'], current_collection['metadata']['unit_number'] = values
                    elif 'actuator_absolute_position_error' not in current_collection['metadata']:
                        current_collection['metadata']['actuator_absolute_position_error'], current_collection['metadata']['position_correction_count'] = values
                elif len(values) == 1:
                    current_collection['metadata']['vwc'] = values[0]
            except ValueError:
                print(f"Error parsing metadata line: {line}")

        # Append the last collection if it has data
        if current_collection['data']:
            parsed_collections.append(current_collection)

        print(f"Loaded {len(parsed_collections)} collections from {filepath}")
        return parsed_collections
    except Exception as e:
        print(f"Error loading ADCP file {filepath}: {e}")
        return None

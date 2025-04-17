import json

def load_json(filepath):
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        print(f"Loaded JSON file: {filepath}")
        if 'data' in data:
            # Extract metadata and wrap measurements separately
            wrapped = []
            for entry in data['data']:
                measurements = entry.get('measurements', [])
                metadata = {k: v for k, v in entry.items() if k != 'measurements'}
                wrapped.append({
                    'measurements': measurements,
                    'metadata': metadata
                })
            return wrapped
        else:
            print("No 'data' key found in JSON file.")
            return None
    except Exception as e:
        print(f"Error loading JSON file {filepath}: {e}")
        return None

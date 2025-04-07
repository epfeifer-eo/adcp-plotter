# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:23:31 2025

@author: elija
"""

# tests/test_json_parsing.py
import sys
import os

# Add the project root directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_parsing import load_json

def test_load_json():
    # Path to your JSON file in the data folder
    filepath = "data/EXAMPLE_adcp_eo.json"

    # Load the JSON file
    data = load_json(filepath)

    if data:
        print("\nSuccessfully loaded JSON file!")
        # Print a summary of the data structure
        print(f"Number of Collections: {len(data)}")
        # Print the first collection for inspection
        print("\nFirst Collection:")
        if len(data) > 0:
            print(data[0])
        else:
            print("No collections found.")
    else:
        print("Failed to load JSON file.")

if __name__ == "__main__":
    test_load_json()


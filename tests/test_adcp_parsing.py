# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 12:03:07 2025

@author: elija
"""
# tests/test_adcp_parsing.py
import sys
import os

# Add the project root directory to the system path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.data_parsing import load_adcp

def test_load_adcp():
    # Path to your ADCP file in the data folder
    filepath = "data/ADCP24_test.adcp"

    # Load the ADCP file
    collections = load_adcp(filepath)

    if collections:
        print("\nSuccessfully loaded ADCP file!")
        # Print the metadata of the first collection for verification
        print("First Collection Metadata:")
        print(collections[0]["metadata"])
    else:
        print("Failed to load ADCP file.")

if __name__ == "__main__":
    test_load_adcp()

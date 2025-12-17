"""
Data extraction script for the SHL Assessment Recommendation System.

This script extracts training and test datasets from an Excel file into separate CSV files
for use in training and evaluating the recommendation system.
"""
import pandas as pd
import os


# Define paths to data files
base_dir = os.path.join(os.path.dirname(__file__), "..", "data", "given_datasets")
excel_file = os.path.join(base_dir, "Gen_AI Dataset.xlsx")

print(f"Processing: {os.path.abspath(excel_file)}")

try:
    # Load all sheets from the Excel file
    xls = pd.read_excel(excel_file, sheet_name=None)

    # Extract training data if available
    if "Train-Set" in xls:
        output_path = os.path.join(base_dir, "train.csv")
        xls["Train-Set"].to_csv(output_path, index=False)
        print(f"Extracted: {output_path}")
    else:
        print("Train-Set sheet not found.")

    # Extract test data if available
    if "Test-Set" in xls:
        output_path = os.path.join(base_dir, "test.csv")
        xls["Test-Set"].to_csv(output_path, index=False)
        print(f"Extracted: {output_path}")
    else:
        print("Test-Set sheet not found.")

except Exception as e:
    print(f"Error: {e}")

from pathlib import Path

# Function to get the dataset path
def get_dataset_path():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "building_dataset.csv"
    return str(csv_path)
from pathlib import Path
import pandas as pd

def get_dataset_path():
    project_root = Path(__file__).resolve().parent.parent
    csv_path = project_root / "data" / "building_dataset.csv"
    return str(csv_path)


def format_document(row):
    timestamp = str(row["timestamp"])
    parsed_timestamp = pd.to_datetime(timestamp, format="%Y-%m-%d %H-%M-%S")
    time_hhmm = parsed_timestamp.strftime("%H:%M")
    time_ampm = parsed_timestamp.strftime("%I %p").lstrip("0")
    text = " ".join([
        f"timestamp: {timestamp}",
        f"time: {time_hhmm}",
        f"{time_ampm}",
        f"zone_name: {row['zone_name']}",
        f"temperature_C: {row['temperature_C']}"
    ])
    return text


def load_dataset_as_documents(path):
    df = pd.read_csv(path, comment="#")
    docs = []
    for _, row in df.iterrows():
        docs.append(format_document(row))
    return docs, df
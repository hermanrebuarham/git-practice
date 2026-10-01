"""Check which lab sensors are overdue for calibration."""

import json
from pathlib import Path

import pandas as pd
import yaml


def read_config(path: Path) -> dict:
    """Read the YAML settings file and return it as a dictionary."""
    # with opens the file and closes it automatically afterwards
    with path.open() as f:
        # safe_load turns the YAML text into a python dictionary
        return yaml.safe_load(f)


def find_overdue(sensors: pd.DataFrame, calibrations: pd.DataFrame,
                 max_days: int) -> pd.DataFrame:
    """Join sensor info with calibration data and keep overdue sensors."""
    # Combine the two tables into one, matching rows with the same sensor_id.
    # Each row now has: sensor_id, lab_room, owner, days_since_calibration
    merged = sensors.merge(calibrations, on="sensor_id")

    # Boolean indexing: keep only rows where days_since_calibration is
    # strictly greater than the limit (> and not >=)
    overdue = merged[merged["days_since_calibration"] > max_days]

    # Keep only the columns we want in the output, in this order
    return overdue[["sensor_id", "lab_room", "owner", "days_since_calibration"]]


def main() -> None:
    """Run the calibration check pipeline."""
    # 1. Read settings (max allowed days and output file name)
    config = read_config(Path("config.yml"))

    # 2. Read the two data files into pandas tables (DataFrames)
    sensors = pd.read_excel("sensors.xlsx")       # needs openpyxl installed
    calibrations = pd.read_csv("calibrations.csv")

    # 3. Join the tables and filter out the overdue sensors
    overdue = find_overdue(sensors, calibrations,
                           config["max_days_since_calibration"])

    # 4. Write the result to a JSON file.
    # to_dict(orient="records") turns the table into a list of dictionaries,
    # one per row, which is what json.dump expects.
    with open(config["output_file"], "w") as f:
        json.dump(overdue.to_dict(orient="records"), f, indent=2)

    # Print a short message so we can see that the script ran
    print(f"Wrote {len(overdue)} overdue sensors to {config['output_file']}")


# This makes main() run only when the file is run directly,
# not when it is imported from another file
if __name__ == "__main__":
    main()

# read all json files in src/logs
import os
import json
import pandas as pd

def read_json_files_from_dir(directory: str) -> list[dict]:
    """
    Read all JSON files from a given directory and return their contents as a list of dictionaries.

    Args:
        directory (str): The path to the directory containing JSON files.

    Returns:
        list[dict]: A list of dictionaries containing the contents of each JSON file.
    """
    json_files = [f for f in os.listdir(directory) if f.endswith('.json')]
    data = []

    for file in json_files:
        with open(os.path.join(directory, file), 'r', encoding='utf-8') as f:
            data.append(json.load(f))

    return data

data = read_json_files_from_dir("src/logs")

def jsons_to_dataframe(data: list[dict]) -> pd.DataFrame:
    rows = []

    for log in data:
        # Get the settings
        num_agents = log["settings"]["num_agents"]
        abled_to_disabled_ratio = log["settings"]["abled_to_disabled_ratio"]
        morality_mean = log["settings"]["morality_mean"]
        morality_std = log["settings"]["morality_std"]
        voting_method = log["settings"]["voting_method"]
    
        for run in log["runs"]:
            # Get the run data
            avg_evac_time = run["avg_evac_time"]
            total_evac_time = run["total_evac_time"]
            num_agents_left = run["num_agents_left"]
            evac_times = run["evac_times"]

            # Create a new row for the dataframe
            rows.append({
                "num_agents": num_agents,
                "abled_to_disabled_ratio": abled_to_disabled_ratio,
                "morality_mean": morality_mean,
                "morality_std": morality_std,
                "voting_method": voting_method,
                "avg_evac_time": avg_evac_time,
                "total_evac_time": total_evac_time,
                "num_agents_left": num_agents_left,
                "evac_times": evac_times
            })

    df = pd.DataFrame(rows)

    return df

def main() -> None:
    """
    Main function to read JSON files and convert them to a pandas DataFrame.
    """
    data = read_json_files_from_dir("src/logs")
    df = jsons_to_dataframe(data)
    print(f"Length of dataframe: {len(df)}")
    print(df.head())
    df.to_csv("sim_data.csv", index=False)
    print("Dataframe saved to sim_data.csv")

if __name__ == "__main__":
    main()
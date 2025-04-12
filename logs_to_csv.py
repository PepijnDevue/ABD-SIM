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
    """
    Convert a list of dictionaries to a pandas DataFrame.

    Args:
        data (list[dict]): A list of dictionaries containing the data.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the data.
    """
    abled_to_disabled_ratio = [d["settings"]["abled_to_disabled_ratio"] for d in data]

    morality_mean = [d["settings"]["morality_mean"] for d in data]

    morality_std = [d["settings"]["morality_std"] for d in data]

    voting_method = [d["settings"]["voting_method"] for d in data]

    num_batches = [len(d["runs"]) for d in data]

    avg_evac_time = [
        sum(
            [run["avg_evac_time"] for run in d["runs"]]
        ) / len(d["runs"]) 
        for d in data
    ]

    total_evac_time = [
        sum(
            [run["total_evac_time"] for run in d["runs"]]
        ) / len(d["runs"])
        for d in data
    ]

    num_agents = [d["settings"]["num_agents"] for d in data]

    num_agents_left = [
        sum(
            [run["num_agents_left"] for run in d["runs"]]
        ) / len(d["runs"])
        for d in data
    ]

    evac_times = [
        [run["evac_times"] for run in d["runs"]]
        for d in data
    ]

    data = pd.DataFrame(
        {
            "abled_to_disabled_ratio": abled_to_disabled_ratio,
            "morality_mean": morality_mean,
            "morality_std": morality_std,
            "voting_method": voting_method,
            "num_batches": num_batches,
            "avg_evac_time": avg_evac_time,
            "total_evac_time": total_evac_time,
            "num_agents": num_agents,
            "num_agents_left": num_agents_left,
            "evac_times": evac_times,
        }
    )

    return data

def main() -> None:
    """
    Main function to read JSON files and convert them to a pandas DataFrame.
    """
    data = read_json_files_from_dir("src/logs")
    df = jsons_to_dataframe(data)
    print(f"Length of dataframe: {len(df)}")
    print(df.head())
    df.to_csv("evacuation_times.csv", index=False)
    print("Dataframe saved to evacuation_times.csv")

if __name__ == "__main__":
    main()
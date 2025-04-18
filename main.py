from src import Simulation

from itertools import product
import gc
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

def main():
    grid_search = {
        "voting_method": ["plurality", "approval", "cumulative"],
        "abled_to_disabled_ratio": [0.95, 0.9, 0.85],
        "morality_mean": [0.2, 0.5, 0.8],
    	"morality_std": [0.1, 0.2, 0.3]
    }

    combinations = [
        dict(zip(grid_search.keys(), values))
        for values in product(*grid_search.values())
    ]

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(run_combination, combinations))

    save_data(results)

def save_data(datas: list[pd.DataFrame], filename: str = "logs/sim_data.csv"):
    """
    Save the data to a CSV file.
    """
    # Concatenate all DataFrames into one
    combined_data = pd.concat(datas, ignore_index=True)

    # Save to CSV
    combined_data.to_csv(filename, index=False)

def run_combination(comb):
    """
    Run a single combination of parameters in a separate thread.
    """
    sim = Simulation(
        floor_plan="Heidelberglaan_15", 
        num_agents=250,
        abled_to_disabled_ratio=comb["abled_to_disabled_ratio"],
        voting_method=comb["voting_method"],
        morality_mean=comb["morality_mean"],
        morality_std=comb["morality_std"]
    )

    data = sim.run(num_batches=10)

    # Clean up
    sim = None
    gc.collect()

    return data
            
if __name__ == "__main__":
    main()
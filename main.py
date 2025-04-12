from src import Simulation

from itertools import product

def main():
    grid_search = {
        "voting_method": ["plurality", "approval", "cumulative"],
        "abled_to_disabled_ratio": [0.95, 0.9, 0.85],
        "morality_mean": [0.4, 0.5, 0.6],
    	"morality_std": [0.1, 0.2, 0.3]
    }

    combinations = [
        dict(zip(grid_search.keys(), values))
        for values in product(*grid_search.values())
    ]

    ready = False

    for comb in combinations:
        if not ready:
            if comb == {'voting_method': 'cumulative', 'abled_to_disabled_ratio': 0.9, 'morality_mean': 0.4, 'morality_std': 0.1}:
                ready = True
            else:
                continue

        print(f"Running simulation with: {comb}")

        sim = Simulation(
            floor_plan="Heidelberglaan_15",
            num_agents=250,
            abled_to_disabled_ratio=comb["abled_to_disabled_ratio"],
            voting_method=comb["voting_method"],
            morality_mean=comb["morality_mean"],
            morality_std=comb["morality_std"]
        )

        sim.run(num_batches=1)

if __name__ == "__main__":
    main()
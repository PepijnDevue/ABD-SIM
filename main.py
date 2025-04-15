from src import Simulation

def main():
    sim = Simulation(
        floor_plan="Heidelberglaan_15",
        num_agents=250,
        abled_to_disabled_ratio=0.95,
        voting_method="approval",
        morality_mean=0.6,
        morality_std=0.1,
        approval_threshold=1.5,
        cluster_search_radius=4,
        cnp_call_radius=10
    )

    sim.run(num_batches=1,
            verbose=True,
            frame_duration_seconds=0.4)

if __name__ == "__main__":
    main()
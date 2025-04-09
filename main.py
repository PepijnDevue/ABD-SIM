from src import Simulation

def main():
    # Example with plurality voting
    sim1 = Simulation(
        floor_plan="Heidelberglaan_15",
        num_agents=250,
        distribution_settings={
            "mean": 0.5,
            "std": 0.2,
        },
        voting_method="plurality",
    )
    sim1.run()
    
    # Example with approval voting
    sim2 = Simulation(
        floor_plan="Heidelberglaan_15",
        num_agents=250,
        distribution_settings={
            "mean": 0.5,
            "std": 0.2,
        },
        voting_method="approval"
    )
    sim2.run()

if __name__ == "__main__":
    main()
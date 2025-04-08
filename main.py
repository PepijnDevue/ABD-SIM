from src import Simulation

sim = Simulation(
    floor_plan="Heidelberglaan_15", 
    num_agents=250, 
    distribution_settings={
        "mean": 0.5, 
        "std": 0.2
    }
)

sim.run(max_time_steps=10_000)
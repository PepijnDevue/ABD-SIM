from src import Simulation

sim = Simulation(floor_plan="Heidelberglaan_15", num_agents=100)

sim.run(max_time_steps=10_000)
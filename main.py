from src import Simulation

sim = Simulation(floor_plan="HUNKEMOLLER_TWISTER", num_agents=2)

sim.run(max_time_steps=100)
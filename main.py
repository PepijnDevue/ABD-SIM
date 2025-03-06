from src import Simulation

sim = Simulation(floor_plan="HUNKEMOLLER_SUPREME", num_agents=20)

sim.run(max_time_steps=100)
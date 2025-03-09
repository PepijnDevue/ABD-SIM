import mesa
import networkx as nx

from .agents import Person, Wall, Exit

from .activation import RandomActivation
from .floor_plan import floor_plans
from .pathfinding import Pathfinder
from .log import log_sim

from .ui import show_grid
import time

class Simulation(mesa.Model):
    """
    Simulation class for the evacuating a building.
    """
    def __init__(self, floor_plan: str, num_agents: int=5):
        """
        Setup the simulation with a grid, agents and schedule.

        Args:
            floor_plan: The used floorplan_name
            num_agents: The number of agents to spawn
        """
        super().__init__()
        self.schedule = RandomActivation(self)

        self.floor_plan = floor_plans[floor_plan]

        self.grid = self.setup_grid()

        self.pathfinder = Pathfinder(self.grid)

        self.spawn_agents(num_agents)

        self.step_count = 0

        self.exit_times = []

        show_grid(self.grid)

    def setup_grid(self) -> mesa.space.SingleGrid:
        """
        Read the building map and create a grid with walls and exits.

        Returns:
            SingleGrid: The grid with walls and exits.
        """
        width = len(self.floor_plan[0])
        height = len(self.floor_plan)

        grid = mesa.space.SingleGrid(width, height, torus=False)

        for y in range(height):
            for x in range(width):
                if self.floor_plan[y][x] == 'W':
                    grid.place_agent(Wall(self), (x, y))
                elif self.floor_plan[y][x] == 'E':
                    grid.place_agent(Exit(self), (x, y))

        return grid

    def spawn_agents(self, num_agents: int=1) -> None:
        """
        Spawn agents scattered around the grid.
        """
        for _ in range(num_agents):
            agent = Person(self)
            self.schedule.add(agent)

    def step(self):
        """
        Simulate one timestep of the simulation.
        """
        self.schedule.step()
        self.step_count += 1

    def run(self, max_time_steps: int=100):
        """
        Run an entire simulation.

        Args:
            max_time_steps: The number of timesteps to run the simulation for.
        """
        for _ in range(max_time_steps):
            show_grid(self.grid, cls=True)

            self.step()

            time.sleep(0.2)

            if self.schedule.is_empty():
                show_grid(self.grid, cls=True)
                break

        print("Simulation completed...")
        log_sim(self.exit_times, self.step_count)
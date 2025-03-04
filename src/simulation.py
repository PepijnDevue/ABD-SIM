import mesa

from .agents import Person, Wall, Exit

from .activation import RandomActivation
from .floor_plan import floor_plan

from .ui import show_grid

class Simulation(mesa.Model):
    """
    Simulation class for the evacuating a building.
    """
    def __init__(self):
        """
        Setup the simulation with a grid, agents and schedule.
        """
        super().__init__()
        self.schedule = RandomActivation(self)

        self.grid = self.setup_grid()

        self.spawn_agents()

        show_grid(self.grid)

    def setup_grid(self) -> mesa.space.SingleGrid:
        """
        Read the building map and create a grid with walls and exits.

        Returns:
            SingleGrid: The grid with walls and exits.
        """
        width = len(floor_plan[0])
        height = len(floor_plan)

        grid = mesa.space.SingleGrid(width, height, torus=False)

        for y in range(height):
            for x in range(width):
                if floor_plan[y][x] == 'W':
                    grid.place_agent(Wall(self), (x, y))
                elif floor_plan[y][x] == 'E':
                    grid.place_agent(Exit(self), (x, y))

        return grid
    
    def spawn_agents(self) -> None:
        """
        Spawn agents scattered around the grid.
        """
        num_agents = 1

        for _ in range(num_agents):
            agent = Person(self)

        self.schedule.add(agent)


    def step(self):
        """
        Simulate one timestep of the simulation.
        """
        self.schedule.step()

    def run(self, n):
        """
        Run an entire simulation.

        Args:
            n: The number of timesteps to run the simulation for.
        """
        for _ in range(n):
            self.step()
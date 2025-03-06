import mesa
import networkx as nx

from .agents import Person, Wall, Exit

from .activation import RandomActivation
from .floor_plan import floor_plans

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
        self.graph = self.setup_graph()

        self.spawn_agents(num_agents)

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
    
    def setup_graph(self) -> nx.Graph:
        """
        Create a graph from the grid.

        Returns:
            nx.Graph: The graph representing the grid.
        """
        graph = nx.Graph()

        for agent, coordinates in self.grid.coord_iter():
            # Skip wall agents and create a node for non-wall agents
            if isinstance(agent, Wall):
                continue
            
            graph.add_node(coordinates)
            neighbors = self.grid.get_neighborhood(coordinates, moore=False, include_center=False)
            
            for neighbor in neighbors:
                # Cell content is a list of agents in the cell, it is empty if the cell is empty and has no agents
                cell_content = self.grid.get_cell_list_contents(neighbor)
                
                # If the neighbor cell is empty and not a wall, add an edge
                if len(cell_content) == 0:
                    graph.add_edge(coordinates, neighbor)
                else:
                    # Otherwise, check if the neighbor contains an agent that is not a wall
                    neighbor_agent = cell_content[0]
                    if not isinstance(neighbor_agent, Wall):
                        graph.add_edge(coordinates, neighbor)

        return graph

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

        input("Simulation completed...")
import mesa
import networkx as nx

from .agents import Person, Wall, Exit

from .activation import RandomActivation
from .floor_plan import floor_plan, floor_plan_pathfindingtest

from .ui import show_grid
import os
import time

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
        self.graph = self.setup_graph()

        self.spawn_agents()

        show_grid(self.grid)

    def setup_grid(self) -> mesa.space.SingleGrid:
        """
        Read the building map and create a grid with walls and exits.

        Returns:
            SingleGrid: The grid with walls and exits.
        """
        width = len(floor_plan_pathfindingtest[0])
        height = len(floor_plan_pathfindingtest)

        grid = mesa.space.SingleGrid(width, height, torus=False)

        for y in range(height):
            for x in range(width):
                if floor_plan_pathfindingtest[y][x] == 'W':
                    grid.place_agent(Wall(self), (x, y))
                elif floor_plan_pathfindingtest[y][x] == 'E':
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
            os.system('cls')
            show_grid(self.grid)
            self.step()
            # time.sleep(0.5)
            if len(self.schedule._agents) == 0:
                print("All agents have reached the exit.")
                show_grid(self.grid)
                break
            input()
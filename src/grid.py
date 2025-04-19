import mesa

from .agents import Exit, Person

class Grid(mesa.space.SingleGrid):
    """
    Class that represents the grid of the simulation.
    The grid contains walls and exits.
    """
    def __init__(self, width: int, height: int):
        """
        Initialize the grid with a given floor plan.
        
        Arguments:
            floor_plan: The floor plan of the simulation.
        """
        super().__init__(width, height, torus=False)

    def swap_agents(self, agent_a: Person, agent_b: Person) -> None:
        """
        Swap the positions of two agents in the grid.

        Args:
            agent_a: The first agent to swap.
            agent_b: The second agent to swap.
        """
        pos_a = agent_a.pos
        pos_b = agent_b.pos

        self.remove_agent(agent_a)
        self.remove_agent(agent_b)

        self.place_agent(agent_a, pos_b)
        self.place_agent(agent_b, pos_a)
    
    def cell_is_exit(self, position: tuple) -> bool:
        """
        Check if a cell on a given position is an exit cell

        Args:
            position: The coordinates of the cell

        Returns:
            bool: True if the cell contains an exit agent
        """
        is_empty = super().is_cell_empty(position)

        cell_content = super().get_cell_list_contents(position)

        return not is_empty and isinstance(cell_content[0], Exit)
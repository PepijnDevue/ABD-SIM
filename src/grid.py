import mesa

from .agents import Wall, Exit

class Grid(mesa.space.SingleGrid):
    """
    Class that represents the grid of the simulation.
    The grid contains walls and exits.
    """
    def __init__(self, model: mesa.model, floor_plan: list[str]):
        """
        Initialize the grid with a given floor plan.
        
        Arguments:
            floor_plan: The floor plan of the simulation.
        """
        width = len(floor_plan[0])
        height = len(floor_plan)

        super().__init__(width, height, torus=False)

        for y in range(height):
            for x in range(width):
                if floor_plan[y][x] == 'W':
                    super().place_agent(Wall(model), (x, y))
                elif floor_plan[y][x] == 'E':
                    super().place_agent(Exit(model), (x, y))
    
    def _cell_is_exit(self, position: tuple) -> bool:
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
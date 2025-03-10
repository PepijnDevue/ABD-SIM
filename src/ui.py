import mesa
import os

from .agents import Person, Wall, Exit

def show_grid(grid: mesa.space._PropertyGrid, cls: bool=False) -> None:
    """
    Print the 2d grid
    . = empty
    W = wall
    E = exit
    P = person

    Args:
        grid: The mesa grid containing the agents.
        cls: If the screen should be cleared before showing the grid
    """
    if cls:
        os.system('cls')

    width = grid.width
    height = grid.height

    for y in range(height):
        for x in range(width):
            cell = grid.get_cell_list_contents((x, y))
            print_cell(cell)
        print()


def print_cell(cell: list) -> None:
    """
    Print the cell based on its content.

    Args:
        cell: The list of agents in the cell (Contains 0 or 1 agent).
    """
    char = '?'

    if len(cell) == 0:
        char = ' '
    elif isinstance(cell[0], Wall):
        char = 'W'
    elif isinstance(cell[0], Exit):
        char = 'E'
    elif isinstance(cell[0], Person):
        char = 'P'

    print(char, end="")
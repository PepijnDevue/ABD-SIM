import mesa
import math
import networkx as nx

"""
Class that represents an Exit in the grid.
"""
class Exit(mesa.Agent):
    def __init__(self, model: mesa.Model):
        super().__init__(model)


class Wall(mesa.Agent):
    """
    Class that represents an Wall in the grid.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)


class Person(mesa.Agent):
    def __init__(self, model: mesa.Model):
        super().__init__(model)
        self._model = model

        # Spawn the agent at a random empty position
        self._model.grid.move_to_empty(self)

    def step(self):
        # TODO: Utility functie voor het bewegen van de agent
        new_position = self.calculateshortestpath()[0]
        # TODO Log agent
        if self._cell_is_exit(new_position):
            self._remove()
        else:
            self._model.grid.move_agent(self, new_position)

    def calculateshortestpath(self) -> list[tuple[int, int]]:
        """
        Calculate the shortest path to the nearest exit

        Args:
            x_pos: The x position of the agent
            y_pos: The y position of the agent

        Returns:
            list[tuple[int, int]]: The shortest path to the nearest exit
        """
        x_pos, y_pos = self.pos
        # Assuming there could be multiple exits
        exit_positions = self.get_exit_positions()
        # Find the closest exit
        closest_exit = self.find_closest_coordinate(self.pos, exit_positions)
        # Calculate the shortest path to the closest exit
        shortest_path = nx.shortest_path(self._model.graph, source=(x_pos, y_pos), target=closest_exit)
        return shortest_path[1:]

    def get_exit_positions(self) -> list[tuple[int, int]]:
        """
        Get the coordinates of all Exit agents in the grid.

        Returns:
            list[tuple[int, int]]: A list of coordinates where Exit agents are located.
        """
        exit_positions = []
        for agent, (x, y) in self._model.grid.coord_iter():
            if isinstance(agent, Exit):
                exit_positions.append((x, y))
        return exit_positions
    
    def find_closest_coordinate(self, target_coordinates: tuple[int, int], coordinates: list[tuple[int, int]]) -> tuple[int, int]:
        """
        Find the closest coordinate to the target coordinates

        Args:
            target_coordinates: The target coordinates
            coordinates: The coordinates to compare

        Returns:
            tuple[int, int]: The closest coordinate
        """
        target_x, target_y = target_coordinates
        closest_coordinate = min(coordinates, key=lambda coord: math.dist((target_x, target_y), coord))
        return closest_coordinate

    def _cell_is_exit(self, position: tuple) -> bool:
        """
        Check if a cell on a given position is an exit cell

        Args:
            position: The coordinates of the cell

        Returns:
            bool: True if the cell contains an exit agent
        """
        is_empty = self._model.grid.is_cell_empty(position)

        cell_content = self._model.grid.get_cell_list_contents(position)

        return not is_empty and isinstance(cell_content[0], Exit)
    
    def _remove(self) -> None:
        """
        Remove self (this agent) from the simulation
        """
        self._model.grid.remove_agent(self)
        self._model.schedule.remove(self)
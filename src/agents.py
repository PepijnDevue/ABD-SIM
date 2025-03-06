import mesa

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
        new_position = self._model.pathfinder.calculateshortestpath(self.pos)[0]
        if self._cell_is_exit(new_position):
            # TODO Log agent
            self._remove()
        else:
            self._model.grid.move_agent(self, new_position)

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
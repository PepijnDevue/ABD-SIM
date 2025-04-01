import mesa
import random

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
        self._speed = 1
        self.cluster = None
        self.target_exit = None
        # Spawn the agent at a random empty position
        self._model.grid.move_to_empty(self)

    def step(self):
        """
        Step function for the agent.
        The agent moves towards the target exit.
        """
        shortest_path = self._model.pathfinder.calculate_shortest_path(self.pos, self.target_exit)

        new_position_idx = min(self._speed, len(shortest_path)) - 1
        new_position = shortest_path[new_position_idx]

        if self._model.grid._cell_is_exit(new_position):
            self._remove()
            self.model.log_agent_evacuate_time()
            
        elif self._model.grid.is_cell_empty(new_position):
            self._model.grid.move_agent(self, new_position)

    def vote_exit(self) -> None:
        """
        Vote for a target exit, for the plurality voting algorithm.
        The target exit is a probability distribution of the exits in the grid.
        """
        sorted_exits, sorted_distances = self._model.pathfinder.get_exits(self.pos)
        
        # total_distance = sum(sorted_distances)

        # probabilities = [distance/total_distance for distance in sorted_distances]

        # chosen_exit = random.choices(sorted_exits, weights=probabilities, k=1)[0]
        # TODO: Als je dit wel goed kiest met voting komen er opstoppingen van mensen die langs elkaar willen
        # Probleem voor vinden en terugzetten
        chosen_exit = sorted_exits[0]

        return chosen_exit
    
    def _remove(self) -> None:
        """
        Remove self (this agent) from the simulation
        """
        self._model.grid.remove_agent(self)
        self._model.schedule.remove(self)

class AbledPerson(Person):
    """
    Class that represents an able-bodied person in the grid derived from the Person class.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)
        self._speed = 2

class DisabledPerson(Person):
    """
    Class that represents a disabled person in the grid derived from the Person class.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)
        self._speed = 1
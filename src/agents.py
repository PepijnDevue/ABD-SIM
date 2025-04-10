import mesa
import numpy as np
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
        self.speed = 1
        self.cluster = None
        self.target_exit = None
        # Spawn the agent at a random empty position
        self._model.grid.move_to_empty(self)

    def step(self):
        """
        Step function for the agent.
        The agent moves towards the target exit.
        """
        shortest_path = self.get_exit_path()

        # If speed is 0 or the shortest path is empty, the agent does not move
        if self.speed == 0 or len(shortest_path) == 0:
            return

        new_position_idx = min(self.speed, len(shortest_path)) - 1
        new_position = shortest_path[new_position_idx]

        if self._model.grid._cell_is_exit(new_position):
            self._remove()
            self.model.log_agent_evacuate_time()
            
        elif self._model.grid.is_cell_empty(new_position):
            self._model.grid.move_agent(self, new_position)

    def get_exit_path(self) -> list[tuple[int, int]]:
        """
        Get the path to the target exit.
        The path is calculated using the pathfinder.

        Returns:
            list[tuple[int, int]]: The path to the target exit.
        """
        return self._model.pathfinder.calculate_shortest_path(self.pos, self.target_exit)
    
    def get_path_to(self, target: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Get the path to a target position.
        The path is calculated using the pathfinder.

        Args:
            target: The target position.

        Returns:
            list[tuple[int, int]]: The path to the target position.
        """
        return self._model.pathfinder.calculate_shortest_path(self.pos, target)

    def vote_exit(self) -> None:
        """
        Vote for a target exit, for the plurality voting algorithm.
        The target exit is a probability distribution of the exits in the grid.
        """
        sorted_exits, sorted_distances = self._model.pathfinder.get_exits(self.pos)
        
        # Invert the distances to weights - the smaller the distance, the higher the weight
        weights = [1 / distance for distance in sorted_distances]

        # Steepen the weights
        # alpha = 3.14159
        alpha = 31.4159 # TODO: terug naar 3.14159 en voting toevoegen
        weights = [weight ** alpha for weight in weights]

        sum_of_weights = sum(weights)

        probabilities = [weight/sum_of_weights for weight in weights]

        chosen_exit = random.choices(sorted_exits, weights=probabilities, k=1)[0]

        return chosen_exit
    
    def _remove(self) -> None:
        """
        Remove self (this agent) from the simulation
        """
        self._model.grid.remove_agent(self)
        self._model.schedule.remove(self)

    def get_approved_exits(self) -> list[tuple[int, int]]:
        """
        Returns a list of exits that the agent approves of.
        An exit is approved if it's within an acceptable distance threshold.
        """
        exits, distances = self.model.pathfinder.get_exits(self.pos)
        
        # Safety check: if no exits/distances found, return empty list
        if not distances:
            return []
        
        approved_exits = []
        
        # Approve exits within 150% of the closest exit's distance
        threshold = distances[0] * 1.5
        
        for exit_pos, distance in zip(exits, distances):
            if distance <= threshold:
                approved_exits.append(exit_pos)
        
        return approved_exits

    def get_cumulative_votes(self) -> dict[tuple[int, int], float]:
        """
        Returns a dictionary of exits and their assigned weights.
        Each agent has 10 points to distribute among exits.
        Points are distributed based on inverse distance to exits.
        
        Returns:
            dict: Dictionary mapping exit positions to vote weights
        """
        exits, distances = self.model.pathfinder.get_exits(self.pos)
        
        # If there are no exits (and thus no distances), 
        # return empty dictionary - meaning the agent can't vote
        if not distances:
            return {}
            
        total_points = 10  # Each agent gets 10 points to distribute
        weights = {}
        
        # Convert distances to inverse weights (closer exits get more points)
        inverse_distances = [1/d for d in distances]
        total_inverse = sum(inverse_distances)
        
        # Distribute points proportionally based on inverse distance
        for exit_pos, inv_dist in zip(exits, inverse_distances):
            weight = (inv_dist / total_inverse) * total_points
            weights[exit_pos] = weight
            
        return weights

class AbledPerson(Person):
    """
    Class that represents an able-bodied person in the grid derived from the Person class.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)
        self._morality_mean = model.distribution_settings["mean"]
        self._morality_std = model.distribution_settings["std"]

        
        morality_sample = np.random.normal(self._morality_mean, self._morality_std)
        clipped_morality = np.clip(morality_sample, 0, 1)
        self.morality = np.round(clipped_morality, 2)

        self.speed = 2

class DisabledPerson(Person):
    """
    Class that represents a disabled person in the grid derived from the Person class.
    """
    def __init__(self, model: mesa.Model):
        super().__init__(model)
        self.speed = 0
import mesa
import numpy as np

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
    def __init__(self, 
                 model: mesa.Model, 
                 approval_threshold: float = 1.5,
                 **kwargs
                 ) -> None:
        super().__init__(model)
        self._model = model
        self.speed = None
        self.cluster = None
        self.target_exit = None
        self.approval_threshold = approval_threshold

        # Spawn the agent at a random empty position
        self._model.grid.move_to_empty(self)

    def step(self):
        """
        Step function for the agent.
        The agent moves towards the target exit.
        """
        path_to_exit = self.get_exit_path()

        if self.speed == 0 or not path_to_exit:
            return

        # Calculate step_size based on the speed of the agent
        num_steps = min(self.speed, len(path_to_exit))

        # Take steps one by one to not jump over other agents
        for _ in range(num_steps):

            target_pos = path_to_exit.pop(0)

            # Remove the agent if it is at the exit
            if self._model.grid.cell_is_exit(target_pos):
                self._remove()
                self._model.log_agent_evacuate_time()
                return
        
            # If the new position is empty, move the agent to the new position
            if self._model.grid.is_cell_empty(target_pos):
                self._model.grid.move_agent(self, target_pos)
                continue
        
            # Handle collision with other agents
            other_agent = self._model.grid.get_cell_list_contents(target_pos)[0]


            if other_agent.target_exit == self.target_exit:
                return # Be patient and wait for the cluster-mate to move
            
            if other_agent.cluster is None:
                # Other agent is helpless disabled agent, swap positions to avoid collision
                self._model.grid.swap_agents(self, other_agent)
            else:
                # Other agent is from another cluster, merge the clusters
                self._model.clusters.merge(self.cluster, other_agent.cluster)

    def get_neighbors(self, radius: int) -> 'list[Person]':
        """
        Get all Person agents in the neighborhood of the agent.
        The neighborhood is defined by the radius parameter, using Von Neumann distance.

        Args:
            radius: The radius to search for neighbors.

        Returns:
            list[tuple[int, int]]: The neighbors of the agent.
        """
        neighbors = self._model.grid.get_neighbors(
            pos=self.pos,
            moore=False,
            include_center=False,
            radius=radius
        )

        # Filter out agents that are not of type Person
        person_neighbors = [
            agent for agent in neighbors
            if isinstance(agent, Person)
        ]

        return person_neighbors

    def get_exit_path(self) -> list[tuple[int, int]]:
        """
        Get the path to the target exit.
        The path is calculated using the pathfinder.

        Returns:
            list[tuple[int, int]]: The path to the target exit.
        """
        if not self.target_exit:
            return None

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

    def vote_exit(self) -> tuple[int, int]:
        """
        Vote for a target exit, for the plurality voting algorithm.
        The target exit is a probability distribution of the exits in the grid.
        """
        sorted_exits, sorted_distances = self._model.pathfinder.get_exits(self.pos)
        
        # Invert the distances to weights - the smaller the distance, the higher the weight
        weights = [1 / distance for distance in sorted_distances]

        # Steepen the weights
        alpha = 3.14159 # 80% chance an agent chooses either of the 3 closests exits, out of 10
        weights = [weight ** alpha for weight in weights]

        # Normalize the weights to sum to 1
        sum_of_weights = sum(weights)
        probabilities = [weight/sum_of_weights for weight in weights]

        chosen_exit_idx = np.random.choice(len(sorted_exits), p=probabilities)
        chosen_exit = sorted_exits[chosen_exit_idx]

        return chosen_exit
    
    def _remove(self) -> None:
        """
        Remove self (this agent) from the simulation
        """
        self._model.grid.remove_agent(self)
        self._model.schedule.remove(self)

    def get_approved_exits(self) -> list[tuple[int, int]]:
        """
        Used by ApprovalVoting.
        Returns a list of exits that the agent approves of.
        An exit is approved if it's within an acceptable distance threshold.
        """
        exits, distances = self.model.pathfinder.get_exits(self.pos)
        
        # Safety check: if no exits/distances found, return empty list
        if not distances:
            return []
        
        approved_exits = []
        
        # Approve exits within X% of the closest exit's distance where X is the approval threshold
        threshold = distances[0] * self.approval_threshold
        
        for exit_pos, distance in zip(exits, distances):
            if distance <= threshold:
                approved_exits.append(exit_pos)
        
        return approved_exits

    def get_cumulative_votes(self) -> dict[tuple[int, int], float]:
        """
        Used by CumulativeVoting.
        Returns a dictionary of exits and their assigned weights.
        Each agent can assert a percentage of their vote to each exit, totalling to 100%.
        Points are distributed based on inverse distance to exits.
        
        Returns:
            dict: Dictionary mapping exit positions to vote weights
        """
        exits, distances = self.model.pathfinder.get_exits(self.pos)
        
        # Safety check: if no exits/distances found, return empty dict
        if not distances:
            return {}
        # Invert distances to get weights (closer exits get more points)
        weights = [1 / distance for distance in distances]
        
        # Normalize weights to sum to 1
        total_weight = sum(weights)
        weights = [weight / total_weight for weight in weights]
        
        # Distribute points
        votes = {}
        for exit_pos, weight in zip(exits, weights):
            votes[exit_pos] = weight
            
        return votes

class AbledPerson(Person):
    """
    Class that represents an able-bodied person in the grid derived from the Person class.
    """
    def __init__(self, 
                 model: mesa.Model,
                 morality_mean: float = 0.5,
                 morality_std: float = 0.1,
                 **kwargs
                 ) -> None:
        super().__init__(model, **kwargs)
        self._morality_mean = morality_mean
        self._morality_std = morality_std
        
        self.morality = -1
        while 0 <= self.morality <= 1: 
            self.morality = np.random.normal(self._morality_mean, self._morality_std)

        self.speed = 2

class DisabledPerson(Person):
    """
    Class that represents a disabled person in the grid derived from the Person class.
    """
    def __init__(self, 
                 model: mesa.Model,
                 **kwargs
                 ) -> None:
        super().__init__(model, **kwargs)
        self.speed = 0

    def step(self) -> None:
        """
        Step function for the disabled agent.
        The agent does not move, but waits for a helping agent.
        """
        if self.speed == 0:
            self.model.clusters.call_out_cnp(self)
            return
        
        super().step()
import mesa

from .agents import DisabledPerson
import numpy as np

class RandomActivation:
    """
    Activation class that activates agents in random order.
    """
    def __init__(self):
        self._agents = {}

    def __iter__(self):
        """
        Iterate over the agents in random order.
        """
        return iter(self._agents.values())
    
    def __len__(self) -> int:
        """
        Return the number of agents in the activation list.
        """
        return len(self._agents)

    def add(self, agent: mesa.Agent) -> None:
        """
        Add an agent to the activation schedule.

        Args:
            agent: The mesa agent to add.
        """
        self._agents[agent.unique_id] = agent

    def step(self) -> None:
        """
        Randomly activate agents.
        """
        agents = list(self._agents.values())
        np.random.shuffle(agents)

        for agent in agents:
            agent.step()

    def get_disabled_agents(self) -> list[DisabledPerson]:
        """
        Get all disabled agents from the activation list.
        """
        return [
            agent for agent in self._agents.values() 
            if isinstance(agent, DisabledPerson)
        ]

    def remove(self, agent: mesa.Agent) -> None:
        """
        Remove agent from the activation list
        """
        unique_id = agent.unique_id

        if unique_id in self._agents:
            del self._agents[unique_id]

    def is_empty(self) -> bool:
        """
        Check if the list of agents is empty
        """
        return len(self._agents) == 0
import mesa

class RandomActivation:
    """
    Activation class that activates agents in random order.
    """
    def __init__(self, model: mesa.Model):
        self._model = model
        self._agents = []

    def add(self, agent: mesa.Agent) -> None:
        """
        Add an agent to the activation schedule.

        Args:
            agent: The mesa agent to add.
        """
        self._agents.append(agent)

    def step(self) -> None:
        """
        Randomly activate agents.
        """
        self._model.random.shuffle(self._agents)

        for agent in self._agents:
            agent.step()

    def remove(self, agent: mesa.Agent) -> None:
        """
        Remove agent from the activation list
        """
        self._agents.remove(agent)
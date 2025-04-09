from .agents import Person

class PluralityVoting:
    """
    Plurality voting algorithm for the simulation.
    Each cluster of students votes for a common target-exit.
    The target exit is the exit with the most votes.
    """
    def run(self, clusters: list[list[Person]]) -> None:
        """
        Run the plurality voting algorithm.
        Each cluster of students votes for a common target-exit.
        The target exit is the exit with the most votes.
        """
        for cluster in clusters:
            self.vote(cluster)

    def vote(self, agents: list[Person]) -> None:
        """
        Run the plurality voting algorithm for a cluster of agents.

        Args:
            cluster: The name of the cluster.
            agents: The agents in the cluster.
        """
        cluster_votes = {}
        for agent in agents:
            agent_vote = agent.vote_exit()

            # Add the vote to the cluster votes
            if agent_vote in cluster_votes:
                cluster_votes[agent_vote] += 1
            else:
                cluster_votes[agent_vote] = 1

        most_voted_exit = max(cluster_votes, key=cluster_votes.get)

        self._assign_target_exit(agents, most_voted_exit)

    def _assign_target_exit(self,
                            agents: list[Person], 
                            most_voted_exit: tuple[int, int]
                            ) -> None:
        """
        Assign the target exit to the agents in the cluster.

        Args:
            agents: The agents in the cluster.
            most_voted_exit: The exit with the most votes.
        """
        for agent in agents:
            agent.target_exit = most_voted_exit
from abc import ABC, abstractmethod
from .agents import Person

class VotingMethod(ABC):
    """Abstract base class for voting methods."""
    def run(self, clusters: list[list[Person]]) -> None:
        """
        Execute the voting process for the simulation.
        Agents are clustered based on their location in the grid.
        Each cluster votes for a common target exit, which is determined
        based on the specific voting method implemented.
        """
        for cluster in clusters:
            self.vote(cluster)

    @abstractmethod
    def vote(self, agents: list[Person]) -> None:
        """
        Execute the voting process for a cluster of agents.
        This method should be implemented by subclasses.
        """
        pass

    def _assign_target_exit(self, agents: list[Person], target_exit: tuple[int, int]) -> None:
        """Assign the chosen exit to all agents in the cluster."""
        for agent in agents:
            agent.target_exit = target_exit

class PluralityVoting(VotingMethod):
    """Implementation of plurality voting method."""

    def vote(self, agents: list[Person]) -> None:
        """
        Run the plurality voting for a cluster of agents.

        Args:
            agents: The agents in the cluster.
        """
        cluster_votes = {}

        for agent in agents:
            agent_vote = agent.vote_exit()

            if agent_vote in cluster_votes:
                cluster_votes[agent_vote] += 1
            else:
                cluster_votes[agent_vote] = 1

        most_voted_exit = max(cluster_votes, key=cluster_votes.get)
        
        self._assign_target_exit(agents, most_voted_exit)

class ApprovalVoting(VotingMethod):
    """Implementation of approval voting method."""

    def vote(self, agents: list[Person]) -> None:
        """
        Run the approval voting for a cluster of agents.

        Args:
            agents: The agents in the cluster.
        """
        approval_scores = {}
        
        for agent in agents:
            approved_exits = agent.get_approved_exits()
            
            for agent_vote in approved_exits:
                if agent_vote in approval_scores:
                    approval_scores[agent_vote] += 1
                else:
                    approval_scores[agent_vote] = 1

        most_approved_exit = max(approval_scores, key=approval_scores.get)
        
        self._assign_target_exit(agents, most_approved_exit)

class CumulativeVoting(VotingMethod):
    """Implementation of cumulative voting method."""

    def vote(self, agents: list[Person]) -> None:
        """
        Run the cumulative voting for a cluster of agents.
        Each agent gets multiple votes (points) they can distribute among exits.

        Args:
            agents: The agents in the cluster.
        """
        cumulative_scores = {}
        
        for agent in agents:
            # Get the weighted votes from the agent
            exit_weights = agent.get_cumulative_votes()
            
            # Add the weights to the cumulative scores
            for exit_pos, weight in exit_weights.items():
                if exit_pos in cumulative_scores:
                    cumulative_scores[exit_pos] += weight
                else:
                    cumulative_scores[exit_pos] = weight

        if not cumulative_scores:
            return

        most_voted_exit = max(cumulative_scores, key=cumulative_scores.get)
        
        self._assign_target_exit(agents, most_voted_exit)
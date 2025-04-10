from abc import ABC, abstractmethod
import mesa
import numpy as np
from .agents import Person

class VotingMethod(ABC):
    """Abstract base class for voting methods."""
    
    def __init__(self, model: mesa.Model):
        """
        Initialize the voting method.

        Args:
            model: The mesa model containing the agents and grid.
        """
        self.clusters = {}
        self._grid = model.grid
        self._schedule = model.schedule
        self._floor_plan = model.floor_plan

    @abstractmethod
    def _vote_cluster(self, cluster: str, agents: list[Person]) -> None:
        """Abstract method for cluster voting logic."""
        pass

    def run(self) -> None:
        """
        Execute the voting process for the simulation.
        Agents are clustered based on their location in the grid.
        Each cluster votes for a common target exit, which is determined
        based on the specific voting method implemented.
        """
        self._create_room_clusters()
        self._create_corridor_clusters()
        self._run_voting()

    def _run_voting(self) -> None:
        """Run the voting for all clusters."""
        for cluster, agents in self.clusters.items():
            self._vote_cluster(cluster, agents)

    def _create_room_clusters(self) -> None:
        """
        Create clusters of students based on the classroom layout.
        Each cluster is a group of students in the same classroom.
        """
        for agent in self._schedule:
            # Skip if the agent is already in a cluster
            if agent.cluster:
                continue

            x, y = agent.pos
            cluster = self._floor_plan[y][x]

            # Skip if the agent is not in a room
            if cluster == '.':
                continue

            # Assign cluster to the agent
            agent.cluster = cluster

            # Add agent to the clusters
            if cluster not in self.clusters:
                self.clusters[cluster] = []
            self.clusters[cluster].append(agent)

    def _link_agent_to_cluster(self, agent: Person, cluster: str) -> None:
        """
        Connect the agent to the cluster.
    
        Args:
            agent: The agent to connect.
            cluster: The cluster to connect to.
        """
        if cluster not in self.clusters:
            self.clusters[cluster] = []

        self.clusters[cluster].append(agent)

        agent.cluster = cluster

    def _create_corridor_clusters(self) -> None:
        """
        Create clusters of students located in the corridors.
        Using Kmeans clustering algorithm.
        """
        curr_cluster_id = 0

        for agent in self._schedule:
            if agent.cluster:
                continue

            curr_cluster_id += 1

            self._add_corridor_cluster(curr_cluster_id, agent)

    def _add_corridor_cluster(self, curr_cluster_id, agent):
        """
        Add a cluster of students located in the corridors.
        Using Kmeans clustering algorithm.
        
        Args:
            curr_cluster_id: The id of the current cluster.
            agent: The agent to add to the cluster.
        """
        cluster_name = f"c_{curr_cluster_id}"
        positions = [agent.pos]

        search_radius = 4
        max_iter = 10

        self._link_agent_to_cluster(agent, cluster_name)

        for _ in range(max_iter):
            centroid = self._calc_centroid(positions)

            # find all agents in the search radius
            search_area = self._grid.get_neighbors(
                centroid,
                moore=False,
                include_center=False,
                radius=search_radius
            )

            search_area = self._filter_neighbours(search_area)

            if len(search_area) == 0:
                break

            # Add the agents to the cluster
            for person in search_area:
                positions.append(person.pos)
                self._link_agent_to_cluster(person, cluster_name)

    def _filter_neighbours(self, search_area: list) -> list:
        """
        Filter the search area to only include Person-agents that are not in a cluster.

        Args:
            search_area: The list of agents in the search area.

        Returns:
            list: The filtered list of agents.
        """
        filtered_neighbours = []

        for obj in search_area:
            if not isinstance(obj, Person):
                continue

            if obj.cluster:
                continue

            filtered_neighbours.append(obj)

        return filtered_neighbours
            
    def _calc_centroid(self, positions: list) -> tuple:
        """
        Calculate the centroid of a set of positions.

        Args:
            positions: List of positions

        Returns:
            tuple: The centroid position
        """
        # Calculate the average position for each dimension
        centroid = np.mean(positions, axis=0)
        
        # Round the average position to the nearest integer and convert to tuple
        centroid = tuple(np.round(centroid).astype(int))
        
        return centroid

    def _assign_target_exit(self, agents: list[Person], target_exit: tuple[int, int]) -> None:
        """Assign the chosen exit to all agents in the cluster."""
        for agent in agents:
            agent.target_exit = target_exit

class PluralityVoting(VotingMethod):
    """Implementation of plurality voting method."""

    def _vote_cluster(self, cluster: str, agents: list[Person]) -> None:
        """
        Run the plurality voting for a cluster of agents.

        Args:
            cluster: The name of the cluster.
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

    def _vote_cluster(self, cluster: str, agents: list[Person]) -> None:
        """
        Run the approval voting for a cluster of agents.

        Args:
            cluster: The name of the cluster.
            agents: The agents in the cluster.
        """
        approval_scores = {}
        
        for agent in agents:
            approved_exits = agent.get_approved_exits()
            
            for exit in approved_exits:
                if exit in approval_scores:
                    approval_scores[exit] += 1
                else:
                    approval_scores[exit] = 1

        most_approved_exit = max(approval_scores, key=approval_scores.get)
        self._assign_target_exit(agents, most_approved_exit)

class CumulativeVoting(VotingMethod):
    """Implementation of cumulative voting method."""

    def _vote_cluster(self, cluster: str, agents: list[Person]) -> None:
        """
        Run the cumulative voting for a cluster of agents.
        Each agent gets multiple votes (points) they can distribute among exits.

        Args:
            cluster: The name of the cluster.
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
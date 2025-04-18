import numpy as np
import mesa

from .agents import Person, AbledPerson, DisabledPerson
from .cnp import ContractNetProtocol
from .voting_methods import VotingMethod, PluralityVoting, ApprovalVoting, CumulativeVoting

class Clusters:
    """
    Keep track of clusters, groups and pairs of agents.
    """
    def __init__(self, 
                 model: mesa.Model, 
                 voting_method: str = "plurality",
                 cluster_search_radius: int = 4,
                 **kwargs
                 ) -> None:
        self._clusters = {}
        self._schedule = model.schedule
        self._floor_plan = model.floor_plan
        self._grid = model.grid
        self.search_radius = cluster_search_radius

        self._cnp = ContractNetProtocol(**kwargs)
        self._voting = self._setup_voting_method(voting_method)

    def __iter__(self):
        return iter(self._clusters.values())
    
    def __len__(self) -> int:
        return len(self._clusters)
    
    def run(self) -> None:
        """
        Run the clustering algorithms.
        Cluster agents based on their positions.
        All agents in the same room are in the same cluster.
        Other agents in the corridor are clustered using k-means.
        """
        self._create_cnp_pairs()

        self._create_room_clusters()

        self._create_corridor_clusters()

        self._voting.run(self._clusters.values())

    def merge(self, cluster1: str, cluster2: str) -> None:
        """
        Merge two clusters into one, returning the new cluster.
        Let the two clusters revote for a new target exit.
        """
        new_cluster = self._merge(cluster1, cluster2)

        agents = self._clusters[new_cluster]

        self._voting.vote(agents)

    def call_out_cnp(self, disabled_agent: DisabledPerson) -> None:
        """
        Call out for proposals from abled agents.
        """
        new_pair = self._cnp.call_out(disabled_agent)

        self._update(new_pair)

    def _setup_voting_method(self, method: str) -> VotingMethod:
        """
        Setup the voting method based on the input parameter.
        
        Args:
            method: The voting method to use ("plurality" or "approval")
            
        Returns:
            VotingMethod: The initialized voting method
        """
        match method.lower():
            case "approval":
                return ApprovalVoting()
            case "plurality":
                return PluralityVoting()
            case "cumulative":
                return CumulativeVoting()
            case _:
                raise ValueError(f"Unknown voting method: {method}.")

    def _create_cnp_pairs(self) -> None:
        """
        Create pairs of disabled agents and helping abled agents.
        The pairs a created using the Contract Net Protocol (CNP).
        """
        disabled_agents = self._schedule.get_disabled_agents()

        new_pairs = self._cnp.run(disabled_agents)

        self._update(new_pairs)

    def _update(self, new_clusters: dict[str, list[Person]]) -> None:
        """
        Update the clusters with new clusters.
        """
        for cluster, agents in new_clusters.items():
            for agent in agents:
                self._add_to_cluster(cluster, agent)

    def _create_room_clusters(self) -> None:
        """
        Create clusters of students based on the classroom layout.
        Each cluster is a group of students in the same classroom.
        """
        for agent in self._schedule:
            # Skip if the agent is already in a cluster or disabled
            if agent.cluster or isinstance(agent, DisabledPerson):
                continue

            x, y = agent.pos
            cluster = self._floor_plan[y][x]

            # Skip if the agent is not in a room
            if cluster == '.':
                continue

            self._add_to_cluster(cluster, agent)

    def _create_corridor_clusters(self) -> None:
        """
        Create clusters of students located in the corridors.
        Using Kmeans clustering algorithm.
        """
        cur_cluster_id = 0

        for agent in self._schedule:
            if agent.cluster or isinstance(agent, DisabledPerson):
                continue

            cur_cluster_id += 1

            self._add_corridor_cluster(cur_cluster_id, agent)

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

        self._add_to_cluster(cluster_name, agent)

        max_iter = 10
        for _ in range(max_iter):
            centroid = self._calc_centroid(positions)

            # find all agents in the search radius
            search_area = self._grid.get_neighbors(
                centroid,
                moore=False,
                include_center=False,
                radius=self.search_radius
            )

            search_area = self._filter_neighbours(search_area)

            if len(search_area) == 0:
                break

            for person in search_area:
                # Update the cluster positions
                positions.append(person.pos)

                self._add_to_cluster(cluster_name, person)

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
            if not isinstance(obj, AbledPerson):
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
    
    def _add_to_cluster(self,
                       cluster: str,
                       agent: Person
                       ) -> None:
        """
        Add an agent to a cluster.
        If the cluster does not exist, create it.
        """
        # Remove the agent from its current cluster
        if agent.cluster:
            self._clusters[agent.cluster].remove(agent)

        self._add_cluster(cluster)
        self._clusters[cluster].append(agent)

        agent.cluster = cluster

    def _add_cluster(self, cluster: str) -> None:
        """
        Add a new cluster to the clusters dictionary.
        """
        self._clusters.setdefault(cluster, [])

    def _merge(self, cluster1: str, cluster2: str) -> str:
        """
        Merge two clusters into one, returning the new cluster.
        """
        new_cluster = f"({cluster1})_({cluster2})"

        for agent in self._clusters[cluster1] + self._clusters[cluster2]:
            self._add_to_cluster(new_cluster, agent)

        self._remove(cluster1)
        self._remove(cluster2)

        return new_cluster

    def _remove(self, cluster: str) -> None:
        """
        Remove a cluster from the clusters dictionary.
        """
        del self._clusters[cluster]

    
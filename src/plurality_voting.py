import mesa

import numpy as np

from .agents import Person

class PluralityVoting:
    """
    Plurality voting algorithm for the simulation.
    Each cluster of students votes for a common target-exit.
    The target exit is the exit with the most votes.
    """
    def __init__(self, model: mesa.Model):
        """
        Initialize the plurality voting algorithm.

        Args:
            model: The mesa model containing the agents and grid.
        """
        self._clusters = model.clusters
        self._grid = model.grid
        self._schedule = model.schedule
        self._floor_plan = model.floor_plan

    def run(self) -> None:
        """
        Setup the plurality voting algorithm for the simulation.
        Cluster the agents based on their location in the grid.
        Each cluster then votes for a common target-exit.
        The target exit is the exit with the most votes.
        """
        # Clustering
        self._create_room_clusters()
        self._create_corridor_clusters()

        # Voting
        self._plurality_voting()

    def revote(self, cluster_a: str, cluster_b: str) -> None:
        """
        Two clusters meet and combine, they need to revote for a target exit.
        The clusters are merged and the agents in the clusters are assigned to the new cluster.
        """
        print("Revote:")
        merged_cluster = self._clusters.merge_clusters(cluster_a, cluster_b)

        self._vote_cluster(merged_cluster)

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

            # Add agent to the clusters
            self._clusters.add_to_cluster(cluster, agent)

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

        self._clusters.add_to_cluster(cluster_name, agent)

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
                self._clusters.add_to_cluster(cluster_name, person)

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

    def _plurality_voting(self) -> None:
        """
        Run the plurality voting algorithm.
        Each cluster of students votes for a common target-exit.
        The target exit is the exit with the most votes.
        """
        for agents in self._clusters:
            self._vote_cluster(agents)

    def _vote_cluster(self,
                      agents: list[Person]) -> None:
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
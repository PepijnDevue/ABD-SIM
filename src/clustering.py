from .agents import Person

class Clusters:
    """
    Keep track of clusters, groups and pairs of agents.
    """
    def __init__(self):
        self._clusters = {}

    def __iter__(self):
        return iter(self._clusters.values())
    
    def __len__(self) -> int:
        return len(self._clusters)
    
    def get_cluster(self, cluster: str) -> list[Person]:
        """
        Get a cluster by its name.
        """
        return self._clusters[cluster]
    
    def add_to_cluster(self,
                       cluster: str,
                       agent: Person
                       ) -> None:
        """
        Add an agent to a cluster.
        If the cluster does not exist, create it.
        """
        self.add_cluster(cluster)
        self._clusters[cluster].append(agent)

        agent.cluster = cluster

    def add_cluster(self, cluster: str) -> None:
        """
        Add a new cluster to the clusters dictionary.
        """
        self._clusters.setdefault(cluster, [])

    def merge_clusters(self, cluster1: str, cluster2: str) -> list[Person]:
        """
        Merge two clusters into one, returning the new cluster.
        """
        new_cluster = f"({cluster1})_({cluster2})"

        self._clusters[new_cluster] = self._clusters[cluster1] + self._clusters[cluster2]

        for agent in self._clusters[new_cluster]:
            agent.cluster = new_cluster

        return self._clusters[new_cluster]

    def remove(self, cluster: str) -> None:
        """
        Remove a cluster from the clusters dictionary.
        """
        del self._clusters[cluster]

    
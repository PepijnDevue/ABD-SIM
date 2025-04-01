import math
import networkx as nx
import mesa

from .agents import Wall, Exit

class Pathfinder:
    def __init__(self, grid: mesa.space.SingleGrid):
        self._exit_positions = self._get_exit_positions(grid)
        self._graph = self._setup_graph(grid)
    
    def calculate_shortest_path(self, 
                                from_pos: tuple[int, int], 
                                to_pos: tuple[int, int]
                                ) -> list[tuple[int, int]]:
        """
        Calculate the shortest path from one position to another using Dijkstra's algorithm.
        """ 
        shortest_path = nx.shortest_path(self._graph, source=from_pos, target=to_pos)

        return shortest_path[1:]
    
    def get_exits(self, from_pos: tuple[int, int]) -> list[tuple[int, int]]:
        """
        Get the exits sorted by distance from the given position.
        
        Args:
            from_pos: The position to get the exits from.

        Returns:
            list: A list of exit positions sorted by distance from the given position.
        """
        exit_distances = self._get_exit_distances(from_pos)

        exit_distance_pairs = zip(self._exit_positions, exit_distances)

        sorted_exit_pairs = sorted(exit_distance_pairs, key=lambda x: x[1])

        # Unzip the sorted pairs into two separate lists
        sorted_exits, sorted_distances = zip(*sorted_exit_pairs)

        return sorted_exits, sorted_distances

    def _get_exit_distances(self, from_pos):
        """
        Get the distances to all exits from a given position.
        """
        exit_distances = []

        for exit_pos in self._exit_positions:
            path = nx.shortest_path(self._graph, source=from_pos, target=exit_pos)

            distance = len(path) - 1

            exit_distances.append(distance)  

        return exit_distances

    def _setup_graph(self, grid: mesa.space.SingleGrid) -> nx.Graph:
        graph = nx.Graph()

        for agent, coordinates in grid.coord_iter():
            # Skip wall agents and create a node for non-wall agents
            if isinstance(agent, Wall):
                continue
            
            graph.add_node(coordinates)
            neighbors = grid.get_neighborhood(coordinates, moore=False, include_center=False)
            
            for neighbor in neighbors:
                # Cell content is a list of agents in the cell, it is empty if the cell is empty and has no agents
                cell_content = grid.get_cell_list_contents(neighbor)
                
                # If the neighbor cell is empty and not a wall, add an edge
                if len(cell_content) == 0:
                    graph.add_edge(coordinates, neighbor)
                else:
                    # Otherwise, check if the neighbor contains an agent that is not a wall
                    neighbor_agent = cell_content[0]
                    if not isinstance(neighbor_agent, Wall):
                        graph.add_edge(coordinates, neighbor)

        return graph
    
    def _get_exit_positions(self, grid: mesa.space.SingleGrid) -> list[tuple[int, int]]:
        exit_positions = []
        for agent, (x, y) in grid.coord_iter():
            if isinstance(agent, Exit):
                exit_positions.append((x, y))
        return exit_positions

    def _find_closest_coordinate(self, 
                                target_coordinates: tuple[int, int], 
                                coordinates: list[tuple[int, int]]
                                ) -> tuple[int, int]:
        target_x, target_y = target_coordinates
        closest_coordinate = min(coordinates, key=lambda coord: math.dist((target_x, target_y), coord))
        return closest_coordinate
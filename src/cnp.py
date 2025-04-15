import mesa
import numpy as np

from .agents import Person, AbledPerson, DisabledPerson

class ContractNetProtocol:
    """
    Contract Net Protocol (CNP) for the simulation.
    Each disabled agent calls for proposals from abled agents.
    The abled agents respond with bids based on distance and morality.
    The best contractor is selected based on the bid score.
    """
    def __init__(self, 
                 cnp_call_radius: int=10, 
                 **kwargs
                 ) -> None:
        """
        Initialize the ContractNetProtocol class.
        """
        self._call_radius = cnp_call_radius

        self._pair_id = 0

    def run(self, 
            disabled_agents: list[DisabledPerson]
            ) -> dict[str, list[Person]]:
        """Run the contract net protocol."""
        pairs = {}

        for agent in disabled_agents:
            pair = self.call_out(agent)

            pairs.update(pair)

        return pairs

    def call_out(self, 
                 disabled_agent: DisabledPerson
                 ) -> dict[str, list[Person]]:
        """
        Call out for proposals from abled agents.
        The disabled agent will set its target exit and call for proposals.
        The abled agents will respond with bids based on distance and morality.
        The best contractor will be selected based on the bid score.
        If no contractors are available, the disabled agent will not be paired.
        """
        disabled_agent.target_exit = disabled_agent.vote_exit()

        # Get available contractors
        contractors = self._call_for_proposal(disabled_agent)

        if not contractors:
            return {} # No contractors available, move to the next disabled agent

        # Add bids to the contractors dictionary
        bids = self._get_bids(contractors, disabled_agent.pos)
        
        # Find the best contractor based on the bid score
        best_bid_idx = np.argmin(bids)
        best_contractor = contractors[best_bid_idx]

        pair = self._pair_agents(disabled_agent, best_contractor)

        return pair

    def _pair_agents(self, 
                     disabled_agent: DisabledPerson, 
                     best_contractor: AbledPerson
                     ) -> dict[str, list[Person]]:
        """
        Pair the disabled agent with the best contractor.
        Match target exit, cluster and speed of the agents.
        """
        best_contractor.target_exit = disabled_agent.target_exit

        best_contractor.speed = 1
        disabled_agent.speed = 1

        self._pair_id += 1

        cluster_name = f"pair_{self._pair_id}"

        return {cluster_name: [disabled_agent, best_contractor]}

    def _call_for_proposal(self, disabled_agent: DisabledPerson) -> list[AbledPerson]:
        """
        Identify contractors willing to bid for assisting the disabled agent.
        """
        contractors = []

        nearby_abled_agents = self._find_contractors(disabled_agent)

        manager_exit_dist = len(disabled_agent.get_exit_path())

        contractors = [
            abled_agent for abled_agent in nearby_abled_agents
            if self._check_bid_willingness(abled_agent, 
                                           disabled_agent.pos,
                                           manager_exit_dist)
        ]

        return contractors
    
    def _check_bid_willingness(self, 
                               contractor: AbledPerson,
                               manager_position: tuple[int, int],
                               manager_exit_dist: int
                               ) -> bool:
        """
        Check if the contractor is willing to bid for the disabled agent.
        This dicision is based on the morality of the contractor and some distances.

        M = Morality of the contractor
        Dm = Distance from contractor to manager
        Dme = Distance from manager to exit
        Dce = Distance from contractor to exit

        willing = (1 - M) * ((Dm / 2) + Dme) <= Dce / 2
        """
        M = contractor.morality
        Dm = len(contractor.get_path_to(manager_position))
        Dme = manager_exit_dist
        Dce = len(contractor.get_path_to(contractor.vote_exit()))

        return (1 - M) * ((Dm / 2) + Dme) <= Dce / 2
    
    def _get_bids(self,
                  contractors: list[DisabledPerson],
                  manager_pos,
                  ) -> list[int]:
        """
        Get the bids of the contractors
        This is sumply the distance between the contractor and the disabled agent.
        """
        bids = []

        for contractor in contractors:
            # Get the path to the disabled agent
            path_to_manager = contractor.get_path_to(manager_pos)

            # Get the bid based on the distance to the disabled agent
            bid = len(path_to_manager)

            bids.append(bid)

        return bids
    
    def _find_contractors(self, disabled_agent: DisabledPerson) -> dict[mesa.Agent, int]:
        """
        Filter the agents in the absolute area by pathfinding and return a list of dictionaries
        containing the agent's ID and the agent object.
        """
        nearby_agents = disabled_agent.get_neighbors(radius=self._call_radius)

        # Filter out agents that are not of type AbledPerson and include their IDs
        nearby_abled_agents = [
            agent for agent in nearby_agents
            if isinstance(agent, AbledPerson)
        ]

        # Filter out agents that are not in the step range of the disabled agent
        nearby_abled_agents = self._filter_by_pathfinding(disabled_agent, nearby_abled_agents)
        
        return nearby_abled_agents

    def _filter_by_pathfinding(self,
                               disabled_agent: DisabledPerson,
                               nearby_abled_agents: list[AbledPerson]) -> list[AbledPerson]:
        """
        Filter the agents in the absolute area by pathfinding and return a list of dictionaries
        containing the agent's ID and the agent object.
        """
        reachable_abled_agents = []

        for agent in nearby_abled_agents:
            # Check if the agent is within the step range of the disabled agent using pathfinding
            shortest_path = disabled_agent.get_path_to(agent.pos)

            if len(shortest_path) <= self._call_radius:
                reachable_abled_agents.append(agent)

        return reachable_abled_agents
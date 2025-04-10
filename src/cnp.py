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
    def __init__(self):
        """
        Initialize the ContractNetProtocol class.
        """
        self._cfp_radius = 10

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

        # Get the path to the exit for the disabled agent
        caller_exit_path = disabled_agent.get_exit_path()

        # Get available contractors
        contractors = self._call_for_proposal(disabled_agent)

        if not contractors:
            return {} # No contractors available, move to the next disabled agent

        # Add bids to the contractors dictionary
        bids = self._get_bids(
            disabled_agent, 
            contractors, 
            len(caller_exit_path)
        )
        
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

    def _get_bids(self,
                      disabled_agent: DisabledPerson,
                      contractors: list[AbledPerson],
                      distance_to_exit: int
                      ) -> list[float]:
        """
        Handle the bidding process for a disabled agent.
        """
        bids = []

        for contractor in contractors:
            path_to_caller = contractor.get_path_to(disabled_agent.pos)

            P_score = self._calculate_bid(
                morality=contractor.morality,
                distance_to_caller=len(path_to_caller),
                distance_to_exit=distance_to_exit
            )

            bids.append(P_score)

        return bids

    def _calculate_bid(self,
                       morality: float, 
                       distance_to_caller: int, 
                       distance_to_exit: int
                       ) -> float:
        """
        Calculate the bid score for the contractor.

        The bid score is calculated based on the morality of the agent,
        the distance to the caller and the distance to the exit.
        The formula is:
        P_score = (1 - M) * ((Dd / 2) + De)
        where:
        M = morality of the agent
        Dd = distance to caller
        De = distance to exit

        Args:
            morality: The morality of the agent.
            distance_to_caller: The distance from the contractor to the caller.
            distance_to_exit: The distance from the caller to the exit.
        """
        M = morality
        Dd = distance_to_caller
        De = distance_to_exit
        
        P_score = (1 - M) * ((Dd / 2) + De)
        return P_score

    def _call_for_proposal(self, disabled_agent: DisabledPerson) -> list[AbledPerson]:
        """
        Identify contractors willing to bid for assisting the disabled agent.
        """
        contractors = []

        nearby_abled_agents = self._find_contractors(disabled_agent)

        contractors = [
            abled_agent for abled_agent in nearby_abled_agents
            if self._check_bid_willingness(abled_agent)
        ]

        return contractors

    def _check_bid_willingness(self, agent: AbledPerson) -> bool:
        """
        Assess if the agent is willing to bid based on their morality
        and if they are not already helping.
        """
        bid_chance = np.random.uniform(0, 1)

        willing_to_bid = bid_chance <= agent.morality

        return willing_to_bid
    
    def _find_contractors(self, disabled_agent: DisabledPerson) -> dict[mesa.Agent, int]:
        """
        Filter the agents in the absolute area by pathfinding and return a list of dictionaries
        containing the agent's ID and the agent object.
        """
        nearby_agents = disabled_agent.get_neighbors(radius=self._cfp_radius)

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

            if len(shortest_path) <= self._cfp_radius:
                reachable_abled_agents.append(agent)

        return reachable_abled_agents
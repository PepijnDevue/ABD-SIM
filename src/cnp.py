import mesa
import numpy as np

from .agents import AbledPerson, DisabledPerson

class ContractNetProtocol:
    """
    Contract Net Protocol (CNP) for the simulation.
    Each disabled agent calls for proposals from abled agents.
    The abled agents respond with bids based on distance and morality.
    The best contractor is selected based on the bid score.
    """
    def __init__(self, model: mesa.Model):
        """
        Initialize the plurality voting algorithm.

        Args:
            model: The mesa model containing the agents and grid.
        """
        self._model = model
        self._clusters = model.clusters
        self._floor_plan = model.floor_plan
        self._grid = model.grid
        self._agents = model.schedule._agents
        self._disabled_agents = {
            agent.unique_id: agent 
            for agent in self._agents.values() 
            if isinstance(agent, DisabledPerson)
        }
        self._cfp_search_area = 10

    def run(self) -> None:
        """Run the contract net protocol."""
        pair_id = 0

        for disabled_agent in self._disabled_agents.values():
            # Set the target exit for the disabled agent
            disabled_agent.target_exit = disabled_agent.vote_exit()

            # Get the path to the exit for the disabled agent
            caller_exit_path = disabled_agent.get_exit_path()

            # Get available contractors
            contractors = self._call_for_proposal(disabled_agent)

            if not contractors:
                continue  # No contractors available, move to the next disabled agent

            # Add bids to the contractors dictionary
            self._process_bids(disabled_agent, 
                               contractors, 
                               len(caller_exit_path)
                               )
            
            # Sort the contractors by bid score
            contractors.sort(key=lambda x: x["bid"], reverse=True)

            # Get the best contractor
            best_contractor = contractors[0]['agent']

            self._pair_agents(pair_id, disabled_agent, best_contractor)

            pair_id += 1

    def _pair_agents(self, couple_id, disabled_agent, best_contractor):
        """
        Pair the disabled agent with the best contractor.
        Match target exit, cluster and speed of the agents.
        """
        best_contractor.target_exit = disabled_agent.target_exit

        cluster_name = f"pair_{couple_id}"
        self._clusters.add_to_cluster(cluster_name, disabled_agent)
        self._clusters.add_to_cluster(cluster_name, best_contractor)

        best_contractor.speed = 1
        disabled_agent.speed = 1

    def _process_bids(self,
                      disabled_agent: DisabledPerson,
                      contractors: list[dict[str, mesa.Agent]],
                      distance_to_exit: int) -> None:
        """
        Handle the bidding process for a disabled agent.
        """
        for contractor in contractors:
            abled_agent = contractor["agent"]
            path_to_caller = abled_agent.get_path_to(disabled_agent.pos)

            P_score = self._calculate_bid(morality=abled_agent.morality,
                                          distance_to_caller=len(path_to_caller),
                                          distance_to_exit=distance_to_exit)
            contractor["bid"] = P_score

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

    def _call_for_proposal(self, disabled_agent: DisabledPerson) -> list[dict[str, mesa.Agent]]:
        """
        Identify contractors willing to bid for assisting the disabled agent.
        """
        contractors = []

        abled_agents_in_range = self._filter_by_search_area(disabled_agent)

        # Check for every abled agent in the range if they are willing to bid
        for agent_dict in abled_agents_in_range:
            agent = agent_dict["agent"]

            # Add the agent to the contractors list if they are willing to bid
            if self._check_bid_willingness(agent):
                contractors.append(agent_dict)

        return contractors

    def _check_bid_willingness(self, agent):
        """
        Assess if the agent is willing to bid based on their morality.
        """
        bid_chance = np.random.uniform(0, 1)

        willing_to_bid = bid_chance <= agent.morality

        return willing_to_bid
    
    def _filter_by_search_area(self, disabled_agent: DisabledPerson) -> dict[mesa.Agent, int]:
        """
        Filter the agents in the absolute area by pathfinding and return a list of dictionaries
        containing the agent's ID and the agent object.
        """
        # First scan the absolute area of the disabled agent ignoring walls
        abs_abled_agents_in_range = self._scan_absolute_area(disabled_agent)

        # Filter out agents that are not in the step range of the disabled agent
        abled_agents_in_range = self._filter_by_pathfinding(disabled_agent, abs_abled_agents_in_range)
        return abled_agents_in_range

    def _scan_absolute_area(self, disabled_agent: DisabledPerson) -> list[dict[mesa.Agent, int]]:
        """
        Scan the absolute area of the disabled agent ignoring walls and return a list of dictionaries
        containing the agent's ID and the agent object.
        """
        agents_in_range = self._grid.get_neighbors(
            pos=disabled_agent.pos,
            moore=False,
            include_center=False,
            radius=self._cfp_search_area
        )
        # Filter out agents that are not of type AbledPerson and include their IDs
        abled_agents_in_range = [
            {"id": {agent.unique_id}, "agent": agent}
            for agent in agents_in_range 
            if isinstance(agent, AbledPerson)
        ]
        return abled_agents_in_range

    def _filter_by_pathfinding(self,
                               disabled_agent: DisabledPerson,
                               abs_abled_agents_in_range: list[dict[mesa.Agent, int]]) -> list[dict[mesa.Agent, int]]:
        """
        Filter the agents in the absolute area by pathfinding and return a list of dictionaries
        containing the agent's ID and the agent object.
        """
        abled_agents_in_range = []

        for agent_dict in abs_abled_agents_in_range:
            agent = agent_dict["agent"]

            # Check if the agent is within the step range of the disabled agent using pathfinding
            shortest_path = disabled_agent.get_path_to(agent.pos)

            if len(shortest_path) <= self._cfp_search_area:
                abled_agents_in_range.append(agent_dict)

        return abled_agents_in_range
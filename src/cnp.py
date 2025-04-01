import mesa

import mesa.agent
import numpy as np

from .agents import AbledPerson, DisabledPerson
from .pathfinding import Pathfinder

class ContractNetProtocol:
    """

    """
    def __init__(self, model: mesa.Model):
        """
        Initialize the plurality voting algorithm.

        Args:
            model: The mesa model containing the agents and grid.
        """
        self.model = model
        self._floor_plan = model.floor_plan
        self._grid = model.grid
        self._pathfinder = Pathfinder(self._grid)
        self._agents = model.schedule._agents
        self._disabled_agents = {
            agent.unique_id: agent for agent in self._agents.values() if isinstance(agent, DisabledPerson)
        }
        self._cfp_search_area = 10

    def run(self) -> None:
        """Run the contract net protocol."""
        for disabled_agent in self._disabled_agents.values():
            caller_exit_path = self._pathfinder.calculate_shortest_path(disabled_agent.pos,
                                                                disabled_agent.target_exit)
            caller_exit_distance = len(caller_exit_path)

            # Get available contractors
            contractors = self._call_for_proposal(disabled_agent)
            if not contractors:
                continue  # No contractors available, move to the next disabled agent

            # Add bids to the contractors dictionary
            self._process_bids(disabled_agent, contractors, caller_exit_distance)
            
            # Sort the contractors by bid score
            contractors.sort(key=lambda x: x["bid"], reverse=True)
            # Get the best contractor
            best_contractor = contractors[0]
            # Assign the best contractor to the disabled agent
            disabled_agent.contractor = best_contractor

    def _process_bids(self,
                      disabled_agent: DisabledPerson,
                      contractors: list[dict[str, mesa.Agent]],
                      caller_exit_distance: int) -> None:
        """
        Handle the bidding process for a disabled agent.
        """
        for contractor in contractors:
            abled_agent = contractor["agent"]
            path_to_caller = self._pathfinder.calculate_shortest_path(abled_agent.pos,
                                                                      disabled_agent.pos)
            distance_to_caller = len(path_to_caller)
            P_score = self._calculate_bid(disabled_agent,
                                          abled_agent,
                                          A=distance_to_caller,
                                          B=caller_exit_distance)
            contractor["bid"] = P_score

    def _calculate_bid(self,disabled_agent: DisabledPerson, abled_agent: AbledPerson, A: int, B: int) -> float:
        """
        Pscore = (1 - M) *((A/2) + B) 
        """
        M = abled_agent.morality
        # Calculate the bid score
        P_score = (1 - M) * ((A / 2) + B)
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
            # Roll a dice between 0 and 1
            bid_chance = np.random.uniform(0, 1)
            # Add the agent to the contractors list if they are willing to bid
            if bid_chance <= agent.morality:
                # Add the agent to the contractors list
                contractors.append(agent_dict)
        # Return the contractors list
        return contractors
    

    def _filter_by_search_area(self, disabled_agent) -> dict[mesa.Agent, int]:
        """
        #TODO doc
        """
        # First scan the absolute area of the disabled agent ignoring walls
        abs_abled_agents_in_range = self._scan_absolute_area(disabled_agent)
        # Filter out agents that are not in the step range of the disabled agent
        abled_agents_in_range = self._filter_by_pathfinding(disabled_agent, abs_abled_agents_in_range)
        return abled_agents_in_range

    def _scan_absolute_area(self, disabled_agent: mesa.Agent) -> list[dict[mesa.Agent, int]]:
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
            for agent in agents_in_range if isinstance(agent, AbledPerson)
        ]
        return abled_agents_in_range

    def _filter_by_pathfinding(self,
                               disabled_agent: mesa.Agent,
                               abs_abled_agents_in_range: list[dict[mesa.Agent, int]]) -> list[dict[mesa.Agent, int]]:
        """
        Filter the agents in the absolute area by pathfinding and return a list of dictionaries
        containing the agent's ID and the agent object.
        """
        abled_agents_in_range = []
        for agent_dict in abs_abled_agents_in_range:
            agent = agent_dict["agent"]
            # Check if the agent is within the step range of the disabled agent using pathfinding
            shortest_path = self._pathfinder.calculate_shortest_path(disabled_agent.pos, agent.pos)
            if len(shortest_path) <= self._cfp_search_area:
                abled_agents_in_range.append(agent_dict)
        return abled_agents_in_range


    # def _assign_target_exit(self,
    #                         agents, 
    #                         most_voted_exit: tuple[int, int]
    #                         ) -> None:
    #     """
    #     Assign the target exit to the agents in the cluster.

    #     Args:
    #         agents: The agents in the cluster.
    #         most_voted_exit: The exit with the most votes.
    #     """
    #     for agent in agents:
    #         agent.target_exit = most_voted_exit
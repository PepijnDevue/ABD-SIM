from agents import DisabledPerson, AbledPerson

import numpy as np

class CNP:
    def __init__(self, abled_agent, disabled_agent):
        """
        Initialize the CNP Process.

        Parameters:
        - valid_persons (list): A list with Abled agents, result from the class AbledPerson.
        - disabled_person (CNPDisabledPerson): The disabled agent.
        - request_radius (float): De maximale afstand waarop hulp gevraagd wordt.
        """
        self.valid_persons = abled_agent
        self.disabled_person = disabled_agent
        self.request_radius = 6

    def request_help(self, person):
        # Lijst met alle abled agents binnen een radius van 6 blokken
        # De invalide agents worden op volgorde gekoppeld
        all_disabled_agents = [agent for agent in self.schedule.agents if isinstance(agent, DisabledPerson)]
        possibile_helpers = [
            agent for agent in self.valid_persons
            if self.disabled_person.distance_to(person) <= self.request_radius
        ]

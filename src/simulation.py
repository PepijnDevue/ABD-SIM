import mesa

from .agents import AbledPerson, DisabledPerson

from .plurality_voting import PluralityVoting
from .cnp import ContractNetProtocol
from .activation import RandomActivation
from .floor_plan import floor_plans
from .pathfinding import Pathfinder
from .grid import Grid
from .log import log_sim

import time

from .ui import show_grid

class Simulation(mesa.Model):
    """
    Simulation class for the evacuating a building.
    """
    def __init__(self, floor_plan: str, distribution_settings: dict[str, float], num_agents: int=5):
        """
        Setup the simulation with a grid, agents and schedule.

        Args:
            floor_plan: The used floorplan_name
            num_agents: The number of agents to spawn
        """
        super().__init__()
        self.schedule = RandomActivation(self)

        self.floor_plan = floor_plans[floor_plan]

        self.grid = Grid(self, self.floor_plan)

        self.pathfinder = Pathfinder(self.grid)

        self.plurality_voting = PluralityVoting(self)

        self.distribution_settings = distribution_settings

        self.spawn_agents(num_agents)

        self.cnp = ContractNetProtocol(self)

        self._step_count = 0

        self._exit_times = []

        show_grid(self.grid)

    def log_agent_evacuate_time(self):
        """
        Log the simulation-time, an agent has evacuated
        """
        self._exit_times.append(
            self._step_count
        )

    def spawn_agents(self, num_agents: int=1, abled_to_disabled_ratio=0.95) -> None:
        """
        Spawn agents scattered around the grid.
        """
        # Spawn able agents
        for _ in range(int(num_agents * abled_to_disabled_ratio)):
            agent = AbledPerson(self)
            self.schedule.add(agent)

        # Spawn disabled agents
        for _ in range(int(num_agents * (1 - abled_to_disabled_ratio))):
            agent = DisabledPerson(self)
            self.schedule.add(agent)

    def step(self):
        """
        Simulate one timestep of the simulation.
        """
        self.schedule.step()

        # time.sleep(0.2)

        self._step_count += 1

    def run(self, max_time_steps: int=100):
        """
        Run an entire simulation.

        Args:
            max_time_steps: The number of timesteps to run the simulation for.
        """
        self.plurality_voting.run()

        self.cnp.run()

        for _ in range(max_time_steps):
            show_grid(self.grid, cls=True)

            time.sleep(1)

            self.step()

            if self.schedule.is_empty():
                show_grid(self.grid, cls=True)
                break

        print("Simulation completed...")
        log_sim(self._exit_times, self._step_count)
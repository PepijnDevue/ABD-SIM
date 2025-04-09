import mesa

from .agents import AbledPerson, DisabledPerson

from .activation import RandomActivation
from .clustering import Clusters
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

        self.distribution_settings = distribution_settings

        self.spawn_agents(num_agents)

        self._step_count = 0

        self._prev_time = time.time()

        self._exit_times = []

        self.clusters = Clusters(self)

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

    def run(self, max_time_steps: int=10_000) -> None:
        """
        Run an entire simulation.

        Args:
            max_time_steps: The number of timesteps to run the simulation for.
        """
        self.clusters.run()

        while not self._is_finished(max_time_steps):
            show_grid(self.grid, cls=True)

            self._sleep(0.15)

            self.schedule.step()

            self._step_count += 1

        show_grid(self.grid, cls=True)

        print("Simulation completed...")
        log_sim(self._exit_times, self._step_count, len(self.schedule))

    def _is_finished(self, max_time_steps: int) -> bool:
        """
        Check if the simulation is finished.
        The simulation is finished when all agents have evacuated.
        """
        if self._step_count >= max_time_steps:
            return True

        only_disabled = all(
            isinstance(agent, DisabledPerson) and agent.speed == 0
            for agent in self.schedule
        )

        if only_disabled:
            return True

        is_empty = self.schedule.is_empty()

        return is_empty
    
    def _sleep(self, seconds: float) -> None:
        """
        Sleep for a given number of seconds.
        Calculate based on time passed since the last step.
        """
        cur_time = time.time()
        delta_time = cur_time - self._prev_time

        if delta_time < seconds:
            time.sleep(seconds - delta_time)

        self._prev_time = cur_time
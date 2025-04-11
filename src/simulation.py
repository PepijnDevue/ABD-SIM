import mesa

from .agents import AbledPerson, DisabledPerson, Wall, Exit

from .activation import RandomActivation
from .clustering import Clusters
from .floor_plan import floor_plans
from .pathfinding import Pathfinder
from .grid import Grid
from .log import Logger

import time

from .ui import show_grid

class Simulation(mesa.Model):
    """
    Simulation class for the evacuating a building.
    """
    def __init__(self, 
                 floor_plan: str,
                 **settings
                 ) -> None:
        """
        Setup the simulation with a grid, agents and schedule.

        Args:
            floor_plan: The used floorplan_name
            distribution_settings: Settings for agent distribution
            voting_method: The voting method to use ("plurality", "approval", or "cumulative")
            num_agents: The number of agents to spawn
        """
        super().__init__()
        self._settings = settings

        self.floor_plan = floor_plans[floor_plan]

        self._log = Logger(settings)

    def _setup(self) -> None:
        """
        Setup the simulation.
        """
        self.schedule = RandomActivation()

        self.grid = Grid(
            width=len(self.floor_plan[0]),
            height=len(self.floor_plan),
        )

        self._initialize_grid()

        self.pathfinder = Pathfinder(self.grid)

        self._spawn_agents()

        self._step_count = 0

        self._prev_time = time.time()

        self._exit_times = []

        self.clusters = Clusters(self, **self._settings)

    def log_agent_evacuate_time(self):
        """
        Log the simulation-time, an agent has evacuated
        """
        self._exit_times.append(
            self._step_count
        )

    def _spawn_agents(self) -> None:
        """
        Spawn agents scattered around the grid.
        """
        num_agents = self._settings.get("num_agents", 250)
        abled_to_disabled_ratio = self._settings.get("abled_to_disabled_ratio", 0.95)

        # Spawn able agents
        for _ in range(int(num_agents * abled_to_disabled_ratio)):
            agent = AbledPerson(self)
            self.schedule.add(agent)

        # Spawn disabled agents
        for _ in range(int(num_agents * (1 - abled_to_disabled_ratio))):
            agent = DisabledPerson(self)
            self.schedule.add(agent)

    def run(self, 
            num_batches: int = 10, 
            verbose: bool = False,
            frame_duration_seconds: float = 0
            ) -> None:
        """
        Run an entire simulation.

        Args:
            max_time_steps: The number of timesteps to run the simulation for.
        """
        max_time_steps = self._settings.get("max_time_steps", 1_000)

        for _ in range(num_batches):
            self._setup()

            print(f"Running batch {_ + 1}/{num_batches}...")

            self.clusters.run()

            while not self._is_finished(max_time_steps):
                if verbose:
                    show_grid(self.grid, cls=True)

                self._sleep(frame_duration_seconds)

                self.schedule.step()

                self._step_count += 1

            if verbose:
                show_grid(self.grid, cls=True)

            self._log.add_run(
                evac_times=self._exit_times, 
                total_evac_time=self._step_count, 
                num_agents_left=len(self.schedule)
            )

        print("Simulation completed...")
        self._log.save()

    def _initialize_grid(self) -> None:
        """
        Fill the grid with walls and exits based on the floor plan.
        """
        for y, row in enumerate(self.floor_plan):
            for x, cell in enumerate(row):
                if cell == 'W':
                    self.grid.place_agent(Wall(self), (x, y))
                elif cell == 'E':
                    self.grid.place_agent(Exit(self), (x, y))

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
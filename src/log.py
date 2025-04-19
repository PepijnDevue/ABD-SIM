import pandas as pd

class Logger:
    """
    A class to handle logging of simulation data.
    """
    def __init__(self, 
                 settings: dict|None=None,
                 ) -> None:
        """
        Initialize the Logger with settings.
        """
        self._log = []

        self._settings = settings or {}

    def add(self, 
                evac_times: list[int],
                total_evac_time: int,
                num_agents_left: int,
                ) -> None:
        """
        Add a single run to the log.

        Args:
            evac_times: The individual evacuation times of the agents
            total_evac_time: The total evacuation time in steps.
            num_agents_left: The number of agents left in the simulation.
        """
        run_data = {
            "avg_evac_time": sum(evac_times) / len(evac_times),
            "total_evac_time": total_evac_time,
            "num_agents_left": num_agents_left,
            "evac_times": evac_times,
        }

        # Add settings and run_data to create row
        row = {**self._settings, **run_data}

        # Add row to the log
        self._log.append(row)

    __call__ = add     

    def get(self) -> pd.DataFrame:
        """
        Get the log as a DataFrame.
        """
        return pd.DataFrame(self._log)
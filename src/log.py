import os
import json

class Logger:
    """
    A class to handle logging of simulation data.
    """
    def __init__(self, settings: dict|None=None) -> None:
        """
        Initialize the Logger with settings.
        """
        self._log = {}

        self._log_num = self._read_increment_log_count()
        self._log["settings"] = settings
        self._log["runs"] = []

    def add_run(self,
                evac_times: list[int],
                total_evac_time: int,
                num_agents_left: int,
                ) -> None:
        """
        Add a run to the log.

        Args:
            evac_times: The individual evacuation times of the agents
            total_evac_time: The total evacuation time in steps.
            num_agents_left: The number of agents left in the simulation.
        """
        run_data = {
            "evac_times": evac_times,
            "avg_evac_time": sum(evac_times) / len(evac_times),
            "total_evac_time": total_evac_time,
            "num_agents_left": num_agents_left,
        }

        self._log["runs"].append(run_data)

    def save(self) -> None:
        """
        Save the log to a JSON file.
        """
        log_json = os.path.join(os.path.dirname(__file__), "logs", f"log_{self._log_num}.json")

        with open(log_json, "w", encoding="utf-8") as json_file:
            json.dump(self._log, json_file, indent=4)

    def _read_increment_log_count(self) -> int:
        """
        Read from logs/cnt for next unique log-number, also increment it

        Returns:
            int: A unique log-num
        """
        file_path = os.path.join(os.path.dirname(__file__), "logs", "cnt.txt")

        with open(file_path, "r", encoding="utf-8") as file:
            count = int(file.read())
        
        count += 1

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(str(count))

        return count
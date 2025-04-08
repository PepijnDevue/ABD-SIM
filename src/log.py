import os
import json

def log_sim(evac_times: list[int],
            total_evac_time: int,
            num_agents_left: int,
            voting_method: str
            ) -> None:
    """
    Log the simulation data, save as log_n.json

    Args:
        exit_times: The individual evac times of the agents
        last_step_cnt: The total evac time in steps. The first timestep where the building is empty.
    """
    log_num = read_increment_log_count()

    data = {
        "voting_method": voting_method,
        "exit_times": evac_times,
        "avg_evacuation_time": sum(evac_times) / len(evac_times),
        "total_evacuation_time": total_evac_time,
        "num_agents_left": num_agents_left
        }
    
    write_log(log_num, data)

def write_log(log_num: int, data: dict|list) -> None:
    """
    Write simdata to a log file with given count

    Args:
        log_num: the unique log num
        data: The data to log
    """
    log_json = os.path.join(os.path.dirname(__file__), "logs", f"log_{log_num}.json")

    with open(log_json, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)

def read_increment_log_count() -> int:
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
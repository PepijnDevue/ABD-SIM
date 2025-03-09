import os
import json

def log_sim(exit_times: list[int], last_step_cnt) -> None:
    file_path = os.path.join(os.path.dirname(__file__), "logs", "cnt")

    with open(file_path, "r", encoding="utf-8") as file:
        cnt = int(file.read())

    log_json = os.path.join(os.path.dirname(__file__), "logs", f"log_{cnt}.json")

    data = {
        "exit_times": exit_times,
        "avg_evacuation_time": sum(exit_times) / len(exit_times),
        "total_evacuation_time": last_step_cnt
        }

    with open(log_json, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)

    cnt += 1

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(str(cnt))
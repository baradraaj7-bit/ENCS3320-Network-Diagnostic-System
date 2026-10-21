import json
import threading
from pathlib import Path


LOG_FILE = Path("logs/commands_log.json")

log_lock = threading.Lock()


def load_logs():

    if not LOG_FILE.exists():
        return []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):
        return []


def read_logs():

    with log_lock:
        return load_logs()


def log_request(client_ip, client_port, result):

    new_log = {
        "timestamp": result["timestamp"],
        "client_ip": client_ip,
        "client_port": client_port,
        "command": result["command"],
        "parameter": result["parameter"],
        "execution_time": result["execution_time"],
        "status": result["status"]
    }

    with log_lock:

        logs = load_logs()

        logs.append(new_log)

        LOG_FILE.parent.mkdir(exist_ok=True)

        with open(LOG_FILE, "w", encoding="utf-8") as file:
            json.dump(logs, file, indent=4)

    return new_log
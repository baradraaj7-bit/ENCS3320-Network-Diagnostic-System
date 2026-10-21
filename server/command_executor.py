import subprocess
import time
import os
from datetime import datetime


def execute_command(command_name, parameter=""):

    command_name = command_name.upper().strip()
    parameter = parameter.strip()

    # These commands need a hostname
    if command_name in ["PING", "TRACERT", "NSLOOKUP"] and parameter == "":
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command_name,
            "parameter": parameter,
            "status": "Failure",
            "execution_time": 0,
            "output": "Missing hostname"
        }

    # Windows commands
    if os.name == "nt":

        if command_name == "PING":
            command = ["ping", parameter]

        elif command_name == "TRACERT":
            command = ["tracert", parameter]

        elif command_name == "NSLOOKUP":
            command = ["nslookup", parameter]

        elif command_name == "IPCONFIG":
            command = ["ipconfig"]

        elif command_name == "ROUTE":
            command = ["route", "print"]

        elif command_name == "ARP":
            command = ["arp", "-a"]

        elif command_name == "NETSTAT":
            command = ["netstat", "-an", "-p", "tcp"]

        else:
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "command": command_name,
                "parameter": parameter,
                "status": "Failure",
                "execution_time": 0,
                "output": "Invalid command"
            }

    # Linux commands
    else:

        if command_name == "PING":
            command = ["ping", "-c", "4", parameter]

        elif command_name == "TRACERT":
            command = ["traceroute", parameter]

        elif command_name == "NSLOOKUP":
            command = ["nslookup", parameter]

        elif command_name == "IPCONFIG":
            command = ["ip", "addr"]

        elif command_name == "ROUTE":
            command = ["ip", "route"]

        elif command_name == "ARP":
            command = ["ip", "neigh"]

        elif command_name == "NETSTAT":
            command = ["ss", "-tan"]

        else:
            return {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "command": command_name,
                "parameter": parameter,
                "status": "Failure",
                "execution_time": 0,
                "output": "Invalid command"
            }

    start_time = time.time()

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            errors="replace"
        )

        end_time = time.time()
        execution_time = round(end_time - start_time, 2)

        if result.returncode == 0:
            status = "Success"
        else:
            status = "Failure"

        output = result.stdout

        if result.stderr:
            output += "\n" + result.stderr

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command_name,
            "parameter": parameter,
            "status": status,
            "execution_time": execution_time,
            "output": output.strip()
        }

    except FileNotFoundError:

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command_name,
            "parameter": parameter,
            "status": "Failure",
            "execution_time": round(time.time() - start_time, 2),
            "output": "Command is not available on this operating system"
        }

    except Exception as error:

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "command": command_name,
            "parameter": parameter,
            "status": "Failure",
            "execution_time": round(time.time() - start_time, 2),
            "output": str(error)
        }
from server.logger import read_logs


def get_statistics():

    logs = read_logs()

    total_commands = len(logs)
    successful_requests = 0
    failed_requests = 0
    total_execution_time = 0
    command_count = {}

    for log in logs:

        total_execution_time += log["execution_time"]

        if log["status"] == "Success":
            successful_requests += 1
        else:
            failed_requests += 1

        command = log["command"]

        if command in command_count:
            command_count[command] += 1
        else:
            command_count[command] = 1

    if total_commands > 0:
        average_execution_time = round(
            total_execution_time / total_commands, 2
        )
    else:
        average_execution_time = 0

    if command_count:
        most_used_command = max(command_count, key=command_count.get)
    else:
        most_used_command = "None"

    return {
        "total_commands": total_commands,
        "most_used_command": most_used_command,
        "average_execution_time": average_execution_time,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests
    }
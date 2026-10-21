from server.logger import read_logs


def search_logs(command="", hostname="", client_ip=""):

    logs = read_logs()
    results = []

    command = command.strip().lower()
    hostname = hostname.strip().lower()
    client_ip = client_ip.strip().lower()

    for log in logs:

        command_match = (
            command == "" or command in log["command"].lower()
        )

        hostname_match = (
            hostname == "" or hostname in log["parameter"].lower()
        )

        ip_match = (
            client_ip == "" or client_ip in str(log["client_ip"]).lower()
        )

        if command_match and hostname_match and ip_match:
            results.append(log)

    return results
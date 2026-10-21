from socket import *
import os
import json
from urllib.parse import urlparse, parse_qs
from server.statistics import get_statistics


# PROJECT PATH

baseFolder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# READ CONFIG FILE

with open(os.path.join(baseFolder, "config.json"), "r") as f:
    config = json.load(f)


serverPort = config["http_server"]["port"]


# SERVER SOCKET

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(('', serverPort))
serverSocket.listen(5)


# FOLDERS AND FILES


htmlFolder = os.path.join(baseFolder, "web")
logFile = os.path.join(baseFolder, "logs", "commands_log.json")


print("The server is ready to receive")


# LOAD LOGS

def load_logs():

    if not os.path.exists(logFile):
        return []

    try:

        with open(logFile, "r", encoding="utf-8") as file:
            return json.load(file)

    except (json.JSONDecodeError, OSError):

        return []
    
# DASHBOARD DATA

def get_dashboard_data():

    logs = load_logs()

    executed_commands = len(logs)

    client_ips = set()

    for log in logs:

        client_ip = log.get("client_ip", "")

        if client_ip:
            client_ips.add(client_ip)

    connected_clients = len(client_ips)

    if logs:

        last_execution = logs[-1].get("timestamp", "")

    else:

        last_execution = "No executions yet"

    return executed_commands, connected_clients, last_execution


# START SERVER

while True:

    connectionSocket, addr = serverSocket.accept()

    request = connectionSocket.recv(4096)
    request = request.decode()

    if not request:

        connectionSocket.close()
        continue


    # REQUEST LINE

    requestLine = request.splitlines()[0]

    print("Request Line:")
    print(requestLine)

    parts = requestLine.split()


    # 400 BAD REQUEST

    if len(parts) != 3:

        response = (
            "HTTP/1.1 400 Bad Request\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            "<html>"
            "<body>"
            "<h1>400 Bad Request</h1>"
            "</body>"
            "</html>"
        )

        connectionSocket.send(response.encode())
        connectionSocket.close()

        continue


    method = parts[0]
    requestTarget = parts[1]
    version = parts[2]


    # PARSE URL

    parsedURL = urlparse(requestTarget)

    path = parsedURL.path
    query = parse_qs(parsedURL.query)


    print("Method:", method)
    print("Path:", path)
    print("Version:", version)


    
    # SEARCH

    if path == "/search.html" and "searchBy" in query and "search" in query:

        searchBy = query["searchBy"][0]
        searchValue = query["search"][0]

        print("Search By:", searchBy)
        print("Search Value:", searchValue)

        logs = load_logs()

        results = []

        for log in logs:

            if searchBy == "command":

                if searchValue.lower() in log.get("command", "").lower():
                    results.append(log)

            elif searchBy == "client_ip":

                if searchValue in log.get("client_ip", ""):
                    results.append(log)

            elif searchBy == "hostname":

                if searchValue.lower() in log.get("parameter", "").lower():
                    results.append(log)


        # Build table rows

        tableRows = ""

        for log in results:

            tableRows += (
                "<tr>"
                "<td>" + str(log.get("timestamp", "")) + "</td>"
                "<td>" + str(log.get("command", "")) + "</td>"
                "<td>" + str(log.get("parameter", "")) + "</td>"
                "<td>" + str(log.get("client_ip", "")) + "</td>"
                "<td>" + str(log.get("execution_time", "")) + "</td>"
                "<td>" + str(log.get("status", "")) + "</td>"
                "</tr>"
            )


        if len(results) == 0:

            tableRows = (
                "<tr>"
                "<td colspan='6'>No results found.</td>"
                "</tr>"
            )


        content = """
        <!DOCTYPE html>

        <html>

        <head>
            <title>Search Results</title>
        </head>

        <body>

            <h1>Search Results</h1>

            <p>Search by: """ + searchBy + """</p>

            <p>Search value: """ + searchValue + """</p>

            <table border="1">

                <tr>
                    <th>Timestamp</th>
                    <th>Command</th>
                    <th>Parameter</th>
                    <th>Client IP</th>
                    <th>Execution Time</th>
                    <th>Status</th>
                </tr>

                """ + tableRows + """

            </table>

            <br>

            <a href="/search.html">Back to Search</a>

        </body>

        </html>
        """


        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            + content
        )

        connectionSocket.send(response.encode())
        connectionSocket.close()

        continue


    # STATISTICS

    if path == "/statistics.html":

        stats = get_statistics()


        content = """
        <!DOCTYPE html>

        <html lang="en">

        <head>

            <meta charset="UTF-8">

            <title>Statistics</title>

        </head>

        <body>

            <header>

                <h1>Statistics</h1>

                <nav>

                    <a href="/">Home</a>
                    <a href="/dashboard.html">Dashboard</a>
                    <a href="/history.html">History</a>
                    <a href="/statistics.html">Statistics</a>
                    <a href="/search.html">Search</a>
                    <a href="/download.html">Download</a>

                </nav>

            </header>


            <main>

                <p>
                    Most Frequently Used Command:
                    """ + str(stats["most_used_command"]) + """
                </p>

                <p>
                    Average Execution Time:
                    """ + str(stats["average_execution_time"]) + """
                    seconds
                </p>

                <p>
                    Successful Requests:
                    """ + str(stats["successful_requests"]) + """
                </p>

                <p>
                    Failed Requests:
                    """ + str(stats["failed_requests"]) + """
                </p>

            </main>


            <footer>

                <p>About ENCS3320</p>

                <p>Brief description of the project</p>

            </footer>

        </body>

        </html>
        """


        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            + content
        )

        connectionSocket.send(response.encode())
        connectionSocket.close()

        continue


    # DASHBOARD

    if path == "/dashboard.html":

        filePath = os.path.join(htmlFolder, "dashboard.html")

        try:

            with open(filePath, "r", encoding="utf-8") as file:
                content = file.read()


            executed_commands, connected_clients, last_execution = get_dashboard_data()


            content = content.replace(
                "{{executed_commands}}",
                str(executed_commands)
            )

            content = content.replace(
                "{{connected_clients}}",
                str(connected_clients)
            )

            content = content.replace(
                "{{last_execution}}",
                str(last_execution)
            )

            content = content.replace(
                "{{server_uptime}}",
                "Not available yet"
            )


            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                + content
            )


        except FileNotFoundError:

            filePath = os.path.join(htmlFolder, "404.html")

            with open(filePath, "r", encoding="utf-8") as file:
                content = file.read()


            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                + content
            )


        connectionSocket.send(response.encode())
        connectionSocket.close()
        continue
 
    if path == "/history.html":

       filePath = os.path.join(htmlFolder, "history.html")

       with open(filePath, "r", encoding="utf-8") as file:
          content = file.read()

       logs = load_logs()

       rows = ""
       for log in logs:
          rows += (
            "<tr>"
            "<td>" + str(log.get("timestamp", "")) + "</td>"
            "<td>" + str(log.get("client_ip", "")) + "</td>"
            "<td>" + str(log.get("command", "")) + "</td>"
            "<td>" + str(log.get("parameter", "")) + "</td>"
            "<td>" + str(log.get("execution_time", "")) + "</td>"
            "<td>" + str(log.get("status", "")) + "</td>"
            "</tr>"
        )

       if not rows:
          rows = "<tr><td colspan='6'>No commands executed yet.</td></tr>"

       content = content.replace("{{history_rows}}", rows)

       response = (
         "HTTP/1.1 200 OK\r\n"
         "Content-Type: text/html\r\n"
         "\r\n"
         + content
       )
       connectionSocket.send(response.encode())
       connectionSocket.close()
       continue
    # DOWNLOAD LOG

    if path == "/download":

        try:

            with open(logFile, "rb") as file:
                content = file.read()


            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: application/json\r\n"
                "Content-Disposition: attachment; filename=\"commands_log.json\"\r\n"
                "Content-Length: " + str(len(content)) + "\r\n"
                "\r\n"
            ).encode() + content


            connectionSocket.send(response)
            connectionSocket.close()

            continue


        except FileNotFoundError:

            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                "<html>"
                "<body>"
                "<h1>404 Not Found</h1>"
                "<p>Log file not found.</p>"
                "</body>"
                "</html>"
            )


            connectionSocket.send(response.encode())
            connectionSocket.close()

            continue


    # 403 FORBIDDEN

    forbidden = False


    if path == "/logs":

        forbidden = True
        fileName = None


    
    # NORMAL ROUTING

    elif path == "/":

        fileName = "index.html"


    elif path == "/dashboard.html":

        fileName = "dashboard.html"


    elif path == "/history.html":

        fileName = "history.html"


    elif path == "/statistics.html":

        fileName = "statistics.html"


    elif path == "/search.html":

        fileName = "search.html"


    elif path == "/download.html":

        fileName = "download.html"


    else:

        fileName = None


    # 403 RESPONSE

    if forbidden:

        response = (
            "HTTP/1.1 403 Forbidden\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            "<html>"
            "<body>"
            "<h1>403 Forbidden</h1>"
            "<p>You do not have permission to access this resource.</p>"
            "</body>"
            "</html>"
        )


    # 200 RESPONSE

    elif fileName is not None:

        filePath = os.path.join(htmlFolder, fileName)


        try:

            with open(filePath, "r", encoding="utf-8") as file:
                content = file.read()


            response = (
                "HTTP/1.1 200 OK\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                + content
            )


        except FileNotFoundError:

            filePath = os.path.join(htmlFolder, "404.html")


            with open(filePath, "r", encoding="utf-8") as file:
                content = file.read()


            response = (
                "HTTP/1.1 404 Not Found\r\n"
                "Content-Type: text/html\r\n"
                "\r\n"
                + content
            )


    # 404 RESPONSE

    else:

        filePath = os.path.join(htmlFolder, "404.html")


        with open(filePath, "r", encoding="utf-8") as file:
            content = file.read()


        response = (
            "HTTP/1.1 404 Not Found\r\n"
            "Content-Type: text/html\r\n"
            "\r\n"
            + content
        )


    # SEND RESPONSE

    connectionSocket.send(response.encode())

    connectionSocket.close()
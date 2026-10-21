from socket import *
import threading
import json

from server.command_executor import execute_command
from server.logger import log_request


# open the config file and read the port number 
with open("config.json", "r") as f:
    config = json.load(f)

SERVER_PORT = config["tcp_server"]["port"]
# get the port number and store it 


HEADER_SIZE = 10


def send_msg(sock, text):
    data = text.encode()
    header = str(len(data)).rjust(HEADER_SIZE).encode()
    sock.sendall(header + data)


def recv_exact(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            return None
        buf += chunk
    return buf


def recv_msg(sock):
    header = recv_exact(sock, HEADER_SIZE)
    if header is None:
        return None
    msg_length = int(header.decode().strip())
    data = recv_exact(sock, msg_length)
    if data is None:
        return None
    return data.decode()


# to handle one client
def handle_client(connection_socket, address):
    client_ip = address[0]
    # the ip address of the client
    client_port = address[1]
    # port number 

    print(f"Client connected: {client_ip}:{client_port}")
    print(f"Thread started for {client_ip}:{client_port}")

    send_msg(connection_socket, "Connected to Network Diagnostic System")

    try:
        while True:
            request = recv_msg(connection_socket)
            # wait until the client sends something

            if request is None:
                # if nothing was received
                break

            request = request.strip()
            

            print(f"Request from {client_ip}:{client_port}: {request}")



            if request == "EXIT":
                send_msg(connection_socket, "Goodbye")
                break

            
            parts = request.split(" ", 1)
            command_name = parts[0]
            parameter = parts[1] if len(parts) > 1 else ""

            result = execute_command(command_name, parameter)

            log_request(client_ip, client_port, result)

            response = (
                f"Command: {result['command']} {result['parameter']}\n"
                f"Status: {result['status']}\n"
                f"Execution Time: {result['execution_time']} seconds\n\n"
                f"{result['output']}"
            )
            

            send_msg(connection_socket, response)
            # send the response back to the client

    except ConnectionResetError:
        # if the client disconnects 
        print(f"Client disconnected unexpectedly: {client_ip}:{client_port}")

    finally:
        connection_socket.close()
        print(f"Connection closed: {client_ip}:{client_port}")


server_socket = socket(AF_INET, SOCK_STREAM)


server_socket.bind(('', SERVER_PORT))


server_socket.listen(5)


print("TCP Server is running...")
print(f"Listening on port {SERVER_PORT}...")
print("Waiting for clients...")


while True:

    connection_socket, address = server_socket.accept()
    # when a client connects we get a new socket 

    client_thread = threading.Thread(
        target=handle_client,
        args=(connection_socket, address)
    )

    client_thread.start()

    print(f"Active thread: {client_thread.name}")
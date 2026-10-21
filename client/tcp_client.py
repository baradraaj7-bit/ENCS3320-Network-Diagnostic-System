from socket import *
import json


with open("config.json", "r") as f:
    config = json.load(f)

SERVER_HOST = "localhost"
SERVER_PORT = config["tcp_server"]["port"]


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


def display_menu():
    print()
    print("       Network Diagnostic System      ")
    print("1. Ping Host")
    print("2. Trace Route")
    print("3. DNS Lookup")
    print("4. IP Configuration")
    print("5. Routing Table")
    print("6. ARP Table")
    print("7. Active TCP Connections")
    print("8. Exit")


client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
# connect to the server 


message = recv_msg(client_socket)
# wait for the welcome message 

print(message)


while True:

    display_menu()

    choice = input("Select: ").strip()
    

    if choice == "1":
        hostname = input("Enter hostname: ").strip()
        request = "PING " + hostname
        # to build the text we will send 

    elif choice == "2":
        hostname = input("Enter hostname: ").strip()
        request = "TRACERT " + hostname

    elif choice == "3":
        hostname = input("Enter hostname: ").strip()
        request = "NSLOOKUP " + hostname

    elif choice == "4":
        request = "IPCONFIG"

    elif choice == "5":
        request = "ROUTE PRINT"

    elif choice == "6":
        request = "ARP"

    elif choice == "7":
        request = "NETSTAT"

    elif choice == "8":
        send_msg(client_socket, "EXIT")

        response = recv_msg(client_socket)
        # goodbye reply

        print(response)

        break

    else:
        print("Invalid choice. Please select a number from 1 to 8")
        continue

    send_msg(client_socket, request)
    

    response = recv_msg(client_socket)

    print()
    print("       ---       ")
    print("Server Response:")
    print(response)

    input("Press enter to continue ")


client_socket.close()
import subprocess
import sys


print("TCP server and HTTP server are both starting...")

# Start TCP server
tcp_server = subprocess.Popen(
    [sys.executable, "-m", "server.tcp_server"]
)

# Start HTTP server
http_server = subprocess.Popen(
    [sys.executable, "-m", "web.Socket"]
)

# Keep run_server.py running
try:
    tcp_server.wait()
    http_server.wait()

except KeyboardInterrupt:
    print("\nStopping servers...")

    tcp_server.terminate()
    http_server.terminate()

    tcp_server.wait()
    http_server.wait()

    print("Servers stopped.")

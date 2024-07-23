import socket
import threading
from queue import Queue
import re

# Initialize the queue and list to hold open ports
queue = Queue()
open_ports = []

# Dictionary of common ports and services
COMMON_PORTS = {
    20: "FTP",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    111: "RPCBind",
    135: "MS RPC",
    139: "NetBIOS",
    143: "IMAP",
    443: "HTTPS",
    445: "Microsoft-DS",
    993: "IMAPS",
    995: "POP3S",
    1723: "PPTP",
    3306: "MySQL",
    3389: "RDP",
    5900: "VNC",
    8080: "HTTP-Proxy",
}

def is_valid_ip(ip):
    """
    Validate an IP address.
    """
    pattern = re.compile(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$")
    return pattern.match(ip) is not None

def is_valid_port_range(port_range):
    """
    Validate a port range.
    """
    try:
        start, end = map(int, port_range.split('-'))
        return 1 <= start <= end <= 65535
    except (ValueError, AttributeError):
        return False

def port_scan(port):
    """
    Scan a single port on the target host.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((TARGET, port))
        if result == 0:
            open_ports.append(port)
        sock.close()
    except socket.error:
        pass

def worker():
    """
    Worker function to get ports from the queue and scan them.
    """
    while not queue.empty():
        port = queue.get()
        port_scan(port)
        queue.task_done()

def run_scanner(target, port_range):
    """
    Main function to run the port scanner.
    """
    start, end = map(int, port_range.split('-'))
    
    # Fill the queue with ports
    for port in range(start, end + 1):
        queue.put(port)

    # Create and start worker threads
    threads = []
    for _ in range(100):  # Adjust the number of threads as needed
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Display results
    print(f"\nOpen ports on {target}:")
    for port in open_ports:
        service = COMMON_PORTS.get(port, "Unknown")
        print(f"Port {port}: {service}")

if __name__ == "__main__":
    # Get user input for target IP and port range
    target = input("Enter the target IP address: ").strip()
    port_range = input("Enter the port range (e.g., 1-1024): ").strip()

    # Validate the input
    if not is_valid_ip(target):
        print("Invalid IP address.")
    elif not is_valid_port_range(port_range):
        print("Invalid port range.")
    else:
        # Run the scanner if inputs are valid
        TARGET = target
        run_scanner(TARGET, port_range)

import socket
from datetime import datetime
import argparse

def scan_ports(target):
    print(f"Scanning target: {target}")
    print("Scanning ports 1–1024...")
    print("-" * 50)

    start_time = datetime.now()

    for port in range(1, 1025):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)  # Timeout for faster scanning
                result = s.connect_ex((target, port))
                
                if result == 0:
                    print(f"Port {port} is OPEN")
                    
        except KeyboardInterrupt:
            print("\nScan stopped by user.")
            break
        except socket.gaierror:
            print("Hostname could not be resolved.")
            break
        except socket.error:
            print("Couldn't connect to server.")
            break

    end_time = datetime.now()
    print("-" * 50)
    print(f"Scanning completed in: {end_time - start_time}")

if __name__ == "__main__":
    target_host = input("Enter target IP or hostname: ")
    scan_ports(target_host)
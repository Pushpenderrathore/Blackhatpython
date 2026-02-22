import socket
import os

target = "scanme.nmap.org"

for port in range(20, 512):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        result = client.connect_ex((target,port))
        
        if result == 0:
            print(f"Port {port} is open")

        else:
            print(f"Port {port} is close")

        client.close()
        
        
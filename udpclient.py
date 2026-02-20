import socket
import argparse

class UDPClient:
    def __init__(self, target: str, port: int, message: str, timeout=5):
        self.target = target
        self.port = port
        self.message = message.encode()  # convert string to bytes
        self.timeout = timeout

    def run(self):
        # create UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
            client.settimeout(self.timeout)

            # send data
            client.sendto(self.message, (self.target, self.port))
            print(f"[+] Sent data to {self.target}:{self.port}")

            try:
                # receive response
                data, addr = client.recvfrom(4096)
                print(f"[+] Received response from {addr}")
                print(data.decode())
            except socket.timeout:
                print("[-] No response received (timeout)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple UDP Client")

    parser.add_argument("-t", "--target", required=True, help="Target IP address")
    parser.add_argument("-p", "--port", required=True, type=int, help="Target port")
    parser.add_argument("-m", "--message", required=True, help="Message to send")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds")

    args = parser.parse_args()

    client = UDPClient(args.target, args.port, args.message, args.timeout)
    client.run()
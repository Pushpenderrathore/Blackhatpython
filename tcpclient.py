import socket
import argparse

class TCPClient:
    def __init__(self, target: str, port: int, timeout=5):
        self.target = target
        self.port = port
        self.timeout = timeout

    def run(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.settimeout(self.timeout)
            client.connect((self.target, self.port))
            client.sendall(data.encode())
            try:
                response = client.recv(4096)
                return response.decode(errors="ignore")
            except socket.timeout:
                return "[!] No response (timeout)"


def main():
    parser = argparse.ArgumentParser(description="Simple TCP Client")
    parser.add_argument("-t", "--target", required=True, help="Target Host")
    parser.add_argument("-p", "--port", required=True, type=int, help="Target Port")
    parser.add_argument("-m", "--message", required=True, help="Message to send")

    args = parser.parse_args()

    client = TCPClient(args.target, args.port)
    response = client.run(args.message)

    print("[+] Response:")
    print(response)


if __name__ == "__main__":
    main()

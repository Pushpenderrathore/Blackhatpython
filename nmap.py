import socket
import argparse
import threading
from datetime import datetime

class NmapLite:
    def __init__(self,target: str,start_port: int,end_port: int,protocol: str = "tcp",timeout: float = 0.5):
        self.target = target
        self.start_port = start_port
        self.end_port = end_port
        self.protocol = protocol.lower()
        self.timeout = timeout
        self.open_ports = []
        self.lock = threading.Lock()

    def scan(self):
        print(f"[+] Scanning {self.target}")
        print(f"[+] Ports: {self.start_port}-{self.end_port}")
        print(f"[+] Protocol: {self.protocol.upper()}")
        print("-" * 50)

        start_time = datetime.now()

        threads = []
        for port in range(self.start_port, self.end_port):
            t = threading.Thread(target=self._scan_port, args=(port,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        end_time = datetime.now()

        print("-" * 50)
        print(f"[+] Scan completed in: {end_time - start_time}")
        print(f"[+] Open Ports: {self.open_ports}")

    def _scan_port(self, port):
        if self.protocol == "tcp":
            self._tcp_scan(port)
        elif self.protocol == "udp":
            self._udp_scan(port)

    def _tcp_scan(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                result = s.connect_ex((self.target, port))

                if result == 0:
                    with self.lock:
                        self.open_ports.append(port)
                    print(f"[OPEN] TCP {port}")

        except:
            pass

    def _udp_scan(self, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(self.timeout)
                s.sendto(b"", (self.target, port))
                s.recvfrom(1024)

                with self.lock:
                    self.open_ports.append(port)
                print(f"[OPEN] UDP {port}")

        except socket.timeout:
            pass
        except:
            pass


def main():
    parser = argparse.ArgumentParser(description="Mini Nmap Scanner")

    parser.add_argument("-t", "--target", required=True, help="Target host")
    parser.add_argument("-sp", "--start-port", type=int, default=1, help="Start port")
    parser.add_argument("-ep", "--end-port", type=int, default=1024, help="End port")
    parser.add_argument("-P", "--protocol", default="tcp", help="tcp or udp")
    parser.add_argument("-T", "--timeout", type=float, default=0.5, help="Timeout")

    args = parser.parse_args()

    scanner = NmapLite(args.target,args.start_port,args.end_port,args.protocol,args.timeout)

    scanner.scan()


if __name__ == "__main__":
    main()
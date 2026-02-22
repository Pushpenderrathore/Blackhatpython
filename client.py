import socket
import argparse


class NetworkClient:
    def __init__(self, target: str, port: int, message: str, protocol: str = "tcp", timeout: int = 5):
        self.target = target
        self.port = port
        self.message = message.encode()
        self.protocol = protocol.lower()
        self.timeout = timeout

    def run(self):
        if self.protocol == "tcp":
            return self._run_tcp()
        elif self.protocol == "udp":
            return self._run_udp()
        else:
            return "[!] Invalid protocol selected. Use tcp or udp."

    def _run_tcp(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(self.timeout)
                client.connect((self.target, self.port))
                client.sendall(self.message)
                response = client.recv(4096)
                return response.decode(errors="ignore")
    
            
        except socket.timeout:
            return "[!] No response (timeout)"
        except KeyboardInterrupt:
            return "[!] User Interrupted"
        except ConnectionRefusedError:
            return "[!] Connection Refused"
        except socket.gaierror:
            return "[!] Invalid Hostname"
        except Exception as e:
            return "[!] Unusual behavior"
    
    def _run_udp(self):
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
                client.settimeout(self.timeout)
                client.sendto(self.message, (self.target, self.port))
                data, addr = client.recvfrom(4096)
                return f"[+] Response from {addr}\n{data.decode(errors='ignore')}"
    
            
        except socket.timeout:
            return "[!] No response (timeout)"
        except KeyboardInterrupt:
            return "[!] User Interrupted"
        except ConnectionRefusedError:
            return "[!] Connection Refused"
        except socket.gaierror:
            return "[!] Invalid Hostname"
        except Exception as e:
            return "[!] Unusual behavior"
                     
def main():
    parser = argparse.ArgumentParser(description="TCP/UDP Network Client")
    parser.add_argument("-t", "--target", required=True, help="Target Host")
    parser.add_argument("-p", "--port", required=True, type=int, help="Target Port")
    parser.add_argument("-m", "--message", required=True, help="Message to send")
    parser.add_argument("--proto", choices=["tcp", "udp"], default="tcp",help="Protocol (tcp or udp)")
    parser.add_argument("--timeout", type=int, default=5,help="Timeout in seconds")

    args = parser.parse_args()

    client = NetworkClient(args.target,args.port,args.message,args.proto,args.timeout)
    response = client.run()

    print("[+] Result:")
    print(response)

if __name__ == "__main__":
    main()
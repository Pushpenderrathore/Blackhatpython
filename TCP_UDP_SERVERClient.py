import socket
import argparse
import threading


class TUClient:
    def __init__(self, target: str, port: int, message: str = "",protocol: str = "tcp", timeout: int = 5):
        self.target = target
        self.port = port
        self.message = message.encode()
        self.protocol = protocol.lower()
        self.timeout = timeout

    def connection(self):
        if self.protocol == "tcp":
            return self._run_tcp()
        elif self.protocol == "udp":
            return self._run_udp()
        elif self.protocol == "tcpserver":
            return self._tcp_server()
        else:
            return "Unknown Command"

    def _run_tcp(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.settimeout(self.timeout)
                client.connect((self.target, self.port))
                client.sendall(self.message)
                resp = client.recv(4096)
                return resp.decode(errors="ignore")
        except socket.timeout:
            return "[!] Connection Time Out"
        except ConnectionRefusedError:
            return "[!] Connection Refused"
        except KeyboardInterrupt:
            return "[!] User Interrupted"
        except socket.gaierror:
            return "[!] Unknown Host"
        except Exception as e:
            return f"[!] Unexpected Error: {e}"
        
    def _run_udp(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
                client.settimeout(self.timeout)
                client.sendto(self.message, (self.target, self.port))
                data, addr = client.recvfrom(4096)
                return f"Response from {addr} -> {data.decode(errors='ignore')}"
        except socket.timeout:
            return "[!] Connection Time Out"
        except ConnectionRefusedError:
            return "[!] Connection Refused"
        except KeyboardInterrupt:
            return "[!] User Interrupted"
        except socket.gaierror:
            return "[!] Unknown Host"
        except Exception as e:
            return f"[!] Unexpected Error: {e}"

    def _tcp_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                server.bind((self.target, self.port))
                server.listen(10)
                print(f"[*] Listening on {self.target}:{self.port}")

                while True:
                    client, addr = server.accept()
                    print(f"[*] Connection from {addr}")

                    thread = threading.Thread(target=self.handle_client,args=(client, addr))
                    thread.start()
        except socket.timeout:
            return "[!] Connection Time Out"
        except ConnectionRefusedError:
            return "[!] Connection Refused"
        except KeyboardInterrupt:
            return "[!] User Interrupted"
        except socket.gaierror:
            return "[!] Unknown Host"
        except Exception as e:
            return f"[!] Server Error: {e}"

    def handle_client(self, client, addr):
        print(f"[+] Connected: {addr}")

        try:
            while True:
                data = client.recv(4096)
    
                if not data:
                    break  # client disconnected
    
                print(f"[{addr}] {data.decode(errors='ignore')}")
                client.sendall(b"Message Received\n")
    
        except socket.timeout:
            return "[!] Connection Time Out"
        except ConnectionRefusedError:
            return "[!] Connection Refused"
        except KeyboardInterrupt:
            return "[!] User Interrupted"
        except socket.gaierror:
            return "[!] Unknown Host"            
        except Exception as e:
            return f"[!] Client Error: {e}"
    
        finally:
            client.close()
            print(f"[-] Disconnected: {addr}")
                
def main():
    parser = argparse.ArgumentParser(description="TSU Client Tool")
    parser.add_argument("-t", "--target", required=True, help="Target Host")
    parser.add_argument("-p", "--port", required=True, type=int, help="Target Port")
    parser.add_argument("-m", "--message", default="", help="Message To Send")
    parser.add_argument("-P", "--protocol",choices=["tcp", "udp", "tcpserver"],default="tcp",help="Protocol: tcp, udp, tcpserver")
    parser.add_argument("-T", "--timeout", type=int, default=5,help="Set Timeout")

    args = parser.parse_args()

    client = TUClient(args.target,args.port,args.message,args.protocol,args.timeout)
    response = client.connection()

    if response:
        print(f"Response from {args.target}:{args.port} -> {response}")

if __name__ == "__main__":
    main()
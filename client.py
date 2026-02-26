import os
import socket
import argparse

class TUClient:
    def __init__(self,target: str, port: int , message: str, proto: str, timeout: int = 5):
        self.target=target
        self.port=port
        self.message=message.encode()
        self.proto=proto.lower()
        self.timeout=timeout

    def connection(self):
        if self.proto == "tcp":
            return self._run_tcp()
        elif self.proto == "udp":
            return self._run_udp()
        else :
            return "[!] Invalid protocol selected. Use tcp or udp."
        
    def _run_tcp(self):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
                client.settimeout(self.timeout)
                client.connect((self.target,self.port))
                client.sendall(self.message)
                response = client.recv(4096)
                return response.decode(error="ignore")
        except socket.timeout:
            return "[!] No response (timeout)"
        except KeyboardInterrupt:
            return "[!] User Interrupted"
        except ConnectionRefusedError:
            return "[!] Connection Refused"
        except socket.gaierror:
            return "[!] Invalid Hostname"
        except Exception as e:
            return "[!] Unusual behavior detected"
        
    def _run_udp(self):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as client:
                client.settimeout(self.timeout)
                client.sendto(self.message,(self.target,self.port))
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
            return "[!] Unusual behavior detected"

def main():
    parser = argparse.ArgumentParser(description="TCP UDP Client")
    parser.add_argument("-t","--target",required=True,help="target host")
    parser.add_argument("-p","--port",required=True,type=int,help="target port")
    parser.add_argument("-m","--message",required=True,help="Message to send")
    parser.add_argument("-P","--protocol",required=True,choices=["tcp","udp"],help="Protocol to use")
    parser.add_argument("--timeout",type=int,default=5,help="Connection timeout in seconds")

    args = parser.parse_args()

    client = TUClient(args.target,args.port,args.message,args.protocol,args.timeout)
    response = client.connection()

    print(f"Response From {args.target}:{args.port} -> {response}")

if __name__=="__main__":
    main()

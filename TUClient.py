import socket
import argparse
import os

class TUClient:
    def __init__(self,target:str,port:int,message:str,protocol:str="tcp",timeout:int=5):
        self.target=target
        self.port=port
        self.message=message.encode()
        self.protocol=protocol.lower()
        self.timeout=timeout

    def connection(self):
        if self.protocol=="tcp":
            return self._run_tcp()
        elif self.protocol=="udp":
            return self._run_udp()
        else:
            return "Unknown Command"
        
    def _run_tcp(self):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
                client.settimeout(self.timeout)
                client.connect((self.target,self.port))
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
            return "[!] Unexpected Error"
        
    def _run_udp(self):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as client:
                client.settimeout(self.timeout)
                client.sendto(self.message,(self.target,self.port))
                data , addr = client.recvfrom(4096)
                return f"Response from {self.target}:{self.port} -> {data.decode(errors='ignore')}:{addr}"
        except socket.timeout:
            return "[!] Connection Time Out"
        except ConnectionRefusedError:
            return "[!] Connection Refused"
        except KeyboardInterrupt:
            return "[!] User Interrupted"
        except socket.gaierror:
            return "[!] Unknown Host"
        except Exception as e:
            return "[!] Unexpected Error"
        
        
def main():
    parser = argparse.ArgumentParser(description="TU Client")
    parser.add_argument("-t ","--target",required=True,help="Target Host")
    parser.add_argument("-p ","--port",required=True,type=int,help="Target Port")
    parser.add_argument("-m ","--message",required=True,type=str,help="Message To Send")
    parser.add_argument("-P ","--protocol",choices=["tcp" , "udp"],default="tcp",help="protocol tcp or udp")
    parser.add_argument("-T ","--timeout",type=int,default=5,help="Set Time Out")

    args = parser.parse_args()

    client = TUClient(args.target,args.port,args.message,args.protocol,args.timeout)
    resp = client.connection()

    print(f"Response from {args.target}:{args.port} -> {resp}")

if __name__=="__main__":
    main()        
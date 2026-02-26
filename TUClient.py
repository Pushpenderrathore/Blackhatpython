import socket
import argparse
import os
import threading

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
            return "Unknown command use [tcp or udp]"

    def _run_tcp(self):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
                client.settimeout(self.timeout)
                client.connect((self.target,self.port))
                client.sendall(self.message)
                resp = client.recv(4096)
                return resp.decode(errors="ignore")

        except socket.timeout:
            return "Connection: Time Out"
        except ConnectionRefusedError:
            return "Host: down/filter"
        except KeyboardInterrupt:
            return "User: Interrupted"
        except socket.gaierror:
            return "Host: Unknown"
        except Exception as e:
            return "Unexpected Error!"

    def _run_udp(self):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_DGRAM) as client:
                client.settimeout(self.timeout)
                client.sendto("Hello",(self.target,self.port))
                data , resp = client.recvfrom(4096)
                return (f"response from {data} -> resp")

        except socket.timeout:
            return "Connection: Time Out"
        except ConnectionRefusedError:
            return "Port: closed"
        except KeyboardInterrupt:
            return "User: Interrupted"
        except socket.gaierror:
            return "Host: Unknown"
        except Exception as e:
            return "Unexpected Error!"

def main():
    parser = argparse.ArgumentParser(description="TU Client")
    parser.add_argument("-t","--target",required=True,help="Target host")
    parser.add_argument("-p","--port",type=int,required=True,help="Target port")
    parser.add_argument("-m","--message",type=str,required=True,help="Message to send")
    parser.add_argument("-P","--protocol",type=str,required=True,default="tcp",help="Use from tcp or udp")
    parser.add_argument("-T","--timeout",type=int,required=True,default=True,help="set time out")

    args = parser.parse_args()

    client = TUClient(args.target,args.port,args.message,args.protocol,args.timeout)
    resp = client.connection()

    print (f"Response from {args.target}:{args.port} -> {resp}")

if __name__=="__main__":
    main()



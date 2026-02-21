import os
import socket
import argparse

class TCPclient:
    def __init__(self,target: str, port: int,message: str, timeout: int = 5):
        self.target=target
        self.port=port
        self.message=message.encode()
        self.timeout=timeout
    def connection(self):
        try:
            with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as client:
                client.settimeout(self.timeout)
                client.connect((self.target,self.port))
                client.sendall(self.message)
                response = client.recv(4096)
                return response.decode(errors="ignore")
        except socket.timeout:
            return "Connection Time Out"
        except KeyboardInterrupt:
            return "User Interrupted"
        except ConnectionRefusedError:
            return "Connection Refused"
        except socket.gaierror:
            return "Invalid Hostname"
        except Exception as e:
            return "Unexpected Error"
    
        
def main():
    parser = argparse.ArgumentParser(description="TCP Client")
    parser.add_argument("-t","--target",required=True,type=str,help="Target host")
    parser.add_argument("-p","--port",required=True,type=int,help="Target port")
    parser.add_argument("-m","--message",required=True,type=str,help="Message to send")
    parser.add_argument("--timeout",type=int,default=5,help="Connection timeout in seconds")

    args = parser.parse_args()

    client = TCPclient(args.target,args.port,args.message,args.timeout)
    response = client.connection()

    print(f"response: {response}")

if __name__=="__main__":
    main()

import socket
import argparse
import os
import threading

class tcpserver:
    def __init__(self,host:str,port:int):
        self.host=host
        self.port=port

    def start(self):
        with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as server:
            server.bind((self.host,self.port))
            server.listen(5)
            print(f"[*] Listening on {self.host}:{self.port}")
            while True:
                client, addr = server.accept()
                print(f"[*] Connection from {addr}")
                threading.Thread(target=self.handle_client,args=(client,addr)).start()

    def handle_client(self,client:socket.socket,addr):
        with client:
            print(f"[*] Handling connection from {addr}")
            while True:
                data = client.recv(4096)
                if not data:
                    break
                print(f"[*] Received from {addr}: {data.decode(errors='ignore')}")
                response = f"Echo: {data.decode(errors='ignore')}"
                client.sendall(response.encode())

def main():
    parser = argparse.ArgumentParser(description="Simple TCP Server")
    parser.add_argument("-H","--host",default="127.0.0.1")
    parser.add_argument("-p","--port",type=int,default=9999)
    args = parser.parse_args()
    server = tcpserver(args.host,args.port)
    server.start()

if __name__ == "__main__":
    main()

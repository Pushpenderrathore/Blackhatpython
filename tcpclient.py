import socket

def tcpclient(target: str,port: int,message: str):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((target,port))
    client.send(message.encode())
    data = client.recv(4096) 
    print(data.decode())

tcpclient("google.com",80,"GET / HTTP/1.1\r\nHOST : google.com\r\n\r\n")
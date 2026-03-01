#!/usr/bin/env python3

import socket
import threading
import argparse
import logging
from typing import Optional


BUFFER_SIZE = 4096
TIMEOUT = 3


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


class TCPProxy:
    def __init__(
        self,
        local_host: str,
        local_port: int,
        remote_host: str,
        remote_port: int,
        receive_first: bool = False
    ):
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.receive_first = receive_first

    def start(self) -> None:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            server.bind((self.local_host, self.local_port))
            server.listen(5)
            logging.info(f"Listening on {self.local_host}:{self.local_port}")
        except Exception as e:
            logging.error(f"Failed to bind: {e}")
            return

        while True:
            client_socket, addr = server.accept()
            logging.info(f"Incoming connection from {addr[0]}:{addr[1]}")

            thread = threading.Thread(
                target=self.proxy_handler,
                args=(client_socket,),
                daemon=True
            )
            thread.start()

    def proxy_handler(self, client_socket: socket.socket) -> None:
        try:
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((self.remote_host, self.remote_port))
        except Exception as e:
            logging.error(f"Remote connection failed: {e}")
            client_socket.close()
            return

        if self.receive_first:
            remote_buffer = self.receive_from(remote_socket)
            self.hexdump(remote_buffer)

            remote_buffer = self.response_handler(remote_buffer)

            if remote_buffer:
                client_socket.sendall(remote_buffer)

        while True:
            local_buffer = self.receive_from(client_socket)

            if local_buffer:
                logging.info(f"Received {len(local_buffer)} bytes from client")
                self.hexdump(local_buffer)

                local_buffer = self.request_handler(local_buffer)
                remote_socket.sendall(local_buffer)

            remote_buffer = self.receive_from(remote_socket)

            if remote_buffer:
                logging.info(f"Received {len(remote_buffer)} bytes from remote")
                self.hexdump(remote_buffer)

                remote_buffer = self.response_handler(remote_buffer)
                client_socket.sendall(remote_buffer)

            if not local_buffer and not remote_buffer:
                logging.info("Closing connections")
                client_socket.close()
                remote_socket.close()
                break

    @staticmethod
    def receive_from(connection: socket.socket) -> bytes:
        buffer = b""
        connection.settimeout(TIMEOUT)

        try:
            while True:
                data = connection.recv(BUFFER_SIZE)
                if not data:
                    break
                buffer += data
        except socket.timeout:
            pass
        except Exception:
            pass

        return buffer

    @staticmethod
    def hexdump(data: bytes, length: int = 16) -> None:
        for i in range(0, len(data), length):
            chunk = data[i:i + length]
            hex_chunk = " ".join(f"{b:02X}" for b in chunk)
            ascii_chunk = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            print(f"{i:04X}  {hex_chunk:<48}  {ascii_chunk}")
        print()

    @staticmethod
    def request_handler(buffer: bytes) -> bytes:
        # Modify outbound traffic here
        return buffer

    @staticmethod
    def response_handler(buffer: bytes) -> bytes:
        # Modify inbound traffic here
        return buffer


def parse_args():
    parser = argparse.ArgumentParser(description="Modern TCP Proxy")
    parser.add_argument("local_host")
    parser.add_argument("local_port", type=int)
    parser.add_argument("remote_host")
    parser.add_argument("remote_port", type=int)
    parser.add_argument("--receive-first", action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    proxy = TCPProxy(
        args.local_host,
        args.local_port,
        args.remote_host,
        args.remote_port,
        args.receive_first
    )

    proxy.start()


if __name__ == "__main__":
    main()

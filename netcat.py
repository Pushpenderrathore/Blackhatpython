import sys
import socket
import threading
import subprocess
import argparse

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if buffer:
            client.send(buffer.encode())
        while True:
            response = b""
            while True:
                data = client.recv(4096)
                if not data:
                    break
                response += data
                if len(data) < 4096:
                    break
            if response:
                print(response.decode(), end="")
            buffer = input("")
            buffer += "\n"
            client.send(buffer.encode())
    except KeyboardInterrupt:
        print("\n[*] User terminated.")
    except Exception as e:
        print(f"[*] Exception! {e}")
    finally:
        client.close()

def server_loop():
    global target

    if not target:
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((target, port))
        server.listen(5)
        print(f"[*] Listening on {target}:{port}")

        while True:
            try:
                client_socket, addr = server.accept()
                print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

                client_thread = threading.Thread(
                    target=client_handler,
                    args=(client_socket,)
                )
                client_thread.start()

            except KeyboardInterrupt:
                print("\n[!] Ctrl+C detected. Stopping server...")
                break

            except Exception as e:
                print(f"[!] Accept error: {e}")

    except Exception as e:
        print(f"[!] Failed to start server: {e}")

    finally:
        print("[*] Closing server socket.")
        server.close()

def run_command(command):
    command = command.strip()
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except Exception:
        output = b"Failed to execute command.\n"
    return output

def client_handler(client_socket):
    global upload_destination
    global execute
    global command

    # File upload
    if upload_destination:
        file_buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            file_buffer += data
        try:
            with open(upload_destination, "wb") as f:
                f.write(file_buffer)
            client_socket.send(f"Successfully saved file to {upload_destination}\n".encode())
        except:
            client_socket.send(f"Failed to save file to {upload_destination}\n".encode())
    
    # Execute command
    if execute:
        output = run_command(execute)
        client_socket.send(output)
    
    # Command shell with dup2 redirection
    if command:
        try:
            import os
            import pty
            import select
            import signal
            import sys
            import termios
            import struct
            import fcntl
            import array
            
            # Send initial prompt
            client_socket.send(b"<enp7s0d:#> \r\n")
            
            # Fork a new pseudo-terminal
            pid, fd = pty.fork()
            
            if pid == 0:  # Child process
                try:
                    # Set up the shell with proper environment
                    os.environ['TERM'] = 'xterm-256color'
                    os.environ['SHELL'] = '/bin/bash'
                    os.environ['PS1'] = '\\u@\\h:\\w\\$ '
                    
                    # Execute bash
                    os.execve("/bin/bash", ["/bin/bash", "--login"], os.environ)
                    
                except Exception as e:
                    # Write error to stderr
                    sys.stderr.write(f"Failed to spawn shell: {e}\n")
                    os._exit(1)
                    
            else:  # Parent process
                try:
                    # Set the terminal window size if possible
                    def set_winsize(fd, rows, cols):
                        winsize = struct.pack("HHHH", rows, cols, 0, 0)
                        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)
                    
                    # Default terminal size
                    set_winsize(fd, 24, 80)
                    
                    # Handle I/O between socket and pty
                    while True:
                        try:
                            rlist, _, _ = select.select([client_socket, fd], [], [])
                            
                            for sock in rlist:
                                if sock == client_socket:  # Data from client
                                    data = client_socket.recv(1024)
                                    if not data:
                                        raise EOFError("Connection closed")
                                    
                                    # Check for window size change (if client sends special sequence)
                                    # This is a simplified version - you might want to implement proper window size handling
                                    os.write(fd, data)
                                    
                                else:  # Data from pty (child process)
                                    try:
                                        data = os.read(fd, 1024)
                                        if not data:
                                            raise EOFError("Child process closed")
                                        client_socket.send(data)
                                    except OSError:
                                        raise EOFError("Child process terminated")
                                        
                        except (EOFError, KeyboardInterrupt):
                            break
                        except Exception as e:
                            print(f"Error in I/O loop: {e}")
                            break
                            
                finally:
                    # Clean up
                    try:
                        os.close(fd)
                        os.kill(pid, signal.SIGTERM)
                        os.waitpid(pid, 0)
                    except:
                        pass
                    
        except Exception as e:
            print(f"Error setting up pty shell: {e}")
            # If pty fails, fall back to original method
            try:
                client_socket.send(b"Falling back to basic command shell...\r\n")
                while True:
                    client_socket.send(b"<enp7s0d:#> ")
                    cmd_buffer = b""
                    while b"\n" not in cmd_buffer:
                        data = client_socket.recv(1024)
                        if not data:
                            return
                        cmd_buffer += data
                    response = run_command(cmd_buffer.decode())
                    client_socket.send(response)
            except:
                pass
    
    client_socket.close()

def parse_args():
    parser = argparse.ArgumentParser(
        description="Netcat IoT Tool (Modern argparse version)",
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        "-l", "--listen",
        action="store_true",
        help="Listen on [host]:[port]"
    )

    parser.add_argument(
        "-e", "--execute",
        metavar="COMMAND",
        help="Execute given command"
    )

    parser.add_argument(
        "-c", "--command",
        action="store_true",
        help="Initialize command shell"
    )

    parser.add_argument(
        "-u", "--upload",
        metavar="DESTINATION",
        help="Upload file and write to destination"
    )

    parser.add_argument(
        "-t", "--target",
        metavar="TARGET",
        help="Target host"
    )

    parser.add_argument(
        "-p", "--port",
        type=int,
        metavar="PORT",
        help="Target port"
    )

    return parser.parse_args()

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    args = parse_args()

    listen = args.listen
    execute = args.execute or ""
    command = args.command
    upload_destination = args.upload or ""
    target = args.target or ""
    port = args.port or 0

    # ---------------- SERVER MODE ---------------- #
    if listen:
        if port == 0:
            print("[!!] Port required in listen mode (-p)")
            sys.exit(1)
        server_loop()
        return

    # ---------------- CLIENT MODE ---------------- #
    if target and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)
        return

    # ---------------- INVALID ---------------- #
    print("[!!] Invalid options. Use -h for help.")
    sys.exit(1)

if __name__ == "__main__":
    main()
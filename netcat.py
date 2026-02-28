import sys
import socket
import getopt
import threading
import subprocess

# Global variables
listen = False
command = False
upload_destination = ""
execute = ""
target = ""
port = 0

def usage():
    print("netcat IoT Tool")
    print("Usage: netcat.py -t target_host -p port")
    print("-l --listen               - listen on [host]:[port]")
    print("-e --execute=command      - execute given command")
    print("-c --command              - initialize command shell")
    print("-u --upload=destination   - upload file and write to destination")
    print("\nExamples:")
    print("netcat.py -t 192.168.1.10 -p 5555 -l -c")
    print("netcat.py -t 192.168.1.10 -p 5555 -l -e='cat /etc/passwd'")
    print("netcat.py -t 192.168.1.10 -p 5555 -l -u=test.txt")
    sys.exit(0)

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
    server.bind((target, port))
    server.listen(5)
    print(f"[*] Listening on {target}:{port}")
    while True:
        client_socket, addr = server.accept()
        print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()

def run_command(command):
    command = command.strip()
    try:
        output = subprocess.check_output(command,stderr=subprocess.STDOUT,shell=True)
    except Exception:
        output = b"Failed to execute command.\n"
    return output

# def run_command(command):
#     command = command.strip()
#     try:
#         result = subprocess.run(
#             command,
#             shell=True,
#             capture_output=True
#         )
#         return result.stdout + result.stderr
#     except Exception as e:
#         return f"Error: {e}".encode()

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

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            "hle:t:p:cu:",
            ["help", "listen", "execute=", "target=", "port=", "command", "upload="]
        )
    except getopt.GetoptError as err:
        print(err)
        usage()
    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"
    if not listen and target and port > 0:
        buffer = sys.stdin.read()
        client_sender(buffer)
    if listen:
        server_loop()
    else:
        print("Invalid options. Use -h for help.")
        sys.exit(0)

if __name__ == "__main__":
    main()
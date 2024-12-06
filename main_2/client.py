import socket
import threading
import sys

server_host = '127.0.0.1'  # Server IP
server_port = 12345        # Server Port
messages = []              # Store chat messages for display
stop_flag = threading.Event()  # Flag for graceful shutdown

class ClientThread(threading.Thread):
    """A thread to handle receiving messages from the server."""
    
    def __init__(self, socket):
        super().__init__()
        self.socket = socket

    def run(self):
        while not stop_flag.is_set():
            try:
                message = self.socket.recv(1024).decode('utf-8')
                if message:
                    print(f"{message}")
                    messages.append(message)
            except Exception as e:
                if not stop_flag.is_set():
                    print(f"Error receiving message: {e}")
                break

        print("Receiving thread stopped.")

def send_message(client_socket):
    """Send a message to the server."""
    while not stop_flag.is_set():
        try:
            message = input().strip()
            if message:         
                client_socket.send(message.encode('utf-8'))
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            stop_flag.set()
            break
        except Exception as e:
            print(f"Error sending message: {e}")
            break

    print("Sending thread stopped.")

def connect_to_server():
    try:
        # Starts the TCP handshake connection by sending a SYN packet to server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_host, server_port))
        print("Connected to the server!")

        # Start a thread to receive messages
        receiver_thread = ClientThread(client_socket)
        receiver_thread.start()

        # Main thread will handle sending messages
        send_message(client_socket)

    except KeyboardInterrupt:
        print("\nConnection interrupted.")
    except Exception as e:
        print(f"Unable to connect to server: {e}")
    finally:
        stop_flag.set()
        client_socket.close()
        print("Client socket closed.")

if __name__ == "__main__":
    try:
        connect_to_server()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Client exited.")

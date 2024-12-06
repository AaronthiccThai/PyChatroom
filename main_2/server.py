import socket
import threading

class ChatServer:
    def __init__(self, host='0.0.0.0', port=12345):
        self.clients = {}  # Mapping of client sockets to user numbers
        self.server_running = True  # Server state
        self.user_counter = 0  # Unique user number counter
        self.host = host
        self.port = port

    def broadcast(self, message, source_socket):
        for client in self.clients:
            if client != source_socket:
                try:
                    client.send(message.encode('utf-8'))
                except:
                    print(f"Failed to send message to client {self.clients[client]}. Removing client.")
                    del self.clients[client]

    def handle_client(self, client_socket, addr):
        user_number = self.clients[client_socket]
        try:
            while self.server_running:
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"<User #{user_number}> {message}")
                    self.broadcast(f"User #{user_number}: {message}", client_socket)
                else:
                    break
        except:
            pass
        finally:
            print(f"Client {addr} (User #{user_number}) disconnected.")
            del self.clients[client_socket]
            client_socket.close()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((self.host, self.port))
        server.listen(5)
        print(f"Server is running on {self.host}:{self.port}...")

        try:
            while self.server_running:
                try:
                    server.settimeout(1)
                    # Server acknowledges the SYN packet from client 
                    client_socket, addr = server.accept()
                    self.user_counter += 1
                    self.clients[client_socket] = self.user_counter  # Assign a unique user number
                    print(f"Connection from {addr} assigned User #{self.user_counter}")
                    thread = threading.Thread(target=self.handle_client, args=(client_socket, addr))
                    thread.daemon = True
                    thread.start()
                except socket.timeout:
                    continue 
        except KeyboardInterrupt:
            print("\nServer interrupted by user.")
        finally:
            self.shutdown(server)

    def shutdown(self, server):
        print("Shutting down the server...")
        self.server_running = False
        for client in list(self.clients):
            client.close()
        server.close()
        print("Server has been shut down.")

if __name__ == "__main__":
    chat_server = ChatServer()
    chat_server.start_server()

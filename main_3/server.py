from socket import *
import threading

serverHost = "127.0.0.1"
serverPort = 12345
serverAddress = (serverHost, serverPort)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddress)
activeClients = {}
running = True  # Flag to control server execution

def server_listener():
    global running
    user_number = 0
    
    print("Server started. Type 'exit' to stop.")
    while running:
        try:
            # Set a timeout to periodically check the running flag
            serverSocket.settimeout(1.0)  
            try:
                message, clientAddress = serverSocket.recvfrom(1024)
                message = message.decode().strip()

                # Add new clients
                if clientAddress not in activeClients:
                    user_number += 1
                    activeClients[clientAddress] = user_number
                    print(f"New client connected: {clientAddress}")

                # Check for shutdown command
                if message.lower() == "exit":
                    print("Shutdown command received. Closing server.")
                    running = False
                    break

                # Broadcast message to other clients
                for client in activeClients:
                    if client != clientAddress:
                        userId = activeClients[clientAddress]
                        msg = f"User<{userId}>: {message}"
                        serverSocket.sendto(msg.encode(), client)

                # Print received message
                if message:
                    userId = activeClients[clientAddress]
                    print(f"User<{userId}>: {message}")

            except timeout:
                continue  # No data received, check the running flag
        except Exception as e:
            print(f"Server error: {e}")
            break

# Run the listener in a separate thread
listener_thread = threading.Thread(target=server_listener)
listener_thread.start()


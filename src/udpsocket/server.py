from socket import *
import threading

serverHost = "127.0.0.1"
serverPort = 12345
serverAddress = (serverHost, serverPort)

serverSocket = socket(AF_INET, SOCK_DGRAM)
serverSocket.bind(serverAddress)
activeClients = {}
running = True 

def serverListener():
    global running
    user_number = 0
    
    print(f"Server started on {serverAddress}")
    while running:
        try:
            serverSocket.settimeout(1.0)  
            try:
                message, clientAddress = serverSocket.recvfrom(1024)
                message = message.decode().strip()
                
                if message.lower() == './exit':
                    del activeClients[clientAddress]


                if clientAddress not in activeClients:
                    user_number += 1
                    activeClients[clientAddress] = user_number
                    print(f"New client connected: {clientAddress}")
                for client in activeClients:
                    if client != clientAddress:
                        userId = activeClients[clientAddress]
                        msg = f"User<{userId}>: {message}"
                        serverSocket.sendto(msg.encode(), client)

                if message:
                    userId = activeClients[clientAddress]
                    print(f"User<{userId}>: {message}")
                    print(f"ACK<User<{userId}>> received")
                    
            except timeout:
                continue  
        except Exception as e:
            print(f"Server error: {e}")
            break

listener_thread = threading.Thread(target=serverListener)
listener_thread.start()


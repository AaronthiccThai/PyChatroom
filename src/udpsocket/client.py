from socket import *
from threading import Thread

serverHost = "127.0.0.1"
serverPort = 12345
serverAddress = (serverHost, serverPort)

clientSocket = socket(AF_INET, SOCK_DGRAM)
clientSocket.bind(("", 0))

def receive_messages():
    while True:
        try:
            message, _ = clientSocket.recvfrom(1024)
            print(message.decode().strip())
        except Exception as e:
            print(f"Error receiving message: {e}")
            break

receiver_thread = Thread(target=receive_messages, daemon=True)
receiver_thread.start()

print("Connected to the chat. Type messages below:")
while True:
    try:
        message = input()
        if message == "./exit":
            print("\nExiting chat.")
            break 
        if message.strip():
            clientSocket.sendto(message.encode(), serverAddress)
            ack, _ = clientSocket.recvfrom(1024)
            print(f"ACK received: {ack.decode().strip()}")

    except KeyboardInterrupt:
        print("\nExiting chat.")
        break

clientSocket.close()

import websockets
import asyncio
import psycopg2
from psycopg2 import sql

class ChatServer():
    def __init__(self):
        self.db_connection = psycopg2.connect(
            dbname="chatdb",
            user="admin",
            password="admin",
            host="localhost",
            port="5432"
        )
        self.cursor = self.db_connection.cursor()
        self.active_clients = {}  # {username: websocket}

    async def authenticate(self, websocket) -> str:
        await websocket.send("Welcome! Please register or login")
        while True:
            await websocket.send("Type 'login' to log in or 'register' to create an account:")
            command = await websocket.recv()
            if command.lower() == "login":
                await websocket.send("Enter username:")
                username = await websocket.recv()
                await websocket.send("Enter password:")
                password = await websocket.recv()

                self.cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                db_password = self.cursor.fetchone()
                if db_password and db_password[0] == password:
                    await websocket.send(f"Login successful! Welcome back, {username}.")
                    self.active_clients[username] = websocket
                    return username
                else:
                    await websocket.send("Invalid credentials. Please try again.")

            elif command.lower() == "register":
                await websocket.send("Please choose a username:")
                username = await websocket.recv()
                self.cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if self.cursor.fetchone():
                    await websocket.send("Username is already taken. Please try a different one.")
                    continue

                await websocket.send("Please enter a password:")
                password = await websocket.recv()
                self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                self.db_connection.commit()
                await websocket.send(f"Registration successful! Welcome, {username}.")
                self.active_clients[username] = websocket
                return username

            else:
                await websocket.send("Invalid command. Please type either login or register.")

    async def deregister(self, websocket) -> None:
        username = None
        for user, ws in self.active_clients.items():
            if ws == websocket:
                username = user
                break
        if username:
            del self.active_clients[username]
            print(f"User {username} disconnected.")

    async def broadcast(self, message, sender) -> None:
        sender_username = None
        for user, ws in self.active_clients.items():
            if ws == sender:
                sender_username = user
                break

        if sender_username:
            for user, ws in self.active_clients.items():
                if ws != sender:  # Avoid sending to the sender
                    try:
                        await ws.send(f"<{sender_username}>: {message}")
                    except Exception as e:
                        print(f"Failed to send message to {user}: {e}")
                        await self.deregister(ws)

    async def handle_client(self, websocket) -> None:
        username = await self.authenticate(websocket)
        try:
            async for message in websocket:
                await websocket.send(f"<{username}>: {message}")
                await self.broadcast(message, websocket)
        finally:
            await self.deregister(websocket)

    async def start(self) -> None:
        server = await websockets.serve(self.handle_client, "0.0.0.0", 12345)
        await server.wait_closed()

if __name__ == "__main__":
    chat_server = ChatServer()
    asyncio.run(chat_server.start())

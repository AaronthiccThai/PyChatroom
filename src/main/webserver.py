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
        # self.activeClients = {}
        # self.credentials = {}
        
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
                    self.cursor.execute("INSERT into active_users (username) VALUES (%s)", (username,))
                    self.db_connection.commit()                
                    return username
                else:
                    await websocket.send("Invalid credentials. Please try again.")                             
                # if username in self.credentials and self.credentials[username] == password:
                #     await websocket.send(f"Login successful! Welcome back, {username}.")
                #     return username
                # else:
                #     await websocket.send("Invalid credentials. Please try again.")                    
                                
            elif command.lower() == "register":
                await websocket.send("Please choose a username:")
                username = await websocket.recv()
                # if username in self.credentials:
                #     await websocket.send("Username is already taken. Please try a different one")
                #     continue
                self.cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if self.cursor.fetchone():
                    await websocket.send("Username is already taken. Please try a different one")
                    continue                           
                await websocket.send("Please enter a password:")
                password = await websocket.recv()
                # if len(password) <= 5: 
                #     await websocket.send("Password is too short. Please try again") 
                #     continue
                self.cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
                self.db_connection.commit()                
                # self.credentials[username] = password
                # self.activeClients[websocket] = {'username': username, 'active': True}
                await websocket.send(f"Registration successful! Welcome, {username}.")
                return username
            else:
                await websocket.send("Invalid command. Please type either login or register")
                                               
        
    async def deregister(self, websocket) -> None:
        username = self.activeClients.get(websocket, None)
        if username:
            print(f"Connection closed: {websocket.remote_address}, {username}")
            self.activeClients.pop(websocket, None)
        
    async def broadcast(self, message, sender) -> None:
        sender_info = self.activeClients.get(sender, None)
        sender_username = sender_info['username'] if sender_info else "Unknown"
        for client, client_info in self.activeClients.items():
            if client != sender:
                try:
                    await client.send(f"<{sender_username}>: {message}")
                except:
                    print(f"Failed to send message to User<{client_info['username']}>.")
                    await self.deregister(client)    
                    
                    
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
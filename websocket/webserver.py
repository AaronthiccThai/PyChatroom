import websockets
import asyncio

class ChatServer():
    def __init__(self):
        self.clients = {}
        self.user_counter = 0
        
    async def register(self, websocket) -> None:
        self.user_counter += 1
        self.clients[websocket] = self.user_counter        
        print(f"New connection: {websocket.remote_address}")
        await websocket.send("Welcome to the chat server!")
        
        
    async def deregister(self, websocket) -> None:
        user_number = self.clients.get(websocket, None)
        if user_number:
            print(f"Connection closed: {websocket.remote_address}, User<{user_number}>")
        self.clients.pop(websocket, None)
        
    async def broadcast(self, message, sender) -> None:
        sender_user_number = self.clients.get(sender, "Unknown")
        for client, user_number in self.clients.items():
            if client != sender:
                try:
                    await client.send(f"User<{sender_user_number}>: {message}")
                except:
                    print(f"Failed to send message to User<{user_number}>.")
                    await self.deregister(client)    
                    
    async def handle_client(self, websocket) -> None:
        await self.register(websocket)
        user_number = self.clients[websocket]
        try:
            async for message in websocket:
                await websocket.send(f"User<{user_number}>: {message}")
                await self.broadcast(message, websocket)
        finally:
            await self.deregister(websocket)
                    
    async def start(self) -> None:
        server = await websockets.serve(self.handle_client, "0.0.0.0", 12345)
        await server.wait_closed()
        
if __name__ == "__main__":
    chat_server = ChatServer()
    asyncio.run(chat_server.start())
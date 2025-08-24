import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TicTacToeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"tictactoe_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive a move from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        move = data["move"]   # { "x": 1, "y": 2, "player": "X" }

        # Broadcast move to the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_move",
                "move": move
            }
        )

    # Send move to WebSocket
    async def send_move(self, event):
        move = event["move"]
        await self.send(text_data=json.dumps({
            "move": move
        }))

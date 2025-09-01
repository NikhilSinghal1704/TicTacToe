import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import Room, Game

class TicTacToeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.room_group_name = f"game_{self.room_code}"

        # Join group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self.send(text_data=json.dumps({
            "message": f"Connected to room {self.room_code}"
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "make_move":
            await self.handle_make_move(data)

    async def handle_make_move(self, data):
        """Handle a player's move."""
        player_id = data.get("player_id")
        index = data.get("index")  # 0-8 (board position)

        try:
            room = Room.objects.get(code=self.room_code)
        except Room.DoesNotExist:
            await self.send(text_data=json.dumps({"error": "Room not found"}))
            return

        game, created = Game.objects.get_or_create(room=room)

        # Assign players if not already set
        if not game.x_player:
            game.x_player = player_id
        elif not game.o_player and player_id != game.x_player:
            game.o_player = player_id

        # Ensure move validity
        if game.finished or index < 0 or index > 8 or game.board[index] != "":
            await self.send(text_data=json.dumps({"error": "Invalid move"}))
            return

        symbol = "X" if player_id == game.x_player else "O" if player_id == game.o_player else None
        if not symbol:
            await self.send(text_data=json.dumps({"error": "Not a participant"}))
            return

        game.board[index] = symbol
        game.save()

        # Check winner
        winner = self.check_winner(game.board)
        if winner:
            game.finished = True
            game.winner = winner
            game.save()

        # Broadcast update to group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_update",
                "board": game.board,
                "finished": game.finished,
                "winner": game.winner,
            }
        )

    async def game_update(self, event):
        await self.send(text_data=json.dumps(event))

    def check_winner(self, board):
        winning_combos = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # cols
            [0, 4, 8], [2, 4, 6],             # diagonals
        ]
        for combo in winning_combos:
            a, b, c = combo
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None
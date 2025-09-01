import json
import random
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Game

class TicTacToeConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_code = self.scope["url_route"]["kwargs"]["room_code"]
        self.player_id = self.scope["query_string"].decode().split("player_id=")[-1]
        self.room_group_name = f"room_{self.room_code}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Add player to room
        room = await self.get_room(self.room_code)
        if room:
            await self.add_player(room, self.player_id)

            # Broadcast updated room status (waiting / players)
            await self.broadcast_room_state(room)

    async def disconnect(self, close_code):
        room = await self.get_room(self.room_code)
        if room:
            await self.remove_player(room, self.player_id)
            await self.broadcast_room_state(room)

        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get("action")

        if action == "start_game":
            await self.handle_start_game()
        elif action == "make_move":
            await self.handle_make_move(data)
        elif action == "request_history":
            await self.send_game_history()

    # -----------------------------
    # Room & Game logic
    # -----------------------------
    async def handle_start_game(self):
        """Only start if 2 players are connected."""
        room = await self.get_room(self.room_code)
        if room and len(room.players) == 2:
            game = await self.create_new_game(room)
            await self.broadcast_game_started(game)

    async def handle_make_move(self, data):
        index = data.get("index")
        player_id = data.get("player_id")

        game = await self.get_active_game(self.room_code)
        if not game:
            await self.send(json.dumps({"error": "No active game"}))
            return

        # Validate move
        if game.finished or index < 0 or index > 8 or game.board[index] != "":
            await self.send(json.dumps({"error": "Invalid move"}))
            return

        symbol = "X" if player_id == game.x_player else "O" if player_id == game.o_player else None
        if not symbol:
            await self.send(json.dumps({"error": "Not a participant"}))
            return

        game.board[index] = symbol
        winner = self.check_winner(game.board)
        if winner:
            game.finished = True
            game.winner = winner
        await database_sync_to_async(game.save)()

        # Broadcast updated board
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_update",
                "board": game.board,
                "finished": game.finished,
                "winner": game.winner
            }
        )

    # -----------------------------
    # Broadcast helpers
    # -----------------------------
    async def broadcast_room_state(self, room):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "room_update",
                "players": room.players,
                "host": room.host_id
            }
        )

    async def broadcast_game_started(self, game):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_started",
                "x_player": game.x_player,
                "o_player": game.o_player,
                "board": game.board
            }
        )

    async def send_game_history(self):
        """Send all previous games in this room."""
        room = await self.get_room(self.room_code)
        if room:
            history = []
            for game in room.games.all():
                history.append({
                    "x_player": game.x_player,
                    "o_player": game.o_player,
                    "board": game.board,
                    "finished": game.finished,
                    "winner": game.winner
                })
            await self.send(json.dumps({"history": history}))

    # -----------------------------
    # Event handlers for group_send
    # -----------------------------
    async def room_update(self, event):
        await self.send(json.dumps(event))

    async def game_started(self, event):
        await self.send(json.dumps(event))

    async def game_update(self, event):
        await self.send(json.dumps(event))

    # -----------------------------
    # Winner check
    # -----------------------------
    def check_winner(self, board):
        winning_combos = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6]
        ]
        for combo in winning_combos:
            a,b,c = combo
            if board[a] and board[a] == board[b] == board[c]:
                return board[a]
        return None

    # -----------------------------
    # Database operations
    # -----------------------------
    @database_sync_to_async
    def get_room(self, code):
        try:
            return Room.objects.get(code=code)
        except Room.DoesNotExist:
            return None

    @database_sync_to_async
    def add_player(self, room, player_id):
        room.add_player(player_id)

    @database_sync_to_async
    def remove_player(self, room, player_id):
        room.remove_player(player_id)

    @database_sync_to_async
    def create_new_game(self, room):
        """Create a new Game for this room and assign X/O randomly."""
        players = room.players.copy()
        random.shuffle(players)
        game = Game.objects.create(
            room=room,
            x_player=players[0],
            o_player=players[1],
            board=[""]*9
        )
        return game

    @database_sync_to_async
    def get_active_game(self, room_code):
        room = Room.objects.get(code=room_code)
        games = room.games.filter(finished=False)
        return games.first() if games.exists() else None

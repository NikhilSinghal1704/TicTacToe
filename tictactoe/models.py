from django.db import models
from nanoid import generate
import random

# custom numeric nanoid generator
def generate_numeric_code():
    return generate("0123456789", 6)  # Only digits, length 6


class Room(models.Model):
    code = models.CharField(
        max_length=6,
        unique=True,
        default=generate_numeric_code,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)

    # List of up to 2 player IDs
    players = models.JSONField(default=list)

    # Track which player is host
    host_id = models.CharField(max_length=50, blank=True, null=True)

    def add_player(self, player_id: str) -> bool:
        """Try to add a player; returns True if successful, False if room full or already joined."""
        if player_id in self.players:
            return True  # already in room
        if len(self.players) < 2:
            self.players.append(player_id)
            self.save()
            return True
        return False  # room is full

    def remove_player(self, player_id: str):
        """Remove a player from the room if present."""
        if player_id in self.players:
            self.players.remove(player_id)
            # Optional: clear host if host leaves
            if player_id == self.host_id:
                self.host_id = self.players[0] if self.players else None
            self.save()

    def has_space(self) -> bool:
        return len(self.players) < 2

    def __str__(self):
        return f"Room {self.code} (players={len(self.players)})"


class Game(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="games")
    x_player = models.CharField(max_length=50, blank=True, null=True)
    o_player = models.CharField(max_length=50, blank=True, null=True)

    # 9 fixed slots for board (store as JSON array of 9 elements)
    board = models.JSONField(default=list)  

    created_at = models.DateTimeField(auto_now_add=True)
    finished = models.BooleanField(default=False)
    winner = models.CharField(max_length=1, blank=True, null=True)  # "X", "O", or None

    def save(self, *args, **kwargs):
        # ensure board always has 9 slots
        if not self.board or len(self.board) != 9:
            self.board = [""] * 9
        super().save(*args, **kwargs)

    @classmethod
    def create_game(cls, room, player_ids: list):
        """Factory to create a game with random X/O assignment."""
        if len(player_ids) != 2:
            raise ValueError("Exactly 2 players required to start a game")
        x_player, o_player = random.sample(player_ids, 2)
        return cls.objects.create(room=room, x_player=x_player, o_player=o_player, board=[""]*9)

    def __str__(self):
        return f"Game in Room {self.room.code} (X={self.x_player}, O={self.o_player})"

from django.contrib import admin
from .models import *

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("code", "host_id", "created_at", "player_count")
    readonly_fields = ("code", "created_at")
    search_fields = ("code", "host_id")
    
    def player_count(self, obj):
        return len(obj.players)
    player_count.short_description = "Players"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("room", "x_player", "o_player", "finished", "winner", "created_at")
    readonly_fields = ("board", "created_at")
    list_filter = ("finished", "winner")
    search_fields = ("room__code", "x_player", "o_player")

from django.urls import re_path, path
from .views import *
from . import consumers


urlpatterns = [
    path("create-room/", CreateRoomView.as_view(), name="create-room"),
    path("add-player/", AddPlayerView.as_view(), name="add-player"),
    path("delete-room/<str:code>/", DeleteRoomView.as_view(), name="delete-room"),
]

websocket_urlpatterns = [
    re_path(r"ws/tictactoe/(?P<room_name>\w+)/$", consumers.TicTacToeConsumer.as_asgi()),
]
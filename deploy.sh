#!/bin/bash
cd /mnt/Main/TicTacToe
git fetch --all
git reset --hard origin/main
git pull
sudo docker stop TicTacToe || true
sudo docker rm TicTacToe || true
sudo docker rmi tictactoe:latest || true
sudo docker build -t tictactoe:latest .
sudo docker run -d -p 8504:8000 --env-file /mnt/Main/TicTacToe/.env --name TicTacToe -v /mnt/Main/TicTacToe:/app tictactoe:latest

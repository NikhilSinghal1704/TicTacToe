pipeline {
    agent any
    triggers {
        githubPush()
    }
    options {
        skipDefaultCheckout()
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                docker stop TicTacToe || true
                docker rm TicTacToe || true
                docker rmi tictactoe:latest || true
                docker build -t tictactoe:latest .
                '''
            }
        }

        stage('Run Docker Container') {
            steps {
                sh '''
                docker run -d \
                  -p 8504:8000 \
                  --env-file /mnt/Main/TicTacToe/.env \
                  --name TicTacToe \
                  -v /mnt/Main/TicTacToe:/app \
                  tictactoe:latest
                '''
            }
        }
    }
}

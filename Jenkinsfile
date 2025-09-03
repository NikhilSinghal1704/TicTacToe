pipeline {
    agent any
    stages {

        stage('Git Fetch') {
            steps {
                sshagent (credentials: ['casaos-ssh']) {
                    sh '''
                        ssh -tt -o StrictHostKeyChecking=no nikhil@192.168.1.104 "
                        cd /mnt/Main/TicTacToe && git fetch --all
                        "
                    '''
                }
            }
        }

        stage('Git Reset & Pull') {
            steps {
                sshagent (credentials: ['casaos-ssh']) {
                    sh '''
                        ssh -tt -o StrictHostKeyChecking=no nikhil@192.168.1.104 "
                        cd /mnt/Main/TicTacToe &&
                        git reset --hard origin/main &&
                        git pull
                        "
                    '''
                }
            }
        }

        stage('Stop & Remove Old Container') {
            steps {
                sshagent (credentials: ['casaos-ssh']) {
                    sh '''
                        ssh -tt -o StrictHostKeyChecking=no nikhil@192.168.1.104 "
                        docker stop TicTacToe || true &&
                        docker rm TicTacToe || true &&
                        docker rmi tictactoe:latest || true
                        "
                    '''
                }
            }
        }

        stage('Build New Docker Image') {
            steps {
                sshagent (credentials: ['casaos-ssh']) {
                    sh '''
                        ssh -tt -o StrictHostKeyChecking=no nikhil@192.168.1.104 "
                        cd /mnt/Main/TicTacToe &&
                        docker build -t tictactoe:latest .
                        "
                    '''
                }
            }
        }

        stage('Run New Container') {
            steps {
                sshagent (credentials: ['casaos-ssh']) {
                    sh '''
                        ssh -tt -o StrictHostKeyChecking=no nikhil@192.168.1.104 "
                        docker run -d \
                          -p 8504:8000 \
                          --env-file /mnt/Main/TicTacToe/.env \
                          --name TicTacToe \
                          -v /mnt/Main/TicTacToe:/app \
                          tictactoe:latest
                        "
                    '''
                }
            }
        }

    }
} 

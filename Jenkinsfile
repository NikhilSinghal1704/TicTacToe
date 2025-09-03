pipeline {
  agent any
  triggers { githubPush() }   // build on every GitHub push
  stages {
    stage('Smoke') {
      steps {
        echo "Webhook OK. Repo: ${env.JOB_NAME}, Build: #${env.BUILD_NUMBER}"
      }
    }
  }
} 

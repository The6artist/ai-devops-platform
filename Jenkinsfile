
pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root:root -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    options {
        timestamps()
    }

    environment {
        DOCKER_IMAGE = 'dima261102/vice-city-api'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out the Python application...'
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run Automated Tests') {
            steps {
                sh 'python -m pytest -v'
            }
        }

        stage('Install Docker CLI') {
            steps {
                sh '''
                    apt-get update
                    apt-get install -y docker.io
                    docker --version
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker build \
                      -t $DOCKER_IMAGE:$BUILD_NUMBER \
                      -t $DOCKER_IMAGE:latest .
                '''
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        echo "$DOCKERHUB_TOKEN" | docker login \
                          -u "$DOCKERHUB_USER" --password-stdin

                        docker push $DOCKER_IMAGE:$BUILD_NUMBER
                        docker push $DOCKER_IMAGE:latest

                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to EC2') {
            steps {
                echo 'Deploying application to EC2...'

                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DOCKERHUB_USER',
                        passwordVariable: 'DOCKERHUB_TOKEN'
                    )
                ]) {
                    sh '''
                        set +x

                        echo "$DOCKERHUB_TOKEN" | docker login \
                          -u "$DOCKERHUB_USER" --password-stdin

                        docker pull $DOCKER_IMAGE:$BUILD_NUMBER

                        docker stop vice-city-api || true
                        docker rm vice-city-api || true

                        docker run -d \
                          --name vice-city-api \
                          --restart unless-stopped \
                          -p 8000:8000 \
                          -v vice-city-data:/app/data \
                          $DOCKER_IMAGE:$BUILD_NUMBER

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'CI/CD pipeline completed successfully. Application deployed to EC2.'
        }

        failure {
            echo 'Pipeline failed. Check the console output.'
        }

        always {
            echo 'Pipeline execution finished.'
        }
    }
}

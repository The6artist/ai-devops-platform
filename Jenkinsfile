pipeline {
    agent {
        docker {
            image 'python:3.12-slim'
            args '-u root:root'
        }
    }

    options {
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out the Python application...'
                checkout scm
            }
        }

        stage('Verify Python') {
            steps {
                sh 'python --version'
                sh 'python -m pip --version'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing application and test dependencies...'
                sh 'python -m pip install --upgrade pip'
                sh 'python -m pip install -r requirements.txt'
            }
        }

        stage('Run Automated Tests') {
            steps {
                echo 'Running the Pytest test suite...'
                sh 'python -m pytest -v'
            }
        }
    }

    post {
        success {
            echo 'CI pipeline completed successfully. All stages passed.'
        }
        failure {
            echo 'CI pipeline failed. Review the stage logs to identify the problem.'
        }
        always {
            echo 'Python CI pipeline execution finished.'
        }
    }
}

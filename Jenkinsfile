pipeline {
    agent {
        docker {
            image 'python:3.11'
        }
    }

    triggers {
        cron('H/30 * * * *')
    }

    environment {
        NSO_BASE_URL = 'http://192.168.68.103:8080/restconf/data'
    }

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install dependencies') {
            steps {
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('NSO Health Validation') {
            environment {
                API_CREDS = credentials('api-creds')
            }
            steps {
                sh '''
                    . venv/bin/activate
                    export API_USERNAME="${API_CREDS_USR}"
                    export API_PASSWORD="${API_CREDS_PSW}"
                    python nso/device_validation.py
                '''
            }
        }
    }

    post {
        success {
            echo 'NSO health check passed'
        }
        failure {
            echo 'NSO health check FAILED'
        }
    }
}


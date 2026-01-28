pipeline {
    agent {
        docker {
            image 'python:3.11'
        }
    }

    environment {
        NSO_BASE_URL = 'http://192.168.68.101:8080/restconf/data'
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

        stage('NSO Device Validation') {
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
            echo 'NSO device validation passed'
        }
        failure {
            echo 'NSO device validation failed'
        }
    }
}


node {
    checkout scm

    try {
        stage('Run unit/integration tests'){
            sh 'make test'
        }
        stage('Build application artifacts'){
            sh 'make build'
        }
        stage('Deploy release'){
            build job: "${REPO_NAME}_deploy", parameters: [[$class: 'StringParameterValue', name: 'REPO_NAME', value: REPO_NAME], [$class: 'StringParameterValue', name: 'BUILD_NUMBER', value: BUILD_ID]]
        }
    }
    finally {
        stage('Clean up') {
            sh 'echo clean'
        }
    }
}

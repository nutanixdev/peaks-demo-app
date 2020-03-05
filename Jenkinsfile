node {
    checkout scm

    try {
        stage('Run unit/integration tests'){
            sh 'make login'
            sh 'make test'
        }
        stage('Build application artifacts'){
            sh 'make build'
        }
        stage('Create release environment and run acceptance tests'){
            sh 'make release'
        }
        stage('Tag and publish release image'){
            sh 'make tag'
            sh 'make publish'
        }
        stage('Deploy release'){
            build job: "${REPO_NAME}_deploy", parameters: [[$class: 'StringParameterValue', name: 'REPO_NAME', value: REPO_NAME], [$class: 'StringParameterValue', name: 'BUILD_NUMBER', value: BUILD_ID]]
        }
    }
    finally {
        stage('Clean up') {
            sh 'make clean'
            sh 'make logout'
        }
    }
}

@Library('jenkins-aspm-scans@main') _

pipeline {
  agent any
  environment {
    ACCUKNOX_ENDPOINT = credentials('accuknox-endpoint')
    ACCUKNOX_LABEL    = credentials('accuknox-label')
    ACCUKNOX_TOKEN    = credentials('accuknox-token')
  }
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('SAST Scan') {
      steps {
        AccuKnoxSAST()
      }
    }
  }
}

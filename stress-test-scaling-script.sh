#!/bin/bash

# Script to execute stress tests and collect Kubernetes metrics

# Initial configurations
SERVICE_URL="http://localhost:80/"
TEST_DURATION="30s"
MAX_CONNECTIONS=5000
TOTAL_REQUESTS=50000
WRK_THREADS=8
OUTPUT_DIR="stress_test_results"

# Create directory for results
mkdir -p $OUTPUT_DIR

# Function to collect Kubernetes metrics
collect_metrics() {
    local i=$1
    printf "\n>>> Collecting Kubernetes metrics..."
    kubectl top pods >> "$OUTPUT_DIR/pods_metrics_${i}.txt"
    kubectl top nodes >> "$OUTPUT_DIR/nodes_metrics_${i}.txt"
}

# Apache Benchmark (ab) test
run_ab_test() {
    local i=$1
    printf "\n>>> Running Apache Benchmark (ab)... \n"
    ab -n $TOTAL_REQUESTS -c 500 $SERVICE_URL >> "$OUTPUT_DIR/ab_test_${i}.txt"
    echo "Apache Benchmark completed. Results saved."
}

# Function to collect Kubernetes metrics after ab test
collect_metrics_ab() {
    local i=$1
    printf "\n>>> Collecting Kubernetes metrics after ab test..."
    kubectl top pods >> "$OUTPUT_DIR/pods_metrics_ab_${i}.txt"
    kubectl top nodes >> "$OUTPUT_DIR/nodes_metrics_ab_${i}.txt"
}

# wrk test with different configurations
run_wrk_test() {
    local i=$1
    printf "\n>>> Running wrk with $MAX_CONNECTIONS connections for $TEST_DURATION... \n"
    wrk -c $MAX_CONNECTIONS -d $TEST_DURATION -t $WRK_THREADS $SERVICE_URL >> "$OUTPUT_DIR/wrk_test_${i}.txt"
    echo "wrk completed. Results saved."
}

# Function to collect Kubernetes metrics after wrk test
collect_metrics_wrk() {
    local i=$1
    printf "\n>>> Collecting Kubernetes metrics after wrk test..."
    kubectl top pods >> "$OUTPUT_DIR/pods_metrics_wrk_${i}.txt"
    kubectl top nodes >> "$OUTPUT_DIR/nodes_metrics_wrk_${i}.txt"
}

# Horizontal scaling
apply_horizontal_scaling() {
    #local i=$1 # Use this to scale manually
    printf "\n>>> Applying horizontal scaling... \n"
    #kubectl scale deployment dogecoin-forecasting --replicas=${i}  # Horizontal scaling in manual mode
    kubectl autoscale deployment dogecoin-forecasting --cpu-percent=80 --min=3 --max=8 # Horizontal scaling with autoscaler
    echo "Horizontal scaling applied."
}

# Vertical scaling
apply_vertical_scaling() {
    printf "\n>>> Updating YAML file for vertical scaling... \n"
    cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dogecoin-forecasting
  labels:
    app: dogecoin-forecasting-app
  namespace: default
spec:
  replicas: 7
  selector:
    matchLabels:
      app: dogecoin-forecasting-app
  template:
    metadata:
      labels:
        app: dogecoin-forecasting-app
    spec:
      containers:
        - name: dogecoin-forecasting
          image: kiritoemo6/dogecoin-forecasting
          resources:
            requests:
              memory: "512Mi"
              cpu: "500m"
            limits:
              memory: "750Mi"
              cpu: "1"
EOF
    echo "Vertical scaling applied."
}

# Full execution of tests
main() {
    printf "\n>>> Starting stress tests and data collection..."

    # Phase 1: Collect initial metrics
    collect_metrics 0

    # Phase 2: Test with Apache Benchmark
    run_ab_test 0
    collect_metrics_ab 0

    # Phase 3: Test with wrk
    run_wrk_test 0
    collect_metrics_wrk 0

    # Phase 4: Horizontal scaling
    apply_horizontal_scaling
    sleep 30  # Wait for pods to stabilize
    collect_metrics 1
    run_ab_test 1
    collect_metrics_ab 1
    run_wrk_test 1
    collect_metrics_wrk 1

    # Phase 5: Vertical scaling
    apply_vertical_scaling
    sleep 30  # Wait for pods to stabilize
    collect_metrics 2
    run_ab_test 2
    collect_metrics_ab 2
    run_wrk_test 2
    collect_metrics_wrk 2

    printf "\n>>> Stress tests completed. Results saved in $OUTPUT_DIR"
}

# Start of the script
main
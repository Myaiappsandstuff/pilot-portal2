#!/bin/bash

# Install test requirements if not already installed
pip install -r requirements-testing.txt

# Set environment variables
export LOCUST_HOST=http://localhost:5000  # Update with your actual URL

# Run Locust with web interface
locust -f tests/load_testing/locustfile.py --host=$LOCUST_HOST --web-host=0.0.0.0 --web-port=8089

# For headless testing, uncomment the following line and adjust parameters as needed
# locust -f tests/load_testing/locustfile.py --host=$LOCUST_HOST --headless -u 100 -r 10 --run-time 10m --html=load_test_report.html

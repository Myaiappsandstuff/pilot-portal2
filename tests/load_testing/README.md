# Load Testing Setup for Pilot Portal

This directory contains load testing scripts using Locust to simulate real user behavior on the Pilot Portal.

## Prerequisites

1. Python 3.8+
2. Docker and Docker Compose (if running in containers)
3. Locust and other testing libraries (install via `pip install -r requirements-testing.txt`)

## Test Users

Update `test_config.py` with actual test user credentials. The file contains a list of `TestUser` objects with email, password, and name.

## Running Tests

### 1. Web Interface Mode

```bash
# Make the script executable (Linux/Mac)
chmod +x run_load_test.sh

# Run the test with web interface
./run_load_test.sh
```

Then open a web browser and go to: http://localhost:8089

### 2. Command Line Mode (Headless)

Uncomment and modify the last line in `run_load_test.sh` for headless testing, then run:

```bash
./run_load_test.sh
```

## Test Scenarios

### Pilot Behavior
- Logs in
- Views dashboard
- Submits logsheets
- Views earnings

### Admin Behavior
- Logs in as admin
- Views admin dashboard
- Manages pilots
- Generates reports

## Customizing Tests

1. **User Behavior**: Modify the `PilotBehavior` and `AdminBehavior` classes in `locustfile.py`
2. **Test Data**: Update `test_config.py` with realistic test users
3. **Load Parameters**: Adjust the `wait_time` and task weights in the Locust user classes

## Analyzing Results

1. **Web Interface**: Real-time statistics in the browser
2. **CSV Reports**: Generated in the `--csv` directory when using the `--csv` flag
3. **HTML Report**: Generated with the `--html` flag in headless mode

## Best Practices

1. Start with a small number of users and gradually increase
2. Monitor server resources during tests
3. Run tests against a staging environment, not production
4. Update test data to match your application's data model

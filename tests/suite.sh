#!/bin/bash
source ~/.virtualenvs/desert/bin/activate

echo "Starting test run..."

# Run tests and capture output
output=$(PYTHONPATH=/home/pln/Work/DataDesert pytest tests/ -vv 2>&1)
retcode=$?

# Print stdout and stderr separately
echo "$output"

echo "Test run completed with exit code: $retcode"

# Return 0 on success, else return the number of failed tests
if [ $retcode -eq 0 ]; then
    echo "All tests passed!"
    exit 0
else
    # Count the number of failed tests from the output
    failed_tests=$(echo "$output" | grep -c "failed")
    echo "Failed tests count: $failed_tests"
    exit $failed_tests
fi

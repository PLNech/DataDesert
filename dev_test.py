#!/usr/bin/env python

import os
import subprocess
import sys

def run_test_suite():
    """Run the test suite and capture output"""
    cmd = [
        "bash", "-c",
        "source ~/.virtualenvs/desert/bin/activate && PYTHONPATH=/home/pln/Work/DataDesert pytest tests/ -vv"
    ]
    
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True,
            check=False
        )
        
        print("============= TEST OUTPUT =============")
        print(f"Return code: {result.returncode}")
        print("\n--- STDOUT ---")
        print(result.stdout)
        print("\n--- STDERR ---")
        print(result.stderr)
        print("=======================================")
        
        return result.returncode
    
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_test_suite()) 
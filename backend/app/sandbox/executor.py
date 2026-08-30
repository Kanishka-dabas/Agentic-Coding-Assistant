"""
Executes agent-generated Python code inside an isolated, throwaway Docker
container - no network access, memory/CPU capped, hard timeout.
"""

import subprocess
import tempfile
import os

from app.sandbox.limits import (
    EXECUTION_TIMEOUT_SECONDS,
    MAX_OUTPUT_BYTES,
    CONTAINER_CPU_LIMIT,
    CONTAINER_MEMORY_LIMIT,
    CONTAINER_IMAGE
)

def run_code(code:str) -> dict:
    """
    Runs `code` inside a fresh Docker container and returns what happened.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        script_path = os.path.join(tmp_dir , "generated_script.py")
        with open(script_path,'w') as f:
            f.write(code)

        docker_cmd = [
            "docker" , "run",
            "--rm" ,
            "--network" , "none",
            "--memory" , CONTAINER_MEMORY_LIMIT,
            "--cpus" , str(CONTAINER_CPU_LIMIT) ,
            "-v" , f"{tmp_dir}:/sandbox:ro",
            "-w" , "/sandbox",
            CONTAINER_IMAGE ,
            "python" , "generated_script.py"
        ]     

        try :
            result = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=EXECUTION_TIMEOUT_SECONDS
            ) 
            return {
                "success":result.returncode==0,
                "stdout":result.stdout[:MAX_OUTPUT_BYTES],
                "stderr":result.stderr[:MAX_OUTPUT_BYTES],
                "timed_out":False
            } 
        except subprocess.TimeoutExpired:
            return {
               "success":False,
                "stdout":"",
                "stderr":f"execution exceeded {EXECUTION_TIMEOUT_SECONDS}s timeout - killed",
                "timed_out":True 
            }

if __name__ == "__main__":
    test_code = "print('hello from docker sandbox')"
    print(run_code(test_code))        
            